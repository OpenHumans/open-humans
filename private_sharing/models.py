from __future__ import unicode_literals

import random

from django.contrib.postgres.fields import ArrayField
from django.db import models

from oauth2_provider.models import Application

from common.utils import app_label_to_verbose_name

from open_humans.models import Member
from open_humans.storage import PublicStorage

active_help_text = """"Active" status is required to perform authorization
processes, including during drafting stage. If a project is not active, it
won't show up in listings, and new data sharing authorizations cannot occur.
Projects which are "active" but not approved may have some information shared
in an "In Development" section, so Open Humans members can see potential
upcoming studies."""

post_sharing_url_help_text = """If provided, after authorizing sharing the
member will be taken to this URL. If this URL includes "OH_PROJECT_MEMBER_ID"
within it, we will replace that with the member's project-specific
project_member_id. This allows you to direct them to an external survey you
operate (e.g. using Google Forms) where a pre-filled project_member_id field
allows you to connect those responses to corresponding data in Open Humans."""


def badge_upload_path(instance, filename):
    """
    Construct the upload path for a project's badge image.
    """
    return 'private-sharing/badges/{0}/{1}'.format(instance.id, filename)


class DataRequestProject(models.Model):
    """
    Base class for data request projects.
    """

    class Meta:
        verbose_name_plural = 'Data request activities'

    BOOL_CHOICES = ((True, 'Yes'), (False, 'No'))
    STUDY_CHOICES = ((True, 'Study'), (False, 'Activity'))

    is_study = models.BooleanField(
        choices=STUDY_CHOICES,
        help_text=('A "study" is doing human subjects research and must have '
                   'Institutional Review Board approval or equivalent ethics '
                   'board oversight. Activities can be anything else, e.g. '
                   'data visualizations.'),
        verbose_name='Is this project a study or an activity?')
    name = models.CharField(
        max_length=100,
        verbose_name='Project name')
    leader = models.CharField(
        max_length=100,
        verbose_name='Leader(s) or principal investigator(s)')
    organization = models.CharField(
        max_length=100,
        verbose_name='Organization or institution')
    contact_email = models.EmailField(
        verbose_name='Contact email for your project')
    info_url = models.URLField(
        verbose_name='URL for general information about your project')
    short_description = models.CharField(
        max_length=140,
        verbose_name='A short description (140 characters max)')
    long_description = models.TextField(
        max_length=1000,
        verbose_name='A long description (1000 characters max)')
    active = models.BooleanField(
        choices=BOOL_CHOICES,
        help_text=active_help_text,
        default=True)
    badge_image = models.ImageField(
        blank=True,
        storage=PublicStorage(),
        upload_to=badge_upload_path,
        max_length=1024,
        help_text=("A badge that will be displayed on the user's profile once "
                   "they've connected your project."))

    request_sources_access = ArrayField(
        models.CharField(max_length=100),
        help_text=('List of sources this project is requesting access to on '
                   'Open Humans.'),
        default=list,
        verbose_name="Data sources you're requesting access to")

    @property
    def request_sources_access_names(self):
        # pylint: disable=not-an-iterable
        return [app_label_to_verbose_name(label)
                for label in self.request_sources_access]

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

    coordinator = models.ForeignKey(Member, on_delete=models.PROTECT)
    approved = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    api_access_secret = models.CharField(max_length=64)

    def __unicode__(self):
        return '{}: {}, {}'.format(self.name, self.coordinator.name,
                                   self.leader)

    @property
    def project_type(self):
        return 'study' if self.is_study else 'activity'

    @property
    def type(self):
        if hasattr(self, 'oauth2datarequestproject'):
            return 'oauth2'

        if hasattr(self, 'onsitedatarequestproject'):
            return 'on-site'


class OAuth2DataRequestProject(DataRequestProject):
    """
    Represents a data request project that authorizes through OAuth2.
    """

    class Meta:
        verbose_name = 'OAuth2 data request project'

    application = models.OneToOneField(Application)

    enrollment_url = models.URLField(
        help_text=("The URL we direct members to if they're interested in "
                   'sharing data with your project.'),
        verbose_name='Enrollment URL')

    redirect_url = models.URLField(
        # TODO: add link
        help_text=('The return URL for our "authorization code" OAuth2 grant '
                   'process. You can <a target="_blank" href="{}">read more '
                   'about OAuth2 "authorization code" transactions here</a>.'
                  ).format(''),
        verbose_name='Redirect URL')

    def save(self, *args, **kwargs):
        if not hasattr(self, 'application'):
            self.application = Application()

        self.application.name = self.name
        self.application.user = self.coordinator.user
        self.application.client_type = Application.CLIENT_CONFIDENTIAL
        self.application.redirect_uris = self.redirect_url
        self.application.authorization_grant_type = (
            Application.GRANT_AUTHORIZATION_CODE)

        self.application.save()

        super(OAuth2DataRequestProject, self).save(*args, **kwargs)


class OnSiteDataRequestProject(DataRequestProject):
    """
    Represents a data request project that authorizes through the Open Humans
    website.
    """

    class Meta:
        verbose_name = 'On-site data request project'

    consent_text = models.TextField(
        help_text=('The "informed consent" text that describes your project '
                   'to Open Humans members.'))

    post_sharing_url = models.URLField(
        blank=True,
        verbose_name='Post-sharing URL',
        help_text=post_sharing_url_help_text)


class DataRequestProjectMember(models.Model):
    """
    Represents a member's approval of a data request.
    """

    member = models.ForeignKey(Member)
    # represents when a member accepts/authorizes a project
    created = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(DataRequestProject)
    project_member_id = models.CharField(max_length=16, unique=True)
    message_permission = models.BooleanField(default=False)
    username_shared = models.BooleanField(default=False)
    sources_shared = ArrayField(models.CharField(max_length=100), default=list)

    @staticmethod
    def random_project_member_id():
        """
        Return a zero-padded string 16 digits long that's not already used in
        the database.
        """
        def random_code():
            return '%016d' % random.randint(0, 9999999999999999)

        code = random_code()

        while DataRequestProjectMember.objects.filter(
                project_member_id=code).count() > 0:
            code = random_code()

        return code

    def save(self, *args, **kwargs):
        if not self.project_member_id:
            self.project_member_id = self.random_project_member_id()

        super(DataRequestProjectMember, self).save(*args, **kwargs)
