from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.db import models

from common import fields
from data_import.models import BaseDataFile, DataRetrievalTask


class UserData(models.Model):
    """
    Used as key when a User has DataFiles for the 23andme activity.
    """

    class Meta:
        verbose_name = '23andMe user data'
        verbose_name_plural = verbose_name

    user = fields.AutoOneToOneField(settings.AUTH_USER_MODEL,
                                    related_name='twenty_three_and_me')

    text_name = '23andMe'
    href_connect = reverse_lazy('activities:23andme:upload')
    href_add_data = reverse_lazy('activities:23andme:upload')
    href_learn = 'https://www.23andme.com/'
    retrieval_url = reverse_lazy('activities:23andme:request-data-retrieval')

    def __unicode__(self):
        return '%s:%s' % (self.user, '23andme')

    @property
    def file_url(self):
        try:
            return self.data.get('fileUrl', '')
        except AttributeError:
            return ''

    @property
    def is_connected(self):
        return self.file_url


class DataFile(BaseDataFile):
    """
    Storage for a 23andme data file.
    """

    class Meta:
        verbose_name = '23andMe data file'

    user_data = models.ForeignKey(UserData)
    task = models.ForeignKey(DataRetrievalTask,
                             related_name='datafile_23andme')

    def __unicode__(self):
        return '%s:%s:%s' % (self.user_data.user,
                             '23andme', self.file)
