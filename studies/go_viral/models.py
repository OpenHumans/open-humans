from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.db import models

from common import fields
from data_import.models import BaseDataFile, DataRetrievalTask

from ..models import BaseStudyUserData


class UserData(BaseStudyUserData):
    """
    Represents the user data for one GoViral participant.
    """

    class Meta:
        verbose_name = 'GoViral user data'
        verbose_name_plural = verbose_name

    user = fields.AutoOneToOneField(settings.AUTH_USER_MODEL,
                                    related_name='go_viral')

    text_name = 'GoViral'
    href_connect = 'http://www.goviralstudy.com/open-humans'
    href_add_data = 'http://www.goviralstudy.com/open-humans'
    href_learn = 'http://goviralstudy.com/'
    retrieval_url = reverse_lazy('studies:go-viral:request-data-retrieval')

    def get_retrieval_params(self):
        # TODO: We assume a single GoViral ID.
        # If true, change GoViralId.user_data to OneToOne?
        # If false, change data processing?
        go_viral_id = (GoViralId.objects.filter(user_data=self)[0].value)

        return {
            'access_token': settings.GO_VIRAL_MANAGEMENT_TOKEN,
            'go_viral_id': go_viral_id
        }

    @property
    def has_key_data(self):
        """
        Return false if key data needed for data retrieval is not present.
        """
        connected = self.is_connected
        if connected:
            try:
                GoViralId.objects.get(user_data=self)
                return True
            except GoViralId.DoesNotExist:
                return False
        return False


class GoViralId(models.Model):
    """
    A GoViral user ID.
    """

    user_data = models.ForeignKey(UserData, related_name='go_viral_ids')

    value = models.CharField(primary_key=True, max_length=64)


class DataFile(BaseDataFile):
    """
    Storage for a GoViral data file.
    """

    class Meta:
        verbose_name = 'GoViral data file'

    user_data = models.ForeignKey(UserData)
    task = models.ForeignKey(DataRetrievalTask,
                             related_name='datafile_go_viral')

    default_subtype = 'sickness-reports'

    def __unicode__(self):
        return '%s:%s:%s' % (self.user_data.user, 'go_viral', self.file)
