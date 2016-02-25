import random

from collections import OrderedDict

from account.models import EmailAddress as AccountEmailAddress

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.postgres.fields import JSONField
from django.contrib.staticfiles import finders
from django.db import models
from django.db.models import Prefetch, Q

from oauth2_provider.models import AccessToken

from .storage import PublicStorage


def get_member_profile_image_upload_path(instance, filename):
    """
    Construct the upload path for a given member and filename.
    """
    return 'member/%s/profile-images/%s' % (instance.user.id, filename)


def random_member_id():
    """
    Return a zero-padded string from 00000000 to 99999999 that's not in use by
    any Member.
    """
    def random_id():
        return '%08d' % random.randint(0, 99999999)

    member_id = random_id()

    while Member.objects.filter(member_id=member_id).count() > 0:
        member_id = random_id()

    return member_id


class OpenHumansUserManager(UserManager):
    """
    Allow user lookup by case-insensitive username or email address.
    """

    def get_by_natural_key(self, username):
        return self.get(Q(username__iexact=username) |
                        Q(email__iexact=username))


class User(AbstractUser):
    """
    The Django base user with case-insensitive username and email lookup.
    """

    objects = OpenHumansUserManager()

    class Meta:
        db_table = 'auth_user'


class EnrichedManager(models.Manager):
    """
    A manager that preloads everything we need for the member list page.
    """
    def get_queryset(self):
        return (super(EnrichedManager, self)
                .get_queryset()
                .select_related('user__american_gut')
                .select_related('user__go_viral')
                .select_related('user__pgp')
                .select_related('user__runkeeper')
                .select_related('user__wildlife')
                .select_related('user__twenty_three_and_me')
                .select_related('public_data_participant')
                .prefetch_related('study_grants__study')
                .prefetch_related('user__social_auth')
                .prefetch_related(Prefetch(
                    'user__accesstoken_set',
                    queryset=AccessToken.objects.select_related(
                        'application__user'))))


class Member(models.Model):
    """
    Represents an Open Humans member.
    """
    objects = models.Manager()
    enriched = EnrichedManager()

    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    name = models.CharField(max_length=30)
    profile_image = models.ImageField(
        blank=True,
        max_length=1024,
        storage=PublicStorage(),
        upload_to=get_member_profile_image_upload_path)
    about_me = models.TextField(blank=True)
    newsletter = models.BooleanField(
        default=True,
        verbose_name='Receive Open Humans news and updates')
    allow_user_messages = models.BooleanField(
        default=False,
        verbose_name='Allow members to contact me')
    member_id = models.CharField(
        max_length=8,
        unique=True,
        default=random_member_id)
    seen_pgp_interstitial = models.BooleanField(default=False)
    badges = JSONField(default=dict)

    def __unicode__(self):
        return unicode(self.user)

    @property
    def primary_email(self):
        """
        EmailAddress from accounts, used to check email validation.
        """
        return AccountEmailAddress.objects.get_primary(self.user)

    def update_badges(self):
        badges = []

        # Badges for activities and deeply integrated studies, e.g. PGP,
        # RunKeeper
        for label, connection in self.connections.items():
            badges.append({
                'url': '{}/images/badge.png'.format(label),
                'name': connection['verbose_name'],
            })

        # Badges for third-party studies, e.g. Keeping Pace
        for study_grant in self.study_grants.all():
            if not study_grant.valid:
                continue

            badges.append({
                'url': 'studies/images/{}.png'.format(study_grant.study.slug),
                'name': study_grant.study.title,
            })

        # The badge for the Public Data Sharing Study
        if self.public_data_participant.enrolled:
            badges.append({
                'url': 'public-data/images/public-data-sharing-badge.png',
                'name': 'Public Data Sharing Study',
            })

        # Only try to render badges with image files
        self.badges = [badge for badge in badges if finders.find(badge['url'])]
        self.save()

    @property
    def study_grant_studies(self):
        """
        Return a list of studies that have study grants.
        Grants represent data sharing authorizations (i.e., Open Humans is
        sharing data with a study or activity).
        """
        studies = {}
        for study_grant in self.study_grants.all():
            if not study_grant.valid:
                continue
            study = study_grant.study
            if study.slug not in studies:
                studies[study.slug] = study
        return studies

    @property
    def connections(self):
        """
        Return a list of dicts containing activity and study connection
        information. Connections represent data import relationships
        (i.e., Open Humans is receiving data from this source).
        """
        connections = {}

        prefix_to_type = {
            'studies': 'study',
            'activities': 'activity'
        }

        app_configs = apps.get_app_configs()

        for app_config in app_configs:
            # Find which type of connection it is.
            connection_type = None

            for prefix in prefix_to_type.keys():
                if app_config.name.startswith(prefix + '.'):
                    connection_type = prefix_to_type[prefix]

                    break

            if not connection_type:
                continue

            # all of the is_connected methods are written in a way that they
            # work against the cached QuerySet of the EnrichedManager
            connected = getattr(self.user, app_config.label).is_connected

            # If connected, add to the dict.
            if connected:
                connections[app_config.label] = {
                    'type': connection_type,
                    'verbose_name': app_config.verbose_name,
                    'label': app_config.label,
                    'name': app_config.name,
                    'disconnectable': app_config.disconnectable,
                }

        return OrderedDict(sorted(connections.items(),
                                  key=lambda x: x[1]['verbose_name']))


class EmailMetadata(models.Model):
    """
    Metadata about email correspondence sent from a user's profile page.
    """
    sender = models.ForeignKey(settings.AUTH_USER_MODEL,
                               related_name='sender')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 related_name='receiver')

    timestamp = models.DateTimeField(auto_now_add=True)
