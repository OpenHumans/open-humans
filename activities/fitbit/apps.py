from django.core.urlresolvers import reverse_lazy

from common.app_configs import BaseConnectionAppConfig


class FitbitConfig(BaseConnectionAppConfig):
    """
    Configure the Fitbit activity application.
    """
    name = __package__
    verbose_name = 'Fitbit'

    data_description = {
        'name': '',
        'description': '',
    }

    connection_url = reverse_lazy('social:begin', args=(__package__,))
    finalization_url = reverse_lazy(
        'activities:{}:finalize-import'.format(__package__))
