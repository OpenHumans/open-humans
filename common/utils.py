import urlparse

from django.apps import apps
from django.conf import settings
from django.http import QueryDict


def app_from_label(app_label):
    """
    Return an app given an app_label or None if the app is not found.
    """
    app_configs = apps.get_app_configs()
    matched_apps = [a for a in app_configs if a.label == app_label]

    if matched_apps and len(matched_apps) == 1:
        return matched_apps[0]

    return None


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
