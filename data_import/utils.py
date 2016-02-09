from django.apps import apps

from studies.models import BaseStudyUserData


def app_name_to_app_config(app_name):
    """
    Given an app's name, return its AppConfig.
    """
    for app_config in apps.get_app_configs():
        app_config_name = app_config.name.split('.')[-1]

        # Continue unless the file path matches the app's name.
        if app_config_name != app_name:
            continue

        return app_config


def app_name_to_app_models(app_name):
    """
    Given an app's name, return its models.
    """
    return app_name_to_app_config(app_name).get_models()


def app_name_to_user_data_model(app_name):
    """
    Given an app name, return its UserData type.
    """
    for model in app_name_to_app_models(app_name):
        if (issubclass(model, BaseStudyUserData) or
                model.__name__ == 'UserData'):
            return model


def get_source_names():
    """
    Return a list of all current data source app names.
    """
    names = []
    for app_config in apps.get_app_configs():
        if (app_config.name.startswith('studies.') or
                app_config.name.startswith('activities.')):
            source_name = app_config.name.split('.')[-1]
            names.append(source_name)
    return names
