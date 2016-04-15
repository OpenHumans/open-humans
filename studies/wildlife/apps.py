from django.core.urlresolvers import reverse_lazy

from common.app_configs import BaseConnectionAppConfig


class WildlifeConfig(BaseConnectionAppConfig):
    """
    Configure the Wildlife of Our Homes study application.

    Note: The verbose_name matches the 'name' assigned for this study's API
    client. This is the 'name' field for its corresponding oauth2_provider
    Application, and was set by the setup_api management command in
    open_humans/management/commands/setup_api.py
    """

    name = __package__
    verbose_name = 'Wild Life of Our Homes'

    href_connect = 'https://wildlifehomes-datareturn.herokuapp.com'
    href_add_data = 'https://wildlifehomes-datareturn.herokuapp.com'
    href_learn = 'http://robdunnlab.com/projects/wild-life-of-our-homes/'
    retrieval_url = reverse_lazy('studies:wildlife:request-data-retrieval')
    msg_add_data = ("We don't have a user ID that we can add "
                    'data for. You can add a user ID through the Wildlife '
                    'of Our Homes website.')

    leader = 'Rob Dunn'
    organization = 'North Carolina State University'

    data_description = {
        'name': 'OTU counts, raw reads, and survey data',
        'description':
            ('Counts of the operational taxonomic units (OTUs) in your '
             'samples (a measure of microbial diversity), the raw data '
             'from your samples, and your responses to survey questions.'),
    }
