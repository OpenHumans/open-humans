from time import time

from django.core.urlresolvers import reverse_lazy

from s3upload.views import DropzoneS3UploadFormView

from common.mixins import PrivateMixin
from common.utils import app_from_label
from data_import.views import DataRetrievalView

from .models import UserData


class UploadView(PrivateMixin, DropzoneS3UploadFormView, DataRetrievalView):
    """
    Allow the user to upload a 23andMe file.
    """
    model = UserData
    fields = ['genome_file']
    template_name = 'twenty_three_and_me/upload.html'
    success_url = reverse_lazy('my-member-research-data')

    def get_upload_to(self):
        return ('member/{}/uploaded-data/data-selfie/{}/'
                .format(self.request.user.id, int(time())))

    def get_upload_to_validator(self):
        return (r'^member/{}/uploaded-data/data-selfie/\d+/'
                .format(self.request.user.id))

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
        user_data = self.get_object()

        user_data.genome_file = form.cleaned_data.get('key_name')
        user_data.save()

        self.trigger_retrieval_task(self.request)

        return super(UploadView, self).form_valid(form)

    def get_object(self, queryset=None):
        return UserData.objects.get(user=self.request.user.pk)
