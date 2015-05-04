from django.conf import settings
from django.contrib.contenttypes.models import ContentType
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
        authorization = (
            self.user.accesstoken_set
            .filter(
                application__user__username='api-administrator',
                application__name=self._meta.app_config.verbose_name)
            .count()) > 0

        return authorization

    @property
    def has_key_data(self):
        """
        Return false if key data needed for data retrieval is not present.
        """
        return self.is_connected

    def get_retrieval_params(self):
        raise NotImplementedError


class Researcher(models.Model):
    """
    Represents an Open Humans researcher.
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    name = models.CharField(max_length=48)

    approved = models.NullBooleanField()


class Study(models.Model):
    """
    Stores information about a study.
    """

    researchers = models.ForeignKey(Researcher)

    title = models.CharField(max_length=128)
    description = models.TextField()

    principal_investigator = models.CharField(max_length=128)
    organization = models.CharField(max_length=128)

    is_live = models.BooleanField(default=False)


class DataRequirement(models.Model):
    """
    Stores the data requirements (a DataFile and a subtype) for a Study.
    """

    study = models.ForeignKey(Study)

    # TODO: filter to data file ContentTypes
    data_file_model = models.ForeignKey(ContentType)

    subtypes = models.TextField()
