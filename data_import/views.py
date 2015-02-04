from datetime import datetime
import json
import urlparse

import requests
from raven.contrib.django.raven_compat.models import client

from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View


from .models import get_upload_dir, DataRetrievalTask


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
        task.save()

    @staticmethod
    def create_datafiles(task, s3_keys):
        for s3_key in s3_keys:
            datafile_model = task.datafile_model.model_class()
            userdata_model = dadattafile_model._meta.get_field_by_name(
                'user_data')[0].rel.to
            user_data, _ = userdata_model.objects.get_or_create(user=task.user)
            data_file, _ = datafile_model.objects.get_or_create(
                user_data=user_data, task=task)
            data_file.file.name = s3_key
            data_file.save()


class BaseDataRetrievalView(View):
    """
    Abstract base class for a view that starts a data retrieval task.

    Class attributes that need to be defined:
        datafile_model (attribute)
            A subclass of BaseDataFile

    Class methods you probably want to override:
        get_task_params(self, **kwargs)
            Returns a dict with parameters sent to the data processing server.
            This could include user or sample IDs, access tokens, or any other
            data needed to construct the resulting data file. Make sure to also
            keep the parameters defined in the default version of this method
            ('s3_key_dir', 's3_bucket_name', 'task_id', and 'update_url').
    """
    datafile_model = None
    redirect_url = reverse_lazy('my-member-research-data')
    message_error = "Sorry, our data retrieval server seems to be down."
    message_started = "Thanks! We've submitted this data import task to our server."

    def post(self, request):
        self.request = request
        self.make_retrieval_task()
        self.start_task()
        return self.redirect()

    def make_retrieval_task(self):
        self.retrieval_task = DataRetrievalTask(
            datafile_model=ContentType.objects.get_for_model(
                self.datafile_model),
            user=self.request.user)
        self.retrieval_task.save()

    def start_task(self):
        # Target URL is automatically determined from relevant app label.
        task_url = urlparse.urljoin(settings.DATA_PROCESSING_URL,
                                    self.datafile_model._meta.app_label)
        try:
            task_req = requests.get(task_url, params=self.get_task_params())
        except requests.exceptions.RequestException as request_error:
            self.fail_task(
                error_message="Error in call to Open Humans Data Processing.",
                error_data=self.get_nonsecret_params(**{
                    'task_url': task_url,
                    'request_error': str(request_error)})
            )
            return
        if not ('task_req' in locals() and task_req.status_code == 200):
            # Note: could update as success later if retrieval app works anyway
            self.fail_task(
                error_message="Open Humans Data Processing not returning 200.",
                error_data=self.get_nonsecret_params(**{'task_url': task_url})
            )
        else:
            messages.success(self.request, self.message_started)

    def get_task_params(self, **kwargs):
        task_params = kwargs
        task_params.update(self.__base_task_params())
        return task_params

    def __base_task_params(self):
        """Task parameters all tasks use. Subclasses may not override."""
        s3_key_dir = get_upload_dir(self.datafile_model, self.request.user)
        s3_bucket_name = settings.AWS_STORAGE_BUCKET_NAME,
        update_url = urlparse.urljoin('http://' +
                                      get_current_site(self.request).domain,
                                      '/data-import/task-update/')
        return {'s3_key_dir': s3_key_dir,
                's3_bucket_name': s3_bucket_name,
                'task_id': self.retrieval_task.id,
                'update_url': update_url}

    def fail_task(self, error_message, error_data):
        self.retrieval_task.status = self.retrieval_task.TASK_FAILED
        self.retrieval_task.save()
        messages.error(self.request, self.message_error)
        print error_message
        print error_data
        client.captureMessage(error_message,
                              error_data=error_data)

    def get_nonsecret_params(self, **kwargs):
        """
        Return task parameters for exception monitoring and logs.

        Separately defined as get_task_params may have secret data (eg tokens).
        """
        nonsecret_params = kwargs
        nonsecret_params.update(self.__base_task_params())
        return nonsecret_params

    def redirect(self):
        """Redirect to self.redirect_url"""
        return HttpResponseRedirect(self.redirect_url)
