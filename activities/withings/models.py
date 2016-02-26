
from common import mixins

from . import label


# XXX: this model only adds properties to the User, it doesn't store any
# additional information. For that reason it doesn't really need to be a model.
class UserData(mixins.UserSocialAuthUserData):
    """
    Used as key when a User has DataFiles for the Withings activity.
    """

    provider = label

    text_name = 'Withings'
