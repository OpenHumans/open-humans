from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from data_import.signal_helpers import task_signal

from .models import GoViralId, DataFile


@receiver(post_save, sender=GoViralId)
def post_save_cb(sender, instance, created, raw, update_fields, **kwargs):
    """
    Initiate retrieval of the data corresponding to an American Gut barcode.
    """
    task_params = {
        'access_token': settings.GO_VIRAL_MANAGEMENT_TOKEN,
        'go_viral_id': [instance.value]
    }

    task_signal(instance, created, raw, task_params, DataFile)
