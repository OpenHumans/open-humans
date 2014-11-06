from django.contrib.auth.models import User
from django.db import models

from ..models import BaseActivityDataFile, BaseDataExtractionTask
from common import fields


class ActivityUser(models.Model):
    """Used as key when a 23andme User has DataSets associated with a study."""
    user = fields.AutoOneToOneField(User, related_name='23andme')

    def __unicode__(self):
        return '%s:%s' % (self.user, '23andme')


class ActivityDataFile(BaseActivityDataFile):
    """Storage for a 23andme data file."""
    study_user = models.ForeignKey(ActivityUser)

    def __unicode__(self):
        return '%s:%s:%s' % (self.study_user.user,
                             '23andme', self.file)


class DataExtractionTask(BaseDataExtractionTask):
    """Data extraction task for a 23andme data file."""
    data_file = fields.OneToOneField(ActivityDataFile, null=True)

    def __unicode__(self):
        status_dict = {x[0]: x[1] for x in self.TASK_STATUS_CHOICES}
        return '%s:%s:%s:%s' % (self.data_file.study_user.user,
                                '23andme', self.data_file.file,
                                status_dict[self.status])

    @classmethod
    def get_task(cls, filename):
        try:
            return cls.objects.get(data_file__file=filename)
        except cls.DoesNotExist:
            return None
