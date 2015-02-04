from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Barcode


@receiver(pre_save, sender=Barcode)
def post_save_cb(sender, instance, created, raw, update_fields, **kwargs):
    """
    Initiate retrieval of the data corresponding to an American Gut barcode.
    """
    # If the model was created but not as part of a fixture
    if created and not raw:
        # Create a data retrieval task
        pass
