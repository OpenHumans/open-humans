import re

from django.core.urlresolvers import reverse_lazy

from s3upload.forms import DropzoneS3UploadForm
from s3upload.views import DropzoneS3UploadFormView

from common.mixins import PrivateMixin
from common.utils import app_from_label
from data_import.views import BaseDataRetrievalView

from .models import DataFile, UserData


class DataRetrievalView(BaseDataRetrievalView):
    """
    Initiate data selfie data retrieval task.
    """
    datafile_model = DataFile


class UploadForm(DropzoneS3UploadForm):
    """
    Our storage instance is private and so django-storages wants to append a
    key to the end of the URL; this form overrides get_action() to remove it.
    """
    def get_action(self):
        url = super(UploadForm, self).get_action()
        url = re.sub(r'\?.*$', '', url)

        return url


class UploadView(PrivateMixin, DropzoneS3UploadFormView, DataRetrievalView):
    """
    Allow the user to upload a data selfie file.
    """
    model = UserData
    form_class = UploadForm
    template_name = 'data_selfie/upload.html'
    success_url = reverse_lazy('my-member-research-data')

    def get_upload_to(self):
        return ('member/{}/uploaded-data/data-selfie/'
                .format(self.request.user.id))

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
