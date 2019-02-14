import arrow

from django.contrib.auth import get_user_model

from oauth2_provider.models import AccessToken
from oauth2_provider.contrib.rest_framework import OAuth2Authentication

from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from .models import DataRequestProject, OAuth2DataRequestProject

UserModel = get_user_model()


class MasterTokenAuthentication(BaseAuthentication):
    """
    Master token based authentication.
    """

    def authenticate(self, request):
        request.oauth2_error = getattr(request, "oauth2_error", {})
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != b"bearer":
            return None

        if len(auth) == 1:
            msg = "Invalid token header. No credentials provided."

            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = "Invalid token header. " "Token string should not contain spaces."

            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = (
                "Invalid token header. "
                "Token string should not contain invalid characters."
            )

            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    @staticmethod
    def authenticate_credentials(key):
        try:
            project = DataRequestProject.objects.get(master_access_token=key)

            if (
                not project.token_expiration_disabled
                and project.token_expiration_date < arrow.utcnow().datetime
            ):
                raise exceptions.AuthenticationFailed("Expired token.")

            user = project.coordinator.user
        except DataRequestProject.DoesNotExist:
            project = None
            user = None

        if not project or not user:
            raise exceptions.AuthenticationFailed("Invalid token.")

        return (user, project)

    def authenticate_header(self, request):
        return 'Bearer realm="api"'


class CustomOAuth2Authentication(OAuth2Authentication):
    """
    Custom OAuth2 auth based on `django-oauth-toolkit` version.

    (1) this raises a better error for expired tokens
    (2) this modifies the return of authenticate() to replace returned
    (user, token) with (user, project), matching the behavior of
    ProjectTokenAuthentication.
    """

    def authenticate(self, request):
        """
        Raises an exception for an expired token, or returns two-tuple of
        (user, project) if authentication succeeds, or None otherwise.
        """
        request.oauth2_error = getattr(request, "oauth2_error", {})
        access_token = None
        try:
            auth = get_authorization_header(request).split()
            token = auth[1].decode()
            access_token = AccessToken.objects.get(token=token)
        except Exception:
            pass

        if access_token and access_token.is_expired():
            raise exceptions.AuthenticationFailed("Expired token.")

        auth = super(CustomOAuth2Authentication, self).authenticate(request)

        if auth:
            project = OAuth2DataRequestProject.objects.get(
                application=auth[1].application
            )
            return (auth[0], project)

        return auth
