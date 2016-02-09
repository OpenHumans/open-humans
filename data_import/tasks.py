import json

from .models import DataRetrievalTask
from .utils import app_name_to_user_data_model


def start_or_postpone_task(user, datafile_model):
    """
    Start (or postpone) a task for a given user and datafile type.
    """
    task = make_retrieval_task(user, datafile_model)

    if user.member.primary_email.verified:
        task.start_task()

        if task.status == task.TASK_FAILED:
            print '- task failed immediately'
        else:
            print '- task was started'
    else:
        task.postpone_task()

        print '- task was postponed'

    return task


def make_retrieval_task(user, source):
    """
    Create a retrieval task for the given user and datafile type.
    """
    task = DataRetrievalTask(
        source=source,
        user=user,
        app_task_params=json.dumps(get_app_task_params(user, source)))

    task.save()

    return task


def get_app_task_params(user, source):
    """
    Generate the task params for the given user and datafile type.
    """
    userdata_model = app_name_to_user_data_model(source)

    return userdata_model.objects.get(user=user).get_retrieval_params()
