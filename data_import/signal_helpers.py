import json

from django.contrib.contenttypes.models import ContentType

from .models import DataRetrievalTask


def task_signal(instance, created, raw, task_params, datafile_model):
    """
    A helper method that studies can use to create retrieval tasks when users
    link datasets.
    """
    # If the model was created but not as part of a fixture
    if raw or not created:
        return

    if hasattr(instance, 'user_data'):
        user = instance.user_data.user
    else:
        user = instance.user

    task = DataRetrievalTask(
        datafile_model=ContentType.objects.get_for_model(datafile_model),
        user=user,
        app_task_params=json.dumps(task_params))

    task.save()

    if user.member.primary_email.verified:
        task.start_task()
    else:
        task.postpone_task()
