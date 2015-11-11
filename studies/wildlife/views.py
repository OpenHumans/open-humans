from data_import.views import BaseDataRetrievalView

from ..views import UserDataDetailView

from .models import UserData, DataFile
from .serializers import UserDataSerializer


class UserDataDetail(UserDataDetailView):
    """
    Detail view for Wildlife of Our Homes user data.
    """

    def get_queryset(self):
        return self.get_user_data_queryset()

    user_data_model = UserData
    serializer_class = UserDataSerializer


class DataRetrievalView(BaseDataRetrievalView):
    """
    Initiate data retrieval task for all data associated with a user.
    """
    datafile_model = DataFile

    def get_app_task_params(self, request):
        return request.user.wildlife_of_our_homes.get_retrieval_params()
