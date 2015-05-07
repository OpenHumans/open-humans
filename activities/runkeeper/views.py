from data_import.views import BaseDataRetrievalView

from .models import DataFile


class DataRetrievalView(BaseDataRetrievalView):
    """
    Initiate RunKeeper data retrieval task.
    """
    datafile_model = DataFile

    def get_app_task_params(self, request):
        return request.user.runkeeper.get_retrieval_params()
