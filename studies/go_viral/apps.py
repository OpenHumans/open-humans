from django.core.urlresolvers import reverse_lazy

from common.app_configs import BaseConnectionAppConfig


class GoViralConfig(BaseConnectionAppConfig):
    """
    Configure the GoViral study application.

    Note: The verbose_name matches the 'name' assigned for this study's API
    client. This is the 'name' field for its corresponding oauth2_provider
    Application, and was set by the setup_api management command in
    open_humans/management/commands/setup_api.py
    """

    name = __package__
    verbose_name = 'GoViral'

    href_connect = 'https://www.goviralstudy.com/open-humans'
    href_add_data = 'https://www.goviralstudy.com/open-humans'
    href_learn = 'https://www.goviralstudy.com/'
    retrieval_url = reverse_lazy('studies:go-viral:request-data-retrieval')

    leader = 'Rumi Chunara'
    organization = 'NYU Polytechnic School of Engineering'

    description = """Participants in this viral surveillance study can get
    kits, then send a sample if they get sick. When possible, your analysis
    data is returned!"""

    data_description = {
        'name': 'Sickness reports and viral profiling data',
        'description':
            ('Sickness reports contain demographic and illness survey '
             'data from GoViral. They may contain sensitive information, '
             'including your exact birthdate and ZIP code. Viral '
             'profiling data contains raw data results from viral '
             'testing, performed on samples you contributed to GoViral.'),
    }
