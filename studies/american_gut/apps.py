from common.app_configs import BaseConnectionAppConfig


class AmericanGutConfig(BaseConnectionAppConfig):
    """
    Configure the American Gut study application.

    Note: The verbose_name matches the 'name' assigned for this study's API
    client. This is the 'name' field for its corresponding oauth2_provider
    Application, and was set by the setup_api management command in
    open_humans/management/commands/setup_api.py
    """
    name = 'studies.american_gut'
    verbose_name = 'American Gut'

    data_description = {
        'name': 'Microbiome profiling and survey data',
        'description':
            ('Raw 16S sequencing data (FASTQ format) for each sample, and '
             'survey data, which may contain your ZIP code, age, and '
             'other sensitive items.'),
    }
