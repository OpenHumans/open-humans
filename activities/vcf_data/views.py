import os
import re

from django.apps import apps
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import Http404, HttpResponseBadRequest
from django.views.generic import DeleteView, UpdateView, ListView

from common.mixins import LargePanelMixin, PrivateMixin
from data_import.views import DataRetrievalView

from ..views import BaseUploadView
from .forms import VCFDataForm
from .models import UserData, VCFData
from . import label


class UploadVCFDataView(BaseUploadView, DataRetrievalView):
    """
    Allow the user to upload a Genome or Exome VCF file.
    """

    model = VCFData
    fields = ['vcf_file']
    template_name = 'vcf_data/upload.html'
    source = label

    def get_success_url(self):
        return reverse('activities:genome-exome-data:file',
                       args=[self.object.id])

    def form_valid(self, form):
        """
        Save updated model. Don't trigger retrieval, redirect to edit view.
        """
        user_data = UserData.objects.get(user=self.request.user)
        vcf_data = VCFData(user_data=user_data,
                           vcf_file=form.cleaned_data.get('key_name'))

        if not user_data.is_connected:
            self.send_connection_email()

        vcf_data.save()

        # self.trigger_retrieval_task(self.request)
        return super(UploadVCFDataView, self).form_valid(form)

    # pylint: disable=arguments-differ
    def form_invalid(self, form, message=None):
        if message:
            return HttpResponseBadRequest(message)
        else:
            return super(UploadVCFDataView, self).form_invalid()

    @staticmethod
    def check_vcf_key_name(vcf_key_name):
        """
        Check that uploaded file looks like VCF data.
        """
        # Check that name matches expected format.
        if not re.search('.vcf(.gz|.bz2|.zip|)$',
                         os.path.basename(vcf_key_name)):
            err_msg = ("Filename doesn't match expected format "
                       '(see instructions above).')
            return err_msg
        if re.search('genotyping',
                     os.path.basename(vcf_key_name)):
            err_msg = ('This appears to be genotyping data. '
                       'This form is only for whole '
                       'genome or exome data.')
            return err_msg
        return

    def validate_upload(self):
        """
        In addition to default validation, check file name and size.
        """
        # Validate a new upload
        form = self.get_validate_upload_form()

        if form.is_valid():
            err_msg = self.check_vcf_key_name(
                form.cleaned_data.get('key_name'))
            if err_msg:
                return self.form_invalid(form, message=err_msg)

            return self.form_valid(form)

        return self.form_invalid(form)


class EditVCFDataView(UpdateView, DataRetrievalView, LargePanelMixin):
    """
    Allow the user to add or edit information about a VCF file.
    """

    form_class = VCFDataForm
    model = VCFData
    template_name = 'vcf_data/file.html'
    success_url = reverse_lazy('activities:genome-exome-data:manage-files')
    source = label
    pk_url_kwarg = 'vcf_data'
    latest = False

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            returnable = self.form_valid(form)
            self.trigger_retrieval_task(request)
            return returnable
        else:
            return self.form_invalid(form)

    def get_object(self, queryset=None):
        """
        Override to provide most recent for a user if latest is True.
        """
        if self.latest:
            vcfdata_set = VCFData.objects.filter(
                user_data=self.request.user.vcf_data)

            if vcfdata_set:
                return vcfdata_set[0]

            raise Http404('No VCF data sets for this user.')

        return super(EditVCFDataView, self).get_object(queryset)


class DeleteVCFDataView(PrivateMixin, DeleteView):
    """
    Let the user delete a uBiome sample.
    """

    template_name = 'vcf_data/delete-file.html'
    success_url = reverse_lazy('activities:genome-exome-data:manage-files')

    def get_object(self, queryset=None):
        return VCFData.objects.get(id=self.kwargs['vcf_data'],
                                   user_data=self.request.user.vcf_data)


class ManageVCFDataView(PrivateMixin, ListView):
    """
    Creates a view for VCF data files.
    """

    template_name = 'vcf_data/manage-files.html'
    context_object_name = 'data_files'

    def get_context_data(self, **kwargs):
        """
        'app' for /studies/templates/scopes/study-data-description.html partial
        """
        context = super(ManageVCFDataView, self).get_context_data(
            **kwargs)
        context['app'] = apps.get_app_config(label)
        return context

    def get_queryset(self):
        return VCFData.objects.filter(user_data=self.request.user.vcf_data)
