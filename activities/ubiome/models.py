import os

from collections import OrderedDict

from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.db import models

from common import fields
from data_import.utils import get_upload_path

from . import label


class UserData(models.Model):
    """
    Used as key when a User has DataFiles for the uBiome activity.
    """

    class Meta:
        verbose_name = 'uBiome user data'
        verbose_name_plural = verbose_name

    user = fields.AutoOneToOneField(settings.AUTH_USER_MODEL,
                                    related_name=label)

    text_name = 'uBiome'
    href_connect = reverse_lazy('activities:ubiome:manage-samples')
    href_add_data = reverse_lazy('activities:ubiome:manage-samples')
    href_learn = 'http://ubiome.com/'
    retrieval_url = reverse_lazy('activities:ubiome:request-data-retrieval')

    def __unicode__(self):
        return '%s:%s' % (self.user, 'uBiome')

    def samples(self):
        return self.ubiomesample_set.all()

    @property
    def is_connected(self):
        return self.samples()

    def disconnect(self):
        samples = self.samples()
        samples.delete()

    def get_retrieval_params(self):
        return {'samples': [s.as_dict() for s in self.samples()]}


class UBiomeSample(models.Model):
    """
    Storage for a uBiome data file.
    """
    SAMPLE_TYPE_CHOICES = OrderedDict(
        [(0, 'Gut'),
         (1, 'Mouth'),
         (2, 'Nose'),
         (3, 'Skin'),
         (4, 'Genitals'),
         (5, 'Other')]
        )
    user_data = models.ForeignKey(UserData)
    sequence_file = models.FileField(upload_to=get_upload_path,
                                     max_length=1024)
    sample_type = models.IntegerField(choices=SAMPLE_TYPE_CHOICES.items())
    sample_date = models.DateField(blank=True, null=True)
    taxonomy = models.TextField(
        help_text=('Click "Download taxonomy" on uBiome. '
                   'Copy all of it and paste it here.')
    )
    additional_notes = models.TextField(
        blank=True,
        help_text='Any additional notes, if you would like to add them.')

    @property
    def sequence_file_basename(self):
        return os.path.basename(self.sequence_file.name)

    def as_dict(self):
        return {
            'sequence_file': {
                'url': self.sequence_file.url
            },
            'sample_date': self.sample_date.strftime('%Y%m%d'),
            'sample_type': self.get_sample_type_display(),
            'additional_notes': self.additional_notes,
            'taxonomy': self.taxonomy,
        }
