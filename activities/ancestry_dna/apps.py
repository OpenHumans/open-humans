from django.core.urlresolvers import reverse_lazy

from activities.app_configs import UploadAppConfig


class AncestryDNAConfig(UploadAppConfig):
    """
    Configure the AncestryDNA activity application.
    """

    name = __package__
    verbose_name = 'AncestryDNA'

    url_slug = 'ancestry-dna'

    href_add_data = reverse_lazy('activities:ancestry-dna:upload')
    retrieval_url = reverse_lazy(
        'activities:ancestry-dna:request-data-retrieval')

    product_website = 'https://www.ancestry.com/dna/'

    description = """Ancestry.com's AncestryDNA is a direct-to-consumer genetic
    testing product that tests about 700,000 genetic locations."""

    long_description = """Ancestry.com's AncestryDNA is a direct-to-consumer
    genetic testing product that tests about 700,000 genetic locations. If you
    have genetic data from AncestryDNA, you can add it and share it with
    studies and other projects!"""

    data_description = {
        'name': 'Genotyping data',
        'description': (
            'Genetic data from roughly 700,000 locations in your genome. '
            'This can reveal information about health, traits, ancestry, and '
            "who you're related to."),
    }
