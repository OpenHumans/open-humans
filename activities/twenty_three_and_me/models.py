import social.strategies.utils

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.db import models

from common import fields
from data_import.models import BaseDataFile, DataRetrievalTask


class UserData(models.Model):
    """
    Used as key when a User has DataFiles for the 23andme activity.
    """
    user = fields.AutoOneToOneField(User, related_name='twenty_three_and_me')

    text_name = '23andMe'
    connection_modal_target = 'add-data-23andme-modal'
    retrieval_url = reverse_lazy('activities:23andme:request-data-retrieval')

    def __unicode__(self):
        return '%s:%s' % (self.user, '23andme')

    @property
    def is_connected(self):
        authorization = [a for a in self.user.social_auth.all() if
                         a.provider == '23andme']
        if authorization:
            try:
                ProfileId.objects.get(user_data=self)
                return True
            except ProfileId.DoesNotExist:
                return False
        return False

    def get_retrieval_params(self):
        app_task_params = {
            'profile_id': self.profileid.profile_id,
            'access_token': self.get_access_token(),
        }
        return app_task_params

    def get_access_token(self):
        """
        Get the access token from the most recent 23andMe association.
        """
        user_social_auth = (self.user.social_auth.filter(provider='23andme')
                            .order_by('-id')[0])
        # Refresh to make sure the token is fresh.
        # MPB: Not yet sure this is working. The following does update the
        # refresh_token, which seems to indicate the refresh worked. But
        # because 23andme returns the same access_token (presumably because
        # it's not yet expired), I haven't yet been able to observe an access
        # token update. (Token expiration is 24 hours.)
        strategy = social.strategies.utils.get_current_strategy()
        user_social_auth.refresh_token(strategy=strategy)
        return user_social_auth.extra_data['access_token']


class ProfileId(models.Model):
    """
    Store the profile ID for this user's 23andme data.

    One user account can have multiple individuals represented within it. Our
    initial connection determines which 23andme profile ID corresponds to the
    Open Humans member and store that here.
    """
    user_data = models.OneToOneField(UserData)

    profile_id = models.CharField(max_length=16)


class DataFile(BaseDataFile):
    """
    Storage for a 23andme data file.
    """
    user_data = models.ForeignKey(UserData)
    task = models.ForeignKey(DataRetrievalTask,
                             related_name='datafile_23andme')

    def __unicode__(self):
        return '%s:%s:%s' % (self.user_data.user,
                             '23andme', self.file)
