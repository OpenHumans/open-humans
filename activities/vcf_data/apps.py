from django.core.urlresolvers import reverse_lazy

from activities.app_configs import UploadAppConfig


class GenomeExomeConfig(UploadAppConfig):
    """
    Configure the Genome/Exome data application.
    """

    name = __package__
    verbose_name = 'Genome/Exome Data'

    url_slug = 'genome-exome-data'

    href_connect = reverse_lazy('activities:genome-exome-data:manage-files')
    href_add_data = reverse_lazy('activities:genome-exome-data:manage-files')
    retrieval_url = reverse_lazy(
        'activities:genome-exome-data:request-data-retrieval')

    description = """A variety of commercial and research groups generate
    genome or exome sequencing data. Open Humans members can add "VCF format"
    genome and exome data their accounts."""

    data_description = {
        'name': 'Genome/exome data',
        'description': (
            'Genome or exome data (VCF format). May reveal information '
            "about health, traits, ancestry, and who you're related to."),
    }
