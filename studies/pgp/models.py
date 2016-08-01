from django.conf import settings
from django.db import models

from common import fields

from . import label
from ..models import BaseStudyUserData


class UserData(BaseStudyUserData):
    """
    Represents the user data for one PGP participant.
    """

    class Meta:
        verbose_name = 'PGP user data'
        verbose_name_plural = verbose_name

    user = fields.AutoOneToOneField(settings.AUTH_USER_MODEL,
                                    related_name=label)

    def get_retrieval_params(self):
        try:
            return {'huID': HuId.objects.filter(user_data=self)[0].id}
        except IndexError:
            return {}

    @property
    def has_key_data(self):
        """
        Return false if key data needed for data retrieval is not present.
        """
        if self.is_connected:
            try:
                HuId.objects.get(user_data=self)

                return True
            except HuId.DoesNotExist:
                return False

        return False


class HuId(models.Model):
    """
    A PGP huID (human ID).
    """

    user_data = models.ForeignKey(UserData, related_name='huids')

    id = models.CharField(primary_key=True, max_length=64)
