from data_import.views import BaseDataRetrievalView

from ..views import StudyDetailView, StudyListView, UserDataDetailView

from .models import UserData, DataFile
from .serializers import (BarcodeSerializer, SurveyIdSerializer,
                          UserDataSerializer)


class BarcodeDetail(StudyDetailView):
    """
    Detail view for a single American Gut barcode.
    """

    def get_queryset(self):
        return self.get_user_data().barcodes.all()

    user_data_model = UserData
    serializer_class = BarcodeSerializer


class BarcodeList(StudyListView):
    """
    List view for American Gut user IDs.
    """

    def get_queryset(self):
        return self.get_user_data().barcodes.all()

    user_data_model = UserData
    serializer_class = BarcodeSerializer


class SurveyIdDetail(StudyDetailView):
    """
    Detail view for a single American Gut survey ID.
    """

    def get_queryset(self):
        return self.get_user_data().survey_ids.all()

    user_data_model = UserData
    serializer_class = SurveyIdSerializer


class SurveyIdList(StudyListView):
    """
    List view for American Gut survey IDs.
    """

    def get_queryset(self):
        return self.get_user_data().survey_ids.all()

    user_data_model = UserData
    serializer_class = SurveyIdSerializer


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
    Initiate data retrieval task for all barcodes associated with DataUser.
    """
    datafile_model = DataFile

    def get_app_task_params(self, request):
        return request.user.american_gut.get_retrieval_params()
