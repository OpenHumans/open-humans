from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic.edit import UpdateView

from data_import.views import BaseDataRetrievalView
from .models import DataFile, UserData


class DataRetrievalView(BaseDataRetrievalView):
    """
    Initiate 23andMe data retrieval task.
    """
    datafile_model = DataFile

    def get_app_task_params(self, request):
        return request.user.twenty_three_and_me.get_retrieval_params()


class UploadView(UpdateView, DataRetrievalView):
    """
    Allow the user to upload a 23andMe file.
    """
    model = UserData
    fields = ['genome_file']
    template_name = 'twenty_three_and_me/upload.html'
    success_url = reverse_lazy('my-member-research-data')

    def form_valid(self, form):
        """
        Save updated model, then trigger retrieval task and redirect.
        """
        super(UploadView, self).form_valid(form)
        self.trigger_retrieval_task(self.request)
        return HttpResponseRedirect(self.get_success_url())

    def get_object(self, queryset=None):
        return UserData.objects.get(user=self.request.user)
