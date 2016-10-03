from django.apps import AppConfig
from django.conf import settings


class OpenHumansConfig(AppConfig):
    """
    Configure the main Open Humans application.
    """

    name = 'open_humans'
    verbose_name = 'Open Humans'

    def ready(self):
        # Import this last as it's going to import settings itself...
        from django.contrib.sites import models as sites_models

        # HACK: django-user-accounts uses both get_current_site and
        # Site.get_current.  The former falls back to a RequestSite if
        # django.contrib.sites is not in INSTALLED_APPS. The latter tries to
        # look up the site in the database but first hits the SITE_CACHE, which
        # we prime here.
        sites_models.SITE_CACHE[settings.SITE_ID] = settings.SITE

        # Make sure our signal handlers get hooked up
        # pylint: disable=unused-variable
        import open_humans.signals  # noqa
