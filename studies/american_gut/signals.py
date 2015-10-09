from django.db.models.signals import post_save
from django.dispatch import receiver

from data_import.signal_helpers import task_signal

from .models import UserData, DataFile


@receiver(post_save, sender=UserData)
def post_save_cb(sender, instance, created, raw, update_fields, **kwargs):
    """
    Initiate retrieval of the data corresponding to an American Gut survey ID.
    """
    if not instance.survey_ids:
        return

    task_params = {
        'survey_ids': [instance.survey_ids]
    }

    task_signal(instance, created, raw, task_params, DataFile)
