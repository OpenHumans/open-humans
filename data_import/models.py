import logging
import os

from collections import OrderedDict
from itertools import groupby
from operator import attrgetter

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import F
from django.dispatch import receiver

import account.signals

from common import fields
from common.utils import app_label_to_verbose_name, full_url, get_source_labels

from .processing import start_task
from .utils import get_upload_path

logger = logging.getLogger(__name__)


def is_public(member, source):
    """
    Return whether a given member has publicly shared the given source.
    """
    return bool(member
                .public_data_participant
                .publicdataaccess_set
                .filter(data_source=source, is_public=True))


@receiver(account.signals.email_confirmed)
def start_processing_cb(email_address, **kwargs):
    """
    A signal that sends all of a user's connections to data-processing when
    they first verify their email.
    """
    for source, _ in email_address.user.member.connections.items():
        start_task(email_address.user, source)


def delete_file(instance, **kwargs):  # pylint: disable=unused-argument
    """
    Delete the DataFile's file from S3 when the model itself is deleted.
    """
    instance.file.delete(save=False)


class DataFileQuerySet(models.QuerySet):
    """
    Custom QuerySet methods for DataFile.
    """

    def grouped_by_source(self):
        installed_apps = get_source_labels()

        filtered_files = [data_file for data_file in self
                          if data_file.source in installed_apps]

        get_source = attrgetter('source')

        sorted_files = sorted(filtered_files, key=get_source)
        grouped_files = groupby(sorted_files, key=get_source)
        list_files = [(group, list(files)) for group, files in grouped_files]

        def to_lower_verbose(source):
            return app_label_to_verbose_name(source[0]).lower()

        return OrderedDict(sorted(list_files, key=to_lower_verbose))


class DataFileManager(models.Manager):
    """
    We use a manager so that subclasses of DataFile also get their
    pre_delete signal connected correctly.
    """

    def for_user(self, user):
        return self.filter(user=user, is_latest=True).order_by('source')

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

    def get_queryset(self):
        return DataFileQuerySet(self.model, using=self._db)


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
    ip_address = models.GenericIPAddressField(null=True)
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
