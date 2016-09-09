from activities.app_configs import UserSocialAuthAppConfig


class WithingsConfig(UserSocialAuthAppConfig):
    """
    Configure the Withings activity application.
    """

    name = __package__
    verbose_name = 'Withings'

    in_development = True

    product_website = 'http://www.withings.com/'

    description = """Withings makes consumer electronics devices for tracking
    health and fitness like a scale and a blood pressure monitor.  Withings
    also makes an app called HealthMate which users can enter their health
    measurements in."""

    data_description = {
        'name': 'Health and activity data',
        'description': """Health and activity data including data about your
                          steps, sleep, weight, and blood pressure.""",
    }
