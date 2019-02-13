from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Participant


@receiver(post_save, sender=Participant)
def post_save_cb(sender, instance, created, raw, update_fields, **kwargs):
    """
    Set all PublicDataAccess objects' is_public to false when a user leaves the
    public sharing study.
    """
    # If the model was updated but not created or udpated as part of a fixture
    if raw or created:
        return

    if not instance.enrolled:
        for public_data_access in instance.publicdataaccess_set.all():
            public_data_access.is_public = False
            public_data_access.save(update_fields=["is_public"])
