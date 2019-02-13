import logging

from urllib.parse import urljoin

from django.conf import settings
from django.http import HttpResponseRedirect

from .models import Member

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

    logger.warning(
        'Redirecting URL "%s" to "%s"', request.get_full_path(), redirect_url
    )

    return HttpResponseTemporaryRedirect(redirect_url)


class QueryStringAccessTokenToBearerMiddleware(object):
    """
    django-oauth-toolkit wants access tokens specified using the
    "Authorization: Bearer" header.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'access_token' in request.GET:
            request.META['HTTP_AUTHORIZATION'] = 'Bearer {}'.format(
                request.GET['access_token']
            )
        return self.get_response(request)


class RedirectStealthToProductionMiddleware(object):
    """
    Redirect a staging URL to production if it contains a production client ID.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # This redirect only happens in production
        if settings.ENV != 'production':
            return self.get_response(request)

        # Only redirect requests sent to stealth.openhumans.org
        if not request.META['HTTP_HOST'].startswith('stealth.openhumans.org'):
            return self.get_response(request)

        # Don't redirect requests to the API
        if request.get_full_path().startswith('/api'):
            return self.get_response(request)

        return get_production_redirect(request)


class RedirectStagingToProductionMiddleware(object):
    """
    Redirect a staging URL to production if it contains a production client ID.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.ENV != 'staging':
            return self.get_response(request)

        if 'client_id' not in request.GET:
            return self.get_response(request)

        if request.GET['client_id'] not in settings.PRODUCTION_CLIENT_IDS:
            return self.get_response(request)

        return get_production_redirect(request)


class AddMemberMiddleware(object):
    """
    A convenience middleware that adds the Member to the request if the user is
    authenticated.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Add the member to the request object if the user is authenticated.
        """
        try:
            request.member = request.user.member
        except (Member.DoesNotExist, AttributeError):
            request.member = None
        return self.get_response(request)
