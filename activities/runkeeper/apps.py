from django.apps import AppConfig
from django.core.urlresolvers import reverse_lazy


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

    connection_url = reverse_lazy('social:begin', args=('runkeeper',))
    finalization_url = reverse_lazy('activities:runkeeper:finalize-import')
