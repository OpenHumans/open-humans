from datetime import datetime

import requests

from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import RedirectView

from .models import get_upload_path, ActivityDataFile, ActivityUser


class RequestDataExportView(RedirectView):
    """
    Initiate of data export task and redirect to user's data page
    """
    url = reverse_lazy('profile_research_data')

    def post(self, request):
        if 'activity' in request.POST:
            if request.POST['activity'] == '23andme':
                if 'profile_id' not in request.POST:
                    messages.error(request, "Please select a profile.")
                    self.url = reverse_lazy('profile_research_data_complete_23andme')
                else:
                    # get_upload_path creates locations for files in
                    # ActivityDataFile23andme (i.e. its the "upload_to" arg).
                    study_user, _ = ActivityUser.objects.get_or_create(user=request.user)
                    userdata = ActivityDataFile(study_user=study_user)
                    filename = '23andme-%s.tar.bz2' % (datetime.now().strftime("%Y%m%d%H%M%S"))
                    s3_key_name = get_upload_path(userdata, filename)

                    # Ask Flask app to put together this dataset.
                    url = 'https://oh-data-extraction-staging.herokuapp.com/23andme'
                    access_token = request.user.social_auth.get(provider='23andme').extra_data['access_token']
                    data_extraction_params = {
                        'access_token': access_token,
                        'profile_id': request.POST['profile_id'],
                        's3_key_name': s3_key_name
                        }
                    requests.get(url,  params=data_extraction_params)

                    # Update with the expected file location.
                    userdata.file.name = s3_key_name
                    userdata.save()
                    message = ("Thanks! We've started the data import " +
                               "for your 23andme data from profile.")
                    messages.success(request, message)
        return super(RequestDataExportView, self).post(request)
