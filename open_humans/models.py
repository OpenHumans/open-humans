from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User)
    profile_image = models.ImageField(blank=True, upload_to='profile-images')
    about_me = models.TextField(blank=True)
    newsletter = models.BooleanField(
        default=True,
        verbose_name='Receive Open Humans news and updates')
    allow_user_messages = models.BooleanField(
        default=True,
        verbose_name='Allow members to contact me')


@receiver(post_save, sender=User, dispatch_uid='create_profile')
def cb_create_profile(sender, instance, created, raw, **kwargs):
    """
    Create an account for the newly created user.
    """
    # If we're loading a user via a fixture then `raw` will be true and in that
    # case we won't want to create a Profile to go with it
    if created and not raw:
        Profile.objects.create(user=instance)
