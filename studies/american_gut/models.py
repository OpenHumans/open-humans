from django.contrib.auth.models import User
from django.db import models

from common import fields
from data_import.models import BaseDataFile, DataRetrievalTask


class UserData(models.Model):
    user = fields.AutoOneToOneField(User, related_name='american_gut')


class Barcode(models.Model):
    user_data = models.ForeignKey(UserData, related_name='barcodes')

    value = models.CharField(primary_key=True, max_length=64)


class DataFile(BaseDataFile):
    """Storage for an American Gut data file."""
    user_data = models.ForeignKey(UserData)
    task = models.ForeignKey(DataRetrievalTask,
                             related_name='datafile_american_gut')

    def __unicode__(self):
        return '%s:%s:%s' % (self.user_data.user,
                             'american_gut', self.file)
