from django.contrib.auth import get_user_model

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
