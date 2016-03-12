import json

from .models import DataRetrievalTask


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
    user_data = getattr(user, source)

    if hasattr(user_data, 'refresh_from_db'):
        user_data.refresh_from_db()

    task = DataRetrievalTask(
        source=source,
        user=user,
        app_task_params=json.dumps(user_data.get_retrieval_params()))

    task.save()

    return task
