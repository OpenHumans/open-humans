import random
import string as string_module  # pylint: disable=deprecated-module
import urllib.parse

from django.apps import apps
from django.conf import settings
from django.http import QueryDict


# TODO: Remove legacy apps and this filtering step.
LEGACY_APPS = ['american_gut', 'ancestry_dna', 'data_selfie', 'fitbit',
               'go_viral', 'jawbone', 'moves', 'mpower', 'pgp', 'runkeeper',
               'twenty_three_and_me', 'ubiome', 'vcf_data', 'wildlife',
               'withings']


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
    if url_fragment and not url_fragment.startswith('/'):
        return url_fragment

    return urllib.parse.urljoin(settings.DEFAULT_HTTP_PROTOCOL + '://' +
                            settings.DOMAIN,
                            str(url_fragment))


def get_source_labels_and_configs():
    """
    Return a list of all current data source app labels and names.
    """
    sources = [(app_config.label, app_config)
               for app_config in apps.get_app_configs()
               if app_config.name.startswith('studies.') or
               app_config.name.startswith('activities.')
               ]

    sources = [x for x in sources if x[0] not in LEGACY_APPS]

    return sorted(sources, key=lambda x: x[1].verbose_name.lower())


def get_activities():
    """
    Get just the activities.
    """
    return [activity for activity in get_source_labels_and_configs()
            if activity[1].name.startswith('activities.')]


def get_studies():
    """
    Get just the studies.
    """
    return [study for study in get_source_labels_and_configs()
            if study[1].name.startswith('studies.')]


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

    app = apps.get_app_config(label)

    if hasattr(app, 'user_data'):
        return app.user_data()


def generate_id(size=64, chars=(string_module.ascii_lowercase +
                                string_module.ascii_uppercase +
                                string_module.digits)):
    """
    Generate an ID consisting of upper and lowercase letters and digits.
    """
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))


def origin(string):
    """
    Coerce an origin to 'open-humans' or 'external', defaulting to 'external'
    """
    return 'open-humans' if string == 'open-humans' else 'external'
