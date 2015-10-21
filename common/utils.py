import urlparse

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
