from django.conf import settings

from data_import.views import BaseDataRetrievalView

from ..views import StudyDetailView, StudyListView, UserDataDetailView

from .models import DataFile, GoViralId, UserData
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


class DataRetrievalView(BaseDataRetrievalView):
    """
    Initiate data retrieval task for all GoViral IDs associated with DataUser.
    """
    datafile_model = DataFile

    def get_app_task_params(self):
        go_viral_id = (GoViralId.objects
                       .filter(user_data__user=self.request.user)[0].id)

        return {
            'access_token': settings.GO_VIRAL_MANAGEMENT_TOKEN,
            'go_viral_id': go_viral_id
        }
