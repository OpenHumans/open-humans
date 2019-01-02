import logging

from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.views.generic import View

from ipware.ip import get_ip

from .models import DataFile, DataFileKey, NewDataFileAccessLog

UserModel = get_user_model()

logger = logging.getLogger(__name__)


class DataFileDownloadView(View):
    """
    Log a download and redirect the requestor to its actual location.
    """

    def get_and_log(self, request):
        """
        Logs the file being accessed and then returns a redirect to the s3 url
        for that file
        """
        user = (request.user if request.user.is_authenticated else None)

        access_log = NewDataFileAccessLog(
            user=user,
            ip_address=get_ip(request),
            data_file=self.data_file)
        access_log.save()

        return HttpResponseRedirect(self.data_file.file_url_as_attachment)

    # pylint: disable=attribute-defined-outside-init
    def get(self, request, *args, **kwargs):
        self.data_file = DataFile.objects.get(pk=self.kwargs.get('pk'))

        unavailable = (
            hasattr(self.data_file, 'parent_project_data_file') and
            self.data_file.parent_project_data_file.completed is False)
        if unavailable:
            return HttpResponseForbidden('<h1>This file is unavailable.</h1>')

        if self.data_file.has_access(user=request.user):
            return self.get_and_log(request)

        query_key = request.GET.get('key', None)
        if query_key:
            key_qs = DataFileKey.objects.filter(datafile=self.data_file)
            key_qs = key_qs.filter(key=query_key)
            if key_qs.exists():
                if not key_qs.get().expired:
                    return self.get_and_log(request)
        return HttpResponseForbidden(
            '<h1>You are not authorized to view this file.</h1>')
