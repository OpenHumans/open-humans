from activities.app_configs import UserSocialAuthAppConfig


class JawboneConfig(UserSocialAuthAppConfig):
    """
    Configure the Jawbone activity application.
    """

    name = __package__
    verbose_name = 'Jawbone'

    in_development = True

    description = """Jawbone makes activity trackers and health devices like
    scales for recording health data."""

    data_description = {
        'name': 'Health and activity data',
        'description': """Health and activity data including data about your
                          steps, sleep, and weight.""",
    }
