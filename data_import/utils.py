from django.apps import apps

from studies.models import BaseStudyUserData


def app_label_to_app_models(label):
    """
    Given an app's name, return its models.
    """
    return apps.get_app_config(label).get_models()


def app_label_to_user_data_model(label):
    """
    Given an app name, return its UserData type.
    """
    for model in app_label_to_app_models(label):
        if (issubclass(model, BaseStudyUserData) or
                model.__name__ == 'UserData'):
            return model
