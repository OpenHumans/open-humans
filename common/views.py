from oauth2_provider.models import (
    get_application_model as get_oauth2_application_model)
from oauth2_provider.views.base import AuthorizationView

from .mixins import LargePanelMixin, PrivateMixin
from .utils import origin


class BaseOAuth2AuthorizationView(PrivateMixin,
                                  LargePanelMixin, AuthorizationView):
    """
    Override oauth2_provider view to add origin, context, and customize login
    prompt.
    """
    def get_login_message(self):
        """
        Custom message for OAuth2 project authorization.
        """
        message = ('Please log in or sign up to Open Humans '
                   'to authorize "{0}"'.format(self.application.name))
        return message

    def create_authorization_response(self, request, scopes, credentials,
                                      allow):
        """
        Add the origin to the callback URL.

        TODO: Potential cleanup, 'origin' may be obsolete code - MPB 2018-12
        """
        uri, headers, body, status = (
            super(BaseOAuth2AuthorizationView,
                  self).create_authorization_response(
                      request, scopes, credentials, allow))

        uri += '&origin={}'.format(origin(request.GET.get('origin')))

        return (uri, headers, body, status)

    @property
    def application(self):
        """
        Get requesting application for custom login-or-signup.
        """
        if self.request.method == 'GET':
            return get_oauth2_application_model().objects.get(
                client_id=self.request.GET.get('client_id'))
        elif self.request.method == 'POST':
            return get_oauth2_application_model().objects.get(
                client_id=self.request.POST.get('client_id'))

    def get(self, request, *args, **kwargs):
        """
        Override to check that we are requesting a valid oauth2 project.
        """
        if not self.application:
            return self.error_response(self.application_error)
        return super().get(request, *args, **kwargs)
