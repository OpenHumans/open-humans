from django.db.models.signals import post_save
from django.dispatch import receiver

from data_import.signal_helpers import task_signal
from social.apps.django_app.default.models import UserSocialAuth

from .models import DataFile


@receiver(post_save, sender=UserSocialAuth)
def post_save_cb(sender, instance, created, raw, update_fields, **kwargs):
    """
    Initiate retrieval of the data corresponding to a RunKeeper access token.
    """
    if instance.provider != 'runkeeper':
        return

    # The UserSocialAuth is created before the whole OAuth2 process is complete
    if 'access_token' not in instance.extra_data:
        return

    task_params = {
        'access_token': instance.extra_data['access_token']
    }

    # Specify created=True since UserSocialAuths are created before there's an
    # access token
    task_signal(instance, True, raw, task_params, DataFile)
