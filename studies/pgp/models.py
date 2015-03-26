from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.db import models

from common import fields
from data_import.models import BaseDataFile, DataRetrievalTask

from ..models import BaseStudyUserData


class UserData(BaseStudyUserData):
    """
    Represents the user data for one PGP participant.
    """

    user = fields.AutoOneToOneField(User, related_name='pgp')

    text_name = 'PGP Harvard'
    href_connect = 'https://my.pgp-hms.org/open_humans/participate'
    href_add_data = 'https://my.pgp-hms.org/open_humans/participate'
    href_learn = 'http://www.personalgenomes.org/harvard/'
    retrieval_url = reverse_lazy('studies:pgp:request-data-retrieval')
    msg_add_data = ("We don't have your PGP Harvard identifier (huID). "
                    'You can add this through the PGP Harvard website.')

    def get_retrieval_params(self):
        # TODO: We assume a single huID.
        # If true, change HuID.user_data to OneToOne?
        # If false, change data processing?
        return {
            'huID': HuId.objects.filter(user_data=self)[0].value,
        }

    @property
    def has_key_data(self):
        """
        Return false if key data needed for data retrieval is not present.
        """
        connected = self.is_connected
        if connected:
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


class DataFile(BaseDataFile):
    """
    Storage for a PGP data file.
    """
    user_data = models.ForeignKey(UserData)
    task = models.ForeignKey(DataRetrievalTask, related_name='datafile_pgp')

    def __unicode__(self):
        return '%s:%s:%s' % (self.user_data.user, 'pgp', self.file)
