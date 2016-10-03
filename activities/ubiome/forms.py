from django import forms

from .models import UBiomeSample


class SampleForm(forms.ModelForm):
    """
    A form that represents a uBiome sample for upload.
    """

    class Meta:  # noqa: D101
        model = UBiomeSample
        fields = ['taxonomy', 'additional_notes']
