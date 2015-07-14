import json
import logging

from datetime import datetime

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse_lazy
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect)
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from .models import BaseDataFile, DataRetrievalTask

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

    @classmethod
    def update_task(cls, task_data):
        try:
            task = DataRetrievalTask.objects.get(id=task_data['task_id'])
        except DataRetrievalTask.DoesNotExist:
            logger.warning('No task for ID: %s', task_data['task_id'])

            return 'Invalid task ID!'

        if 'task_state' in task_data:
            cls.update_task_state(task, task_data['task_state'])

        if 's3_keys' in task_data:
            cls.create_datafiles(task, **task_data)

        return 'Thanks!'

    @staticmethod
    def update_task_state(task, task_state):
        # XXX: change SUCCESS/SUCCESSFUL to SUCCEEDED to match FAILED
        if task_state == 'SUCCESS':
            task.status = task.TASK_SUCCESSFUL
            task.complete_time = datetime.now()
        elif task_state == 'QUEUED':
            task.status = task.TASK_QUEUED
        elif task_state == 'INITIATED':
            task.status = task.TASK_INITIATED
        # XXX: change FAILURE to FAILED to match
        elif task_state == 'FAILURE':
            task.status = task.TASK_FAILED
            task.complete_time = datetime.now()

        task.save()

    # pylint: disable=unused-argument
    @staticmethod
    def create_datafiles(task, s3_keys, subtype=None, **kwargs):
        datafile_model = task.datafile_model.model_class()

        assert issubclass(datafile_model, BaseDataFile), (
            '%r is not a subclass of BaseDataFile' % datafile_model)

        userdata_model = (datafile_model._meta
                          .get_field_by_name('user_data')[0]
                          .rel.to)

        user_data, _ = userdata_model.objects.get_or_create(user=task.user)

        # XXX: there's only ever one s3_key (at this point in time)
        for s3_key in s3_keys:
            data_file = datafile_model(user_data=user_data, task=task)

            if subtype:
                data_file.subtype = subtype

            data_file.file.name = s3_key
            data_file.save()


class BaseDataRetrievalView(View):
    """
    Abstract base class for a view that starts a data retrieval task.

    Class attributes that need to be defined:
        datafile_model (attribute)
            App-specific, a subclass of BaseDataFile

    Class methods that need to be defined:
        get_app_task_params(self)
            Returns a dict with app-specific task parameters. These will be
            stored in the DataRetrievalTask.app_task_params, and will be sent
            to the data processing server wehn the task is run.
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
        task = self.make_retrieval_task(request)

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

    def make_retrieval_task(self, request):
        assert issubclass(self.datafile_model, BaseDataFile), (
            '%r is not a subclass of BaseDataFile' % self.datafile_model)

        task = DataRetrievalTask(
            datafile_model=ContentType.objects.get_for_model(
                self.datafile_model),
            user=request.user,
            app_task_params=json.dumps(self.get_app_task_params(request)))

        task.save()

        return task

    def get_app_task_params(self, request):
        raise NotImplementedError

    def redirect(self):
        """
        Redirect to self.redirect_url
        """
        return HttpResponseRedirect(self.redirect_url)
