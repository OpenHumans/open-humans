import re

from distutils.util import strtobool
from string import digits  # pylint: disable=deprecated-module

import datetime
import dateutil
import json
import requests
import arrow

from autoslug import AutoSlugField

from django.contrib.auth.models import AnonymousUser
from django.contrib.postgres.fields import ArrayField
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.db import models, router
from django.db.models import F
from django.db.models.deletion import Collector
from django.urls import reverse
from django.utils import timezone

from oauth2_provider.models import AccessToken, Application, RefreshToken

from common.utils import app_label_to_verbose_name, generate_id
from data_import.models import DataFile, DataType
from open_humans.models import Member
from open_humans.storage import PublicStorage


active_help_text = """"Active" status is required to perform authorization
processes, including during drafting stage. If a project is not active, it
won't show up in listings of activities that can be joined by participants, and
new data sharing authorizations cannot occur. Projects which are "active" but
not approved may have some information shared in an "In Development" section,
so Open Humans members can see potential upcoming studies. Removing "active"
status from a project will not remove any uploaded files from a project
member's profile."""

post_sharing_url_help_text = """If provided, after authorizing sharing the
member will be taken to this URL. If this URL includes "PROJECT_MEMBER_ID"
within it, we will replace that with the member's project-specific
project_member_id. This allows you to direct them to an external survey you
operate (e.g. using Google Forms) where a pre-filled project_member_id field
allows you to connect those responses to corresponding data in Open Humans."""


def now_plus_24_hours():
    """
    Return a datetime 24 hours in the future.
    """
    return arrow.utcnow().replace(hours=+24).datetime


def id_label_to_project(id_label):
    """
    Given a project's id_label, return the project.
    """
    match = re.match(r"direct-sharing-(?P<id>\d+)", id_label)

    if match:
        project = DataRequestProject.objects.get(id=int(match.group("id")))
        return project


def app_label_to_verbose_name_including_dynamic(label):
    """
    Given an app's name, return its verbose name.
    """
    try:
        return app_label_to_verbose_name(label)
    except LookupError:
        match = re.match(r"direct-sharing-(?P<id>\d+)", label)

        if match:
            project = DataRequestProject.objects.get(id=int(match.group("id")))

            return project.name


def badge_upload_path(instance, filename):
    """
    Construct the upload path for a project's badge image.
    """
    return "direct-sharing/badges/{0}/{1}".format(instance.id, filename)


def project_membership_visible(member, source):
    """
    Determine if the user's membership in a project is visible or not.
    """
    project = id_label_to_project(source)

    if project is not None:
        qs = DataRequestProjectMember.objects.filter(member=member, project=project)
        if qs.exists():
            project_member = qs.get(member=member, project=project)
            return bool(project_member.visible)

    return False


class DataRequestProject(models.Model):
    """
    Base class for data request projects.

    Some fields are only available to Open Humans admins, including:
        all_sources_access (Boolean): when True, all data sources shared w/proj
        approved (Boolean): when True, member cap is removed and proj is listed
        token_expiration_disabled (Boolean): if True master tokens don't expire
    """

    BOOL_CHOICES = ((True, "Yes"), (False, "No"))
    STUDY_CHOICES = ((True, "Study"), (False, "Activity"))

    is_study = models.BooleanField(
        choices=STUDY_CHOICES,
        help_text=(
            'A "study" is doing human subjects research and must have '
            "Institutional Review Board approval or equivalent ethics "
            "board oversight. Activities can be anything else, e.g. "
            "data visualizations."
        ),
        verbose_name="Is this project a study or an activity?",
    )
    name = models.CharField(max_length=100, verbose_name="Project name")
    slug = AutoSlugField(populate_from="name", unique=True, always_update=True)
    leader = models.CharField(
        max_length=100, verbose_name="Leader(s) or principal investigator(s)"
    )
    organization = models.CharField(
        blank=True, max_length=100, verbose_name="Organization or institution"
    )
    is_academic_or_nonprofit = models.BooleanField(
        choices=BOOL_CHOICES,
        verbose_name=(
            "Is this institution or organization an academic "
            "institution or non-profit organization?"
        ),
    )
    add_data = models.BooleanField(
        help_text=(
            'If your project collects data, choose "Add data" here. If '
            'you choose "Add data", you will need to provide a '
            '"Returned data description" below.'
        ),
        verbose_name="Add data",
        default=False,
    )
    explore_share = models.BooleanField(
        help_text=(
            "If your project performs analysis on data, choose " '"Explore & share".'
        ),
        verbose_name="Explore & share",
        default=False,
    )
    contact_email = models.EmailField(verbose_name="Contact email for your project")
    info_url = models.URLField(
        blank=True, verbose_name="URL for general information about your project"
    )
    short_description = models.CharField(
        max_length=140, verbose_name="A short description (140 characters max)"
    )
    long_description = models.TextField(
        max_length=1000, verbose_name="A long description (1000 characters max)"
    )
    returned_data_description = models.CharField(
        blank=True,
        max_length=140,
        verbose_name=(
            "Description of data you plan to upload to member "
            " accounts (140 characters max)"
        ),
        help_text=(
            "Leave this blank if your project doesn't plan to add or "
            "return new data for your members.  If your project is set "
            'to be displayed under "Add data", then you must provide '
            "this information."
        ),
    )
    active = models.BooleanField(
        choices=BOOL_CHOICES, help_text=active_help_text, default=True
    )
    badge_image = models.ImageField(
        blank=True,
        storage=PublicStorage(),
        upload_to=badge_upload_path,
        max_length=1024,
        help_text=(
            "A badge that will be displayed on the user's profile once "
            "they've connected your project."
        ),
    )
    requested_sources = models.ManyToManyField(
        "self", related_name="requesting_projects", symmetrical=False
    )
    all_sources_access = models.BooleanField(default=False)
    deauth_email_notification = models.BooleanField(
        default=False,
        help_text="Receive emails when a member deauthorizes your project",
        verbose_name="Deauthorize email notifications",
    )
    erasure_supported = models.BooleanField(
        default=False,
        help_text="Whether your project supports erasing a member's data on request",
    )
    request_username_access = models.BooleanField(
        choices=BOOL_CHOICES,
        help_text=(
            "Access to the member's username. This implicitly enables "
            "access to anything the user is publicly sharing on Open "
            "Humans. Note that this is potentially sensitive and/or "
            "identifying."
        ),
        verbose_name="Are you requesting Open Humans usernames?",
    )
    registered_datatypes = models.ManyToManyField(DataType)

    class Meta:
        ordering = ["name"]

    coordinator = models.ForeignKey(Member, on_delete=models.PROTECT)
    approved = models.BooleanField(default=False)
    approval_history = ArrayField(
        ArrayField(models.CharField(max_length=32), size=2),
        default=list,
        editable=False,
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    master_access_token = models.CharField(max_length=64, default=generate_id)

    token_expiration_date = models.DateTimeField(default=now_plus_24_hours)
    token_expiration_disabled = models.BooleanField(default=False)
    no_public_data = models.BooleanField(default=False)
    auto_add_datatypes = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        # Adds self.old_approved so that we can detect when the field changes
        super().__init__(*args, **kwargs)
        self.old_approved = self.approved

    def __str__(self):
        return str("{0}").format(self.name)

    def save(self, *args, **kwargs):
        """
        Override save to update the timestamp for when approved gets changed.
        """
        if self.old_approved != self.approved:
            self.approval_history.append(
                (self.approved, datetime.datetime.utcnow().isoformat())
            )
        return super().save(*args, **kwargs)

    @property
    def project_approval_date(self):
        """
        Returns None if project is not approved, most recent approval date
        otherwise.
        """
        if not self.approved:
            return None
        if self.approval_history == []:
            return None
        return dateutil.parser.parse(self.approval_history[-1][1])

    def refresh_token(self):
        """
        Generate a new master access token that expires in 24 hours.
        """
        self.master_access_token = generate_id()
        self.token_expiration_date = now_plus_24_hours()

        self.save()

    @property
    def id_label(self):
        return str("direct-sharing-{0}").format(self.id)

    @property
    def project_type(self):
        return "study" if self.is_study else "activity"

    @property
    def type(self):
        if hasattr(self, "oauth2datarequestproject"):
            return "oauth2"

        if hasattr(self, "onsitedatarequestproject"):
            return "on-site"

    @property
    def authorized_members(self):
        return self.project_members.filter_active().count()

    def active_user(self, user):
        try:
            return DataRequestProjectMember.objects.get(
                member__user=user,
                project=self,
                joined=True,
                authorized=True,
                revoked=False,
            )
        except (TypeError, AttributeError, DataRequestProjectMember.DoesNotExist):
            return None

    def is_joined(self, user):
        if self.active_user(user):
            return True
        else:
            return False

    @property
    def join_url(self):
        if self.type == "on-site":
            return reverse("direct-sharing:join-on-site", kwargs={"slug": self.slug})
        return self.oauth2datarequestproject.enrollment_url

    @property
    def connect_verb(self):
        return "join" if self.type == "on-site" else "connect"

    def delete_without_cascade(self, using=None, keep_parents=False):
        """
        Modified version of django's default delete() method.

        This method is added to enable safe deletion of the child models without
        removing objects related to it through the parent. As of Feb 2017,
        no models are directly related to the OAuth2DataRequestProject or
        OnSiteDataRequestProject child models.
        """
        allowed_models = [
            "private_sharing.onsitedatarequestproject",
            "private_sharing.oauth2datarequestproject",
        ]
        if self._meta.label_lower not in allowed_models:
            raise Exception("'delete_without_cascade' only for child models!")
        using = using or router.db_for_write(self.__class__, instance=self)
        assert self._get_pk_val() is not None, (
            "%s object can't be deleted because its %s attribute is set to None."
            % (self._meta.object_name, self._meta.pk.attname)
        )

        collector = Collector(using=using)
        collector.collect([self], keep_parents=keep_parents, collect_related=False)
        return collector.delete()


class OAuth2DataRequestProject(DataRequestProject):
    """
    Represents a data request project that authorizes through OAuth2.
    """

    class Meta:  # noqa: D101
        verbose_name = "OAuth2 data request project"

    application = models.OneToOneField(Application, on_delete=models.CASCADE)

    enrollment_url = models.URLField(
        help_text=(
            "The URL we direct members to if they're interested in "
            "sharing data with your project."
        ),
        verbose_name="Enrollment URL",
    )

    terms_url = models.URLField(
        help_text='The URL for your "terms of use" (or "terms of service").',
        verbose_name="Terms of Use URL",
    )

    # Note 20170731 MPB: URL is hard-coded below, unfortunately
    # reverse and reverse_lazy can't be used in this case.
    redirect_url = models.CharField(
        max_length=256,
        # TODO: add link
        help_text="""The return URL for our "authorization code" OAuth2 grant
        process. You can <a target="_blank" href="{0}">read more about OAuth2
        "authorization code" transactions here</a>.""".format(
            "/direct-sharing/oauth2-setup/#setup-oauth2-authorization"
        ),
        verbose_name="Redirect URL",
    )

    deauth_webhook = models.URLField(
        blank=True,
        default="",
        max_length=256,
        help_text="""The URL to send a POST to when a member
                     requests data erasure.  This request will be in the form
                     of JSON,
                     { 'project_member_id': '12345678', 'erasure_requested': True}""",
        verbose_name="Deauthorization Webhook URL",
    )

    def save(self, *args, **kwargs):
        if hasattr(self, "application"):
            application = self.application
        else:
            application = Application()

        application.name = self.name
        application.user = self.coordinator.user
        application.client_type = Application.CLIENT_CONFIDENTIAL
        application.redirect_uris = self.redirect_url
        application.authorization_grant_type = Application.GRANT_AUTHORIZATION_CODE

        application.save()

        self.application = application

        super(OAuth2DataRequestProject, self).save(*args, **kwargs)


class OnSiteDataRequestProject(DataRequestProject):
    """
    Represents a data request project that authorizes through the Open Humans
    website.
    """

    class Meta:  # noqa: D101
        verbose_name = "On-site data request project"

    consent_text = models.TextField(
        help_text=(
            'The "informed consent" text that describes your project '
            "to Open Humans members."
        )
    )

    post_sharing_url = models.URLField(
        blank=True,
        verbose_name="Post-sharing URL",
        help_text=post_sharing_url_help_text,
    )


class DataRequestProjectManagerQuerySet(models.QuerySet):
    """
    Add convenience method for getting an active user of the given project.
    """

    def filter_active(self):
        return self.filter(joined=True, authorized=True, revoked=False).filter(
            member__user__is_active=True
        )


class DataRequestProjectMember(models.Model):
    """
    Represents a member's approval of a data request.
    """

    objects = DataRequestProjectManagerQuerySet.as_manager()

    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    # represents when a member accepts/authorizes a project
    created = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(
        DataRequestProject, related_name="project_members", on_delete=models.CASCADE
    )
    project_member_id = models.CharField(max_length=16, unique=True)
    username_shared = models.BooleanField(default=False)
    granted_sources = models.ManyToManyField(DataRequestProject)
    all_sources_shared = models.BooleanField(default=False)
    consent_text = models.TextField(blank=True)
    joined = models.BooleanField(default=False)
    authorized = models.BooleanField(default=False)
    revoked = models.BooleanField(default=False)
    visible = models.BooleanField(default=True)
    erasure_requested = models.DateTimeField(null=True, blank=True, default=None)
    last_joined = ArrayField(
        ArrayField(models.CharField(max_length=32), size=2),
        default=list,
        editable=False,
    )
    last_authorized = ArrayField(
        ArrayField(models.CharField(max_length=32), size=2),
        default=list,
        editable=False,
    )

    def __init__(self, *args, **kwargs):
        # Adds self.old_joined so that we can detect when the field changes
        super().__init__(*args, **kwargs)
        self.old_joined = self.joined
        self.old_authorized = self.authorized

    def __str__(self):
        return str("{0}:{1}:{2}").format(
            repr(self.project), self.member, self.project_member_id
        )

    class Meta:
        unique_together = ("member", "project")

    @property
    def authorized_date(self):
        """
        Returns None if not authorized, most recent authorize date otherwise.
        """
        if not self.authorized:
            return None
        if self.last_authorized == []:
            return None
        return dateutil.parser.parse(self.last_authorized[-1][1])

    @property
    def joined_date(self):
        """
        Returns None if not joined, most recent joined date otherwise.
        """
        if not self.joined:
            return None
        if self.last_joined == []:
            return None
        return dateutil.parser.parse(self.last_joined[-1][1])

    @staticmethod
    def random_project_member_id():
        """
        Return a zero-padded string 16 digits long that's not already used in
        the database.
        """
        code = generate_id(size=8, chars=digits)

        while (
            DataRequestProjectMember.objects.filter(project_member_id=code).count() > 0
        ):
            code = generate_id(size=8, chars=digits)

        return code

    def deauth_webhook(self):
        """
        Sends a POST to an OAUTH2 project's specificed member erasure webhook URL.
        """
        erasure_requested = bool(self.erasure_requested)

        slug = {
            "project_member_id": self.project_member_id,
            "erasure_requested": erasure_requested,
        }

        url = self.project.oauth2datarequestproject.deauth_webhook
        json_p = json.dumps(slug)

        request_p = requests.post(url, json=json_p)
        return request_p.status_code

    def leave_project(
        self, remove_datafiles=False, done_by=None, erasure_requested=False
    ):
        self.revoked = True
        self.joined = False
        self.authorized = False
        if erasure_requested:
            self.erasure_requested = timezone.now()
        self.save()

        if self.project.type == "oauth2":
            application = self.project.oauth2datarequestproject.application
            AccessToken.objects.filter(
                user=self.member.user, application=application
            ).delete()
            RefreshToken.objects.filter(
                user=self.member.user, application=application
            ).delete()
            if self.project.oauth2datarequestproject.deauth_webhook != "":
                # It seems that there is at least one project that supplied an
                # invalid URL here.  Test for this.
                validator = URLValidator(schemes=["http", "https"])
                try:
                    validator(self.project.oauth2datarequestproject.deauth_webhook)
                except ValidationError:
                    return
                self.deauth_webhook()

        if self.project.deauth_email_notification:
            send_withdrawal_email(self.project, erasure_requested)

        log_data = {"project-id": self.project.id}
        if done_by:
            log_data["done-by"] = done_by
        self.member.user.log(
            "direct-sharing:{0}:revoke".format(self.project.type), log_data
        )

        if remove_datafiles:
            items = DataFile.objects.filter(
                user=self.member.user, source=self.project.id_label
            )
            items.delete()

    def set_visibility(self, visible_status):
        self.visible = visible_status
        self.save()

    def save(self, *args, **kwargs):
        """
        Overide to record when a project is joined and authorized and generate a
        random project member id as needed.
        """
        if self.old_joined != self.joined:
            self.last_joined.append(
                (self.joined, datetime.datetime.utcnow().isoformat())
            )
        if self.old_authorized != self.authorized:
            self.last_authorized.append(
                (self.authorized, datetime.datetime.utcnow().isoformat())
            )

        if not self.project_member_id:
            self.project_member_id = self.random_project_member_id()

        super().save(*args, **kwargs)


class CompletedManager(models.Manager):
    """
    A manager that only returns completed ProjectDataFiles.
    """

    def get_queryset(self):
        return super(CompletedManager, self).get_queryset().filter(completed=True)

    def for_user(self, user):
        return self.filter(user=user).exclude(completed=False).order_by("source")

    def public(self):
        prefix = "user__member__public_data_participant__publicdataaccess"

        filters = {
            prefix + "__is_public": True,
            prefix + "__project_membership__project": F("direct_sharing_project"),
        }

        return (
            self.filter(**filters).exclude(completed=False).order_by("user__username")
        )


class ProjectDataFile(DataFile):
    """
    A DataFile specific to DataRequestProjects; these files are linked to a
    project.
    """

    objects = CompletedManager()
    all_objects = models.Manager()

    parent = models.OneToOneField(
        DataFile,
        parent_link=True,
        related_name="parent_project_data_file",
        on_delete=models.CASCADE,
    )
    datatypes = models.ManyToManyField(DataType)
    completed = models.BooleanField(default=False)
    direct_sharing_project = models.ForeignKey(
        DataRequestProject, on_delete=models.PROTECT
    )

    def save(self, *args, **kwargs):
        if not self.source:
            self.source = self.direct_sharing_project.id_label

        super(ProjectDataFile, self).save(*args, **kwargs)

    @property
    def is_public(self):
        return bool(
            self.user.member.public_data_participant.publicdataaccess_set.filter(
                project_membership__project=self.direct_sharing_project, is_public=True
            )
        )


class ActivityFeed(models.Model):
    """
    Holds publicly shareable logs of user activity.

    Because non-project data import activities is a legacy issue, those events
    are not recorded by this model.
    """

    ACTION_CHOICES = (
        ("created-account", "created-account"),
        ("joined-project", "joined-project"),
        ("publicly-shared", "publicly-shared"),
    )

    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    project = models.ForeignKey(DataRequestProject, null=True, on_delete=models.CASCADE)
    action = models.CharField(ACTION_CHOICES, max_length=15)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.project:
            return str("{0}:{1}:{2}").format(
                self.member.user.username, self.action, self.project.slug
            )
        else:
            return str("{0}:{1}").format(self.member.user.username, self.action)

    def save(self, *args, **kwargs):
        # Check that project is null only for a project-less action.
        PROJECTLESS_ACTIONS = ["created-account"]
        if not self.project and self.action not in PROJECTLESS_ACTIONS:
            raise ValueError(
                str("Project required unless action is: {0}").format(
                    PROJECTLESS_ACTIONS
                )
            )
        super(ActivityFeed, self).save(*args, **kwargs)

    @property
    def timedelta(self):
        td = arrow.now() - arrow.get(self.timestamp)
        td_return = {"days": td.days}

        remaining_seconds = td.seconds
        td_return["hours"] = int(remaining_seconds / 3600)
        remaining_seconds -= td_return["hours"] * 3600
        td_return["minutes"] = int(remaining_seconds / 60)
        remaining_seconds -= td_return["hours"] * 60
        td_return["seconds"] = remaining_seconds

        return td_return


class FeaturedProject(models.Model):
    """
    Set up three featured projects for the home page.
    """

    project = models.ForeignKey(DataRequestProject, on_delete=models.CASCADE)
    description = models.TextField(blank=True)


from .utilities import send_withdrawal_email
