from ..views import StudyDetailView, StudyListView, UserDataDetailView

from .models import UserData
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
