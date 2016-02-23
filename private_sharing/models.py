from __future__ import unicode_literals

from django.contrib.postgres.fields import JSONField
from django.db import models

from open_humans.models import Member


class DataRequestActivity(models.Model):
    """
    Base class for data request activities.
    """

    is_study = models.BooleanField()
    name = models.CharField(max_length=100)
    leader = models.CharField(max_length=100)
    organization = models.CharField(max_length=100)
    contact_email = models.EmailField()
    info_url = models.URLField()
    short_description = models.CharField(max_length=140)
    long_description = models.TextField(max_length=1000)
    active = models.BooleanField()

    request_sources_access = JSONField(default=[])
    request_message_permission = models.BooleanField()
    request_username_access = models.BooleanField()

    coordinator = models.OneToOneField(Member)
    approved = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    api_access_secret = models.CharField(max_length=64)


class OAuth2DataRequestActivity(DataRequestActivity):
    """
    Represents a data request activity that authorizes through OAuth2.
    """

    enrollment_text = models.TextField()
    redirect_url = models.URLField()


class OnSiteDataRequestActivity(DataRequestActivity):
    """
    Represents a data request activity that authorizes through the Open Humans
    website.
    """

    consent_text = models.TextField()
    post_sharing_url = models.URLField()


class DataRequestActivityMember(models.Model):
    """
    Represents a member's approval of a data request.
    """

    member = models.OneToOneField(Member)
    activity = models.OneToOneField(DataRequestActivity)
    user_id_code = models.CharField(max_length=16)
    message_permission = models.BooleanField()
    username_shared = models.BooleanField()
    sources_shared = JSONField(default=[])
