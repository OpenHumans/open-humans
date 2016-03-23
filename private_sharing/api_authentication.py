from django.contrib.auth import get_user_model

from rest_framework import exceptions
from rest_framework.authentication import (BaseAuthentication,
                                           get_authorization_header)

from .models import DataRequestProject

UserModel = get_user_model()


class ProjectTokenAuthentication(BaseAuthentication):
    """
    Project token based authentication.
    """

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'bearer':
            return None

        if len(auth) == 1:
            msg = ('Invalid token header. No credentials provided.')

            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = ('Invalid token header. '
                   'Token string should not contain spaces.')

            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = ('Invalid token header. '
                   'Token string should not contain invalid characters.')

            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    @staticmethod
    def authenticate_credentials(key):
        try:
            project = DataRequestProject.objects.get(master_access_token=key)
        except DataRequestProject.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        return (project.coordinator.user, project)

    def authenticate_header(self, request):
        return 'Bearer realm="api"'
