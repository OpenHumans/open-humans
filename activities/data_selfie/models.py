from django.conf import settings
from django.db import models

from common import fields
from data_import.models import DataFile

from . import label


class UserData(models.Model):
    """
    Used as key when a User has DataFiles for the data_selfie activity.
    """

    class Meta:  # noqa: D101
        verbose_name = 'data selfie user data'
        verbose_name_plural = verbose_name

    user = fields.AutoOneToOneField(settings.AUTH_USER_MODEL,
                                    related_name=label)

    seen_page = models.BooleanField(default=False)

    def __unicode__(self):
        return '%s:%s' % (self.user, 'data_selfie')

    @property
    def is_connected(self):
        return DataFile.objects.filter(user=self.user).filter(
            source='direct-sharing-133').count() > 0

    @staticmethod
    def get_retrieval_params():
        return {}
