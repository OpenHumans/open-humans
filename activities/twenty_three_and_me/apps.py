from django.core.urlresolvers import reverse_lazy

from activities.app_configs import UploadAppConfig


class TwentyThreeAndMeConfig(UploadAppConfig):
    """
    Configure the 23andme activity application.
    """

    name = __package__
    verbose_name = '23andMe'

    href_connect = reverse_lazy('activities:23andme:upload')
    href_add_data = reverse_lazy('activities:23andme:upload')
    href_learn = 'https://www.23andme.com/'
    retrieval_url = reverse_lazy('activities:23andme:request-data-retrieval')

    description = """23andMe is a direct-to-consumer genetic testing company
    that tests about one million genetic locations."""

    data_description = {
        'name': 'Genotyping data',
        'description': (
            'Genetic data from roughly one million locations in your '
            'genome. This can reveal information about health, traits, '
            "ancestry, and who you're related to."),
    }
