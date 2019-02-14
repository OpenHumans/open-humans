from django.conf import settings
from django.test.runner import DiscoverRunner

from .celery import app as celery_app

__all__ = ("celery_app",)


default_app_config = "open_humans.apps.OpenHumansConfig"


class OpenHumansDiscoverRunner(DiscoverRunner):
    """
    A test runner that silences a warning that occurs during testing against
    sqlite databases.
    """

    def __init__(self, **kwargs):
        # ./manage.py test adds back DeprecationWarnings if verbose is > 0
        if settings.IGNORE_SPURIOUS_WARNINGS:
            import logging

            logger = logging.getLogger("py.warnings")
            logger.handlers = []

        super(OpenHumansDiscoverRunner, self).__init__(**kwargs)

    def setup_test_environment(self, **kwargs):
        super(OpenHumansDiscoverRunner, self).setup_test_environment(**kwargs)

        import warnings
        import builtins

        # Filter out the 'naive timezone' warning when using a sqlite database
        warnings.filterwarnings(
            "ignore",
            category=builtins.RuntimeWarning,
            module="django.db.models.fields",
            lineno=1282,
        )
