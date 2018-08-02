import urllib.parse

from django.urls import reverse
from django.http import HttpResponseRedirect

from oauth2_provider.models import (
    get_application_model as get_oauth2_application_model)
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
        """
        Get requesting application for custom login-or-signup.
        """
        if self.request.method == 'GET':
            return get_oauth2_application_model().objects.get(
                client_id=self.request.GET.get('client_id'))
        elif self.request.method == 'POST':
            return get_oauth2_application_model().objects.get(
                client_id=self.request.POST.get('client_id'))

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch, if unauthorized use a custom login-or-signup view.

        This renders redundant the LoginRequiredMixin used by the parent class
        (oauth_provider.views.base's AuthorizationView).
        """
        if request.user.is_authenticated:
            return (super(BaseOAuth2AuthorizationView, self)
                    .dispatch(request, *args, **kwargs))

        if not self.application:
            return self.error_response(self.application_error)

        querydict = querydict_from_dict({
            'next': request.get_full_path(),
            'connection': str(self.application.name)
        })

        url = reverse('account-login-oauth2')

        url_parts = list(urllib.parse.urlparse(url))
        url_parts[4] = querydict.urlencode()

        return HttpResponseRedirect(urllib.parse.urlunparse(url_parts))
