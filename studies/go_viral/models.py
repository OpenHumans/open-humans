from django.conf import settings
from django.core.urlresolvers import reverse_lazy

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

    text_name = 'GoViral'
    href_connect = 'http://www.goviralstudy.com/open-humans'
    href_add_data = 'http://www.goviralstudy.com/open-humans'
    href_learn = 'http://goviralstudy.com/'
    retrieval_url = reverse_lazy('studies:go-viral:request-data-retrieval')

    @property
    def go_viral_id(self):
        self.data.get('goViralId', None)

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
