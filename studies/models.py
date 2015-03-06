from django.db import models


class BaseStudyUserData(models.Model):
    """
    Abstract base class for study UserData models.

    When implemented, a user field should be defined as AutoOneToOne to
    a User from django.contrib.auth.models.
    """

    class Meta:
        abstract = True

    @property
    def is_connected(self):
        authorization = [
            c for c in self.user.accesstoken_set.all() if
            c.application.user.username == 'api-administrator' and
            c.application.name == self._meta.app_config.verbose_name]
        if authorization:
            return True
        return False

    @property
    def has_key_data(self):
        """
        Return false if key data needed for data retrieval is not present.
        """
        return self.is_connected

    def get_retrieval_params(self):
        raise NotImplementedError
