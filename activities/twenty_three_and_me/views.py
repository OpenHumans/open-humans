from django.core.urlresolvers import reverse_lazy

from s3upload.views import DropzoneS3UploadFormView

from common.mixins import PrivateMixin
from common.utils import app_label_to_app_config
from data_import.utils import get_upload_dir, get_upload_dir_validator
from data_import.views import DataRetrievalView

from .models import UserData


class UploadView(PrivateMixin, DropzoneS3UploadFormView, DataRetrievalView):
    """
    Allow the user to upload a 23andMe file.
    """
    model = UserData
    fields = ['genome_file']
    template_name = 'twenty_three_and_me/upload.html'
    source = 'twenty_three_and_me'
    success_url = reverse_lazy('my-member-research-data')

    def get_upload_to(self):
        return get_upload_dir(self.model, self.request.user)

    def get_upload_to_validator(self):
        return get_upload_dir_validator(self.model, self.request.user)

    def get_context_data(self, **kwargs):
        context = super(UploadView, self).get_context_data(**kwargs)

        context.update({
            'app': app_label_to_app_config('twenty_three_and_me'),
        })

        return context

    def form_valid(self, form):
        """
        Save updated model, then trigger retrieval task and redirect.
        """
        user_data = UserData.objects.get(user=self.request.user)

        user_data.genome_file = form.cleaned_data.get('key_name')
        user_data.save()

        self.trigger_retrieval_task(self.request)

        return super(UploadView, self).form_valid(form)
