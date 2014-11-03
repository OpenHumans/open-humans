from datetime import datetime
import json

import bugsnag
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
                extraction_task = DataExtractionTask(data_file=data_file)
                extraction_task.save()

                # Ask Flask app to put together this dataset.
                url = 'https://oh-data-exttraction-staging.herokuapp.com/23andme'
                access_token = request.user.social_auth.get(
                    provider='23andme').extra_data['access_token']
                data_extraction_params = {
                    'access_token': access_token,
                    'profile_id': request.POST['profile_id'],
                    's3_key_name': s3_key_name,
                    }
                task_req = requests.get(url,  params=data_extraction_params)
                if task_req.status_code != 200:
                    # FWIW - this may update as success later if the
                    # data extraction app worked despite this.
                    extraction_task.status = extraction_task.TASK_FAILED
                    extraction_task.save()
                    message = ("Sorry! It looks like our data extraction " +
                               "server might be down.")
                    messages.error(request, message)
                    # TODO: Use BugSnag, but be careful about sharing env.
                    # error_data = {
                    #     'url': url,
                    #     's3_key_name': data_extraction_params['s3_key_name']
                    #     }
                    # error_msg = ("Open Humans Data Extraction not returning " +
                    #              "200 status.\n%s" % json.dumps(error_data))
                    # bugsnag.notify(Exception(error_msg))
                else:
                    message = ("Thanks! We've started the data import " +
                               "for your 23andme data from profile.")
                    messages.success(request, message)
        return super(RequestDataExportView, self).post(request)
