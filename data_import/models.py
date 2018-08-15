import logging
import os

from botocore.exceptions import ClientError

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.urls import reverse
from django.db import models
from django.db.models import F

from common import fields
from common.utils import full_url

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

    def for_user(self, user):
        return self.filter(user=user).exclude(
            parent_project_data_file__completed=False).order_by('source')

    def contribute_to_class(self, model, name):
        super(DataFileManager, self).contribute_to_class(model, name)

        models.signals.pre_delete.connect(delete_file, model)

    def public(self):
        prefix = 'user__member__public_data_participant__publicdataaccess'

        filters = {
            prefix + '__is_public': True,
            prefix + '__data_source': F('source'),
        }

        return self.filter(**filters).exclude(
            parent_project_data_file__completed=False).order_by(
            'user__username')


class DataFile(models.Model):
    """
    Represents a data file from a study or activity.
    """

    objects = DataFileManager()

    file = models.FileField(upload_to=get_upload_path, max_length=1024)
    metadata = JSONField(default=dict)
    created = models.DateTimeField(auto_now_add=True)

    source = models.CharField(max_length=32)

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='datafiles',
                             on_delete=models.CASCADE)

    def __unicode__(self):
        return '%s:%s:%s' % (self.user, self.source, self.file)

    @property
    def download_url(self):
        return full_url(
            reverse('data-management:datafile-download', args=(self.id,)))

    @property
    def file_url_as_attachment(self):
        """
        Get an S3 pre-signed URL specifying content disposation as attachment.
        """
        return self.file.storage.url(self.file.name)

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
        except (AttributeError, ClientError):
            return ''


class NewDataFileAccessLog(models.Model):
    """
    Represents a download of a datafile.
    """

    date = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             null=True)
    data_file = models.ForeignKey(DataFile,
                                  related_name='access_logs',
                                  on_delete=models.CASCADE)

    def __unicode__(self):
        return '{} {} {} {}'.format(self.date, self.ip_address, self.user,
                                    self.data_file.file.url)


class TestUserData(models.Model):
    """
    Used for unit tests in public_data.tests; there's not currently a way to
    make test-specific model definitions in Django (a bug open since 2009,
    #7835)
    """

    user = fields.AutoOneToOneField(settings.AUTH_USER_MODEL,
                                    related_name='test_user_data',
                                    on_delete=models.CASCADE)
