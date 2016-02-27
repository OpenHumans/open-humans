from django.conf import settings
from django.db import models

from activities.user_data import UserSocialAuthUserData
from common import fields

from . import label


# XXX: this model only adds properties to the User, it doesn't store any
# additional information. For that reason it doesn't really need to be a model.
class UserData(models.Model, UserSocialAuthUserData):
    """
    Used as key when a User has DataFiles for the RunKeeper activity.
    """

    provider = label

    user = fields.AutoOneToOneField(settings.AUTH_USER_MODEL,
                                    related_name=label)

    text_name = 'RunKeeper'
