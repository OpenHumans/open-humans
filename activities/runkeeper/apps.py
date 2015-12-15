from django.apps import AppConfig
from django.core.urlresolvers import reverse_lazy


class RunKeeperConfig(AppConfig):
    """
    Configure the RunKeeper activity application.
    """
    name = 'activities.runkeeper'
    verbose_name = 'RunKeeper'

    data_description = {
        'name': 'Activity data',
        'description': ('GPS maps and times of activities, as well as '
                        'other logged fitness. Maps and logs can reveal '
                        'information about your location and routines.'),
    }

    connection_url = reverse_lazy('social:begin', args=('runkeeper',))
    finalization_url = reverse_lazy('activities:runkeeper:finalize-import')
