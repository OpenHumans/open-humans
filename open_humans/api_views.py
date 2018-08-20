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
from private_sharing.models import project_membership_visible
from private_sharing.utilities import (
     get_source_labels_and_names_including_dynamic)

from .filters import StartEndDateFromToRangeFilter
from .serializers import MemberSerializer, MemberDataSourcesSerializer

UserModel = get_user_model()


class PublicDataMembers(ListAPIView):
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


class PublicDataListAPIView(APIView):
    """
    Return the list of public data files.
    """

    @staticmethod
    def get(request):
        source = request.query_params['source']
        users = (UserModel.objects.filter(is_active=True)
                 .values('member__member_id', 'member__name', 'username'))
        queryset = DataFile.objects.public().filter(source=source)
        results = []
        for item in queryset:
            user_t = users.get(id=item.user.id)
            if project_membership_visible(item.user, item.source):
                user = {"id": user_t['member__member_id'],
                        "name": user_t['member__name'],
                        "username": user_t['username']}
            else:
                user = {"id": "",
                        "name": "",
                        "username": ""}
            result = {"id": item.id,
                      "basename": item.basename,
                      "created": item.created.isoformat(),
                      "download_url": item.download_url,
                      "metadata": item.metadata,
                      "source": item.source,
                      "user": user}
            results.append(result)
        pagination = LimitOffsetPagination()
        pagination.paginate_queryset(results, request)
        return pagination.get_paginated_response(results)


class PublicDataSourcesByUserAPIView(ListAPIView):
    """
    Return an array where each entry is an object with this form:

    {
      username: "beau",
      sources: ["fitbit", "runkeeper"]
    }
    """
    queryset = UserModel.objects.filter(is_active=True)
    serializer_class = MemberDataSourcesSerializer


class PublicDataUsersBySourceAPIView(APIView):
    """
    Return an array where each entry is an object with this form:

    {
      source: "fitbit",
      name: "Fitbit",
      usernames: ["beau", "madprime"]
    }
    """

    # pylint: disable=unused-argument
    @staticmethod
    def get(request):
        users = (UserModel.objects.filter(is_active=True)
                 .values('username', 'member__badges', 'id'))
        sources = defaultdict(list)

        for user in users:
            for badge in user['member__badges'] or []:
                if 'label' not in badge:
                    continue

                if project_membership_visible(user, badge['label']):
                    sources[badge['label']].append(user['username'])

        source_filter = request.GET.get('source')

        source_list = [
            {
                'source': label,
                'name': verbose_name,
                'usernames': sources[label],
            }
            for label, verbose_name
            in get_source_labels_and_names_including_dynamic()
            if (not source_filter) or
            (source_filter and label in source_filter.split(','))
        ]

        return Response(source_list)
