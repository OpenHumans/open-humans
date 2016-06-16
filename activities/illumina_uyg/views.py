import os
import re

from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseBadRequest

from data_import.views import DataRetrievalView

from ..views import BaseUploadView
from . import label
from .models import UserData


class UploadView(BaseUploadView, DataRetrievalView):
    """
    Allow the user to upload an Illumina UYG file.
    """

    model = UserData
    fields = ['genome_file']
    template_name = 'illumina_uyg/upload.html'
    source = label
    success_url = reverse_lazy('my-member-research-data')

    def form_valid(self, form):
        """
        Save updated model. Don't trigger retrieval task yet. Redirect.
        """
        user_data = UserData.objects.get(user=self.request.user)

        user_data.genome_file = form.cleaned_data.get('key_name')
        user_data.save()

        # self.trigger_retrieval_task(self.request)

        return super(UploadView, self).form_valid(form)

    def form_invalid(self, form, message=None):
        if message:
            return HttpResponseBadRequest(message)
        else:
            return super(UploadView, self).form_invalid()

    def validate_upload(self):
        """
        In addition to default validation, check file name and size.
        """
        # Validate a new upload
        form = self.get_validate_upload_form()

        if form.is_valid():

            # S3 upload successful, now check file matches expected formats.
            genome_file_key = form.cleaned_data.get('key_name')

            # Check that name matches expected format.
            if not re.match('PG[0-9]+-BLD.genome.vcf.gz',
                            os.path.basename(genome_file_key)):
                err_msg = ("Filename doesn't match expected format "
                           '(see instructions above).')
                return self.form_invalid(form, message=err_msg)

            # Create model with file field (but don't save) to access methods.
            # Check that file size is expected size.
            user_data = UserData.objects.get(user=self.request.user)
            user_data.genome_file = form.cleaned_data.get('key_name')
            if not user_data.genome_file.size > 1073741824:
                err_msg = ("File size too small. Illumina UYG files are "
                           "expected to be at least 1 GB in size.")
                return self.form_invalid(form, message=err_msg)

            # If these checks pass, return form_valid.
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
