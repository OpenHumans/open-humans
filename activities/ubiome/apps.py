from django.core.urlresolvers import reverse_lazy

from activities.app_configs import UploadAppConfig


class UBiomeConfig(UploadAppConfig):
    """
    Configure the uBiome activity application.
    """

    name = __package__
    verbose_name = 'uBiome'

    href_connect = reverse_lazy('activities:ubiome:manage-samples')
    href_add_data = reverse_lazy('activities:ubiome:manage-samples')
    href_learn = 'http://ubiome.com/'
    retrieval_url = reverse_lazy('activities:ubiome:request-data-retrieval')

    description = """uBiome is a biotechnology company based in San Francisco
    that gives individuals and organizations access to sequencing technology to
    sequence their microbiomes with a sampling kit and website."""

    data_description = {
        'name': 'Microbiome data',
        'description': (
            'Taxonomy and raw 16S microbiome sequencing data (FASTQ format).'
        ),
    }
