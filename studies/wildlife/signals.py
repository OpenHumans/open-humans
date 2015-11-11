from django.db.models.signals import pre_save
from django.dispatch import receiver

from data_import.signal_helpers import task_signal_pre_save

from .models import UserData, DataFile


@receiver(pre_save, sender=UserData)
def pre_save_cb(**kwargs):
    """
    Create data retrieval task when Wildlife of Our Homes UserData's data is
    updated.
    """
    instance = kwargs['instance']

    if not instance.data:
        return

    task_params = instance.get_retrieval_params()

    task_signal_pre_save(
        task_params=task_params, datafile_model=DataFile, **kwargs)
