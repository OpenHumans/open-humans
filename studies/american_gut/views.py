from data_import.views import BaseDataRetrievalView

from ..views import StudyDetailView, StudyListView, UserDataDetailView

from .models import UserData, DataFile
from .serializers import BarcodeSerializer, UserDataSerializer


class BarcodeDetail(StudyDetailView):
    def get_queryset(self):
        return self.get_user_data().barcodes.all()

    user_data_model = UserData
    serializer_class = BarcodeSerializer


class BarcodeList(StudyListView):
    def get_queryset(self):
        return self.get_user_data().barcodes.all()

    user_data_model = UserData
    serializer_class = BarcodeSerializer


class UserDataDetail(UserDataDetailView):
    def get_queryset(self):
        return self.get_user_data_queryset()

    user_data_model = UserData
    serializer_class = UserDataSerializer


class DataRetrievalView(BaseDataRetrievalView):
    """
    Initiate data retrieval task for all barcodes associated with DataUser.
    """
    datafile_model = DataFile

    def get_app_task_params(self, request):
        return request.user.american_gut.get_retrieval_params()
