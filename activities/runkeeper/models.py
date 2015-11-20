from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.db import models

from common import fields
from data_import.models import BaseDataFile, DataRetrievalTask


class UserData(models.Model):
    """
    Used as key when a User has DataFiles for the RunKeeper activity.
    """

    class Meta:
        verbose_name = 'RunKeeper user data'
        verbose_name_plural = verbose_name

    user = fields.AutoOneToOneField(settings.AUTH_USER_MODEL,
                                    related_name='runkeeper')

    text_name = 'RunKeeper'
    href_connect = reverse_lazy('social:begin', args=('runkeeper',))
    href_next = reverse_lazy('activities:runkeeper:finalize-import')
    retrieval_url = reverse_lazy('activities:runkeeper:request-data-retrieval')

    def __unicode__(self):
        return '%s:%s' % (self.user, 'runkeeper')

    @property
    def is_connected(self):
        # filter in Python to benefit from the prefetch data
        return len([s for s in self.user.social_auth.all()
                    if s.provider == 'runkeeper']) > 0

    def disconnect(self):
        self.user.social_auth.filter(provider='runkeeper').delete()

    def get_retrieval_params(self):
        return {
            'access_token': self.get_access_token(),
        }

    def get_access_token(self):
        """
        Get the access token from the most recent RunKeeeper association.
        """
        user_social_auth = (self.user.social_auth.filter(provider='runkeeper')
                            .order_by('-id')[0])

        return user_social_auth.extra_data['access_token']


class DataFile(BaseDataFile):
    """
    Storage for a RunKeeper data file.
    """

    class Meta:
        verbose_name = 'RunKeeper data file'

    user_data = models.ForeignKey(UserData, related_name='datafiles')
    task = models.ForeignKey(DataRetrievalTask,
                             related_name='datafile_runkeeper')

    def __unicode__(self):
        return '%s:%s:%s' % (self.user_data.user, 'runkeeper', self.file)
