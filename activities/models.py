from datetime import datetime

from django.db import models

TASK_SUBMITTED = 'SUBM'
TASK_SUCCESSFUL = 'SUCC'
TASK_FAILED = 'FAIL'
TASK_STATUS_CHOICES = (
    (TASK_SUBMITTED, 'Submitted'),
    (TASK_SUCCESSFUL, 'Completed successfully'),
    (TASK_FAILED, 'Failed'),
)


def get_upload_path(instance, filename=''):
    return "activity_data/%s/%s/%s" % (instance.study_user.user.username,
                                       instance._meta.app_label,
                                       filename)


class BaseActivityDataFile(models.Model):
    """Base file information model, study_user left undefined."""
    file = models.FileField(upload_to=get_upload_path)

    class Meta:
        abstract = True


class BaseDataExtractionTask(models.Model):
    """Base task tracking model, data_file left undefined."""
    status = models.CharField(max_length=4, choices=TASK_STATUS_CHOICES,
                              default=TASK_SUBMITTED)
    start_time = models.DateTimeField(default=datetime.now)
    complete_time = models.DateTimeField(null=True)

    class Meta:
        abstract = True
