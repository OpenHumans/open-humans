from collections import defaultdict

from django.contrib.auth import get_user_model
from django_filters import CharFilter, MultipleChoiceFilter
from django_filters.filterset import STRICTNESS
from django_filters.widgets import CSVWidget

from rest_framework import status
from rest_framework.filters import DjangoFilterBackend, FilterSet
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from social.apps.django_app.default.models import UserSocialAuth

from common.permissions import HasPreSharedKey
from data_import.models import DataFile
from private_sharing.utilities import (
    get_source_labels_and_names_including_dynamic)
from public_data.serializers import PublicDataFileSerializer
from studies.views import RetrieveStudyDetailView

from .filters import StartEndDateFromToRangeFilter
from .serializers import MemberSerializer, MemberDataSourcesSerializer

UserModel = get_user_model()


class MemberDetailAPIView(RetrieveStudyDetailView):
    """
    Return information about the member.
    """

    def get_queryset(self):
        return UserModel.objects.filter(pk=self.request.user.pk)

    lookup_field = None
    serializer_class = MemberSerializer


class PublicDataFileFilter(FilterSet):
    """
    A FilterSet that maps member_id and username to less verbose names.
    """

    created = StartEndDateFromToRangeFilter()
    member_id = CharFilter(name='user__member__member_id')
    username = CharFilter(name='user__username')
    source = MultipleChoiceFilter(
        choices=get_source_labels_and_names_including_dynamic,
        widget=CSVWidget())
    # don't filter by source if no sources are specified; this improves speed
    source.always_filter = False

    strict = STRICTNESS.RAISE_VALIDATION_ERROR

    class Meta:
        model = DataFile
        fields = ('created', 'source', 'username', 'member_id')


class PublicDataListAPIView(ListAPIView):
    """
    Return the list of public data files.
    """

    queryset = DataFile.objects.public()
    serializer_class = PublicDataFileSerializer

    filter_backends = (DjangoFilterBackend,)
    filter_class = PublicDataFileFilter


class PublicDataSourcesByUserAPIView(ListAPIView):
    """
    Return an array where each entry is an object with this form:

    {
      username: "beau",
      sources: ["fitbit", "runkeeper"]
    }
    """

    queryset = UserModel.objects.all()
    serializer_class = MemberDataSourcesSerializer


class PublicDataUsersBySourceAPIView(APIView):
    """
    Return an array where each entry is an object with this form:

    {
      source: "fitbit",
      name: "Fitbit",
      usernames: ["beau", "mpball"]
    }
    """

    def get(self, request, format=None):
        users = UserModel.objects.all().values('username', 'member__badges')
        sources = defaultdict(list)

        for user in users:
            for badge in user['member__badges'] or []:
                if 'label' not in badge:
                    continue

                sources[badge['label']].append(user['username'])

        source_list = [
            {
                'source': label,
                'name': verbose_name,
                'usernames': sources[label],
            }
            for label, verbose_name
            in get_source_labels_and_names_including_dynamic()
        ]

        return Response(source_list)


class ProcessingRefreshTokenView(APIView):
    """
    Given a user and a provider, refresh the token and return it to the
    requestor.
    """

    permission_classes = (HasPreSharedKey,)

    def post(self, request, format=None):
        user_id = self.request.data.get('user_id')
        provider = self.request.data.get('provider')

        if not user_id or not provider:
            return Response(
                {'error': 'user_id and provider must be specified'},
                status=status.HTTP_400_BAD_REQUEST)

        try:
            auth = UserSocialAuth.objects.get(user_id=user_id,
                                              provider=provider)
        except UserSocialAuth.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        backend = auth.get_backend_instance()
        token = backend.refresh_token(auth.extra_data['refresh_token'])

        return Response(token)
