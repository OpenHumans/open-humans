from django.contrib import messages as django_messages
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, View

from data_import.views import BaseDataRetrievalView

from .models import DataFile


class DataRetrievalView(BaseDataRetrievalView):
    """
    Initiate the RunKeeper data retrieval task.
    """

    datafile_model = DataFile

    def get_app_task_params(self, request):
        return request.user.runkeeper.get_retrieval_params()


class FinalizeImportView(TemplateView, DataRetrievalView):
    """
    Handle the finalization of the RunKeeper import process.
    """

    template_name = 'runkeeper/finalize-import.html'


class DisconnectView(View):
    """
    Delete any RunKeeper credentials the user may have.
    """

    @staticmethod
    def post(request):
        django_messages.success(request, (
            'You have cancelled your connection to RunKeeper.'))

        request.user.runkeeper.disconnect()

        return HttpResponseRedirect(reverse_lazy('my-member-research-data'))
