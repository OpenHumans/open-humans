import logging

from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, TemplateView, UpdateView, View

from ipware.ip import get_ip

from common.mixins import NeverCacheMixin, PrivateMixin

from .forms import DataTypeForm
from .models import DataFile, DataFileKey, DataType, NewDataFileAccessLog
from data_import.serializers import serialize_datafile_to_dict

UserModel = get_user_model()

logger = logging.getLogger(__name__)


class DataFileDownloadView(View):
    """
    Log a download and redirect the requestor to its actual location.
    """

    def get_and_log(self, request, key_object=None):
        """
        Logs the file being accessed and then returns a redirect to the s3 url
        for that file
        """
        user = request.user if request.user.is_authenticated else None

        access_log = NewDataFileAccessLog(
            user=user, ip_address=get_ip(request), data_file=self.data_file
        )
        access_log.data_file_key = {
            "id": key_object.id,
            "created": key_object.created.isoformat(),
            "key": key_object.key,
            "datafile_id": key_object.datafile_id,
            "key_creation_ip_address": key_object.ip_address,
            "access_token": key_object.access_token,
            "project_id": key_object.project_id,
        }

        aws_url = self.data_file.file_url_as_attachment
        url = "{0}&x-oh-key={1}".format(aws_url, key_object.key)
        access_log.aws_url = url

        access_log.serialized_data_file = serialize_datafile_to_dict(self.data_file)
        access_log.save()

        return HttpResponseRedirect(url)

    # pylint: disable=attribute-defined-outside-init
    def get(self, request, *args, **kwargs):
        data_file_qs = DataFile.objects.filter(pk=self.kwargs.get("pk"))
        if data_file_qs.exists():
            self.data_file = data_file_qs.get()
            unavailable = (
                hasattr(self.data_file, "parent_project_data_file")
                and self.data_file.parent_project_data_file.completed is False
            )
        else:
            unavailable = True
        if unavailable:
            return HttpResponseForbidden("<h1>This file is unavailable.</h1>")

        query_key = request.GET.get("key", None)
        if query_key:
            key_qs = DataFileKey.objects.filter(datafile_id=self.data_file.id)
            key_qs = key_qs.filter(key=query_key)
            if key_qs.exists():
                # exists() is only a method for querysets
                key_object = key_qs.get()
                # Now we need the actual object
                if not key_object.expired:
                    return self.get_and_log(request, key_object=key_object)
        return HttpResponseForbidden(
            "<h1>You are not authorized to view this file.</h1>"
        )


class DataTypesListView(NeverCacheMixin, TemplateView):
    """
    List all DataTypes.
    """

    template_name = "data_import/datatypes-list.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        datatypes_sorted = DataType.sorted_by_ancestors()
        try:
            max_depth = max([i["depth"] for i in datatypes_sorted])
        except ValueError:
            max_depth = 0
        context.update({"datatypes_sorted": datatypes_sorted, "max_depth": max_depth})
        return context


class DataTypesDetailView(NeverCacheMixin, DetailView):
    """
    Information about a DataType.
    """

    model = DataType
    template_name = "data_import/datatypes-detail.html"


class FormEditorMixin(object):
    """
    Override get_form_kwargs to pass request user as 'editor' kwarg to a form.
    """

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs["editor"] = self.request.user.member
        return kwargs


class DataTypesCreateView(PrivateMixin, FormEditorMixin, CreateView):
    """
    Create a new DataType.
    """

    form_class = DataTypeForm
    template_name = "data_import/datatypes-create.html"

    def get_success_url(self):
        return reverse("data-management:datatypes-list")


class DataTypesUpdateView(PrivateMixin, FormEditorMixin, UpdateView):
    """
    Edit a DataType.
    """

    model = DataType
    form_class = DataTypeForm
    template_name = "data_import/datatypes-update.html"

    def get_success_url(self):
        return reverse(
            "data-management:datatypes-detail", kwargs={"pk": self.object.id}
        )
