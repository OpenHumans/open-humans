import logging

from urlparse import urljoin

from django.conf import settings
from django.http import HttpResponseRedirect

from ipware.ip import get_ip

logger = logging.getLogger(__name__)


class HttpResponseTemporaryRedirect(HttpResponseRedirect):
    """
    Redirect the request in a way that it is re-POSTed.
    """
    status_code = 307


def get_production_redirect(request):
    """
    Generate an appropriate redirect to production.
    """
    redirect_url = urljoin(settings.PRODUCTION_URL, request.get_full_path())

    logger.warning('Redirecting URL "%s" to "%s"', request.get_full_path(),
                   redirect_url)

    return HttpResponseTemporaryRedirect(redirect_url)


class QueryStringAccessTokenToBearerMiddleware:
    """
    django-oauth-toolkit wants access tokens specified using the
    "Authorization: Bearer" header.
    """
    def process_request(self, request):
        if 'access_token' not in request.GET:
            return

        request.META['HTTP_AUTHORIZATION'] = 'Bearer {}'.format(
            request.GET['access_token'])


class RedirectStealthToProductionMiddleware:
    """
    Redirect a staging URL to production if it contains a production client ID.
    """
    def process_request(self, request):
        if settings.ENV != 'production':
            return

        if not request.META['HTTP_HOST'].startswith('stealth.openhumans.org'):
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
