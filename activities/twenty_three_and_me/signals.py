from django.db.models.signals import post_save
from django.dispatch import receiver

from data_import.signal_helpers import task_signal

from .models import UserData, DataFile


@receiver(post_save, sender=UserData)
def post_save_cb(instance, created, raw, **kwargs):
    """
    Create data retrieval task when 23andMe UserData's data is updated.
    """
    if not instance.file_url:
        return

    task_signal(instance=instance,
                created=True,
                raw=raw,
                task_params=instance.get_retrieval_params(),
                datafile_model=DataFile)
