from django.contrib.auth import get_user_model

from rest_framework import exceptions
from rest_framework.authentication import (BaseAuthentication,
                                           get_authorization_header)
from rest_framework.filters import BaseFilterBackend
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import BasePermission

from common.mixins import NeverCacheMixin

from .models import DataRequestProject, DataRequestProjectMember
from .serializers import ProjectDataSerializer, ProjectMemberDataSerializer

UserModel = get_user_model()


class HasValidProjectToken(BasePermission):
    """
    Return True if the request has a valid project token.
    """

    def has_permission(self, request, view):
        return bool(request.auth)


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


class ProjectFilterBackend(BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(project=request.auth)


class ProjectAPIView(NeverCacheMixin):
    """
    The base class for all Project-related API views.
    """

    authentication_classes = (ProjectTokenAuthentication,)
    permission_classes = (HasValidProjectToken,)


class ProjectDetailView(ProjectAPIView, RetrieveAPIView):
    """
    A detail view for the Project or models directly related to it.
    """

    def get_object(self):
        """
        Get the project related to the access_token.
        """
        return DataRequestProject.objects.get(pk=self.request.auth.pk)


class ProjectListView(ProjectAPIView, ListAPIView):
    """
    A list view for models directly related to the Project model.
    """

    filter_backends = (ProjectFilterBackend,)


class ProjectDataView(ProjectDetailView):
    """
    Return information about the project itself.
    """

    serializer_class = ProjectDataSerializer


class ProjectMemberDataView(ProjectListView):
    """
    Return information about the project's members.
    """

    def get_queryset(self):
        return DataRequestProjectMember.objects.filter(
            revoked=False,
            authorized=True)

    serializer_class = ProjectMemberDataSerializer
