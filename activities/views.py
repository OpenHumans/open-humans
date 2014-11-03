from datetime import datetime

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from twenty_three_and_me.models import DataExtractionTask as DataExtractionTask23andme

from .models import TASK_SUCCESSFUL, TASK_FAILED


class TaskUpdateView(View):
    """Receive and record task success/failure input."""

    def post(self, request, *args, **kwargs):
        task_name = request.POST['name']
        task_state = request.POST['state']
        s3_key_name = request.POST['s3_key_name']
        response = self.update_task(task_name, task_state, s3_key_name)
        return HttpResponse(response)

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(TaskUpdateView, self).dispatch(*args, **kwargs)

    @staticmethod
    def update_task(task_name, task_state, s3_key_name):
        task_data = None
        if task_name == 'client.start_23andme_ohdataset':
            try:
                task_data = DataExtractionTask23andme.objects.get(
                    data_file__file=s3_key_name)
            except DataExtractionTask23andme.DoesNotExist:
                pass
        if not task_data:
            return 'Invalid task and key name data!'

        if task_state == 'SUCCESS':
            task_data.status = TASK_SUCCESSFUL
            task_data.complete_time = datetime.now()
        elif task_state == 'FAILURE':
            task_data.status = TASK_FAILED
        task_data.save()
        return 'Thanks!'
