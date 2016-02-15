from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.db import models

from common import fields
from data_import.models import DataFile


class UserData(models.Model):
    """
    Used as key when a User has DataFiles for the data_selfie activity.
    """

    class Meta:
        verbose_name = 'data selfie user data'
        verbose_name_plural = verbose_name

    user = fields.AutoOneToOneField(settings.AUTH_USER_MODEL,
                                    related_name='data_selfie')

    seen_page = models.BooleanField(default=False)

    text_name = 'Data selfie'
    href_connect = reverse_lazy('activities:data-selfie:upload')
    href_add_data = reverse_lazy('activities:data-selfie:upload')

    def __unicode__(self):
        return '%s:%s' % (self.user, 'data_selfie')

    @property
    def is_connected(self):
        return True

    @staticmethod
    def get_retrieval_params():
        return {}


class DataSelfieDataFile(DataFile):
    """
    Storage for a data_selfie data file.
    """

    parent = models.OneToOneField(DataFile,
                                  parent_link=True,
                                  related_name='parent_data_selfie')

    # We define this DataFile specifcally to create this field which makes it
    # much easier to create forms
    user_description = models.CharField(max_length=255, blank=True, null=True)
