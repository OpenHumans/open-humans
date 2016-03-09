from collections import OrderedDict

from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.db import models

from common import fields
from data_import.models import DataFile

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
        return UBiomeSample.objects.filter(user=self.user)

    @property
    def is_connected(self):
        return self.samples()

    def disconnect(self):
        samples = self.samples()
        samples.delete()

    def get_retrieval_params(self):
        return {'samples': [f.url for f in self.samples()]}


class UBiomeSample(DataFile):
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

    parent = models.OneToOneField(DataFile,
                                  parent_link=True,
                                  related_name='parent_ubiome')

    # We define this DataFile specifcally to create additional fields capturing
    # other information about the sample this file comes from.
    sample_type = models.IntegerField(choices=SAMPLE_TYPE_CHOICES.items())
    sample_date = models.DateField(
        blank=True,
        null=True,
        help_text="Format: month/day/year, e.g. 10/23/2015")
    taxonomy = models.TextField(
        help_text='Click "Download taxonomy" on uBiome. Copy all of it and paste it here.'
    )
    additional_notes = models.TextField(
        blank=True,
        help_text="Any additional notes, if you would like to add them.")
