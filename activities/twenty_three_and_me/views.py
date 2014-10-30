from datetime import datetime

import requests

from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import RedirectView

from ..models import get_upload_path
from .models import ActivityDataFile, ActivityUser, DataExtractionTask


class RequestDataExportView(RedirectView):
    """Initiate of data export task and redirect to user's data page"""
    url = reverse_lazy('profile_research_data')

    def post(self, request):
        if 'activity' in request.POST:
            if 'profile_id' not in request.POST:
                messages.error(request, "Please select a profile.")
                self.url = reverse_lazy('activies:23andme:complete-import')
            else:
                study_user, _ = ActivityUser.objects.get_or_create(
                    user=request.user)
                data_file = ActivityDataFile(study_user=study_user)
                filename = '23andme-%s.tar.bz2' % (
                    datetime.now().strftime("%Y%m%d%H%M%S"))
                # activity_file_upload_path creates locations for files used by
                # ActivityDataFile models (i.e. its the "upload_to" argument)
                s3_key_name = get_upload_path(data_file, filename)
                data_file.file.name = s3_key_name
                data_file.save()
                data_extraction_task = DataExtractionTask(data_file=data_file)
                data_extraction_task.save()

                # Ask Flask app to put together this dataset.
                url = 'https://oh-data-extraction-staging.herokuapp.com/23andme'
                access_token = request.user.social_auth.get(
                    provider='23andme').extra_data['access_token']
                data_extraction_params = {
                    'access_token': access_token,
                    'profile_id': request.POST['profile_id'],
                    's3_key_name': s3_key_name,
                    }
                requests.get(url,  params=data_extraction_params)

                # Update with the expected file location.
                message = ("Thanks! We've started the data import " +
                           "for your 23andme data from profile.")
                messages.success(request, message)
        return super(RequestDataExportView, self).post(request)
