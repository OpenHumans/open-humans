from django.apps import apps
from django.contrib import messages as django_messages
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import View

from s3upload.views import DropzoneS3UploadFormView

from common.mixins import PrivateMixin
from common.utils import app_label_to_verbose_name
from data_import.utils import get_upload_dir, get_upload_dir_validator


class DisconnectView(PrivateMixin, View):
    """
    Delete any credentials the user may have.
    """

    source = None

    def post(self, request):
        user_data = getattr(request.user, self.source)
        user_data.disconnect()

        django_messages.success(request, (
            'You have removed your connection to {}.'.format(
                app_label_to_verbose_name(self.source))))

        return HttpResponseRedirect(reverse_lazy('my-member-research-data'))


class BaseUploadView(DropzoneS3UploadFormView):
    """
    A base clase for upload views that use the Dropzone S3 upload form.
    """

    def get_upload_to(self):
        return get_upload_dir(self.model)

    def get_upload_to_validator(self):
        return get_upload_dir_validator(self.model)

    def get_context_data(self, **kwargs):
        context = super(BaseUploadView, self).get_context_data(**kwargs)

        context.update({
            'app': apps.get_app_config(self.source),
        })

        return context
