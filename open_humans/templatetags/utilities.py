import os
import re

import markdown as markdown_library

from django import template
from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch
from django.template.loader_tags import do_include
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='zip')
def zip_lists(a, b):
    """
    zip() the two arguments.
    """
    return zip(a, b)


class TryIncludeNode(template.Node):
    """
    A Node that instantiates an IncludeNode but wraps its render() in a
    try/except in case the template doesn't exist.
    """
    def __init__(self, parser, token):
        self.include_node = do_include(parser, token)

    def render(self, context):
        try:
            return self.include_node.render(context)
        except template.TemplateDoesNotExist:
            return ''


@register.tag
def try_include(parser, token):
    """
    Include the specified template but only if it exists.
    """
    return TryIncludeNode(parser, token)


# TODO: Verify security of this; use markdown2 instead? Use
# django-markdown-deux?
@register.filter()
def markdown(value):
    return mark_safe(markdown_library.markdown(value, safe_mode='escape'))


@register.simple_tag(takes_context=True)
def page_bundle(context):
    path = (context['request'].path
            .lower()
            .strip('/')
            .replace('/', '-')
            .replace('_', '-'))

    fs_path = os.path.join(settings.BASE_DIR,
                           'build/js/bundle-{}.js'.format(path))

    if os.path.exists(fs_path):
        return '<script src="{}js/bundle-{}.js"></script>'.format(
            settings.STATIC_URL, path)

    return ''


@register.simple_tag(takes_context=True)
def page_body_id(context):
    path = (context['request'].path
            .lower()
            .strip('/')
            .replace('/', '-')
            .replace('_', '-'))
    if not path:
        path = 'home'
    page_body_id_tag = 'page-' + path
    return page_body_id_tag


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
