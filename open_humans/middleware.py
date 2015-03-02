import logging

from urlparse import urljoin

from django.conf import settings
from django.http import HttpResponseRedirect

logger = logging.getLogger(__name__)


class RedirectStagingToProductionMiddleware:
    """
    Redirect a staging URL to production if it contains a production client ID.
    """
    def process_request(self, request):
        if settings.ENV != 'staging':
            return

        if 'client_id' not in request.GET:
            return

        if request.GET['client_id'] not in settings.PRODUCTION_CLIENT_IDS:
            return

        new_url = urljoin(settings.PRODUCTION_URL, request.get_full_path())

        logger.warning('Redirecting production client URL "%s" to "%s"',
                       request.get_full_path(), new_url)

        return HttpResponseRedirect(new_url)
