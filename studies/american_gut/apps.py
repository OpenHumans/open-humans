from django.apps import AppConfig


class AmericanGutConfig(AppConfig):
    """
    Configure the American Gut study application.
    """
    name = 'studies.american_gut'
    verbose_name = 'American Gut'

    def ready(self):
        # Make sure our signal handlers get hooked up

        # pylint: disable=unused-variable
        import studies.american_gut.signals  # noqa
