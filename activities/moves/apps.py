from activities.app_configs import UserSocialAuthAppConfig


class MovesConfig(UserSocialAuthAppConfig):
    """
    Configure the Moves activity application.
    """

    name = __package__
    verbose_name = 'Moves'

    data_description = {
        'name': '',
        'description': '',
    }
