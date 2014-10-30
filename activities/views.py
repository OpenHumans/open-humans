from datetime import datetime

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from twenty_three_and_me.models import DataExtractionTask as DataExtractionTask23andme

from .models import TASK_SUCCESSFUL, TASK_FAILED


class TaskUpdateView(View):

    # GET only for testing purposes.
    @csrf_exempt
    def get(self, request, *args, **kwargs):
        task_name = request.GET['name']
        task_state = request.GET['state']
        s3_key_name = request.GET['s3_key_name']
        return self.update_task(task_name, task_state, s3_key_name)

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        task_name = request.POST['name']
        task_state = request.POST['state']
        s3_key_name = request.POST['s3_key_name']
        return self.update_task(task_name, task_state, s3_key_name)

    @staticmethod
    def update_task(task_name, task_state, s3_key_name):
        task_data = None
        if task_name == 'client.start_23andme_ohdataset':
            task_data = DataExtractionTask23andme.objects.get(
                data_file__file=s3_key_name)
        if not task_data:
            return HttpResponse('Invalid task name!')

        if task_state == 'SUCCESS':
            task_data.status = TASK_SUCCESSFUL
        elif task_state == 'FAILURE':
            task_data.status = TASK_FAILED
        task_data.complete_time = datetime.now()
        task_data.save()
        return HttpResponse('Thanks!')
