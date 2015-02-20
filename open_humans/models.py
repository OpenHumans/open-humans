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
    return "member/%s/profile-images/%s" % (instance.user.username, filename)


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
        connections = (self._get_connections('study') +
                       self._get_connections('activity'))
        return connections

    def _get_connections(self, cnxn_type):
        connections = []
        if cnxn_type == 'study':
            prefix = 'studies'
            verbose_names = [
                c.application.name for c in self.user.accesstoken_set.all() if
                c.application.user.username == 'api-administrator']
        elif cnxn_type == 'activity':
            prefix = 'activities'
            verbose_names = [c.provider for c in self.user.social_auth.all()]
        else:
            return connections
        app_configs = apps.get_app_configs()
        for verbose_name in verbose_names:
            matched = [a for a in app_configs if a.verbose_name == verbose_name
                       and a.name.startswith(prefix)]
            if matched and len(matched) == 1:
                connections.append(
                    {'type': cnxn_type,
                     'verbose_name': verbose_name,
                     'label': matched[0].label,
                     'name': matched[0].name})
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
