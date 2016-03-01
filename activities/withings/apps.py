from activities.app_configs import UserSocialAuthAppConfig


class WithingsConfig(UserSocialAuthAppConfig):
    """
    Configure the Withings activity application.
    """

    name = __package__
    verbose_name = 'Withings'

    in_development = True

    data_description = {
        'name': 'Health and activity data',
        'description': '',
    }
