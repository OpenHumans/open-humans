from django.core.urlresolvers import reverse_lazy

from common.app_configs import BaseConnectionAppConfig


class WithingsConfig(BaseConnectionAppConfig):
    """
    Configure the Withings activity application.
    """
    name = __package__
    verbose_name = 'Withings'

    data_description = {
        'name': '',
        'description': '',
    }

    connection_url = reverse_lazy('social:begin', args=('withings',))
    finalization_url = reverse_lazy('activities:withings:finalize-import')
