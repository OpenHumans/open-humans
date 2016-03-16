from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import exceptions
from rest_framework.authentication import (BaseAuthentication,
                                           get_authorization_header)
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import BasePermission

from common.mixins import NeverCacheMixin

from .models import DataRequestProject
from .serializers import ProjectDataSerializer

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


class RetrieveProjectDetailView(NeverCacheMixin, RetrieveAPIView):
    """
    A detail view that can be GET.
    """

    authentication_classes = (ProjectTokenAuthentication,)
    permission_classes = (HasValidProjectToken,)

    def get_object(self):
        """
        Get an object from its `pk`.
        """
        filters = {}

        # There's only one DataRequestProject for a given master_access_token
        # so we don't need to filter for it. We set its lookup_field to None
        # for this reason.
        if self.lookup_field:
            filters[self.lookup_field] = self.kwargs[self.lookup_field]

        obj = get_object_or_404(self.get_queryset(), **filters)

        self.check_object_permissions(self.request, obj)

        return obj


class ProjectDataView(RetrieveProjectDetailView):
    """
    Return information about the member.
    """

    def get_queryset(self):
        return DataRequestProject.objects.filter(pk=self.request.auth.pk)

    lookup_field = None
    serializer_class = ProjectDataSerializer
