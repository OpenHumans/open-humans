from datetime import datetime

from autoslug import AutoSlugField

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models

from jsonfield import JSONField

from open_humans.models import Member


class BaseStudyUserData(models.Model):
    """
    Abstract base class for study UserData models.

    When implemented, a user field should be defined as AutoOneToOne to
    a User from django.contrib.auth.models.
    """

    class Meta:
        abstract = True

    data = JSONField()

    @property
    def is_connected(self):
        """
        A study is connected if the user has 1 or more access tokens for the
        study's OAuth2 application.
        """
        # filter in Python to benefit from the prefetch data
        return len([
            a for a in self.user.accesstoken_set.all()
            if a.application.user.username == 'api-administrator' and
            a.application.name == self._meta.app_config.verbose_name
        ]) > 0

    @property
    def has_key_data(self):
        """
        Return false if key data needed for data retrieval is not present.
        """
        return self.is_connected

    def get_retrieval_params(self):
        return {'data': self.data}


class Researcher(models.Model):
    """
    Represents an Open Humans researcher.
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    name = models.CharField(max_length=48)

    approved = models.NullBooleanField()

    def __unicode__(self):
        return '{}: {}'.format(self.user.username, self.name)


class Study(models.Model):
    """
    Stores information about a study.
    """

    class Meta:
        verbose_name_plural = 'studies'

    researchers = models.ManyToManyField(Researcher, blank=True)

    title = models.CharField(max_length=128)

    # This slug is used in URLs and in the name of the badge image
    slug = AutoSlugField(populate_from='title', unique=True)

    short_description = models.CharField(max_length=140)
    long_description = models.TextField()

    website = models.CharField(max_length=128)

    principal_investigator = models.CharField(max_length=128)
    organization = models.CharField(max_length=128)

    is_live = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.title


class DataRequest(models.Model):
    """
    Stores the request for a given DataFile for a Study.
    """

    study = models.ForeignKey(Study, related_name='data_requests',
                              related_query_name='data_request')
    # TODO: filter to data file ContentTypes, maybe in pre_save or form?
    data_file_model = models.ForeignKey(ContentType)
    required = models.BooleanField(default=False)

    def __unicode__(self):
        return '{}, {}, {}'.format(
            self.study.title,
            self.app_name,
            'required' if self.required else 'not required')

    @property
    def request_key(self):
        return '{}'.format(self.app_key)

    @property
    def app_url(self):
        try:
            return self.app_config.connection_url
        except AttributeError:
            return reverse('activities')

    @property
    def app_finalization_url(self):
        try:
            return self.app_config.finalization_url
        except AttributeError:
            return ''

    @property
    def app_config(self):
        return self.data_file_model.model_class()._meta.app_config

    @property
    def app_key(self):
        return self.app_config.name.split('.')[-1]

    @property
    def app_name(self):
        return self.app_config.verbose_name


class StudyGrant(models.Model):
    """
    Tracks members who have joined a study and approved access to their data.
    """

    study = models.ForeignKey(Study)
    member = models.ForeignKey(Member, related_name='study_grants')

    # XXX: should these all be validated so that they belong to the linked
    # study?
    data_requests = models.ManyToManyField(DataRequest)

    created = models.DateTimeField(auto_now_add=True)
    revoked = models.DateTimeField(null=True)

    def __unicode__(self):
        return '{}, {}, [{}]'.format(
            self.member.user.username,
            self.study.title,
            ', '.join(['{}'.format(request.app_name)
                       for request in self.data_requests.all()]))

    @property
    def valid(self):
        return (not self.revoked or
                self.revoked >= datetime.now())

    def revoke(self):
        self.revoked = datetime.now()
        self.save()
