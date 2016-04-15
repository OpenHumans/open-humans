from django.core.urlresolvers import reverse_lazy

from activities.app_configs import UploadAppConfig


class AncestryDNAConfig(UploadAppConfig):
    """
    Configure the AncestryDNA activity application.
    """

    name = __package__
    verbose_name = 'AncestryDNA'

    url_slug = 'ancestry-dna'

    href_connect = reverse_lazy('activities:ancestry-dna:upload')
    href_add_data = reverse_lazy('activities:ancestry-dna:upload')
    href_learn = 'http://dna.ancestry.com/'
    retrieval_url = reverse_lazy(
        'activities:ancestry-dna:request-data-retrieval')

    description = """Ancestry.com's AncestryDNA is a direct-to-consumer genetic
    testing product that tests about 700,000 genetic locations."""

    data_description = {
        'name': 'Genotyping data',
        'description': (
            'Genetic data from roughly 700,000 locations in your genome. '
            'This can reveal information about health, traits, ancestry, and '
            "who you're related to."),
    }
