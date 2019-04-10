import logging

from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.views.generic import View

from django_filters.rest_framework import DjangoFilterBackend
from ipware.ip import get_ip
from rest_framework.generics import ListAPIView

from .filters import AccessLogFilter
from .models import AWSDataFileAccessLog, DataFile, DataFileKey, NewDataFileAccessLog
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


class NewDataFileAccessLogView(NeverCacheMixin, ListAPIView):
    """
    Return the list of public data files.
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
    Return the list of public data files.
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
