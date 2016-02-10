from studies.models import BaseStudyUserData

from common.utils import app_label_to_app_config


def app_label_to_app_models(label):
    """
    Given an app's name, return its models.
    """
    return app_label_to_app_config(label).get_models()


def app_label_to_user_data_model(label):
    """
    Given an app name, return its UserData type.
    """
    for model in app_label_to_app_models(label):
        if (issubclass(model, BaseStudyUserData) or
                model.__name__ == 'UserData'):
            return model
