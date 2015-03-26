from data_import.views import BaseDataRetrievalView

from ..views import StudyDetailView, StudyListView, UserDataDetailView

from .models import DataFile, UserData
from .serializers import GoViralIdSerializer, UserDataSerializer


class GoViralIdDetail(StudyDetailView):
    """
    Detail view for a single GoViral user ID.
    """

    def get_queryset(self):
        return self.get_user_data().go_viral_ids.all()

    user_data_model = UserData
    serializer_class = GoViralIdSerializer


class GoViralIdList(StudyListView):
    """
    List view for GoViral user IDs.
    """

    def get_queryset(self):
        return self.get_user_data().go_viral_ids.all()

    user_data_model = UserData
    serializer_class = GoViralIdSerializer


class UserDataDetail(UserDataDetailView):
    """
    Detail view for GoViral user data.
    """

    def get_queryset(self):
        return self.get_user_data_queryset()

    user_data_model = UserData
    serializer_class = UserDataSerializer


class DataRetrievalView(BaseDataRetrievalView):
    """
    Initiate data retrieval task for all GoViral IDs associated with DataUser.
    """
    datafile_model = DataFile

    def get_app_task_params(self, request):
        return request.user.go_viral.get_retrieval_params()
