from django.contrib.auth import get_user_model
from rest_framework import generics

from public_data.models import PublicDataAccess
from public_data.serializers import PublicDataSerializer
from studies.views import RetrieveStudyDetailView

from .serializers import MemberSerializer

UserModel = get_user_model()


class MemberDetailAPIView(RetrieveStudyDetailView):
    """
    Return information about the member.
    """
    def get_queryset(self):
        return UserModel.objects.filter(pk=self.request.user.pk)

    lookup_field = None
    serializer_class = MemberSerializer


class PublicDataListAPIView(generics.ListCreateAPIView):
    """
    Return the list of public data files.
    """
    queryset = PublicDataAccess.objects.filter(is_public=True)
    serializer_class = PublicDataSerializer
    paginate_by = 100
