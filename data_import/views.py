import logging

from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from django.views.generic import RedirectView

from ipware.ip import get_ip

from rest_framework import serializers
from rest_framework.generics import ListAPIView

from .models import DataFile, NewDataFileAccessLog, RemovedData
from .serializers import RemovedDataSerializer

UserModel = get_user_model()

logger = logging.getLogger(__name__)


class DataFileDownloadView(RedirectView):
    """
    Log a download and redirect the requestor to its actual location.
    """

    permanent = False

    # pylint: disable=attribute-defined-outside-init
    def get(self, request, *args, **kwargs):
        self.data_file = DataFile.objects.get(pk=self.kwargs.get('pk'))

        if not self.data_file.has_access(user=request.user):
            return HttpResponseForbidden(
                '<h1>You do not have permission to access this file.</h1>')

        unavailable = (
            hasattr(self.data_file, 'parent_project_data_file') and
            self.data_file.parent_project_data_file.completed is False)
        if unavailable:
            return HttpResponseForbidden('<h1>This file is unavailable.</h1>')

        return super(DataFileDownloadView, self).get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        user = (self.request.user
                if self.request.user.is_authenticated
                else None)

        access_log = NewDataFileAccessLog(
            user=user,
            ip_address=get_ip(self.request),
            data_file=self.data_file)
        access_log.save()

        return self.data_file.file_url_as_attachment


class RemovedDataView(ListAPIView):
    """
    Return a list of deleted data.
    """

    queryset = RemovedData.objects.all()
    serializer_class = RemovedDataSerializer
