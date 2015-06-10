from django.apps import AppConfig


class RunKeeperConfig(AppConfig):
    """
    Configure the RunKeeper activity application.
    """
    name = 'activities.runkeeper'
    verbose_name = 'RunKeeper'

    subtypes = {
        'activities': {
            'name': 'Activity data',
            'description': ('GPS maps and times of activities, as well as '
                            'other logged fitness. Maps and logs can reveal '
                            'information about your location and routines.'),
        },
        'sleep': {
            'name': 'Sleep data',
            'description': 'Sleep log data.',
        },
        'social': {
            'name': 'Social data',
            'description': ('User IDs of your friends and the sharing status '
                            'of activity data (public, friend-only, or '
                            'private).'),
        },
    }

    # TODO: DRY this URL
    connection_url = '/auth/login/runkeeper/'
