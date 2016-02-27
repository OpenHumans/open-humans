from activities.app_configs import UserSocialAuthAppConfig


class RunKeeperConfig(UserSocialAuthAppConfig):
    """
    Configure the RunKeeper activity application.
    """
    name = __package__
    verbose_name = 'RunKeeper'

    data_description = {
        'name': 'Activity data',
        'description': ('GPS maps and times of activities, as well as '
                        'other logged fitness. Maps and logs can reveal '
                        'information about your location and routines.'),
    }
