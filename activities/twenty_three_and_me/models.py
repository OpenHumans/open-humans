from django.contrib.auth.models import User
from django.db import models

from common import fields
from data_import.models import BaseDataFile, BaseDataRetrievalTask


class UserData(models.Model):
    """Used as key when a User has DataFiles for the 23andme activity."""
    user = fields.AutoOneToOneField(User, related_name='23andme')

    def __unicode__(self):
        return '%s:%s' % (self.user, '23andme')


class DataFile(BaseDataFile):
    """Storage for a 23andme data file."""
    user_data = models.ForeignKey(UserData)

    def __unicode__(self):
        return '%s:%s:%s' % (self.user_data.user,
                             '23andme', self.file)


class DataRetrievalTask(BaseDataRetrievalTask):
    """Data retrieval task for a 23andme data file."""
    data_file = fields.OneToOneField(DataFile, null=True)

    def __unicode__(self):
        return '%s:%s:%s:%s' % (self.data_file.user_data.user,
                                '23andme', self.data_file.file,
                                self.TASK_STATUS_CHOICES[self.status])

    @classmethod
    def get_task(cls, filename):
        try:
            return cls.objects.get(data_file__file=filename)
        except cls.DoesNotExist:
            return None
