from django.apps import AppConfig


class PGPConfig(AppConfig):
    """
    Configure the PGP Harvard study application.

    Note: The verbose_name matches the 'name' assigned for this study's API
    client. This is the 'name' field for its corresponding oauth2_provider
    Application, and was set by the setup_api management command in
    open_humans/management/commands/setup_api.py
    """
    name = 'studies.pgp'
    verbose_name = 'Harvard Personal Genome Project'

    subtypes = {
        'genome': {
            'name': 'Genome data',
            'description': ('Harvard Personal Genome Project whole genome '
                            'data. This can reveal information about health, '
                            "traits, ancestry, and who you're related to."),
        },
        'surveys': {
            'name': 'Survey data',
            'description': ('Harvard Personal Genome Project public survey '
                            'data. This may contain data about your age, '
                            'health, and other potentially sensitive items.'),
        },
    }

    def ready(self):
        # Make sure our signal handlers get hooked up

        # pylint: disable=unused-variable
        import studies.pgp.signals  # noqa
