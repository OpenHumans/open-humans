from importlib import import_module

from django.conf.urls import include, url

from common.utils import get_activities


def to_url(label, app_config):
    """
    Generate a url for an activity.
    """
    if hasattr(app_config, 'url_slug'):
        name = app_config.url_slug
    else:
        name = app_config.verbose_name.lower().replace(' ', '-')

    path = '^{}/'.format(name)
    urls = import_module('.{}.urls'.format(label), 'activities')

    return url(path, include(urls, namespace=name))


urlpatterns = [to_url(*activity) for activity in get_activities()]
