from activities.app_configs import UploadAppConfig


class IlluminaUYGConfig(UploadAppConfig):
    """
    Configure the Illumina Understand Your Genome activity application.
    """

    name = __package__
    verbose_name = 'Illumina Understand Your Genome'

    url_slug = 'illumina-uyg'

    in_development = True

    organization_description = """Illumina makes genetic sequencing hardware
    and also providers sequencing services to individuals through its
    'Understand Your Genome' product."""

    data_description = {
        'name': 'Genome data',
        'description': (
            'Whole genome data in gVCF format. This can reveal information '
            "about health, traits, ancestry, and who you're related to."),
    }
