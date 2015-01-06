from collections import OrderedDict
from datetime import datetime

from django.db import models


def get_upload_path(instance, filename=''):
    return "member/%s/activity-data/%s/%s" % (
        instance.study_user.user.username,
        instance._meta.app_label,
        filename)


class BaseActivityDataFile(models.Model):
    """Base file information model, study_user left undefined."""
    file = models.FileField(upload_to=get_upload_path)

    class Meta:
        abstract = True


class BaseDataExtractionTask(models.Model):
    """Base task tracking model, data_file left undefined."""
    TASK_SUCCESSFUL = 0
    TASK_SUBMITTED = 1
    TASK_FAILED = 2
    TASK_STATUS_CHOICES = OrderedDict(
        [(TASK_SUCCESSFUL, 'Completed successfully'),
         (TASK_SUBMITTED, 'Submitted'),
         (TASK_FAILED, 'Failed')])
    status = models.IntegerField(choices=TASK_STATUS_CHOICES.items(),
                                 default=TASK_SUBMITTED)
    start_time = models.DateTimeField(default=datetime.now)
    complete_time = models.DateTimeField(null=True)

    class Meta:
        abstract = True
