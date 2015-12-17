from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import UpdateView

from common.mixins import PrivateMixin
from common.utils import app_from_label
from data_import.views import BaseDataRetrievalView
from .models import DataFile, UserData


class DataRetrievalView(BaseDataRetrievalView):
    """
    Initiate 23andMe data retrieval task.
    """
    datafile_model = DataFile

    def get_app_task_params(self, request):
        return UserData.objects.get(user=request.user).get_retrieval_params()


class UploadView(PrivateMixin, UpdateView, DataRetrievalView):
    """
    Allow the user to upload a 23andMe file.
    """
    model = UserData
    fields = ['genome_file']
    template_name = 'twenty_three_and_me/upload.html'
    success_url = reverse_lazy('my-member-research-data')

    def get_context_data(self, **kwargs):
        context = super(UploadView, self).get_context_data(**kwargs)

        context.update({
            'app': app_from_label('twenty_three_and_me'),
        })

        return context

    def form_valid(self, form):
        """
        Save updated model, then trigger retrieval task and redirect.
        """
        response = super(UploadView, self).form_valid(form)

        self.trigger_retrieval_task(self.request)

        return response

    def get_object(self, queryset=None):
        return UserData.objects.get(user=self.request.user.pk)
