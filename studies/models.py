from django.contrib.postgres.fields import JSONField
from django.db import models


class BaseStudyUserData(models.Model):
    """
    Abstract base class for study UserData models.

    When implemented, a user field should be defined as AutoOneToOne to
    a User from django.contrib.auth.models.
    """

    class Meta:
        abstract = True

    data = JSONField(default={})

    def __unicode__(self):
        return 'UserData: {}, {}'.format(self.user, self.__module__)

    @property
    def is_connected(self):
        """
        A study is connected if the user has 1 or more access tokens for the
        study's OAuth2 application.
        """
        # filter in Python to benefit from the prefetch data
        return len([
            a for a in self.user.accesstoken_set.all()
            if a.application.user.username == 'api-administrator' and
            a.application.name == self._meta.app_config.verbose_name
        ]) > 0

    @property
    def has_key_data(self):
        """
        Return false if key data needed for data retrieval is not present.
        """
        return self.is_connected

    def get_retrieval_params(self):
        return {'data': self.data}
