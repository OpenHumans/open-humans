from time import time

from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.db import models

from common import fields
from data_import.models import BaseDataFile, DataRetrievalTask


def get_upload_path(instance, filename=''):
    """
    Construct the upload path for a data selfie upload.
    """
    return 'member/{}/uploaded-data/data_selfie/{}-{}'.format(
        instance.user.id, int(time()), filename)


class UserData(models.Model):
    """
    Used as key when a User has DataFiles for the data_selfie activity.
    """

    class Meta:
        verbose_name = 'data selfie user data'
        verbose_name_plural = verbose_name

    user = fields.AutoOneToOneField(settings.AUTH_USER_MODEL,
                                    related_name='data_selfie')

    genome_file = models.FileField(upload_to=get_upload_path, max_length=1024,
                                   null=True)

    text_name = 'data selfie'
    href_connect = reverse_lazy('activities:data-selfie:upload')
    href_add_data = reverse_lazy('activities:data-selfie:upload')
    retrieval_url = reverse_lazy('activities:data-selfie:'
                                 'request-data-retrieval')

    def __unicode__(self):
        return '%s:%s' % (self.user, 'data_selfie')

    @property
    def file_url(self):
        try:
            return self.genome_file.url
        except ValueError:
            return ''

    @property
    def is_connected(self):
        return self.file_url

    def disconnect(self):
        self.genome_file.delete()

    def get_retrieval_params(self):
        return {'file_url': self.file_url, 'username': self.user.username}


class DataFile(BaseDataFile):
    """
    Storage for a data_selfie data file.
    """

    class Meta:
        verbose_name = 'data selfie data file'

    user_data = models.ForeignKey(UserData)
    task = models.ForeignKey(DataRetrievalTask,
                             related_name='datafile_data_selfie')

    def __unicode__(self):
        return '%s:%s:%s' % (self.user_data.user,
                             'data_selfie', self.file)
