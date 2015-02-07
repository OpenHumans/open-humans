import json

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

from data_import.models import DataRetrievalTask

from .models import Barcode, DataFile


@receiver(post_save, sender=Barcode)
def post_save_cb(sender, instance, created, raw, update_fields, **kwargs):
    """
    Initiate retrieval of the data corresponding to an American Gut barcode.
    """
    # If the model was created but not as part of a fixture
    if raw or not created:
        return

    task = DataRetrievalTask(
        datafile_model=ContentType.objects.get_for_model(DataFile),
        user=instance.user_data.user,
        app_task_params=json.dumps({'barcodes': [instance.value]}))

    task.save()

    if instance.user_data.user.member.primary_email.verified:
        task.start_task()
    else:
        task.postpone_task()
