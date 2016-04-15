from django.conf import settings
from django.core.urlresolvers import reverse_lazy

from common.app_configs import BaseConnectionAppConfig


class PGPConfig(BaseConnectionAppConfig):
    """
    Configure the PGP Harvard study application.

    Note: The verbose_name matches the 'name' assigned for this study's API
    client. This is the 'name' field for its corresponding oauth2_provider
    Application, and was set by the setup_api management command in
    open_humans/management/commands/setup_api.py
    """

    name = __package__
    verbose_name = 'Harvard Personal Genome Project'

    if settings.ENV == 'staging':
        href_connect = 'https://my-dev.pgp-hms.org/open_humans/participate'
        href_add_data = 'https://my-dev.pgp-hms.org/open_humans/participate'
    else:
        href_connect = 'https://my.pgp-hms.org/open_humans/participate'
        href_add_data = 'https://my.pgp-hms.org/open_humans/participate'

    href_learn = 'http://www.personalgenomes.org/harvard/'
    retrieval_url = reverse_lazy('studies:pgp:request-data-retrieval')
    msg_add_data = ("We don't have your PGP Harvard identifier (huID). "
                    'You can add this through the PGP Harvard website.')
    leader = 'George Church'
    organization = 'Harvard Medical School'

    data_description = {
        'name': 'Genome and survey data',
        'description': ('Harvard Personal Genome Project whole genome data '
                        'and survey data. This can reveal information about '
                        "health, traits, ancestry, and who you're related to.")
    }
