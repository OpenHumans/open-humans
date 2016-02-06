from data_import.views import BaseDataRetrievalView

from ..views import UserDataDetailView

from .models import DataFile, UserData
from .serializers import UserDataSerializer


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
