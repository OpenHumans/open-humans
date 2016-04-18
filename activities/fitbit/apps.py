from activities.app_configs import UserSocialAuthAppConfig


class FitbitConfig(UserSocialAuthAppConfig):
    """
    Configure the Fitbit activity application.
    """

    name = __package__
    verbose_name = 'Fitbit'

    in_development = True

    description = """Fitbit makes activity trackers and health devices like
    scales for recording health data."""

    data_description = {
        'name': 'Health and activity data',
        'description': """Health and activity data including data about your
                          steps, sleep, and weight.""",
    }
