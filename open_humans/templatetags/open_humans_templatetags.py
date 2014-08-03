import re

import markdown as markdown_library

from django import template
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.safestring import mark_safe

register = template.Library()


# TODO: Verify security of this; use markdown2 instead? Use
# django-markdown-deux?
@register.filter()
def markdown(value):
    return mark_safe(markdown_library.markdown(value, safe_mode='escape'))


@register.filter()
def path_to_filename(value):
    return value.lower().strip('/').replace('/', '-')


@register.simple_tag(takes_context=True)
def active(context, pattern_or_urlname):
    try:
        pattern = '^' + reverse(pattern_or_urlname)
    except NoReverseMatch:
        pattern = pattern_or_urlname

    path = context['request'].path

    if re.search(pattern, path):
        return 'active'

    return ''
