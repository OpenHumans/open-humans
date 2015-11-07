from django.views.generic.edit import UpdateView

from data_import.views import BaseDataRetrievalView
from .models import DataFile, UserData


class DataRetrievalView(BaseDataRetrievalView):
    """
    Initiate 23andMe data retrieval task.
    """
    datafile_model = DataFile

    def get_app_task_params(self, request):
        return request.user.twenty_three_and_me.get_retrieval_params()


class UploadView(UpdateView):
    """
    Allow the user to upload a 23andMe file.
    """

    model = UserData
    fields = ['genome_file']
    template_name = 'twenty_three_and_me/upload.html'
