from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Participant


@receiver(post_save, sender=Participant)
def post_save_cb(sender, instance, created, raw, update_fields, **kwargs):
    """
    Initiate retrieval of the data corresponding to an American Gut barcode.
    """
    # If the model was updated but not created or udpated as part of a fixture
    if raw or created:
        return

    if not instance.enrolled:
        for data_file in instance.member.user.data_files:
            public_data_access = data_file.public_data_access

            public_data_access.is_public = False
            public_data_access.save(update_fields=['is_public'])
