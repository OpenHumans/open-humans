from django import forms

from .models import VCFData


class VCFDataForm(forms.ModelForm):
    class Meta:
        model = VCFData
        fields = ['vcf_source', 'additional_notes']
