import datetime
import logging
import os
import uuid

from botocore.exceptions import ClientError

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.urls import reverse
from django.db import models
from django.db.models import F

from ipware.ip import get_ip

from common import fields
from common.utils import full_url

from .utils import get_upload_path

logger = logging.getLogger(__name__)


def is_public(member, source):
    """
    Return whether a given member has publicly shared the given source.
    """
    return bool(
        member.public_data_participant.publicdataaccess_set.filter(
            data_source=source, is_public=True
        )
    )


def delete_file(instance, **kwargs):  # pylint: disable=unused-argument
    """
    Delete the DataFile's file from S3 when the model itself is deleted.
    """
    instance.file.delete(save=False)


class DataFileKey(models.Model):
    """
    Temporary key for accessing private files.
    """

    created = models.DateTimeField(auto_now=True)
    key = models.CharField(max_length=36, blank=False, unique=True, default=uuid.uuid4)
    datafile_id = models.IntegerField()
    ip_address = models.GenericIPAddressField(null=True)
    access_token = models.CharField(max_length=64, null=True)
    project_id = models.IntegerField(null=True)
    # ^^ Not a foreign key due to circular deps, also when we serialize this
    # model to json for storing in the log, we'd lose all the fancy, anyway

    @property
    def expired(self):
        """
        Returns True if key is expired, False if not expired
        Expiration set at one hour
        """
        expiration = self.created + datetime.timedelta(hours=1)
        if expiration > datetime.datetime.now(tz=expiration.tzinfo):
            return False
        return True


class DataFileManager(models.Manager):
    """
    We use a manager so that subclasses of DataFile also get their
    pre_delete signal connected correctly.
    """

    def for_user(self, user):
        return (
            self.filter(user=user)
            .exclude(parent_project_data_file__completed=False)
            .order_by("source")
        )

    def contribute_to_class(self, model, name):
        super(DataFileManager, self).contribute_to_class(model, name)

        models.signals.pre_delete.connect(delete_file, model)

    def public(self):
        prefix = "user__member__public_data_participant__publicdataaccess"

        filters = {prefix + "__is_public": True, prefix + "__data_source": F("source")}

        return (
            self.filter(**filters)
            .exclude(parent_project_data_file__completed=False)
            .order_by("user__username")
        )


class DataFile(models.Model):
    """
    Represents a data file from a study or activity.
    """

    objects = DataFileManager()

    file = models.FileField(upload_to=get_upload_path, max_length=1024)
    metadata = JSONField(default=dict)
    created = models.DateTimeField(auto_now_add=True)

    source = models.CharField(max_length=32)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="datafiles", on_delete=models.CASCADE
    )

    def __str__(self):
        return str("{0}:{1}:{2}").format(self.user, self.source, self.file)

    @property
    def download_url(self):
        return full_url(reverse("data-management:datafile-download", args=(self.id,)))

    @property
    def file_url_as_attachment(self):
        """
        Get an S3 pre-signed URL specifying content disposation as attachment.
        """
        return self.file.storage.url(self.file.name)

    def private_download_url(self, request):
        if hasattr(request, "public_sources"):
            if self.source in request.public_sources:
                return self.download_url
        elif self.is_public:
            return self.download_url
        key = self.generate_key(request)
        return "{0}?key={1}".format(self.download_url, key)

    def generate_key(self, request):
        """
        Generate new link expiration key
        """
        new_key = DataFileKey(datafile_id=self.id)
        if request:
            # Log the entity that is requesting the key be generated
            new_key.ip_address = get_ip(request)
            new_key.access_token = request.query_params.get("access_token", None)
            if hasattr(request.auth, "application"):
                # oauth2 project auth
                new_key.project_id = request.auth.application.id
            else:
                # onsite project auth
                new_key.project_id = request.auth.id
        new_key.save()
        return new_key.key

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
        return self.metadata.get("description", "")

    @property
    def tags(self):
        """
        Filled in by the data-processing server.
        """
        return self.metadata.get("tags", [])

    @property
    def size(self):
        """
        Return file size, or empty string if the file key can't be loaded.

        Keys should always load, but this is a more graceful failure mode.
        """
        try:
            return self.file.size
        except (AttributeError, ClientError):
            return ""


class NewDataFileAccessLog(models.Model):
    """
    Represents a download of a datafile.
    """

    date = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    )
    data_file = models.ForeignKey(
        DataFile, related_name="access_logs", on_delete=models.CASCADE
    )
    data_file_key = JSONField(default=dict)

    def __str__(self):
        return str("{0} {1} {2} {3}").format(
            self.date, self.ip_address, self.user, self.data_file.file.url
        )


class TestUserData(models.Model):
    """
    Used for unit tests in public_data.tests; there's not currently a way to
    make test-specific model definitions in Django (a bug open since 2009,
    #7835)
    """

    user = fields.AutoOneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="test_user_data",
        on_delete=models.CASCADE,
    )


class DataTypes(models.Model):
    """
    Describes the types of data a DataFile can contain.
    """

    name = models.CharField(max_length=128, blank=False, unique=True)
    parent = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE)
    description = models.CharField(max_length=512, blank=False)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        parents = self.get_all_parents
        if parents:
            parents.reverse()
            parents = [parent.name for parent in parents if parent]
            parents = "-".join(parents)
            return str("{0}-{1}").format(parents, self.name)
        return self.name

    @property
    def get_all_parents(self):
        """
        Returns the level within the tree
        """
        parent = self.parent
        parents = []
        if parent:
            while True:
                if not parent:
                    break
                parents.append(parent)
                parent = parent.parent

        return parents
