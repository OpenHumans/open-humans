from django.apps import AppConfig
from django.conf import settings


class OpenHumansConfig(AppConfig):
    """
    Configure the main Open Humans application.
    """

    name = 'open_humans'
    verbose_name = 'Open Humans'

    def ready(self):
        # Make sure our signal handlers get hooked up
        # pylint: disable=unused-variable
        import open_humans.signals  # noqa
