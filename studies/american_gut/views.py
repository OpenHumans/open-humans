from data_import.views import BaseDataRetrievalView

from ..views import StudyDetailView, StudyListView, UserDataDetailView

from .models import UserData, DataFile, Barcode
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

    def get_app_task_params(self):
        barcodes = [barcode.value for barcode in
                    Barcode.objects.filter(user_data__user=self.request.user)]
        app_task_params = {'barcodes': barcodes}
        return app_task_params
