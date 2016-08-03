import json
import logging

from django.apps import apps
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseForbidden, HttpResponseRedirect)
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView, TemplateView, View
from django.views.generic.base import ContextMixin

from ipware.ip import get_ip

from common.mixins import PrivateMixin

from .models import DataFile, NewDataFileAccessLog
from .processing import start_task_for_source

logger = logging.getLogger(__name__)


class TaskUpdateView(View):
    """
    Receive and record task success/failure input.
    """

    def post(self, request):
        logger.info('Received task update with: %s', str(request.body))

        data = json.loads(request.body)

        if 'task_data' not in data:
            return HttpResponseBadRequest()

        response = self.update_source(data['task_data'])

        return HttpResponse(response)

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(TaskUpdateView, self).dispatch(*args, **kwargs)

    def update_source(self, task_data):
        if 'user' not in task_data or 'source' not in task_data:
            # XXX TODO_DATAFILE_MANAGEMENT add error response
            return 'Error!'

        if 'data_files' in task_data:
            self.create_datafiles_with_metadata(**task_data)
        elif 's3_keys' in task_data:
            self.create_datafiles(**task_data)

        return 'Thanks!'

    # pylint: disable=unused-argument
    @staticmethod
    def create_datafiles(user, source, s3_keys, **kwargs):
        for s3_key in s3_keys:
            data_file = DataFile(user=user, source=source)

            data_file.file.name = s3_key

            data_file.save()

    @staticmethod
    def create_datafiles_with_metadata(user, source, data_files, **kwargs):
        for data_file in data_files:
            data_file_object = DataFile(user=user,
                                        source=source,
                                        metadata=data_file['metadata'])

            data_file_object.file.name = data_file['s3_key']

            data_file_object.save()


class DataRetrievalView(ContextMixin, PrivateMixin, View):
    """
    Abstract base class for a view that starts a data retrieval task.
    """

    source = None
    redirect_url = reverse_lazy('my-member-research-data')
    message_error = 'Sorry, our data retrieval server seems to be down.'
    message_started = "Thanks! We've submitted this import task to our server."
    message_postponed = """We've postponed imports pending email verification.
    Check for our confirmation email, which has a verification link. To send a
    new confirmation, go to your account settings."""
    message_in_development = """Thanks for connecting this data source! We'll
    use your data to finish implementing our data processing pipeline for this
    source and we'll notify you when you're able to download the data from this
    source."""

    @property
    def app(self):
        return apps.get_app_config(self.source)

    def post(self, request):
        return self.trigger_retrieval_task(request)

    def trigger_retrieval_task(self, request):
        if self.app.in_development:
            messages.success(request, self.message_in_development)

            return self.redirect()

        if request.user.member.primary_email.verified:
            task = start_task_for_source(request.user, self.source)

            if task == 'error':
                messages.error(request, self.message_error)
            else:
                messages.success(request, self.message_started)
        else:
            messages.warning(request, self.message_postponed)

        return self.redirect()

    def redirect(self):
        """
        Redirect to self.redirect_url or the value specified for 'next'.
        """
        next_url = self.request.GET.get('next', self.redirect_url)

        return HttpResponseRedirect(next_url)

    def get_context_data(self, **kwargs):
        context = super(DataRetrievalView, self).get_context_data(**kwargs)

        context.update({'app': self.app})

        return context


class FinalizeRetrievalView(TemplateView, DataRetrievalView):
    """
    A DataRetrievalView with an additional template; used by activities to
    display a finalization screen and start data retrieval in one step.
    """

    def get_template_names(self):
        return ['{}/finalize-import.html'.format(self.source)]


class DataFileDownloadView(RedirectView):
    """
    Log a download and redirect the requestor to its actual location.
    """
    permanent = False

    # pylint: disable=attribute-defined-outside-init
    def get(self, request, *args, **kwargs):
        self.data_file = DataFile.objects.get(pk=self.kwargs.get('pk'))

        if not self.data_file.has_access(user=request.user):
            return HttpResponseForbidden(
                '<h1>You do not have permission to access this file.</h1>')

        return super(DataFileDownloadView, self).get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        user = (self.request.user
                if self.request.user.is_authenticated()
                else None)

        access_log = NewDataFileAccessLog(
            user=user,
            ip_address=get_ip(self.request),
            data_file=self.data_file)
        access_log.save()

        return self.data_file.file.url
