from django.conf import settings
from django.urls import reverse

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class MyAccountAdapter(DefaultAccountAdapter):
    """
    Subclass allauth's adapter to change the redirect on login behavior
    """

    def get_login_redirect_url(self, request):
        """
        We want to redirect based on what is set in the session rather than
        use the default method of passing a ?next= parameter on the URL.
        """
        path = request.session.pop('next_url', reverse(settings.LOGIN_REDIRECT_URL))
        return path


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Subclass allauth's social account adapter to change the redirect on login
    behavior
    """

    def get_connect_redirect_url(self, request, socialaccount):
        """
        We want to redirect based on what is set in the session rather than
        use the default method of passing a ?next= parameter on the URL.
        """
        assert request.user.is_authenticated
        path = request.session.pop('next_url',
                                   reverse(settings.LOGIN_REDIRECT_URL))
        return path
