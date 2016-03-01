from django.apps import apps
from django.core.urlresolvers import reverse_lazy

from s3upload.views import DropzoneS3UploadFormView

from common.mixins import PrivateMixin
from data_import.utils import get_upload_dir, get_upload_dir_validator
from data_import.views import DataRetrievalView

from . import label
from .models import UserData


class UploadView(PrivateMixin, DropzoneS3UploadFormView, DataRetrievalView):
    """
    Allow the user to upload a 23andMe file.
    """
    model = UserData
    fields = ['genome_file']
    template_name = 'illumina_uyg/upload.html'
    source = label
    success_url = reverse_lazy('my-member-research-data')

    def get_upload_to(self):
        return get_upload_dir(self.model, self.request.user)

    def get_upload_to_validator(self):
        return get_upload_dir_validator(self.model, self.request.user)

    def get_context_data(self, **kwargs):
        context = super(UploadView, self).get_context_data(**kwargs)

        context.update({
            'app': apps.get_app_config(self.source),
        })

        return context

    def form_valid(self, form):
        """
        Save updated model. Don't trigger retrieval task yet. Redirect.
        """
        user_data = UserData.objects.get(user=self.request.user)

        user_data.genome_file = form.cleaned_data.get('key_name')
        user_data.save()

        # self.trigger_retrieval_task(self.request)

        return super(UploadView, self).form_valid(form)
