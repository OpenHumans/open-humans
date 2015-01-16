from ..views import StudyDetailView, StudyListView, UserDataDetailView

from .models import UserData
from .serializers import HuIdSerializer, UserDataSerializer


class HuIdDetail(StudyDetailView):
    def get_queryset(self):
        return self.get_user_data().huids.all()

    user_data_model = UserData
    serializer_class = HuIdSerializer


class HuIdList(StudyListView):
    def get_queryset(self):
        return self.get_user_data().huids.all()

    user_data_model = UserData
    serializer_class = HuIdSerializer


class UserDataDetail(UserDataDetailView):
    def get_queryset(self):
        return self.get_user_data_queryset()

    user_data_model = UserData
    serializer_class = UserDataSerializer
