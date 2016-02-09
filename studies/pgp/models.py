from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.db import models

from common import fields

from ..models import BaseStudyUserData


class UserData(BaseStudyUserData):
    """
    Represents the user data for one PGP participant.
    """

    class Meta:
        verbose_name = 'PGP user data'
        verbose_name_plural = verbose_name

    user = fields.AutoOneToOneField(settings.AUTH_USER_MODEL,
                                    related_name='pgp')

    text_name = 'PGP Harvard'

    if settings.ENV == 'staging':
        href_connect = 'https://my-dev.pgp-hms.org/open_humans/participate'
        href_add_data = 'https://my-dev.pgp-hms.org/open_humans/participate'
    else:
        href_connect = 'https://my.pgp-hms.org/open_humans/participate'
        href_add_data = 'https://my.pgp-hms.org/open_humans/participate'

    href_learn = 'http://www.personalgenomes.org/harvard/'
    retrieval_url = reverse_lazy('studies:pgp:request-data-retrieval')
    msg_add_data = ("We don't have your PGP Harvard identifier (huID). "
                    'You can add this through the PGP Harvard website.')

    def get_retrieval_params(self):
        try:
            return {'huID': HuId.objects.filter(user_data=self)[0].value}
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

    value = models.CharField(primary_key=True, max_length=64)
