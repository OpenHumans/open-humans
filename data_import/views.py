from datetime import datetime
import urlparse

import requests
from raven.contrib.django.raven_compat.models import client

from django.conf import settings
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from activities.twenty_three_and_me.models import DataRetrievalTask as \
    DataRetrievalTask23andme

from .models import get_upload_path


class TaskUpdateView(View):
    """Receive and record task success/failure input."""

    task_retrieval_methods = {
        'client.make_23andme_ohdataset': DataRetrievalTask23andme.get_task,
    }

    def post(self, request):
        task_name = request.POST['name']
        task_state = request.POST['state']
        s3_key_name = request.POST['s3_key_name']
        response = self.update_task(task_name, task_state, s3_key_name)
        return HttpResponse(response)

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(TaskUpdateView, self).dispatch(*args, **kwargs)

    @classmethod
    def update_task(cls, task_name, task_state, s3_key_name):
        task_data = None
        if task_name in cls.task_retrieval_methods:
            task_data = cls.task_retrieval_methods[task_name](
                filename=s3_key_name)
        if not task_data:
            return 'Invalid task and key name data!'
        if task_state == 'SUCCESS':
            task_data.status = task_data.TASK_SUCCESSFUL
            task_data.complete_time = datetime.now()
        elif task_state == 'QUEUED':
            task_data.status = task_data.TASK_QUEUED
        elif task_state == 'INITIATED':
            task_data.status = task_data.TASK_INITIATED
        elif task_state == 'FAILURE':
            task_data.status = task_data.TASK_FAILED
        task_data.save()
        return 'Thanks!'


class BaseDataRetrievalView(View):
    """
    Abstract base class for a view that starts a data retrieval task.

    Class attributes that need to be defined:
        datafile_model: A subclass of BaseDataFile
        userdata_model: Model used by the datafile_model's user_data field.
        dataretrievaltask_model: A subclass of BaseDataRetrievalTask
    """
    datafile_model = None
    userdata_model = None
    dataretrievaltask_model = None
    redirect_url = reverse_lazy('my-member-research-data')
    message_error = "Sorry, our data retrieval server seems to be down."
    message_started = "Thanks! We've submitted this data import task to our server."

    def post(self, request):
        self.request = request
        self.make_data_file()
        self.make_retrieval_task()
        self.start_task()
        return self.redirect()

    def make_data_file(self):
        """Create data_file object, which this task will import to."""
        user_data, _ = self.userdata_model.objects.get_or_create(
            user=self.request.user)
        self.data_file = self.datafile_model(user_data=user_data)
        filename = self.create_filename()
        self.data_file.file.name = get_upload_path(self.data_file, filename)
        self.data_file.save()

    def create_filename(self):
        """Generate base filename (does not include storage path)."""
        return '%s-%s.tar.bz2' % (self.data_file._meta.app_label,
                                  datetime.now().strftime('%Y%m%d%H%M%S'))

    def make_retrieval_task(self):
        self.retrieval_task = self.dataretrievaltask_model(
            data_file=self.data_file)
        self.retrieval_task.save()

    def start_task(self):
        task_url = urlparse.urljoin(settings.DATA_PROCESSING_URL,
                                    self.data_file._meta.app_label)
        print task_url
        print self.get_task_params()
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
        s3_key_name = self.data_file.file.name
        s3_bucket_name = settings.AWS_STORAGE_BUCKET_NAME,
        update_url = urlparse.urljoin('http://' +
                                      get_current_site(self.request).domain,
                                      '/data-import/task-update/')
        return {'s3_key_name': s3_key_name,
                's3_bucket_name': s3_bucket_name,
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
