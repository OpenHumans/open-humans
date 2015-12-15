from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.db import models

from common import fields
from data_import.models import BaseDataFile, DataRetrievalTask

from ..models import BaseStudyUserData


class UserData(BaseStudyUserData):
    """
    Represents the user data for one Wildlife of Our Homes participant.
    """

    class Meta:
        verbose_name = 'Wildlife of Our Homes user data'
        verbose_name_plural = verbose_name

    user = fields.AutoOneToOneField(settings.AUTH_USER_MODEL,
                                    related_name='wildlife')

    text_name = 'Wildlife of Our Homes'
    href_connect = 'https://wildlifehomes-datareturn.herokuapp.com'
    href_add_data = ''
    href_learn = 'http://homes.yourwildlife.org/'
    retrieval_url = reverse_lazy('studies:wildlife:request-data-retrieval')
    msg_add_data = ("We don't have a user ID that we can add "
                    'data for. You can add a user ID through the Wildlife '
                    'of Our Homes website.')

    @property
    def msg_curr_data(self):
        return ('Current data: {}. <a href="{}">Go to Wildlife of Our Homes'
                '</a> to add more.'.format(self.data, self.href_add_data))

    @property
    def has_key_data(self):
        """
        Return false if key data needed for data retrieval is not present.
        """
        return self.is_connected and self.data


class DataFile(BaseDataFile):
    """
    Storage for a Wildlife of Our Homes data file.
    """

    class Meta:
        verbose_name = 'Wildlife of Our Homes data file'

    user_data = models.ForeignKey(UserData)
    task = models.ForeignKey(DataRetrievalTask,
                             related_name='datafile_wildlife')

    def __unicode__(self):
        return '%s:%s:%s' % (self.user_data.user, 'wildlife', self.file)
