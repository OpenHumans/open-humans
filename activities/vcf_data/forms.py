from django import forms

from .models import VCFData


class VCFDataForm(forms.ModelForm):
    """
    A form representing a VCF data file for upload.
    """

    class Meta:  # noqa: D101
        model = VCFData
        fields = ['vcf_source', 'additional_notes']
