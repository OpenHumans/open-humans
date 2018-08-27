from collections import defaultdict

from django.contrib.auth import get_user_model
from django_filters import rest_framework
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from data_import.models import DataFile
from private_sharing.models import DataRequestProject, project_membership_visible
from private_sharing.utilities import (
     get_source_labels_and_names_including_dynamic)
from public_data.serializers import PublicDataFileSerializer

from common.mixins import NeverCacheMixin
from .filters import PublicDataFileFilter, StartEndDateFromToRangeFilter
from .serializers import DataUsersBySourceSerializer, MemberSerializer, MemberDataSourcesSerializer


UserModel = get_user_model()


class PublicDataMembers(NeverCacheMixin, ListAPIView):
    """
    Return the list of public data files.
    """

    def get_queryset(self):
        return (UserModel.objects
                .filter(is_active=True)
                .exclude(username='api-administrator')
                .order_by('member__name'))

    serializer_class = MemberSerializer

    filter_backends = (SearchFilter,)
    search_fields = ('username', 'member__name')


class PublicDataListAPIView(NeverCacheMixin, ListAPIView):
    """
    Return the list of public data files.
    """

    queryset = DataFile.objects.public()
    serializer_class = PublicDataFileSerializer

    filter_backends = (DjangoFilterBackend,)
    filter_class = PublicDataFileFilter


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


class PublicDataUsersBySourceAPIView(NeverCacheMixin, ListAPIView):
    """
    Return an array where each entry is an object with this form:

    {
      source: "fitbit",
      name: "Fitbit",
      usernames: ["beau", "madprime"]
    }
    """
    queryset = DataRequestProject.objects.filter(active=True, approved=True)
    serializer_class = DataUsersBySourceSerializer
