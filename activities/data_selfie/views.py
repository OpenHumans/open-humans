from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import UpdateView

from common.mixins import PrivateMixin
from common.utils import app_from_label
from data_import.views import BaseDataRetrievalView
from .models import DataFile, UserData


class DataRetrievalView(BaseDataRetrievalView):
    """
    Initiate data selfie data retrieval task.
    """
    datafile_model = DataFile


class UploadView(PrivateMixin, UpdateView, DataRetrievalView):
    """
    Allow the user to upload a data selfie file.
    """
    model = UserData
    fields = ['file']
    template_name = 'data_selfie/upload.html'
    success_url = reverse_lazy('my-member-research-data')

    def get_context_data(self, **kwargs):
        context = super(UploadView, self).get_context_data(**kwargs)

        context.update({
            'app': app_from_label('data_selfie'),
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
