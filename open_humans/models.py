from account.models import EmailAddress as AccountEmailAddress

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Member(models.Model):
    user = models.OneToOneField(User)
    profile_image = models.ImageField(blank=True, upload_to='member-images')
    about_me = models.TextField(blank=True)
    newsletter = models.BooleanField(
        default=True,
        verbose_name='Receive Open Humans news and updates')
    allow_user_messages = models.BooleanField(
        default=True,
        verbose_name='Allow members to contact me')

    def __unicode__(self):
        return unicode(self.user)

    @property
    def primary_email(self):
        """EmailAddress from accounts, used to check email validation"""
        return AccountEmailAddress.objects.get_primary(self.user)


@receiver(post_save, sender=User, dispatch_uid='create_member')
def cb_create_member(sender, instance, created, raw, **kwargs):
    """
    Create a member account for the newly created user.
    """
    # If we're loading a user via a fixture then `raw` will be true and in that
    # case we won't want to create a Member to go with it
    if created and not raw:
        Member.objects.create(user=instance)
