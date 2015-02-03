from collections import OrderedDict
from datetime import datetime

from django.db import models


def get_upload_path(instance, filename=''):
    """
    Construct the upload path for a given DataFile and filename.
    """
    return "member/%s/imported-data/%s/%s" % (
        instance.user_data.user.username,
        instance._meta.app_label,
        filename)


class BaseDataFile(models.Model):
    """
    Base file information model, 'user_data' field left undefined.

    The 'user_data' field must be defined, and must be a model which
    itself has a 'user' field that is a OneToOneField to User.
    """
    file = models.FileField(upload_to=get_upload_path)

    class Meta:
        abstract = True

    def __unicode__(self):
        return '%s:%s:%s' % (self.user_data.user,
                             self._meta.app_label,
                             self.file)

    @property
    def source(self):
        return self._meta.app_label


class BaseDataRetrievalTask(models.Model):
    """
    Base model for tracking DataFile retrieval, 'data_file' undefined.

    The 'data_file' field must be defined, and must be a OneToOneField
    to a model that is an app-specific subclass of BaseDataFile.
    """
    TASK_SUCCESSFUL = 0  # Celery task complete, successful.
    TASK_SUBMITTED = 1   # Sent to Open Humans Data Processing.
    TASK_FAILED = 2      # Celery task complete, failed.
    TASK_QUEUED = 3      # OH Data Processing has sent to broker.
    TASK_INITIATED = 4   # Celery has received and started the task.
    TASK_POSTPONED = 5   # Task not submitted yet (eg pending email validation)

    TASK_STATUS_CHOICES = OrderedDict(
        [(TASK_SUCCESSFUL, 'Completed successfully'),
         (TASK_SUBMITTED, 'Submitted'),
         (TASK_FAILED, 'Failed'),
         (TASK_QUEUED, 'Queued'),
         (TASK_INITIATED, 'Initiated'),
         (TASK_POSTPONED, 'Postponed')])

    status = models.IntegerField(choices=TASK_STATUS_CHOICES.items(),
                                 default=TASK_SUBMITTED)
    start_time = models.DateTimeField(default=datetime.now)
    complete_time = models.DateTimeField(null=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return '%s:%s:%s:%s' % (self.data_file.user_data.user,
                                self._meta.app_label,
                                self.data_file.file,
                                self.TASK_STATUS_CHOICES[self.status])
