from activities.app_configs import UserSocialAuthAppConfig


class MovesConfig(UserSocialAuthAppConfig):
    """
    Configure the Moves activity application.
    """

    name = __package__
    verbose_name = 'Moves'

    in_development = True

    data_description = {
        'name': 'Location and GPS data',
        'description': """Your Moves data contains locations and GPS recordings
        of your movements from everywhere you've been while the app has been
        running on your device.""",
    }
