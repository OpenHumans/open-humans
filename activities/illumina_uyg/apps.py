from django.core.urlresolvers import reverse_lazy

from activities.app_configs import UploadAppConfig


class IlluminaUYGConfig(UploadAppConfig):
    """
    Configure the Illumina Understand Your Genome activity application.
    """

    name = __package__
    verbose_name = 'Illumina Understand Your Genome'

    url_slug = 'illumina-uyg'

    in_development = False

    href_connect = reverse_lazy('activities:illumina-uyg:upload')
    href_add_data = reverse_lazy('activities:illumina-uyg:upload')
    href_learn = ('http://www.illumina.com/company/events'
                  '/understand-your-genome.html')
    retrieval_url = reverse_lazy(
        'activities:illumina-uyg:request-data-retrieval')

    description = """Illumina makes genetic sequencing hardware and also
    providers sequencing services to individuals through its 'Understand Your
    Genome' product."""

    data_description = {
        'name': 'Genome data',
        'description': (
            'Whole genome data in gVCF format. This can reveal information '
            "about health, traits, ancestry, and who you're related to."),
    }
