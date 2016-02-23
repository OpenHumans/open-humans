from __future__ import unicode_literals

from django.contrib.postgres.fields import ArrayField
from django.db import models

from open_humans.models import Member


class DataRequestActivity(models.Model):
    """
    Base class for data request activities.
    """

    is_study = models.BooleanField(
        verbose_name='Is this activity an IRB-approved study?')
    name = models.CharField(
        max_length=100,
        verbose_name='Activity or study name')
    leader = models.CharField(
        max_length=100,
        verbose_name='Activity leader(s) or principal investigator(s)')
    organization = models.CharField(
        max_length=100,
        verbose_name='Organization or institution')
    contact_email = models.EmailField()
    info_url = models.URLField(
        verbose_name='URL for general information about your activity or study')
    short_description = models.CharField(
        max_length=140,
        verbose_name='A short description')
    long_description = models.TextField(
        max_length=1000,
        verbose_name='A long description')
    active = models.BooleanField(
        verbose_name='Whether the activity is currently active')

    request_sources_access = ArrayField(
        models.CharField(max_length=100),
        verbose_name="Data sources you're requesting access to")
    request_message_permission = models.BooleanField(
        verbose_name='Are you requesting permission to message users?')
    request_username_access = models.BooleanField(
        verbose_name='Are you requesting Open Humans usernames?')

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
    redirect_url = models.URLField(
        verbose_name='Redirect URL')


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
    sources_shared = ArrayField(models.CharField(max_length=100))
