from datetime import date

from django import forms

from .models import UBiomeSample


class SampleForm(forms.ModelForm):
    class Meta:
        model = UBiomeSample
        fields = ['taxonomy', 'additional_notes']
