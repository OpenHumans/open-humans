import json
import logging

from datetime import datetime

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse_lazy
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseForbidden, HttpResponseRedirect)
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView, View

from ipware.ip import get_ip

from .models import BaseDataFile, DataRetrievalTask, DataFileAccessLog
from .tasks import make_retrieval_task

logger = logging.getLogger(__name__)


class TaskUpdateView(View):
    """
    Receive and record task success/failure input.
    """

    def post(self, request):
        logger.info('Received task update with: %s', str(request.POST))

        if 'task_data' not in request.POST:
            return HttpResponseBadRequest()

        # TODO: since this is just JSON we could post the JSON directly
        task_data = json.loads(request.POST['task_data'])

        response = self.update_task(task_data)

        return HttpResponse(response)

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(TaskUpdateView, self).dispatch(*args, **kwargs)

    def update_task(self, task_data):
        try:
            task = DataRetrievalTask.objects.get(id=task_data['task_id'])
        except DataRetrievalTask.DoesNotExist:
            logger.warning('No task for ID: %s', task_data['task_id'])

            return 'Invalid task ID!'

        if 'task_state' in task_data:
            self.update_task_state(task, task_data['task_state'])

        if 'data_files' in task_data:
            self.create_datafiles_with_metadata(task, **task_data)
        elif 's3_keys' in task_data:
            self.create_datafiles(task, **task_data)

        return 'Thanks!'

    @staticmethod
    def update_task_state(task, task_state):
        # TODO: change SUCCESS to SUCCEEDED on data_processing to match
        if task_state in ['SUCCESS', 'SUCCEEDED']:
            task.status = task.TASK_SUCCEEDED
            task.complete_time = datetime.now()
        elif task_state == 'QUEUED':
            task.status = task.TASK_QUEUED
        elif task_state == 'INITIATED':
            task.status = task.TASK_INITIATED
        # TODO: change FAILURE to FAILED on data_processing to match
        elif task_state in ['FAILURE', 'FAILED']:
            task.status = task.TASK_FAILED
            task.complete_time = datetime.now()

        task.save()

    @staticmethod
    def get_user_data_and_datafile_model(task):
        datafile_model = task.datafile_model.model_class()

        assert issubclass(datafile_model, BaseDataFile), (
            '%r is not a subclass of BaseDataFile' % datafile_model)

        user_data_model = (datafile_model._meta
                           .get_field_by_name('user_data')[0]
                           .rel.to)

        user_data, _ = user_data_model.objects.get_or_create(user=task.user)

        return user_data, datafile_model

    # pylint: disable=unused-argument
    def create_datafiles(self, task, s3_keys, **kwargs):
        user_data, datafile_model = self.get_user_data_and_datafile_model(task)

        for s3_key in s3_keys:
            data_file = datafile_model(user_data=user_data, task=task)

            data_file.file.name = s3_key
            data_file.save()

    def create_datafiles_with_metadata(self, task, data_files, **kwargs):
        user_data, datafile_model = self.get_user_data_and_datafile_model(task)

        for data_file in data_files:
            data_file_object = datafile_model(user_data=user_data, task=task)

            data_file_object.file.name = data_file['s3_key']
            data_file_object.metadata = data_file['metadata']

            data_file_object.save()


class BaseDataRetrievalView(View):
    """
    Abstract base class for a view that starts a data retrieval task.

    Class attributes that need to be defined:
        datafile_model (attribute)
            App-specific, a subclass of BaseDataFile
    """
    datafile_model = None
    redirect_url = reverse_lazy('my-member-research-data')
    message_error = 'Sorry, our data retrieval server seems to be down.'
    message_started = "Thanks! We've submitted this import task to our server."
    message_postponed = (
        """We've postponed imports pending email verification. Check for our
        confirmation email, which has a verification link. To send a new
        confirmation, go to your account settings.""")

    def post(self, request):
        return self.trigger_retrieval_task(request)

    def trigger_retrieval_task(self, request):
        task = make_retrieval_task(request.user, self.datafile_model)

        if request.user.member.primary_email.verified:
            task.start_task()

            if task.status == task.TASK_FAILED:
                messages.error(request, self.message_error)
            else:
                messages.success(request, self.message_started)
        else:
            task.postpone_task()

            messages.warning(request, self.message_postponed)

        return self.redirect()

    def redirect(self):
        """
        Redirect to self.redirect_url or the value specified for 'next'.
        """
        next_url = self.request.GET.get('next', self.redirect_url)

        return HttpResponseRedirect(next_url)


class DataFileDownloadView(RedirectView):
    """
    Log a download and redirect the requestor to its actual location.
    """
    permanent = False

    def get_object(self):
        self.datafile_model_type = ContentType.objects.get(
            pk=self.kwargs.get('pk1'))
        datafile = self.datafile_model_type.get_object_for_this_type(
            pk=self.kwargs.get('pk2'))
        return datafile

    # pylint: disable=attribute-defined-outside-init
    def get(self, request, *args, **kwargs):
        self.datafile = self.get_object()

        if not self.datafile.has_access(user=request.user):
            return HttpResponseForbidden(
                '<h1>You do not have permission to access this file.</h1>')

        return super(DataFileDownloadView, self).get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        user = (self.request.user
                if self.request.user.is_authenticated()
                else None)

        access_log = DataFileAccessLog(
            user=user,
            ip_address=get_ip(self.request),
            data_file_model=self.datafile_model_type,
            data_file_id=self.kwargs.get('pk2'))
        access_log.save()

        return self.datafile.file.url
