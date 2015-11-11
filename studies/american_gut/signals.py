from django.db.models.signals import pre_save
from django.dispatch import receiver

from data_import.signal_helpers import task_signal_pre_save

from .models import UserData, DataFile


@receiver(pre_save, sender=UserData)
def pre_save_cb(instance, **kwargs):
    """
    Create data retrieval task when American Gut UserData's data is updated.
    """
    task_signal_pre_save(task_params=instance.get_retrieval_params(),
                         datafile_model=DataFile,
                         instance=instance,
                         **kwargs)
