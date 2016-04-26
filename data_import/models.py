import json
import logging
import os
import urlparse

from collections import OrderedDict
from itertools import groupby
from operator import attrgetter

import requests

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import F
from django.dispatch import receiver
from django.utils import timezone

from raven.contrib.django.raven_compat.models import client

import account.signals

from common import fields
from common.utils import app_label_to_verbose_name, full_url, get_source_labels

from .utils import get_upload_dir, get_upload_path

logger = logging.getLogger(__name__)


def is_public(member, source):
    """
    Return whether a given member has publicly shared the given source.
    """
    return bool(member
                .public_data_participant
                .publicdataaccess_set
                .filter(data_source=source, is_public=True))


def most_recent_task(tasks):
    """
    Return the most recent task with files if there are any, and the most
    recent task if not.
    """
    with_files = [task for task in tasks if task.datafiles.count() > 0]

    if with_files:
        return with_files[0]

    return tasks[0]


class DataRetrievalTaskQuerySet(models.QuerySet):
    """
    Convenience methods for filtering DataRetrievalTasks.
    """
    def for_user(self, user):
        return self.filter(user=user).order_by('-start_time')

    def grouped_recent(self):
        """
        Return a dict where each key is the name of a source and each value is
        the latest task for that source.
        """
        get_source = attrgetter('source')

        # during development it's possible to have DataRetrievalTasks from apps
        # that aren't installed on the current branch so we will them to the
        # installed apps
        installed_apps = get_source_labels()

        filtered_tasks = [task for task in self
                          if task.source in installed_apps]

        sorted_tasks = sorted(filtered_tasks, key=get_source)
        grouped_tasks = groupby(sorted_tasks, key=get_source)

        groups = {}

        for key, group in grouped_tasks:
            groups[key] = most_recent_task(list(group))

        return OrderedDict(sorted(
            groups.items(),
            key=lambda x: app_label_to_verbose_name(x[0])))

    # Filter these in Python rather than in SQL so we can reuse the query cache
    # rather than hit the database each time
    def normal(self):
        return [task for task in self
                if task.status not in [DataRetrievalTask.TASK_FAILED,
                                       DataRetrievalTask.TASK_POSTPONED]]

    def postponed(self):
        return [task for task in self
                if task.status == DataRetrievalTask.TASK_POSTPONED]

    def failed(self):
        return [task for task in self
                if task.status == DataRetrievalTask.TASK_FAILED]


class DataRetrievalTask(models.Model):
    """
    Model for tracking DataFile import requests.

    A DataRetrievalTask is related to DataFile models as a ForeignKey.

    Fields:
        status          (IntegerField): Task status, choices defined by
                        self.TASK_STATUS_CHOICES
        start_time      (DateTimeField): Time task was sent to processing.
        complete_time   (DateTimeField): Time task reported as complete/failed.
        user            (ForeignKey): User that requested this import task.
        app_task_params (TextField): JSON string with app-specific task params,
                        e.g. sample/user IDs. Default is blank.
    """
    objects = DataRetrievalTaskQuerySet.as_manager()

    TASK_SUCCEEDED = 0   # Celery task complete, successful.
    TASK_SUBMITTED = 1   # Sent to Open Humans Data Processing.
    TASK_FAILED = 2      # Celery task complete, failed.
    TASK_QUEUED = 3      # OH Data Processing has sent to broker.
    TASK_INITIATED = 4   # Celery has received and started the task.
    TASK_POSTPONED = 5   # Task not submitted yet (eg pending email validation)

    TASK_STATUS_CHOICES = OrderedDict(
        [(TASK_SUCCEEDED, 'Completed successfully'),
         (TASK_SUBMITTED, 'Submitted'),
         (TASK_FAILED, 'Failed'),
         (TASK_QUEUED, 'Queued'),
         (TASK_INITIATED, 'Initiated'),
         (TASK_POSTPONED, 'Postponed')])

    status = models.IntegerField(choices=TASK_STATUS_CHOICES.items(),
                                 default=TASK_SUBMITTED)
    start_time = models.DateTimeField(default=timezone.now)
    complete_time = models.DateTimeField(null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    app_task_params = models.TextField(default='')
    source = models.CharField(max_length=32, null=True)

    # Order reverse chronologically by default
    class Meta:
        ordering = ['-start_time']

    def __unicode__(self):
        return '%s:%s:%s' % (self.user,
                             self.source,
                             self.TASK_STATUS_CHOICES[self.status])

    def start_task(self):
        # Target URL is automatically determined from relevant app label.
        task_url = urlparse.urljoin(settings.DATA_PROCESSING_URL, self.source)

        try:
            task_req = requests.get(
                task_url,
                params={'task_params': json.dumps(self.get_task_params())})
        except requests.exceptions.RequestException:
            logger.error('Error in sending request to data processing')
            logger.error('These were the task params: %s',
                         self.get_task_params())

            error_message = 'Error in call to Open Humans Data Processing.'

        if 'task_req' in locals() and not task_req.status_code == 200:
            logger.error('Non-200 response from data processing')
            logger.error('These were the task params: %s',
                         self.get_task_params())

            error_message = 'Open Humans Data Processing not returning 200.'

        if 'error_message' in locals():
            # Note: could change later if processing works anyway
            self.status = self.TASK_FAILED
            self.save()

            if not settings.TESTING:
                client.captureMessage(error_message,
                                      error_data=self.__base_task_params())

    def postpone_task(self):
        self.status = self.TASK_POSTPONED
        self.save()

    def get_task_params(self):
        params = json.loads(self.app_task_params)
        params.update(self.__base_task_params())
        return params

    def __base_task_params(self):
        """
        Task parameters all tasks use. Subclasses may not override.
        """
        return {
            'member_id': self.user.member.member_id,
            's3_key_dir': get_upload_dir(self.source),
            's3_bucket_name': settings.AWS_STORAGE_BUCKET_NAME,
            'task_id': self.id,
            'update_url': full_url('/data-import/task-update/'),
        }


@receiver(account.signals.email_confirmed)
def start_postponed_tasks_cb(email_address, **kwargs):
    """
    A signal that starts any postponed address when a user's email is
    confirmed.
    """
    postponed_tasks = (DataRetrievalTask.objects.for_user(email_address.user)
                       .postponed())

    for task in postponed_tasks:
        task.start_task()


def delete_file(instance, **kwargs):  # pylint: disable=unused-argument
    """
    Delete the DataFile's file from S3 when the model itself is deleted.
    """
    instance.file.delete(save=False)


class DataFileManager(models.Manager):
    """
    We use a manager so that subclasses of DataFile also get their
    pre_delete signal connected correctly.
    """
    def contribute_to_class(self, model, name):
        super(DataFileManager, self).contribute_to_class(model, name)

        models.signals.pre_delete.connect(delete_file, model)

    def public(self):
        prefix = 'user__member__public_data_participant__publicdataaccess'

        filters = {
            prefix + '__is_public': True,
            prefix + '__data_source': F('source'),
            'is_latest': True,
        }

        return self.filter(**filters).order_by('user__username')


class DataFile(models.Model):
    """
    Represents a data file from a study or activity.
    """
    objects = DataFileManager()

    file = models.FileField(upload_to=get_upload_path, max_length=1024)
    metadata = JSONField(default={})
    created = models.DateTimeField(auto_now_add=True)

    source = models.CharField(max_length=32)

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='datafiles')

    task = models.ForeignKey(DataRetrievalTask,
                             related_name='datafiles',
                             null=True)

    is_latest = models.BooleanField(default=True)

    def __unicode__(self):
        return '%s:%s:%s' % (self.user, self.source, self.file)

    @property
    def download_url(self):
        return full_url(
            reverse('data-management:datafile-download', args=(self.id,)))

    @property
    def private_download_url(self):
        if self.is_public:
            return self.download_url

        return self.file.url

    @property
    def is_public(self):
        return is_public(self.user.member, self.source)

    def has_access(self, user=None):
        return self.is_public or self.user == user

    @property
    def basename(self):
        return os.path.basename(self.file.name)

    @property
    def description(self):
        """
        Filled in by the data-processing server.
        """
        return self.metadata.get('description', '')

    @property
    def tags(self):
        """
        Filled in by the data-processing server.
        """
        return self.metadata.get('tags', [])

    @property
    def size(self):
        """
        Return file size, or empty string if the file key can't be loaded.

        Keys should always load, but this is a more graceful failure mode.
        """
        try:
            return self.file.size
        except AttributeError:
            return ''


class NewDataFileAccessLog(models.Model):
    """
    Represents a download of a datafile.
    """
    date = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    data_file = models.ForeignKey(DataFile, related_name='access_logs')

    def __unicode__(self):
        return '{} {} {} {}'.format(self.date, self.ip_address, self.user,
                                    self.data_file.file.url)


class TestUserData(models.Model):
    """
    This is used for unit tests in public_data.tests; there's not currently a
    way to make test-specific model definitions in Django (a bug open since
    2009, #7835)
    """
    user = fields.AutoOneToOneField(settings.AUTH_USER_MODEL,
                                    related_name='test_user_data')
