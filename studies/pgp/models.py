from django.contrib.auth.models import User
from django.db import models

from common import fields
from data_import.models import BaseDataFile, DataRetrievalTask


class UserData(models.Model):
    user = fields.AutoOneToOneField(User, related_name='pgp')


class HuId(models.Model):
    user_data = models.ForeignKey(UserData, related_name='huids')

    value = models.CharField(primary_key=True, max_length=64)


class DataFile(BaseDataFile):
    """
    Storage for an PGP data file.
    """
    user_data = models.ForeignKey(UserData)
    task = models.ForeignKey(DataRetrievalTask, related_name='datafile_pgp')

    def __unicode__(self):
        return '%s:%s:%s' % (self.user_data.user, 'pgp', self.file)
