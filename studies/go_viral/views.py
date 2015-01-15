from ..views import StudyDetailView, StudyListView, UserDataDetailView

from .models import UserData
from .serializers import GoViralIdSerializer, UserDataSerializer


class GoViralIdDetail(StudyDetailView):
    def get_queryset(self):
        return self.get_user_data().go_viral_ids.all()

    user_data_model = UserData
    serializer_class = GoViralIdSerializer


class GoViralIdList(StudyListView):
    def get_queryset(self):
        return self.get_user_data().go_viral_ids.all()

    user_data_model = UserData
    serializer_class = GoViralIdSerializer


class UserDataDetail(UserDataDetailView):
    def get_queryset(self):
        return self.get_user_data_queryset()

    user_data_model = UserData
    serializer_class = UserDataSerializer
