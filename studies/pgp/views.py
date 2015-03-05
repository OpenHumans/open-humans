from data_import.views import BaseDataRetrievalView

from ..views import StudyDetailView, StudyListView, UserDataDetailView

from .models import DataFile, UserData
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


class DataRetrievalView(BaseDataRetrievalView):
    """
    Initiate data retrieval task for all GoViral IDs associated with DataUser.
    """
    datafile_model = DataFile

    def get_app_task_params(self):
        user = self.request.user
        return user.pgp.get_retrieval_params()
