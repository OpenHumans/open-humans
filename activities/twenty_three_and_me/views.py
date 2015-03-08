import requests

from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import CreateView

from data_import.views import BaseDataRetrievalView
from ..views import BaseJSONDataView
from .models import DataFile, ProfileId, UserData


class DataRetrievalView(BaseDataRetrievalView):
    """
    Initiate 23andme data retrieval task.
    """
    datafile_model = DataFile

    def get_app_task_params(self, request):
        return request.user.twenty_three_and_me.get_retrieval_params()


class ProfileIdCreateView(CreateView, DataRetrievalView):
    model = ProfileId
    template_name = 'twenty_three_and_me/complete-import-23andme.html'
    success_url = reverse_lazy('activities:23andme:request-data-retrieval')

    def form_valid(self, form):
        """
        Save ProfileId data, then call DataRetrievalView's post to start task.
        """
        self.object = form.save()
        return DataRetrievalView.post(self, self.request)

    def dispatch(self, request, *args, **kwargs):
        """
        Cache request as instance attribute, used for DataRetrievalView.
        """
        self.request = request
        return super(ProfileIdCreateView, self).dispatch(
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
        user_data = UserData.objects.get(user=request.user)
        access_token = user_data.get_access_token()
        headers = {'Authorization': 'Bearer %s' % access_token}
        names_request = requests.get('https://api.23andme.com/1/names/',
                                     headers=headers, verify=False)
        if names_request.status_code == 200:
            return names_request.json()
        return None
