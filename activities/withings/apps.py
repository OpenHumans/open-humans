from activities.app_configs import UserSocialAuthAppConfig


class WithingsConfig(UserSocialAuthAppConfig):
    """
    Configure the Withings activity application.
    """

    name = __package__
    verbose_name = 'Withings'

    data_description = {
        'name': 'Health and activity data',
        'description': '',
    }
