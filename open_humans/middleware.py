import logging

from urlparse import urljoin

from django.conf import settings
from django.http import HttpResponseRedirect

from ipware.ip import get_ip

logger = logging.getLogger(__name__)


def get_production_redirect(request):
    """
    Generate an appropriate redirect to production.
    """
    redirect_url = urljoin(settings.PRODUCTION_URL, request.get_full_path())

    logger.warning('Redirecting production client URL "%s" to "%s"',
                   request.get_full_path(), redirect_url)

    return HttpResponseRedirect(redirect_url)


class RedirectAmericanGutToProductionMiddleware:
    """
    Redirect a request from American Gut to production.
    """
    def process_request(self, request):
        if get_ip(request) != '128.138.93.14':
            return

        return get_production_redirect(request)


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

        return get_production_redirect(request)
