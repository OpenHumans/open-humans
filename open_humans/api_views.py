from distutils.util import strtobool

from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.exceptions import APIException
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView

from common.mixins import NeverCacheMixin
from data_import.models import DataType
from data_import.serializers import DataTypeSerializer
from public_data.serializers import (
    PublicDataFileSerializer as LegacyPublicDataFileSerializer,
)
from private_sharing.models import (
    id_label_to_project,
    DataRequestProject,
    DataRequestProjectMember,
    ProjectDataFile,
)
from private_sharing.serializers import ProjectDataSerializer

from .filters import (
    PublicDataFileFilter,
    PublicDataTypeFilter,
    PublicMemberFilter,
    PublicProjectFilter,
    LegacyPublicDataFileFilter,
)
from .models import Member
from .serializers import (
    DataUsersBySourceSerializer,
    MemberDataSourcesSerializer,
    PublicMemberSerializer,
    PublicDataFileSerializer,
)


UserModel = get_user_model()


class PublicDataFileAPIView(NeverCacheMixin, RetrieveAPIView):
    """
    Return public DataFile information.
    """

    serializer_class = PublicDataFileSerializer

    def get_queryset(self):
        """
        Exclude projects where all public sharing is disabled
        """
        return ProjectDataFile.objects.public().exclude(
            direct_sharing_project__no_public_data=True
        )


class PublicDataFileListAPIView(NeverCacheMixin, ListAPIView):
    """
    Return list of public DataFiles and associated information.

    Supported filters:
    - datatype_id
    - source_project_id
    - username
    """

    serializer_class = PublicDataFileSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = PublicDataFileFilter

    def get_queryset(self):
        """
        Exclude projects where all public sharing is disabled
        """
        return ProjectDataFile.objects.public().exclude(
            direct_sharing_project__no_public_data=True
        )


class PublicDataTypeAPIView(NeverCacheMixin, RetrieveAPIView):
    """
    Return information about an individual DataType.
    """

    serializer_class = DataTypeSerializer

    def get_queryset(self):
        """
        Get the queryset.
        """
        return DataType.objects.all()


class PublicDataTypeDataFilesAPIView(NeverCacheMixin, ListAPIView):
    """
    Return a list of publicly available DataFiles for a DataType.

    Supported filters extend PublicDataFileListAPI:
    - datatype_id
    - source_project_id
    - username
    - include_children
    """

    serializer_class = PublicDataFileSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = PublicDataFileFilter

    def get_queryset(self):
        """
        Get the queryset.
        """

        def _all_children(dt, children=[]):
            for child in dt.children.all():
                children = children + [child.id] + _all_children(child)
            return children

        datatype = DataType.objects.get(id=self.kwargs["pk"])
        datatypes = [datatype.id]

        if strtobool(self.request.GET.get("include_children", "False")):
            datatypes = datatypes + _all_children(datatype)

        qs = (
            ProjectDataFile.objects.public()
            .exclude(direct_sharing_project__no_public_data=True)
            .filter(datatypes__in=datatypes)
        )
        return qs


class PublicDataTypeListAPIView(NeverCacheMixin, ListAPIView):
    """
    Return list of DataTypes and source projects that have registered them.

    Supported filters:
    - source_project_id
    """

    serializer_class = DataTypeSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = PublicDataTypeFilter

    def get_queryset(self):
        return DataType.objects.all()


class PublicMemberAPIView(NeverCacheMixin, RetrieveAPIView):
    """
    Return publicly available member information.
    """

    serializer_class = PublicMemberSerializer
    lookup_field = "user__username"

    def get_queryset(self):
        return (
            Member.objects.filter(user__is_active=True)
            .exclude(user__username="api-administrator")
            .order_by("user__username")
        )


class PublicMemberDataFilesAPIView(NeverCacheMixin, ListAPIView):
    """
    Return list of DataFiles a member has publicly shared.

    Supported filters the same as for PublicDataFileListAPI:
    - datatype_id
    - source_project_id
    - username
    """

    serializer_class = PublicDataFileSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = PublicDataFileFilter

    def get_queryset(self):
        member = (
            Member.objects.filter(user__is_active=True)
            .exclude(user__username="api-administrator")
            .get(user__username=self.kwargs["user__username"])
        )
        drpms = DataRequestProjectMember.objects.filter(
            member=member,
            visible=True,
            joined=True,
            authorized=True,
            project__approved=True,
        )
        visible_projs = [drpm.project for drpm in drpms]
        return (
            ProjectDataFile.objects.public()
            .exclude(direct_sharing_project__no_public_data=True)
            .filter(direct_sharing_project__in=visible_projs)
            .filter(user=member.user)
        )


class PublicMemberProjectsAPIView(NeverCacheMixin, ListAPIView):
    """
    Return publicly available information about projects a member joined.
    """

    serializer_class = ProjectDataSerializer

    def get_queryset(self):
        member = (
            Member.objects.filter(user__is_active=True)
            .exclude(user__username="api-administrator")
            .get(user__username=self.kwargs["user__username"])
        )
        drpms = DataRequestProjectMember.objects.filter(
            member=member,
            visible=True,
            joined=True,
            authorized=True,
            project__approved=True,
        )
        qs = [drpm.project for drpm in drpms]
        return qs


class PublicMemberListAPIView(NeverCacheMixin, ListAPIView):
    """
    Return a list of all active members.

    Supported filters:
    - name
    - username
    """

    serializer_class = PublicMemberSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = PublicMemberFilter

    def get_queryset(self):
        qs = (
            Member.objects.filter(user__is_active=True)
            .exclude(user__username="api-administrator")
            .order_by("user__username")
        )
        return qs


class PublicProjectAPIView(NeverCacheMixin, RetrieveAPIView):
    """
    Return publicly available project information.
    """

    serializer_class = ProjectDataSerializer

    def get_queryset(self):
        """
        Get the queryset.
        """
        return DataRequestProject.objects.filter(approved=True)


class PublicProjectDataFilesAPIView(NeverCacheMixin, ListAPIView):
    """
    Return publicly available project DataFiles.

    Supported filters the same as for PublicDataFileListAPI:
    - datatype_id
    - source_project_id
    - username
    """

    serializer_class = PublicDataFileSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = PublicDataFileFilter

    def get_queryset(self):
        """
        Get the queryset and filter on project if provided.
        """
        project = DataRequestProject.objects.filter(approved=True).get(
            id=self.kwargs["pk"]
        )
        return (
            ProjectDataFile.objects.public()
            .exclude(direct_sharing_project__no_public_data=True)
            .filter(direct_sharing_project=project)
        )


class PublicProjectMembersAPIView(NeverCacheMixin, ListAPIView):
    """
    Return list of project members with visible membership.
    """

    serializer_class = PublicMemberSerializer

    def get_queryset(self):
        """
        Get the queryset and filter on project if provided.
        """
        project = DataRequestProject.objects.filter(approved=True).get(
            id=self.kwargs["pk"]
        )
        drpms = DataRequestProjectMember.objects.filter(
            project=project,
            visible=True,
            joined=True,
            authorized=True,
            member__user__is_active=True,
        )
        qs = [drpm.member for drpm in drpms]
        return qs


class PublicProjectListAPIView(NeverCacheMixin, ListAPIView):
    """
    Return list of all approved projects.

    Supported filters:
    - active
    - id
    - name
    """

    serializer_class = ProjectDataSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = PublicProjectFilter

    def get_queryset(self):
        """
        Get the queryset; filter on approved projects.
        """
        return DataRequestProject.objects.filter(approved=True)


#####################################################################
# LEGACY ENDPOINTS
#
# The following views are used by deprecated API endpoints.
#
#####################################################################


class PublicDataListAPIView(NeverCacheMixin, ListAPIView):
    """
    Return the list of public data files.
    """

    serializer_class = LegacyPublicDataFileSerializer

    filter_backends = (DjangoFilterBackend,)
    filter_class = LegacyPublicDataFileFilter

    def get_queryset(self):
        """
        Exclude projects where all public sharing is disabled
        """
        qs = ProjectDataFile.objects.public().exclude(
            direct_sharing_project__no_public_data=True
        )
        return qs


class PublicDataSourcesByUserAPIView(NeverCacheMixin, ListAPIView):
    """
    Return an array where each entry is an object with this form:

    {
      username: "beau",
      sources: ["fitbit", "runkeeper"]
    }
    """

    queryset = UserModel.objects.filter(is_active=True)
    serializer_class = MemberDataSourcesSerializer

    filter_backends = (DjangoFilterBackend,)


class PublicDataUsersBySourceAPIView(NeverCacheMixin, ListAPIView):
    """
    Return an array where each entry is an object with this form:

    {
      source: "fitbit",
      name: "Fitbit",
      usernames: ["beau", "madprime"]
    }
    """

    queryset = DataRequestProject.objects.filter(
        active=True, approved=True, no_public_data=False
    )
    serializer_class = DataUsersBySourceSerializer
