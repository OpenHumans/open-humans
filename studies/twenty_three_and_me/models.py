from django.contrib.auth.models import User
from django.db import models

from common import fields


class ActivityUser(models.Model):
    """Used as key when a User has DataSets associated with a study."""
    user = fields.AutoOneToOneField(User, related_name='23andme')


def get_upload_path(instance, filename=''):
    return "activity_data/%s/%s/%s" % (instance.study_user.user.username,
                                       instance._meta.app_label,
                                       filename)


class ActivityDataFile(models.Model):
    study_user = models.ForeignKey(ActivityUser)
    file = models.FileField(upload_to=get_upload_path)
