from django.contrib.auth.models import User

from studies.views import RetrieveStudyDetailView

from .serializers import MemberSerializer


class MemberDetailAPIView(RetrieveStudyDetailView):
    """
    Return information about the member.
    """
    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)

    lookup_field = None
    serializer_class = MemberSerializer
