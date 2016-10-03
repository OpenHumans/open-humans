from django.conf import settings

from common import fields

from . import label
from ..models import BaseStudyUserData


class UserData(BaseStudyUserData):
    """
    Represents the user data for one American Gut participant.
    """

    class Meta:  # noqa: D101
        verbose_name = 'American Gut user data'
        verbose_name_plural = verbose_name

    user = fields.AutoOneToOneField(settings.AUTH_USER_MODEL,
                                    related_name=label)

    @property
    def survey_ids(self):
        try:
            return self.data.get('surveyIds', [])
        except AttributeError:
            return []

    @property
    def has_key_data(self):
        """
        Return false if key data needed for data retrieval is not present.
        """
        return self.is_connected and self.survey_ids
