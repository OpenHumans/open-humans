import json

from django.contrib.contenttypes.models import ContentType

from .models import DataRetrievalTask


def rec_hasattr(obj, attr):
    """
    Recursively check for attributes.
    """
    try:
        left, right = attr.split('.', 1)
    except ValueError:
        return hasattr(obj, attr)

    return rec_hasattr(getattr(obj, left), right)


def rec_getattr(obj, attr):
    """
    Recursively retrieve attributes.
    """
    return reduce(getattr, attr.split('.'), obj)


def task_signal_pre_save(task_params, datafile_model, sender, instance, raw,
                         comparison_field='data', **kwargs):
    """
    Trigger data retrieval a study adds new data via UserData's data field.

    Data retrieval task creation is triggered on a pre_save signal to a
    UserData object (derived from studies.models.BaseStudyUserData) and only
    occurs if the new instance's comparison field is non-empty and changed.
    The default comparison field is the 'data' field.

    (This abstraction may be unnecessary. As of November 2015 no objects are
    triggered on non-data fields.)

    If the user's email address is verified, the task is started. Otherwise it
    is postponed.
    """
    instance = instance

    # Skip is this is fixture data.
    if raw:
        return

    # Require the object looks like a UserData-derived object
    if (not rec_hasattr(instance, comparison_field) or
            not hasattr(instance, 'user')):
        return

    data = rec_getattr(instance, comparison_field)

    # Only create a task if the new 'data' field is not empty and has changed.
    if not data:
        return

    # If previously saved, get old version and compare.
    if instance.pk:
        try:
            current_object = sender.objects.get(pk=instance.pk)

            if comparison_field == 'data':
                current_data = json.dumps(current_object.data, sort_keys=True)
                data = json.dumps(data, sort_keys=True)
            else:
                current_data = rec_getattr(current_object, comparison_field)

            if current_data == data:
                return
        except sender.DoesNotExist:
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
