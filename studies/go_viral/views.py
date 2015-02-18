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
        ids = [go_viral_id.value for go_viral_id in
               GoViralId.objects.filter(user_data__user=self.request.user)]

        return {'ids': ids}
