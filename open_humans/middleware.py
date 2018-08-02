import logging

from urllib.parse import urljoin

from django.conf import settings
import django.urls as urlresolvers
from django.http import HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin
from django.utils.http import urlencode

from data_import.models import is_public
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

    logger.warning('Redirecting URL "%s" to "%s"', request.get_full_path(),
                   redirect_url)

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
                request.GET['access_token'])
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


class PGPInterstitialRedirectMiddleware(object):
    """
    Redirect users with more than 1 private PGP datasets and zero public
    datasets to an interstitial page exactly one time.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    # pylint: disable=unused-argument
    def __call__(self, request):
        if request.user.is_anonymous:
            return self.get_response(request)

        try:
            request.user.member
        except Member.DoesNotExist:
            return self.get_response(request)

        if 'pgp' not in request.user.member.connections:
            return self.get_response(request)

        if request.user.member.seen_pgp_interstitial:
            return self.get_response(request)

        # Don't redirect if user is already on the intended interstitial.
        try:
            if request.resolver_match.url_name == 'pgp-interstitial':
                return self.get_response(request)
        except AttributeError:
            pass

        # Try gently, give up if this breaks.
        try:
            if not is_public(request.user.member, 'pgp'):
                url = '{}?{}'.format(
                    urlresolvers.reverse('pgp-interstitial'),
                    urlencode({'next': request.get_full_path()}))
                return HttpResponseRedirect(url)
            else:
                request.user.member.seen_pgp_interstitial = True
                request.user.member.save()
        except:  # pylint: disable=bare-except
            pass
        return self.get_response(request)


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
