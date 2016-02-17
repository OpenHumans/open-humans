from django.core.urlresolvers import reverse_lazy

from common.app_configs import BaseConnectionAppConfig


class RunKeeperConfig(BaseConnectionAppConfig):
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

    connection_url = reverse_lazy('social:begin', args=('runkeeper',))
    finalization_url = reverse_lazy('activities:runkeeper:finalize-import')
