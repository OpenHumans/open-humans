import random

from collections import OrderedDict

import arrow
from account.models import EmailAddress as AccountEmailAddress
from bs4 import BeautifulSoup

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Prefetch, Q

from oauth2_provider.models import AccessToken
import requests

from common.utils import LEGACY_APPS

from .storage import PublicStorage
from .testing import has_migration


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


class UserEvent(models.Model):
    """
    Holds logs of user events.
    """

    user = models.ForeignKey('User')
    event_type = models.CharField(max_length=32)
    timestamp = models.DateTimeField(auto_now_add=True)
    data = JSONField(default=dict)

    def __unicode__(self):
        return '{0}:{1}:{2}'.format(self.timestamp, self.user,
                                    repr(self.data)[0:50])


class OpenHumansUserManager(UserManager):
    """
    Allow user lookup by case-insensitive username or email address.
    """

    def get_queryset(self):
        """
        Alter the queryset to always get the member and the member's
        public_data_participant; this reduces the number of queries for most
        views.
        """
        # need to check that the Member and PublicDataParticipant model exist;
        # we do this by ensuring that the migration has ran (this is only
        # important when tests are being run)
        # TODO: check if this is still needed after the squash that happened
        if not has_migration('open_humans', '0006_userevent_event_type'):
            return super(OpenHumansUserManager, self).get_queryset()

        return (super(OpenHumansUserManager, self)
                .get_queryset()
                .select_related('member')
                .select_related('member__public_data_participant'))

    def get_by_natural_key(self, username):
        return self.get(Q(username__iexact=username) |
                        Q(email__iexact=username))


class User(AbstractUser):
    """
    The Django base user with case-insensitive username and email lookup.
    """

    objects = OpenHumansUserManager()

    def log(self, event_type, data):
        """
        Log an event to this user.
        """
        user_event = UserEvent(user=self, event_type=event_type, data=data)
        user_event.save()

    class Meta:  # noqa: D101
        db_table = 'auth_user'


class EnrichedManager(models.Manager):
    """
    A manager that preloads everything we need for the member list page.
    """

    def get_queryset(self):
        return (super(EnrichedManager, self)
                .get_queryset()
                .select_related('public_data_participant')
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
        # Stored on S3
        storage=PublicStorage(),
        upload_to=get_member_profile_image_upload_path)
    about_me = models.TextField(blank=True)
    # When the model is saved and this field has changed we subscribe or
    # unsubscribe the user from the Mailchimp list accordingly
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
        Get the EmailAddress from the django-accounts application, used to
        check email validation.
        """
        return AccountEmailAddress.objects.get_primary(self.user)

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
            if '.' not in app_config.name:
                continue

            prefix = app_config.name.split('.')[0]  # 'studies', 'activity'
            connection_type = prefix_to_type.get(prefix)  # 'study', 'activity'

            if not connection_type:
                continue

            # TODO: Remove this when completing app removal.
            if app_config.label in LEGACY_APPS:
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


class BlogPost(models.Model):
    """
    Store data about blogposts, to be displayed on the site.
    """
    rss_id = models.CharField(max_length=120, unique=True)
    title = models.CharField(max_length=120, blank=True)
    summary_long = models.TextField(blank=True)
    summary_short = models.TextField(blank=True)
    image_url = models.CharField(max_length=120, blank=True)
    published = models.DateTimeField()

    @classmethod
    def create(cls, rss_feed_entry):
        post = cls(rss_id=rss_feed_entry['id'])
        post.summary_long = rss_feed_entry['summary']
        req = requests.get(rss_feed_entry['id'])
        soup = BeautifulSoup(req.text)
        post.title = soup.find(attrs={'property': 'og:title'})['content']
        post.summary_short = soup.find(
            attrs={'property': 'og:description'})['content']
        image_url = soup.find(attrs={'property': 'og:image'})['content']
        if 'gravatar' not in image_url:
            post.image_url = image_url
        post.published = arrow.get(soup.find(
            attrs={'property': 'article:published_time'})['content']).datetime
        post.save()
        return post

    @property
    def published_day(self):
        return arrow.get(self.published).format('ddd, MMM D YYYY')
