import json
import logging

from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseForbidden, HttpResponseRedirect)
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView, View

from ipware.ip import get_ip

from .models import DataFile, DataRetrievalTask, NewDataFileAccessLog
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

        # if we're creating datafiles then the files for this task are now the
        # latest files for the user/source and we need to mark all others as
        # not the latest
        if 'data_files' in task_data or 's3_keys' in task_data:
            tasks = DataRetrievalTask.objects.filter(user=task.user,
                                                     source=task.source)

            for user_task in tasks:
                if user_task.id != task.id:
                    task.datafiles.update(is_latest=False)

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
            task.complete_time = timezone.now()
        elif task_state == 'QUEUED':
            task.status = task.TASK_QUEUED
        elif task_state == 'INITIATED':
            task.status = task.TASK_INITIATED
        # TODO: change FAILURE to FAILED on data_processing to match
        elif task_state in ['FAILURE', 'FAILED']:
            task.status = task.TASK_FAILED
            task.complete_time = timezone.now()

        task.save()

    # pylint: disable=unused-argument
    @staticmethod
    def create_datafiles(task, s3_keys, **kwargs):
        for s3_key in s3_keys:
            data_file = DataFile(user=task.user,
                                 task=task,
                                 source=task.source)

            data_file.file.name = s3_key

            data_file.save()

    @staticmethod
    def create_datafiles_with_metadata(task, data_files, **kwargs):
        for data_file in data_files:
            data_file_object = DataFile(user=task.user,
                                        task=task,
                                        source=task.source,
                                        metadata=data_file['metadata'])

            data_file_object.file.name = data_file['s3_key']

            data_file_object.save()


class DataRetrievalView(View):
    """
    Abstract base class for a view that starts a data retrieval task.
    """
    source = None
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
        task = make_retrieval_task(request.user, self.source)

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
