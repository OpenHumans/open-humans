import re

from django import forms

from .models import DataFile


class ArchiveDataFilesForm(forms.Form):

    data_file_ids = forms.CharField(
        label='Data file IDs',
        help_text='A comma-separated list of data file IDs',
        required=True,
        widget=forms.Textarea)

    def clean_data_file_ids(self):
        raw_ids = self.data.get('data_file_ids', '')

        # the HTML form is a comma-delimited string; the API is a list
        if not isinstance(raw_ids, basestring):
            raw_ids = ','.join(str(raw_id) for raw_id in raw_ids)

        data_file_ids = re.split(r'[ ,\r\n]+', raw_ids)

        # remove empty IDs
        data_file_ids = [data_file_id for data_file_id
                         in data_file_ids if data_file_id]

        # look up each ID in the database
        data_files = DataFile.objects.filter(id__in=data_file_ids)

        # if some of the data files weren't found then they were invalid
        if len(data_file_ids) != len(data_files):
            def in_data_files(data_file_id):
                for data_file in data_files:
                    if data_file.id == data_file_id:
                        return True

            raise forms.ValidationError(
                'Invalid data file ID(s): {0}'.format(', '.join([
                    data_file_id
                    for data_file_id in data_file_ids
                    if not in_data_files(data_file_id)])))

        # return the actual objects
        return data_files
