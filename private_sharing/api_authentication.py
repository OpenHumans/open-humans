import arrow

from django.contrib.auth import get_user_model

from oauth2_provider.models import AccessToken

from rest_framework import exceptions
from rest_framework.authentication import (BaseAuthentication,
                                           get_authorization_header)

from .models import (DataRequestProject, DataRequestProjectMember,
                     OAuth2DataRequestProject)

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

            if (not project.token_expiration_disabled and
                    project.token_expiration_date < arrow.utcnow().datetime):
                raise exceptions.AuthenticationFailed('Expired token.')

            user = project.coordinator.user
        except DataRequestProject.DoesNotExist:
            project = None
            user = None

        try:
            access_token = AccessToken.objects.get(token=key)
            project = OAuth2DataRequestProject.objects.get(
                application=access_token.application)
            project_member = DataRequestProjectMember.objects.get(
                project=project,
                member=access_token.user.member,
                joined=True,
                authorized=True,
                revoked=False)
            user = project_member.member.user
        except (AccessToken.DoesNotExist,
                OAuth2DataRequestProject.DoesNotExist,
                DataRequestProject.DoesNotExist):
            pass

        if not project or not user:
            raise exceptions.AuthenticationFailed('Invalid token.')

        return (user, project)

    def authenticate_header(self, request):
        return 'Bearer realm="api"'
