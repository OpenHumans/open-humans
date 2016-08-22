from django.db.models.signals import post_save
from django.dispatch import receiver

from data_import.signal_helpers import task_signal

from .models import UserData


@receiver(post_save, sender=UserData)
def post_save_cb(sender, instance, created, raw, update_fields, **kwargs):
    """
    Initiate retrieval of the data corresponding to a GoViral ID.
    """
    if not instance.go_viral_id:
        return

    task_signal(instance, created, raw, 'go_viral')
