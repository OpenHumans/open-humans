from django import forms

from activities.data_selfie.models import DataSelfieDataFile


class DataSelfieUpdateViewForm(forms.ModelForm):
    """
    A form for editing a data selfie DataFile
    """

    class Meta:  # noqa: D101
        model = DataSelfieDataFile
        fields = ('user_description',)
