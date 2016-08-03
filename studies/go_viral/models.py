from django.conf import settings

from common import fields

from . import label
from ..models import BaseStudyUserData


class UserData(BaseStudyUserData):
    """
    Represents the user data for one GoViral participant.
    """

    class Meta:
        verbose_name = 'GoViral user data'
        verbose_name_plural = verbose_name

    user = fields.AutoOneToOneField(settings.AUTH_USER_MODEL,
                                    related_name=label)

    @property
    def go_viral_id(self):
        return self.data.get('goViralId', None)

    def get_retrieval_params(self):
        return {
            'access_token': settings.GO_VIRAL_MANAGEMENT_TOKEN,
            'go_viral_id': self.go_viral_id
        }

    @property
    def has_key_data(self):
        """
        Return false if key data needed for data retrieval is not present.
        """
        return self.is_connected and self.go_viral_id is not None
