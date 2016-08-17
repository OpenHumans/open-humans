from django.db.models.signals import pre_save
from django.dispatch import receiver

from data_import.signal_helpers import task_signal_pre_save

from . import label
from .models import UserData


@receiver(pre_save, sender=UserData)
def pre_save_cb(instance, **kwargs):
    """
    Create data retrieval task when American Gut UserData's data is updated.
    """
    task_signal_pre_save(instance=instance, source=label, **kwargs)
