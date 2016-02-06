from time import time

from django.core.urlresolvers import reverse_lazy

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


class UploadView(PrivateMixin, DropzoneS3UploadFormView, DataRetrievalView):
    """
    Allow the user to upload a data selfie file.
    """
    model = UserData
    template_name = 'data_selfie/upload.html'
    success_url = reverse_lazy('my-member-data-selfie')

    def get_upload_to(self):
        return ('member/{}/uploaded-data/data-selfie/{}/'
                .format(self.request.user.id, int(time())))

    def get_upload_to_validator(self):
        return (r'^member/{}/uploaded-data/data-selfie/\d+/'
                .format(self.request.user.id))

    def get_context_data(self, **kwargs):
        context = super(UploadView, self).get_context_data(**kwargs)

        context.update({
            'app': app_from_label('data_selfie'),
        })

        return context

    def form_valid(self, form):
        """
        Save the uploaded DataFile.
        """
        data_file = DataFile(file=form.cleaned_data.get('key_name'),
                             user_data=self.get_object())

        data_file.save()

        return super(UploadView, self).form_valid(form)

    def get_object(self, queryset=None):
        return UserData.objects.get(user=self.request.user.pk)
