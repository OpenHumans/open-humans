from ..views import StudyDetailView, StudyListView, UserDataDetailView

from .models import UserData
from .serializers import HuIdSerializer, UserDataSerializer


class HuIdDetail(StudyDetailView):
    """
    Detail view for a single PGP huID.

    GET /api/pgp/huids/huF06AD0/
    DELETE /api/pgp/huids/huF06AD0/
    """

    def get_queryset(self):
        return self.get_user_data().huids.all()

    user_data_model = UserData
    serializer_class = HuIdSerializer


class HuIdList(StudyListView):
    """
    List view for PGP huIDs.

    GET /api/pgp/huids/
    POST /api/pgp/huids/
    """

    def get_queryset(self):
        return self.get_user_data().huids.all()

    user_data_model = UserData
    serializer_class = HuIdSerializer


class UserDataDetail(UserDataDetailView):
    """
    Detail view for PGP user data.

    GET /api/pgp/user-data/
    """

    def get_queryset(self):
        return self.get_user_data_queryset()

    user_data_model = UserData
    serializer_class = UserDataSerializer
