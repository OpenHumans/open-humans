from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.db import models

from common import fields
from data_import.models import BaseDataFile


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


class DataFile(BaseDataFile):
    """
    Storage for a data_selfie data file.
    """

    class Meta:
        verbose_name = 'data selfie data file'

    user_data = models.ForeignKey(UserData)
    user_description = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return '%s:%s:%s' % (self.user_data.user,
                             'data_selfie', self.file)
