from django.apps import AppConfig


class PublicDataConfig(AppConfig):
    """
    Configure the public data application.
    """
    name = 'public_data'
    verbose_name = 'Public Data'

    def ready(self):
        # Make sure our signal handlers get hooked up

        # pylint: disable=unused-variable
        import public_data.signals  # noqa
