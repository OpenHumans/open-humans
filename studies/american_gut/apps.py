from django.core.urlresolvers import reverse_lazy

from common.app_configs import BaseConnectionAppConfig


class AmericanGutConfig(BaseConnectionAppConfig):
    """
    Configure the American Gut study application.

    Note: The verbose_name matches the 'name' assigned for this study's API
    client. This is the 'name' field for its corresponding oauth2_provider
    Application, and was set by the setup_api management command in
    open_humans/management/commands/setup_api.py
    """

    name = __package__
    verbose_name = 'American Gut'

    href_connect = 'https://www.microbio.me/AmericanGut/authed/open-humans/'
    href_add_data = 'https://www.microbio.me/AmericanGut/authed/open-humans/'
    href_learn = 'http://americangut.org/'
    retrieval_url = reverse_lazy('studies:american-gut:request-data-retrieval')

    msg_add_data = ("We don't have any survey IDs that we can add "
                    'data for. You can add survey IDs through the American '
                    'Gut website.')

    leader = 'Rob Knight'
    organization = 'University of California, San Diego'
    description = ('American Gut is a crowdfunded study building on '
                   "the Knight Lab's work with the Human Microbiome "
                   'Project. Answer survey questions and collect '
                   'samples at home, and get an analysis of your '
                   'microbiome.')

    data_description = {
        'name': 'Microbiome profiling and survey data',
        'description': ('Raw 16S sequencing data (FASTQ format) for each '
                        'sample, and your responses to survey questions.'),
    }
