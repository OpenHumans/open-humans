from django.apps import apps
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, DeleteView, ListView

from s3upload.views import DropzoneS3UploadFormView

from common.mixins import LargePanelMixin, PrivateMixin
from data_import.utils import get_upload_dir, get_upload_dir_validator

from . import label
from .models import UBiomeSample


class CreateUBiomeSampleView(PrivateMixin, LargePanelMixin, CreateView):
    """
    Allow the user to upload a uBiome file.
    """
    model = UBiomeSample
    template_name = 'ubiome/sample-info.html'
    success_url = reverse_lazy('activities:ubiome:sample-upload')
    fields = ['sample_type', 'sample_date', 'taxonomy', 'additional_notes']
    source = label

    def get_context_data(self, **kwargs):
        context = super(CreateUBiomeSampleView, self).get_context_data(**kwargs)
        context['app'] = apps.get_app_config(label)
        return context

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        self.object = form.save(commit=False)
        self.object.user_data = self.request.user.ubiome
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('activities:ubiome:sample-upload', args=[self.object.id])


class DeleteUBiomeSampleView(PrivateMixin, DeleteView):
    """
    Let the user delete a uBiome sample.
    """
    template_name = 'ubiome/delete-sample.html'
    success_url = reverse_lazy('activities:ubiome:manage-samples')

    def get_object(self, queryset=None):
        return UBiomeSample.objects.get(id=self.kwargs['sample'],
                                        user_data=self.request.user.ubiome)


class ManageUBiomeSamplesView(PrivateMixin, ListView):
    """
    Creates a view for uBiome samples.
    """
    template_name = 'ubiome/manage-samples.html'
    context_object_name = 'samples'

    def get_queryset(self):
        return UBiomeSample.objects.filter(user_data=self.request.user.ubiome)

    def get_context_data(self, **kwargs):
        context = super(ManageUBiomeSamplesView, self).get_context_data(**kwargs)
        context.update({
            'app': apps.get_app_config(label),
        })
        return context


class UploadUBiomeSequenceView(PrivateMixin, DropzoneS3UploadFormView):
    """
    Allow the user to upload a uBiome file.
    """
    template_name = 'ubiome/sample-upload.html'
    success_url = reverse_lazy('activities:ubiome:manage-samples')
    source = label

    def get_upload_to(self):
        return get_upload_dir(UBiomeSample, self.request.user)

    def get_upload_to_validator(self):
        return get_upload_dir_validator(UBiomeSample, self.request.user)

    def form_valid(self, form):
        """
        Save updated model, then trigger retrieval task and redirect.
        """
        sample = UBiomeSample.objects.get(
            user_data=self.request.user.ubiome, id=self.kwargs['sample'])
        sample.sequence_file = form.cleaned_data.get('key_name')
        sample.save()
        return super(UploadUBiomeSequenceView, self).form_valid(form)
