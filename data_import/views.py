from datetime import datetime

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from activities.twenty_three_and_me.models import DataRetrievalTask as \
    DataRetrievalTask23andme


class TaskUpdateView(View):
    """Receive and record task success/failure input."""

    task_retrieval_methods = {
        'client.make_23andme_ohdataset':  DataRetrievalTask23andme.get_task,
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
        elif task_state == 'FAILURE':
            task_data.status = task_data.TASK_FAILED
        task_data.save()
        return 'Thanks!'
