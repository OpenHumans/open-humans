from time import time

from django.apps import apps
from django.core.urlresolvers import reverse_lazy

from s3upload.views import DropzoneS3UploadFormView

from common.mixins import PrivateMixin

from . import label
from .models import DataSelfieDataFile


class UploadView(PrivateMixin, DropzoneS3UploadFormView):
    """
    Allow the user to upload a data selfie file.
    """
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
            'app': apps.get_app_config(label),
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
