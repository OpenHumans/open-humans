import json
import logging

from django.apps import apps
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseForbidden, HttpResponseRedirect)
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView, TemplateView, View
from django.views.generic.base import ContextMixin

from ipware.ip import get_ip
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView

from common.mixins import NeverCacheMixin, PrivateMixin
from common.permissions import HasPreSharedKey
from common.utils import full_url
from open_humans.signals import send_connection_email
from private_sharing.utilities import source_to_url_slug

from .models import DataFile, NewDataFileAccessLog
from .processing import start_task, task_params_for_source
from .serializers import DataFileSerializer

UserModel = get_user_model()

logger = logging.getLogger(__name__)


class DataFileListView(NeverCacheMixin, ListAPIView):
    """
    Return a list of data files in JSON format.

    This view is used internally by our data processing server.
    """

    permission_classes = (HasPreSharedKey,)
    serializer_class = DataFileSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id', None)
        source = self.request.query_params.get('source', None)

        if user_id is None or source is None:
            raise APIException('user_id and source must be specified')

        return DataFile.objects.filter(
            user=user_id, source=source).exclude(
            parent_project_data_file__completed=False)


class ProcessingParametersView(NeverCacheMixin, APIView):
    """
    Returns the task parameters for data-processing as JSON.
    """

    permission_classes = (HasPreSharedKey,)

    @staticmethod
    def get(request):
        user_id = request.query_params.get('user_id', None)
        source = request.query_params.get('source', None)

        if user_id is None or source is None:
            raise APIException('user_id and source must be specified')

        try:
            user = UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            raise APIException('user does not exist')

        return Response(task_params_for_source(user, source))


class TaskUpdateView(View):
    """
    Receive and record task success/failure input.
    """

    def post(self, request):
        logger.info('Received task update with: %s', str(request.body))

        data = json.loads(request.body)

        if 'task_data' not in data:
            return HttpResponseBadRequest()

        task_data = data['task_data']

        if 'oh_user_id' not in task_data or 'oh_source' not in task_data:
            return HttpResponseBadRequest()

        if 'data_files' in task_data:
            self.create_datafiles_with_metadata(**task_data)

        return HttpResponse('success')

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(TaskUpdateView, self).dispatch(*args, **kwargs)

    # pylint: disable=unused-argument
    @staticmethod
    def create_datafiles_with_metadata(oh_user_id, oh_source, data_files,
                                       **kwargs):
        user = UserModel.objects.get(pk=oh_user_id)

        for data_file in data_files:
            data_file_object = DataFile(user=user,
                                        source=oh_source,
                                        metadata=data_file['metadata'])

            data_file_object.file.name = data_file['s3_key']

            data_file_object.save()


class DataRetrievalView(ContextMixin, PrivateMixin, View):
    """
    Abstract base class for a view that starts a data retrieval task.
    """

    source = None
    redirect_url = reverse_lazy('my-member-data')
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

    def send_connection_email(self):
        user = self.request.user
        connection_name = self.app.verbose_name
        activity_url = full_url(
            reverse('activity-management',
                    kwargs={'source': source_to_url_slug(self.source)}))
        send_connection_email(user, connection_name, activity_url)

    def trigger_retrieval_task(self, request):
        if self.app.in_development:
            messages.success(request, self.message_in_development)

            return self.redirect()

        if request.user.member.primary_email.verified:
            task = start_task(request.user, self.source)

            if task == 'error':
                messages.error(request, self.message_error)
            else:
                messages.success(request, self.message_started)
        else:
            messages.warning(request, self.message_postponed)

        return self.redirect()

    def get_redirect_url(self):
        """
        Redirect to a source's activity page, if possible.
        """
        if self.source:
            try:
                url_slug = self.app.url_slug
            except AttributeError:
                url_slug = self.app.label
            activity_url = reverse('activity-management',
                                   kwargs={'source': url_slug})
            return activity_url

        return self.redirect_url

    def redirect(self):
        """
        Redirect to value specified for 'next', otherwise to get_redirect_url()
        """
        next_url = self.request.GET.get('next', self.get_redirect_url())

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
        """
        Get authorization page template for this source.
        """
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

        unavailable = (
            hasattr(self.data_file, 'parent_project_data_file') and
            self.data_file.parent_project_data_file.completed is False)
        if unavailable:
            return HttpResponseForbidden('<h1>This file is unavailable.</h1>')

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

        return self.data_file.file_url_as_attachment
