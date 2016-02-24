from __future__ import unicode_literals

from django.contrib.postgres.fields import ArrayField
from django.db import models

from oauth2_provider.models import Application

from open_humans.models import Member
from open_humans.storage import PublicStorage

active_help_text = """If your activity is not active, it won't show up in
listings, and new data sharing authorizations cannot occur. "Active" status is
required to test authorization processes. Activities which are "active" but not
approved may have some information shared in an "In Development" section,
enabling Open Humans members to comment on upcoming studies."""

post_sharing_url_help_text = """If provided, after authorizing sharing the
member will be taken to this URL. If this URL includes "OH_USER_ID_CODE" within
it, we will replace that with the member's activity-specific user_id_code. This
allows you to direct them to an external survey you operate (e.g. using Google
Forms) where a pre-filled user_id_code field allows you to connect those
responses to corresponding data in Open Humans."""


def badge_upload_path(instance, filename):
    """
    Construct the upload path for a study or activity's badge image.
    """
    return 'private-sharing/badges/{0}/{1}'.format(instance.id, filename)


class DataRequestActivity(models.Model):
    """
    Base class for data request activities.
    """

    class Meta:
        verbose_name_plural = 'Data request activities'

    BOOL_CHOICES = ((True, 'Yes'), (False, 'No'))

    is_study = models.BooleanField(
        choices=BOOL_CHOICES,
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
        choices=BOOL_CHOICES,
        help_text=active_help_text,
        verbose_name='Is the activity currently active?')
    badge_image = models.ImageField(
        blank=True,
        storage=PublicStorage(),
        upload_to=badge_upload_path,
        max_length=1024,
        help_text=("A badge that will be displayed on the user's profile once "
                   "they've connected your activity."))

    request_sources_access = ArrayField(
        models.CharField(max_length=100),
        help_text=('List of sources this activity or study is requesting '
                   'access to on Open Humans.'),
        verbose_name="Data sources you're requesting access to")

    request_message_permission = models.BooleanField(
        choices=BOOL_CHOICES,
        help_text=('Permission to send messages to the member. This does not '
                   'grant access to their email address.'),
        verbose_name='Are you requesting permission to message users?')

    request_username_access = models.BooleanField(
        choices=BOOL_CHOICES,
        help_text=("Access to the member's username. This implicitly enables "
                   'access to anything the user is publicly sharing on Open '
                   'Humans. Note that this is potentially sensitive and/or '
                   'identifying.'),
        verbose_name='Are you requesting Open Humans usernames?')

    coordinator = models.OneToOneField(Member)
    approved = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    api_access_secret = models.CharField(max_length=64)


class OAuth2DataRequestActivity(DataRequestActivity):
    """
    Represents a data request activity that authorizes through OAuth2.
    """

    class Meta:
        verbose_name = 'OAuth2 data request activity'
        verbose_name_plural = 'OAuth2 data request activities'

    application = models.OneToOneField(Application)

    enrollment_url = models.URLField(
        help_text=("The URL we direct members to if they're interested in "
                   'sharing data with your study or activity.'),
        verbose_name='Enrollment URL')

    redirect_url = models.URLField(
        # TODO: add link
        help_text=('The return URL for our "authorization code" OAuth2 grant '
                   'process. You can <a target="_blank" href="{}">read more '
                   'about OAuth2 "authorization code" transactions here</a>.'
                  ).format(''),
        verbose_name='Redirect URL')

    def save(self, *args, **kwargs):
        if self.pk is None:
            application = Application(
                name=self.name,
                user=self.coordinator.user,
                client_type=Application.CLIENT_CONFIDENTIAL,
                authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE)

            application.save()

            self.application = application

        super(OAuth2DataRequestActivity, self).save(*args, **kwargs)


class OnSiteDataRequestActivity(DataRequestActivity):
    """
    Represents a data request activity that authorizes through the Open Humans
    website.
    """

    class Meta:
        verbose_name = 'On-site data request activity'
        verbose_name_plural = 'On-site data request activities'

    consent_text = models.TextField(
        help_text=('The "informed consent" text that describes your activity '
                   'to Open Humans members.'))

    post_sharing_url = models.URLField(
        verbose_name='Post-sharing URL',
        help_text=post_sharing_url_help_text)


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
