import logging
import json

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

    def get_and_log(self, request, key_object=None):
        """
        Logs the file being accessed and then returns a redirect to the s3 url
        for that file
        """
        user = (request.user if request.user.is_authenticated else None)

        if key_object:
            key = {'id': key_object.id,
                   'created': key_object.created.isoformat(),
                   'key': key_object.key,
                   'datafile_id': key_object.datafile_id,
                   'key_creation_ip_address': key_object.ip_address,
                   'access_token': key_object.access_token,
                   'project_id': key_object.project_id}
        else:
            key = {}
        access_log = NewDataFileAccessLog(
            user=user,
            ip_address=get_ip(request),
            data_file=self.data_file,
            data_file_key=json.dumps(key))
        access_log.save()

        return HttpResponseRedirect(self.data_file.file_url_as_attachment)

    # pylint: disable=attribute-defined-outside-init
    def get(self, request, *args, **kwargs):
        data_file_qs = DataFile.objects.filter(pk=self.kwargs.get('pk'))
        if data_file_qs.exists():
            self.data_file = data_file_qs.get()
            unavailable = (
                hasattr(self.data_file, 'parent_project_data_file') and
            self.data_file.parent_project_data_file.completed is False)
        else:
            unavailable = True
        if unavailable:
            return HttpResponseForbidden('<h1>This file is unavailable.</h1>')

        if self.data_file.has_access(user=request.user):
            return self.get_and_log(request)

        query_key = request.GET.get('key', None)
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
            '<h1>You are not authorized to view this file.</h1>')
