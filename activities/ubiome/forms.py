from datetime import date

from django import forms

from .models import UBiomeSample


class SampleForm(forms.ModelForm):
    class Meta:
        model = UBiomeSample
        fields = ['sample_type', 'sample_date', 'taxonomy', 'additional_notes']
        widgets = {
            'sample_date': forms.SelectDateWidget(
                years=range(2012, date.today().year + 1),
                attrs={'class': 'select-date-widget'}),
        }
