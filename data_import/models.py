from collections import OrderedDict
import datetime
import logging
import os
import uuid

import arrow
from botocore.exceptions import ClientError

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.validators import RegexValidator
from django.urls import reverse
from django.db import models
from django.utils import timezone

from ipware import get_client_ip

from common import fields
from common.utils import full_url
from open_humans.models import Member

from .utils import get_upload_path

logger = logging.getLogger(__name__)

charvalidator = RegexValidator(
    r"^[\w\-\s]+$",
    "Only alphanumeric characters, space, dash, and underscore are allowed.",
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

    created = models.DateTimeField(auto_now_add=True)
    key = models.CharField(
        max_length=36, blank=False, unique=True, default=uuid.uuid4, primary_key=True
    )
    datafile_id = models.BigIntegerField()
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

    def contribute_to_class(self, model, name):
        super(DataFileManager, self).contribute_to_class(model, name)

        models.signals.pre_delete.connect(delete_file, model)


class DataFile(models.Model):
    """
    Represents a data file from a study or activity.
    """

    objects = DataFileManager()

    file = models.FileField(upload_to=get_upload_path, max_length=1024, unique=True)
    metadata = JSONField(default=dict)
    created = models.DateTimeField(auto_now_add=True)

    source = models.CharField(max_length=32)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="datafiles", on_delete=models.CASCADE
    )

    def __str__(self):
        return str("{0}:{1}:{2}").format(self.user, self.source, self.file)

    def download_url(self, request):
        key = self.generate_key(request)
        url = full_url(reverse("data-management:datafile-download", args=(self.id,)))
        return "{0}?key={1}".format(url, key)

    @property
    def file_url_as_attachment(self):
        """
        Get an S3 pre-signed URL specifying content disposation as attachment.
        """
        return self.file.storage.url(self.file.name)

    def generate_key(self, request):
        """
        Generate new link expiration key
        """
        new_key = DataFileKey(datafile_id=self.id)

        if request:
            # Log the entity that is requesting the key be generated
            new_key.ip_address = get_client_ip(request)

            try:
                new_key.access_token = request.query_params.get("access_token", None)
            except (AttributeError, KeyError):
                new_key.access_token = None
            try:
                new_key.project_id = request.auth.id
            except AttributeError:
                # We do not have an accessing project
                new_key.project_id = None

        new_key.save()
        return new_key.key

    @property
    def is_public(self):
        return self.parent_project_data_file.is_public

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
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    data_file = models.ForeignKey(
        DataFile, related_name="access_logs", on_delete=models.SET_NULL, null=True
    )
    serialized_data_file = JSONField(default=dict, null=True)
    data_file_key = JSONField(default=dict, null=True)
    aws_url = models.CharField(max_length=400, null=True)

    def __str__(self):
        return str("{0} {1} {2} {3}").format(
            self.date, self.ip_address, self.user, self.aws_url
        )


class AWSDataFileAccessLog(models.Model):
    """
    Logs every time a file is accessed on the Amazon side.
    """

    created = models.DateTimeField(auto_now_add=True)

    serialized_data_file = JSONField(default=dict, null=True)
    oh_data_file_access_log = models.ManyToManyField(NewDataFileAccessLog)

    # The following fields are populated from the AWS data
    bucket_owner = models.CharField(max_length=100)
    bucket = models.CharField(max_length=64)
    time = models.DateTimeField()
    remote_ip = models.GenericIPAddressField(null=True)
    requester = models.CharField(max_length=64, null=True)
    request_id = models.CharField(max_length=32, null=True)
    operation = models.CharField(max_length=32, null=True)
    bucket_key = models.CharField(max_length=500, null=True)
    request_uri = models.CharField(max_length=500, null=True)
    status = models.IntegerField(null=True)
    error_code = models.CharField(max_length=64, null=True)
    bytes_sent = models.BigIntegerField(null=True)
    object_size = models.BigIntegerField(null=True)
    total_time = models.IntegerField(null=True)
    turn_around_time = models.IntegerField(null=True)
    referrer = models.CharField(max_length=500, null=True)
    user_agent = models.CharField(max_length=254, null=True)
    version_id = models.CharField(max_length=128, null=True)
    host_id = models.CharField(max_length=128, null=True)
    signature_version = models.CharField(max_length=32, null=True)
    cipher_suite = models.CharField(max_length=128, null=True)
    auth_type = models.CharField(max_length=32, null=True)
    host_header = models.CharField(max_length=64, null=True)

    @property
    def datafile(self):
        """
        Helper that returns a queryset with the DataFile if it exists still, empty if not.
        """
        datafile_id = self.serialized_data_file.get("id", None)
        df = DataFile.objects.filter(id=datafile_id)
        if df.count() == 1:
            return df.get()
        return None


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


class DataType(models.Model):
    """
    Describes the types of data a DataFile can contain.
    """

    name = models.CharField(
        max_length=40, blank=False, unique=True, validators=[charvalidator]
    )
    parent = models.ForeignKey(
        "self", blank=True, null=True, related_name="children", on_delete=models.PROTECT
    )
    last_editor = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True)
    description = models.CharField(max_length=100, blank=False)
    details = models.TextField(blank=True)
    uploadable = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    history = JSONField(default=dict, editable=False)

    def __str__(self):
        parents = self.all_parents
        if parents:
            parents.reverse()
            parents = [parent.name for parent in parents if parent]
            parents = ":".join(parents)
            return str("{0}:{1}").format(parents, self.name)
        return self.name

    def save(self, *args, **kwargs):
        """
        Override save to record edit history and require an associated "editor".

        "editor" is an instance-specific parameter; this avoids accepting an update
        that is merely retaining the existing value for the "last_editor" field.
        """
        if not self.editor:
            raise ValueError("'self.editor' must be set when saving DataType.")
        else:
            self.last_editor = self.editor
        self.history[arrow.get(timezone.now()).isoformat()] = {
            "name": self.name,
            "parent": self.parent.id if self.parent else None,
            "description": self.description,
            "details": self.details,
            "uploadable": self.uploadable,
            "editor": self.last_editor.id,
        }
        return super().save(*args, **kwargs)

    @property
    def history_sorted(self):
        history_sorted = OrderedDict()
        items_sorted = sorted(
            self.history.items(), key=lambda item: arrow.get(item[0]), reverse=True
        )
        for item in items_sorted:
            parent = (
                DataType.objects.get(id=item[1]["parent"])
                if item[1]["parent"]
                else None
            )
            try:
                editor = Member.objects.get(id=item[1]["editor"])
            except Member.DoesNotExist:
                editor = None
            history_sorted[arrow.get(item[0]).datetime] = {
                "parent": parent,
                "editor": editor,
                "hash": hash(item[0]),
            }
            history_sorted[arrow.get(item[0]).datetime].update(
                {
                    field: item[1][field]
                    for field in ["name", "description", "details", "uploadable"]
                    if field in item[1]
                }
            )

        return history_sorted

    @property
    def editable(self):
        """
        Return True if no approved projects are registered as using this.
        """
        # Always true for a new instance that hasn't yet been saved:
        if not self.id:
            return True

        approved_registered = self.source_projects.filter(approved=True)
        if approved_registered:
            return False
        else:
            return True

    @property
    def all_parents(self):
        """
        Return list of parents, from immediate to most ancestral.
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

    @classmethod
    def all_as_tree(cls):
        """
        Dict tree of all datatypes. Key = parent & value = array of child dicts.

        This method is intended to make all ancestry relationships available without
        having to hit the database more than necessary.
        """

        def _children(parent, all_datatypes):
            children = {}
            for dt in [dt for dt in all_datatypes if dt.parent == parent]:
                children[dt] = _children(dt, all_datatypes)
            return children

        all_datatypes = list(DataType.objects.all())
        roots = DataType.objects.filter(parent=None)
        tree = {dt: _children(dt, all_datatypes) for dt in roots}
        return tree

    @classmethod
    def sorted_by_ancestors(cls, queryset=None):
        """
        Sort DataTypes by ancestors array of dicts containing 'datatype' and 'depth'.
        """

        def _flatten(node, depth=0):
            flattened = []
            for child in sorted(node.keys(), key=lambda obj: obj.name):
                flattened.append({"datatype": child, "depth": depth})
                flattened = flattened + _flatten(node[child], depth=depth + 1)
            return flattened

        datatypes_tree = cls.all_as_tree()
        return _flatten(datatypes_tree)
