from django.apps import AppConfig


class WildlifeConfig(AppConfig):
    """
    Configure the Wildlife of Our Homes study application.

    Note: The verbose_name matches the 'name' assigned for this study's API
    client. This is the 'name' field for its corresponding oauth2_provider
    Application, and was set by the setup_api management command in
    open_humans/management/commands/setup_api.py
    """
    name = 'studies.wildlife'
    verbose_name = 'Wildlife of Our Homes'

    def ready(self):
        # Make sure our signal handlers get hooked up

        # pylint: disable=unused-variable
        import studies.wildlife.signals  # noqa
