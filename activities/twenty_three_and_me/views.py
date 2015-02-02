import requests

from django.contrib import messages
from django.core.urlresolvers import reverse_lazy

from data_import.views import BaseDataRetrievalView
from ..views import BaseJSONDataView
from .models import DataFile, UserData, DataRetrievalTask


def access_token_from_request(request):
    """
    Get the access token from the most recent 23andMe association.
    """
    user_social_auth = (request.user.social_auth.filter(provider='23andme')
                        .order_by('-id')[0])

    return user_social_auth.extra_data['access_token']


class DataRetrievalView(BaseDataRetrievalView):
    """
    Initiate 23andme data retrieval task.
    """
    datafile_model = DataFile
    userdata_model = UserData
    dataretrievaltask_model = DataRetrievalTask

    def get_task_params(self, **kwargs):
        kwargs.update({
            'profile_id': self.request.POST['profile_id'],
            'access_token': access_token_from_request(self.request)
        })
        return super(DataRetrievalView, self).get_task_params(**kwargs)

    def post(self, request, *args, **kwargs):
        # Is passing and double-checking activity unnecessary?
        if ('activity' not in request.POST or
                request.POST['activity'] != '23andme'):
            return self.redirect()

        if 'profile_id' not in request.POST:
            messages.error(request, 'Please select a profile.')
            self.redirect_url = reverse_lazy(
                'activities:23andme:complete-import')
            return self.redirect()
        return super(DataRetrievalView, self).post(
            request, *args, **kwargs)


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
