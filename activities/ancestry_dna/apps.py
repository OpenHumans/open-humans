from common.app_configs import BaseConnectionAppConfig


class AncestryDNAConfig(BaseConnectionAppConfig):
    """
    Configure the AncestryDNA activity application.
    """

    name = __package__
    verbose_name = 'AncestryDNA'

    url_slug = 'ancestry-dna'

    connection_template = 'partials/upload-activity.html'

    data_description = {
        'name': 'Genotyping data',
        'description': (
            'Genetic data from roughly 700,000 locations in your genome. '
            'This can reveal information about health, traits, ancestry, and '
            "who you're related to."),
    }
