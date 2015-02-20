from datetime import datetime
import json

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from .models import DataRetrievalTask


class TaskUpdateView(View):
    """Receive and record task success/failure input."""

    def post(self, request):
        print "Recieved task update with: " + request.POST['task_data']
        task_data = json.loads(request.POST['task_data'])
        print "task_data parameters:"
        print task_data
        response = self.update_task(task_data)
        return HttpResponse(response)

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(TaskUpdateView, self).dispatch(*args, **kwargs)

    @classmethod
    def update_task(cls, task_data):
        print "Updating task with: " + str(task_data)

        try:
            task = DataRetrievalTask.objects.get(id=task_data['task_id'])
        except DataRetrievalTask.DoesNotExist:
            print "No task for ID??"
            return 'Invalid task ID!'

        if 'task_state' in task_data:
            print "Updating state with: " + task_data['task_state']
            cls.update_task_state(task, task_data['task_state'])

        if 's3_keys' in task_data:
            print "Adding files..."
            cls.create_datafiles(task, task_data['s3_keys'])

        return 'Thanks!'

    @staticmethod
    def update_task_state(task, task_state):
        if task_state == 'SUCCESS':
            task.status = task.TASK_SUCCESSFUL
            task.complete_time = datetime.now()
        elif task_state == 'QUEUED':
            task.status = task.TASK_QUEUED
        elif task_state == 'INITIATED':
            task.status = task.TASK_INITIATED
        elif task_state == 'FAILURE':
            task.status = task.TASK_FAILED
            task.complete_time = datetime.now()

        task.save()

    @staticmethod
    def create_datafiles(task, s3_keys):
        for s3_key in s3_keys:
            print "Getting datafile model"
            datafile_model = task.datafile_model.model_class()
            print datafile_model
            userdata_model = datafile_model._meta.get_field_by_name(
                'user_data')[0].rel.to
            print userdata_model
            user_data, _ = userdata_model.objects.get_or_create(user=task.user)
            print "User data is:"
            print user_data
            data_file, _ = datafile_model.objects.get_or_create(
                user_data=user_data, task=task)
            print "Data file is:"
            print data_file
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
            Returns a dict with app-specific task parameters. (Note: you can use the
            instance attribute self.request to get request data.) These will be
            stored in the DataRetrievalTask.app_task_params, and will be sent
            to the data processing server wehn the task is run.
    """
    datafile_model = None
    redirect_url = reverse_lazy('my-member-research-data')
    message_error = "Sorry, our data retrieval server seems to be down."
    message_started = "Thanks! We've submitted this import task to our server."
    message_postponed = (
        """We've postponed imports pending email verification. Check for our
        confirmation email, which has a verification link. To send a new
        confirmation, go to your account settings.""")

    def post(self, request):
        self.request = request
        task = self.make_retrieval_task(request)
        if self.request.user.member.primary_email.verified:
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
        task = DataRetrievalTask(
            datafile_model=ContentType.objects.get_for_model(
                self.datafile_model),
            user=request.user,
            app_task_params=json.dumps(self.get_app_task_params())
            )
        task.save()
        return task

    def get_app_task_params(self):
        raise NotImplementedError

    def redirect(self):
        """Redirect to self.redirect_url"""
        return HttpResponseRedirect(self.redirect_url)
