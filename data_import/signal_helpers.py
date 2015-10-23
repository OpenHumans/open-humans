import json

from django.contrib.contenttypes.models import ContentType

from .models import DataRetrievalTask


def task_signal_pre_save(task_params, datafile_model, **kwargs):
    """
    Trigger data retrieval a study adds new data via UserData's data field.

    Data retrieval task creation is triggered on a pre_save signal to a
    UserData object (derived from studies.models.BaseStudyUserData) and only
    occurs if the new instance's data field is non-empty and changed.

    If the user's email address is verified, the task is started. Otherwise it
    is postponed.
    """
    instance = kwargs['instance']

    # Require the object looks like a UserData-derived object
    if not hasattr(instance, 'data') and hasattr(instance, 'user'):
        return

    # Only create a task if the new 'data' field is not empty and has changed.
    if not instance.data:
        return
    curr_version = kwargs['sender'].objects.get(pk=instance.pk)
    curr_data = json.dumps(curr_version.data, sort_keys=True)
    new_data = json.dumps(instance.data, sort_keys=True)
    if curr_data == new_data:
        return

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
