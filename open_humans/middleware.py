import logging

from urlparse import urljoin

from django.conf import settings
from django.core import urlresolvers
from django.http import HttpResponseRedirect
from django.utils.http import urlencode

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


class QueryStringAccessTokenToBearerMiddleware:
    """
    django-oauth-toolkit wants access tokens specified using the
    "Authorization: Bearer" header.
    """
    @staticmethod
    def process_request(request):
        if 'access_token' not in request.GET:
            return

        request.META['HTTP_AUTHORIZATION'] = 'Bearer {}'.format(
            request.GET['access_token'])


class RedirectStealthToProductionMiddleware:
    """
    Redirect a staging URL to production if it contains a production client ID.
    """
    @staticmethod
    def process_request(request):
        # This redirect only happens in production
        if settings.ENV != 'production':
            return

        # Only redirect requests sent to stealth.openhumans.org
        if not request.META['HTTP_HOST'].startswith('stealth.openhumans.org'):
            return

        # Don't redirect requests to the API
        if request.get_full_path().startswith('/api'):
            return

        return get_production_redirect(request)


class RedirectStagingToProductionMiddleware:
    """
    Redirect a staging URL to production if it contains a production client ID.
    """
    @staticmethod
    def process_request(request):
        if settings.ENV != 'staging':
            return

        if 'client_id' not in request.GET:
            return

        if request.GET['client_id'] not in settings.PRODUCTION_CLIENT_IDS:
            return

        return get_production_redirect(request)


class PGPInterstitialRedirectMiddleware:
    """
    Redirect users with more than 1 private PGP datasets and zero public
    datasets to an interstitial page exactly one time.
    """
    @staticmethod
    def process_view(request, view_func, *view_args, **view_kwargs):
        if request.user.is_anonymous():
            return

        try:
            request.user.member
        except Member.DoesNotExist:
            return

        if 'pgp' not in request.user.member.connections:
            return

        if request.user.member.seen_pgp_interstitial:
            return

        # Don't redirect if user is already on the intended interstitial.
        try:
            if request.resolver_match.url_name == 'pgp-interstitial':
                return
        except AttributeError:
            pass

        private = (request.user.pgp.datafile_set
                   .filter(_public_data_access__is_public=False))
        public = (request.user.pgp.datafile_set
                  .filter(_public_data_access__is_public=True))

        if private.count() > 0 and public.count() < 1:
            url = '{}?{}'.format(urlresolvers.reverse('pgp-interstitial'),
                                 urlencode({'next': request.get_full_path()}))

            return HttpResponseRedirect(url)
        elif public.count() > 0:
            request.user.member.seen_pgp_interstitial = True
            request.user.member.save()
