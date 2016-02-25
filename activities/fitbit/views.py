from django.apps import apps
from django.contrib import messages as django_messages
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, View

from data_import.views import DataRetrievalView

from . import label


class FinalizeImportView(TemplateView, DataRetrievalView):
    """
    Handle the finalization of the Fitbit import process.
    """

    source = label
    template_name = 'fitbit/finalize-import.html'

    def get_context_data(self, **kwargs):
        context = super(FinalizeImportView, self).get_context_data(**kwargs)

        context.update({
            'app': apps.get_app_config(self.source),
        })

        return context


class DisconnectView(View):
    """
    Delete any Fitbit credentials the user may have.
    """

    @staticmethod
    def post(request):
        django_messages.success(request, (
            'You have cancelled your connection to Fitbit.'))

        request.user.fitbit.disconnect()

        return HttpResponseRedirect(reverse_lazy('my-member-research-data'))
