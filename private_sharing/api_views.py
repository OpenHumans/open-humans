from django.contrib.auth import get_user_model

from rest_framework.generics import ListAPIView, RetrieveAPIView

from common.mixins import NeverCacheMixin
from common.permissions import HasValidToken

from .api_authentication import ProjectTokenAuthentication
from .api_filter_backends import ProjectFilterBackend
from .api_permissions import HasValidProjectToken
from .models import DataRequestProject, DataRequestProjectMember
from .serializers import ProjectDataSerializer, ProjectMemberDataSerializer

UserModel = get_user_model()


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


class ProjectMemberExchangeView(NeverCacheMixin, RetrieveAPIView):
    """
    Return the project member information attached to the OAuth2 access token.
    """

    permission_classes = (HasValidToken,)
    serializer_class = ProjectMemberDataSerializer

    def get_object(self):
        """
        Get the project member related to the access_token.
        """
        return DataRequestProjectMember.objects.get(
            member=self.request.user.member)


class ProjectMemberDataView(ProjectListView):
    """
    Return information about the project's members.
    """

    serializer_class = ProjectMemberDataSerializer

    def get_queryset(self):
        return DataRequestProjectMember.objects.filter(
            revoked=False,
            authorized=True)
