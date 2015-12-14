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

    data_description = {
        'name': 'Genome and survey data',
        'description': ('Harvard Personal Genome Project whole genome data '
                        'and survey data. This can reveal information about '
                        "health, traits, ancestry, and who you're related to.")
    }

    def ready(self):
        # Make sure our signal handlers get hooked up

        # pylint: disable=unused-variable
        import studies.pgp.signals  # noqa
