from django.contrib.auth.models import User
from django.db import models

from common import fields
from data_import.models import BaseDataFile, DataRetrievalTask


class UserData(models.Model):
    """Used as key when a User has DataFiles for the 23andme activity."""
    user = fields.AutoOneToOneField(User, related_name='23andme')

    def __unicode__(self):
        return '%s:%s' % (self.user, '23andme')


class DataFile(BaseDataFile):
    """Storage for a 23andme data file."""
    user_data = models.ForeignKey(UserData)
    task = models.ForeignKey(DataRetrievalTask,
                             related_name='datafile_23andme')

    def __unicode__(self):
        return '%s:%s:%s' % (self.user_data.user,
                             '23andme', self.file)
