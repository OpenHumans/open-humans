import requests
import urlparse

from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import RedirectView

from raven.contrib.django.raven_compat.models import client

from common.models import get_upload_path
from ..views import BaseJSONDataView
from .models import DataFile, UserData, DataRetrievalTask


def access_token_from_request(request):
    """
    Get the access token from the most recent 23andMe association.
    """
    user_social_auth = (request.user.social_auth.filter(provider='23andme')
                        .order_by('-id')[0])

    return user_social_auth.extra_data['access_token']


class RequestDataExportView(RedirectView):
    """
    Initiate of data export task and redirect to user's data page
    """
    url = reverse_lazy('my-member-research-data')

    def post(self, request):
        # TODO: Is passing and checking the 'activity' necessary or desired?
        if ('activity' not in request.POST or
                request.POST['activity'] != '23andme'):
            return super(RequestDataExportView, self).post(request)

        if 'profile_id' not in request.POST:
            messages.error(request, 'Please select a profile.')
            self.url = reverse_lazy('activies:23andme:complete-import')
            return super(RequestDataExportView, self).post(request)

        user_data, _ = UserData.objects.get_or_create(user=request.user)

        data_file = DataFile(user_data=user_data)

        filename = '23andme-%s.tar.bz2' % (
            datetime.now().strftime('%Y%m%d%H%M%S'))

        # get_upload_path generates locations for files used by
        # DataFile models (i.e. its the "upload_to" argument)
        s3_key_name = get_upload_path(data_file, filename)

        data_file.file.name = s3_key_name
        data_file.save()

        retrieval_task = DataRetrievalTask(data_file=data_file)
        retrieval_task.save()

        # Ask our Flask app to put together this dataset.
        url = urlparse.urljoin(settings.DATA_PROCESSING_URL, '/23andme')

        access_token = access_token_from_request(request)

        update_url = urlparse.urljoin('https://' +
                                      get_current_site(request).domain,
                                      '/activity/task_update/')

        data_retrieval_params = {
            'access_token': access_token,
            'profile_id': request.POST['profile_id'],
            's3_key_name': s3_key_name,
            's3_bucket_name': settings.AWS_STORAGE_BUCKET_NAME,
            'update_url': update_url,
        }

        task_req = requests.get(url, params=data_retrieval_params)

        if task_req.status_code != 200:
            # FWIW - this may update as success later if the
            # data retrieval app worked despite this.
            retrieval_task.status = retrieval_task.TASK_FAILED
            retrieval_task.save()

            message = ('Sorry! It looks like our data retrieval ' +
                       'server might be down.')

            messages.error(request, message)

            error_data = {
                'url': url,
                's3_key_name': data_retrieval_params['s3_key_name'],
                's3_bucket_name': data_retrieval_params['s3_bucket_name'],
            }

            error_msg = 'Open Humans Data Retrieval not returning 200 status.'

            client.captureMessage(error_msg, error_data=error_data)
        else:
            message = ("Thanks! We've started the data import " +
                       'for your 23andme data from profile.')

            messages.success(request, message)

        return super(RequestDataExportView, self).post(request)


class TwentyThreeAndMeNamesJSON(BaseJSONDataView):
    """
    Return JSON containing 23andme names data for a profile.

    Because some 23andme accounts contain genetic data for more than one
    individual, we need to ask the user to select between profiles - thus
    we need to access the names to enable the user to do that selection.
    """
    @staticmethod
    def get_data(request):
        access_token = access_token_from_request(request)

        headers = {'Authorization': 'Bearer %s' % access_token}

        names_request = requests.get('https://api.23andme.com/1/names/',
                                     headers=headers, verify=False)

        if names_request.status_code == 200:
            return names_request.json()

        return None
