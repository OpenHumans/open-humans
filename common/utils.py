import urlparse

from operator import itemgetter

from django.apps import apps
from django.conf import settings
from django.http import QueryDict


def querydict_from_dict(input_dict):
    """
    Given a dict, return a QueryDict.
    """
    querydict = QueryDict('', mutable=True)
    querydict.update(input_dict)

    return querydict


def full_url(url_fragment):
    """
    Given a fragment, return that fragment joined to the full Open Humans URL.
    """
    return urlparse.urljoin(settings.DEFAULT_HTTP_PROTOCOL + '://' +
                            settings.DOMAIN,
                            url_fragment)

def get_source_labels_and_configs():
    """
    Return a list of all current data source app labels and names.
    """
    sources = [(app_config.label, app_config)
               for app_config in apps.get_app_configs()
               if app_config.name.startswith('studies.') or
               app_config.name.startswith('activities.')]

    return sorted(sources, key=lambda x: x[1].verbose_name)


def get_activities():
    """
    Get just the activities.
    """
    return [activity for activity in get_source_labels_and_configs()
            if activity[1].name.startswith('activities.')]


def get_source_labels_and_names():
    """
    Return a list of all current data source app labels and names.
    """
    return [(label, app_config.verbose_name)
            for label, app_config in get_source_labels_and_configs()]


def get_source_labels():
    """
    Return a list of all current data source app labels.
    """
    # Use get_source_labels_and_names so labels are sorted by verbose names
    return [label for label, _ in get_source_labels_and_names()]


def app_label_to_app_models(label):
    """
    Given an app's name, return its models.
    """
    return apps.get_app_config(label).get_models()


def app_label_to_verbose_name(label):
    """
    Given an app's name, return its verbose name.
    """
    return apps.get_app_config(label).verbose_name


def app_label_to_user_data_model(label):
    """
    Given an app name, return its UserData type.
    """
    for model in app_label_to_app_models(label):
        if (model.__base__.__name__ == 'BaseStudyUserData' or
                model.__name__ == 'UserData'):
            return model
