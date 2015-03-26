import random

from account.models import EmailAddress as AccountEmailAddress

from django.apps import apps
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


def get_member_profile_image_upload_path(instance, filename):
    """
    Construct the upload path for a given member and filename.
    """
    return 'member/%s/profile-images/%s' % (instance.user.username, filename)


def random_member_id():
    """
    Return a zero-padded string from 00000000 to 99999999 that's not in use by
    any Member.
    """
    def random_id():
        return '%08d' % random.randint(0, 99999999)

    member_id = random_id()

    while Member.objects.filter(member_id=member_id):
        member_id = random_id()

    return member_id


class Member(models.Model):
    """
    Represents an Open Humans member.
    """
    user = models.OneToOneField(User)
    name = models.CharField(max_length=30)
    profile_image = models.ImageField(
        blank=True,
        upload_to=get_member_profile_image_upload_path)
    about_me = models.TextField(blank=True)
    newsletter = models.BooleanField(
        default=True,
        verbose_name='Receive Open Humans news and updates')
    allow_user_messages = models.BooleanField(
        default=False,
        verbose_name='Allow members to contact me')
    member_id = models.CharField(max_length=8, unique=True,
                                 default=random_member_id)

    def __unicode__(self):
        return unicode(self.user)

    @property
    def primary_email(self):
        """
        EmailAddress from accounts, used to check email validation.
        """
        return AccountEmailAddress.objects.get_primary(self.user)

    @property
    def connections(self):
        """
        Return a list of dicts containing activity and study connection
        information.
        """
        connections = {}
        cnxn_prefix_to_type = {'studies': 'study',
                               'activities': 'activity'}

        app_configs = apps.get_app_configs()
        for app_config in app_configs:

            # Find which type of connection it is.
            cnxn_type = None
            for cnxn_prefix in cnxn_prefix_to_type.keys():
                if app_config.name.startswith(cnxn_prefix + '.'):
                    cnxn_type = cnxn_prefix_to_type[cnxn_prefix]
                    break
            if not cnxn_type:
                continue

            # If a connection app, check UserData.is_connected.
            user_data_model = apps.get_model(app_config.label, 'UserData')
            try:
                user_data = user_data_model.objects.get(user=self.user)
            except user_data_model.DoesNotExist:
                continue
            connected = user_data.is_connected

            # If connected, add to the dict.
            if connected:
                connections[app_config.label] = {
                    'type': cnxn_type,
                    'verbose_name': app_config.verbose_name,
                    'label': app_config.label,
                    'name': app_config.name
                }

        return connections


@receiver(post_save, sender=User, dispatch_uid='create_member')
def cb_create_member(sender, instance, created, raw, **kwargs):
    """
    Create a member account for the newly created user.
    """
    # If we're loading a user via a fixture then `raw` will be true and in that
    # case we won't want to create a Member to go with it
    if created and not raw:
        Member.objects.create(user=instance)
