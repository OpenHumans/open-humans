import urlparse

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from oauth2_provider.models import (
    get_application_model as get_oauth2_application_model)
from oauth2_provider.exceptions import OAuthToolkitError
from oauth2_provider.views.base import AuthorizationView

from .mixins import LargePanelMixin
from .utils import origin, querydict_from_dict


class BaseOAuth2AuthorizationView(LargePanelMixin, AuthorizationView):
    """
    Override oauth2_provider view to add origin, context, and customize login
    prompt.
    """

    def create_authorization_response(self, request, scopes, credentials,
                                      allow):
        """
        Add the origin to the callback URL.
        """
        uri, headers, body, status = (
            super(BaseOAuth2AuthorizationView,
                  self).create_authorization_response(
                      request, scopes, credentials, allow))

        uri += '&origin={}'.format(origin(request.GET.get('origin')))

        return (uri, headers, body, status)

    @property
    def application(self):
        try:
            # Get requesting application for custom login-or-signup
            _, credentials = self.validate_authorization_request(self.request)

            application_model = get_oauth2_application_model()

            return application_model.objects.get(
                client_id=credentials['client_id'])
        except OAuthToolkitError as error:
            # XXX: maybe a cleaner way to do this?
            self.application_error = error

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch, if unauthorized use a custom login-or-signup view.

        This renders redundant the LoginRequiredMixin used by the parent class
        (oauth_provider.views.base's AuthorizationView).
        """
        if request.user.is_authenticated():
            return (super(BaseOAuth2AuthorizationView, self)
                    .dispatch(request, *args, **kwargs))

        if not self.application:
            return self.error_response(self.application_error)

        querydict = querydict_from_dict({
            'next': request.get_full_path(),
            'connection': str(self.application.name)
        })

        url = reverse('account_login_oauth2')

        url_parts = list(urlparse.urlparse(url))
        url_parts[4] = querydict.urlencode()

        return HttpResponseRedirect(urlparse.urlunparse(url_parts))
