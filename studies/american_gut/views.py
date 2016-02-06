from data_import.views import BaseDataRetrievalView

from ..views import UserDataDetailView

from .models import UserData, DataFile
from .serializers import UserDataSerializer


class UserDataDetail(UserDataDetailView):
    """
    Detail view for American Gut user data.
    """

    def get_queryset(self):
        return self.get_user_data_queryset()

    user_data_model = UserData
    serializer_class = UserDataSerializer


class DataRetrievalView(BaseDataRetrievalView):
    """
    Initiate data retrieval task for all survey IDs associated with DataUser.
    """
    datafile_model = DataFile
