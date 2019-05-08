from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView

from common.mixins import NeverCacheMixin
from data_import.models import DataType
from data_import.serializers import DataTypeSerializer
from private_sharing.models import (
    id_label_to_project,
    DataRequestProject,
    ProjectDataFile,
)
from private_sharing.serializers import ProjectDataSerializer
from public_data.serializers import PublicDataFileSerializer

from .filters import PublicDataFileFilter
from .serializers import (
    DataUsersBySourceSerializer,
    MemberSerializer,
    MemberDataSourcesSerializer,
)


UserModel = get_user_model()


class PublicDataMembers(NeverCacheMixin, ListAPIView):
    """
    Return the list of public data files.
    """

    def get_queryset(self):
        return (
            UserModel.objects.filter(is_active=True)
            .exclude(username="api-administrator")
            .order_by("member__name")
        )

    serializer_class = MemberSerializer

    filter_backends = (SearchFilter,)
    search_fields = ("username", "member__name")


class PublicDataListAPIView(NeverCacheMixin, ListAPIView):
    """
    Return the list of public data files.
    """

    serializer_class = PublicDataFileSerializer

    filter_backends = (DjangoFilterBackend,)
    filter_class = PublicDataFileFilter

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


class PublicDataTypesListAPIView(ListAPIView):
    """
    Return list of DataTypes and source projects that have registered them.
    """

    serializer_class = DataTypeSerializer

    def get_queryset(self):
        """
        Get the queryset and filter on project if provided.
        """
        source_project_label = self.request.GET.get("source_project_label", None)
        if source_project_label:
            source_project = id_label_to_project(source_project_label)
            queryset = source_project.registered_datatypes.all()
        else:
            queryset = DataType.objects.all()
        return queryset


class PublicProjectsListAPIView(ListAPIView):
    """
    Return list of DataTypes and source projects that have registered them.
    """

    serializer_class = ProjectDataSerializer

    def get_queryset(self):
        """
        Get the queryset and filter on project if provided.
        """
        qs = DataRequestProject.objects.filter(approved=True)
        project_label = self.request.GET.get("id_label", None)
        if project_label:
            project = id_label_to_project(project_label)
            qs = qs.filter(id=project.id)
        proj_id = self.request.GET.get("id", None)
        if proj_id:
            qs = qs.filter(id=proj_id)
        return qs
