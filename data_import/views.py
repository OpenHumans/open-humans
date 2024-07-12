import logging

from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, TemplateView, UpdateView, View

from django_filters.rest_framework import DjangoFilterBackend
from ipware import get_client_ip
from rest_framework.generics import ListAPIView
from waffle import get_waffle_flag_model

from common.mixins import NeverCacheMixin, PrivateMixin

from .filters import AccessLogFilter
from .forms import DataTypeForm
from .models import (
    AWSDataFileAccessLog,
    DataFile,
    DataFileKey,
    DataType,
    NewDataFileAccessLog,
)
from .permissions import LogAPIAccessAllowed
from common.mixins import NeverCacheMixin
from data_import.serializers import (
    AWSDataFileAccessLogSerializer,
    NewDataFileAccessLogSerializer,
    serialize_datafile_to_dict,
)
from private_sharing.api_authentication import CustomOAuth2Authentication
from private_sharing.api_permissions import HasValidProjectToken

UserModel = get_user_model()
FlagModel = get_waffle_flag_model()

logger = logging.getLogger(__name__)


class DataFileDownloadView(View):
    """
    Log a download and redirect the requestor to its actual location.
    """

    def get_and_log(self, request, key_object=None):
        """
        Redirect to S3 URL for file. Log access if this feature is active.

        Feature activity for specific users is based on whether the datafile
        belongs to that user, not based on the user doing the download.
        """
        aws_url = self.data_file.file_url_as_attachment
        url = "{0}&x-oh-key={1}".format(aws_url, key_object.key)

        # Check feature flag based on file user (subject), not request user.
        flag = FlagModel.get("datafile-access-logging")
        if not flag.is_active(request=request, subject=self.data_file.user):
            return HttpResponseRedirect(url)

        user = request.user if request.user.is_authenticated else None

        access_log = NewDataFileAccessLog(
            user=user, ip_address=get_client_ip(request), data_file=self.data_file
        )
        access_log.data_file_key = {
            "created": key_object.created.isoformat(),
            "key": key_object.key,
            "datafile_id": key_object.datafile_id,
            "key_creation_ip_address": key_object.ip_address,
            "access_token": key_object.access_token,
            "project_id": key_object.project_id,
        }

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


class NewDataFileAccessLogView(NeverCacheMixin, ListAPIView):
    """
    Custom API endpoint returning logs of file access requests for OHLOG_PROJECT_ID
    """

    authentication_classes = (CustomOAuth2Authentication,)
    filter_backends = (AccessLogFilter, DjangoFilterBackend)
    filterset_fields = ("date",)
    permission_classes = (HasValidProjectToken, LogAPIAccessAllowed)
    serializer_class = NewDataFileAccessLogSerializer

    def get_queryset(self):
        queryset = NewDataFileAccessLog.objects.filter(
            serialized_data_file__user_id=self.request.user.id
        )
        return queryset


class AWSDataFileAccessLogView(NeverCacheMixin, ListAPIView):
    """
    Custom API endpoint returning logs of AWS file access events for OHLOG_PROJECT_ID
    """

    authentication_classes = (CustomOAuth2Authentication,)
    filter_backends = (AccessLogFilter, DjangoFilterBackend)
    filterset_fields = ("time",)
    permission_classes = (HasValidProjectToken, LogAPIAccessAllowed)
    serializer_class = AWSDataFileAccessLogSerializer

    def get_queryset(self):
        queryset = AWSDataFileAccessLog.objects.filter(
            serialized_data_file__user_id=self.request.user.id
        )
        return queryset


class DataTypesSortedMixin(object):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        datatypes_sorted = DataType.sorted_by_ancestors()
        try:
            max_depth = max([i["depth"] for i in datatypes_sorted])
        except ValueError:
            max_depth = 0
        context.update({"datatypes_sorted": datatypes_sorted, "max_depth": max_depth})
        return context


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


class DataTypesCreateView(
    PrivateMixin, DataTypesSortedMixin, FormEditorMixin, CreateView
):
    """
    Create a new DataType.
    """

    form_class = DataTypeForm
    template_name = "data_import/datatypes-create.html"

    def get_success_url(self):
        return reverse("data-management:datatypes-list")


class DataTypesUpdateView(
    PrivateMixin, DataTypesSortedMixin, FormEditorMixin, UpdateView
):
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
