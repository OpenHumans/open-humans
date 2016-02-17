from django.core.urlresolvers import reverse_lazy

from s3upload.views import DropzoneS3UploadFormView

from common.mixins import PrivateMixin
from common.utils import app_label_to_app_config
from data_import.utils import get_upload_dir, get_upload_dir_validator

from .models import DataSelfieDataFile


class UploadView(PrivateMixin, DropzoneS3UploadFormView):
    """
    Allow the user to upload a data selfie file.
    """
    template_name = 'data_selfie/upload.html'
    success_url = reverse_lazy('my-member-data-selfie')

    def get_upload_to(self):
        return get_upload_dir(DataSelfieDataFile, self.request.user)

    def get_upload_to_validator(self):
        return get_upload_dir_validator(DataSelfieDataFile, self.request.user)

    def get_context_data(self, **kwargs):
        context = super(UploadView, self).get_context_data(**kwargs)

        context.update({
            'app': app_label_to_app_config('data_selfie'),
        })

        return context

    def form_valid(self, form):
        """
        Save the uploaded DataFile.
        """
        data_file = DataSelfieDataFile(file=form.cleaned_data.get('key_name'),
                                       user=self.request.user,
                                       source='data_selfie')
        data_file.save()

        return super(UploadView, self).form_valid(form)
