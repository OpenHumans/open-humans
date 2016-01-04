import json

from django.contrib.contenttypes.models import ContentType

from .models import BaseDataFile, DataRetrievalTask


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


def make_retrieval_task(user, datafile_model):
    """
    Create a retrieval task for the given user and datafile type.
    """
    assert issubclass(datafile_model, BaseDataFile), (
        '%r is not a subclass of BaseDataFile' % datafile_model)

    task = DataRetrievalTask(
        datafile_model=ContentType.objects.get_for_model(datafile_model),
        user=user,
        app_task_params=json.dumps(get_app_task_params(user, datafile_model)))

    task.save()

    return task


def get_app_task_params(user, datafile_model):
    """
    Generate the task params for the given user and datafile type.
    """
    userdata_model = (datafile_model._meta
                      .get_field_by_name('user_data')[0]
                      .rel.to)

    return userdata_model.objects.get(user=user).get_retrieval_params()
