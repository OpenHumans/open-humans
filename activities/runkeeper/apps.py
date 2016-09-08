from activities.app_configs import UserSocialAuthAppConfig


class RunKeeperConfig(UserSocialAuthAppConfig):
    """
    Configure the RunKeeper activity application.
    """

    name = __package__
    verbose_name = 'RunKeeper'

    product_website = 'https://runkeeper.com/'

    description = """RunKeeper is a free smartphone app for GPS
    fitness-tracking. You can use it to record GPS timepoint data for runs,
    walks, bicycling, and other exercise."""

    data_description = {
        'name': 'Activity data',
        'description': ('GPS maps and times of activities, as well as '
                        'other logged fitness. Maps and logs can reveal '
                        'information about your location and routines.'),
    }
