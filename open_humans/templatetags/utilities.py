import logging
import os
import re

import bleach
import markdown as markdown_library

from django import template
from django.apps import apps
from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch
from django.template.loader_tags import do_include
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)

register = template.Library()


@register.filter(name='source_to_name')
def source_to_name(source):
    """
    Given 'go_viral', return 'GoViral'
    """
    try:
        return apps.get_app_config(source).verbose_name
    except:  # pylint: disable=bare-except
        return source


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


@register.filter()
def markdown(value):
    """
    Translate markdown to a safe subset of HTML.
    """
    cleaned = bleach.clean(markdown_library.markdown(value),
                           tags=bleach.ALLOWED_TAGS +
                           ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

    linkified = bleach.linkify(cleaned)

    return mark_safe(linkified)


@register.simple_tag(takes_context=True)
def next_page(context):
    """
    Get the next page for signup or login.

    The query string takes priority over the template variable and the default
    is an empty string.
    """
    if 'next' in context.request.GET:
        return context.request.GET['next']

    if 'next' in context.request.POST:
        return context.request.POST['next']

    if 'next' in context:
        return context['next']

    return ''


def slugify_url(url):
    """
    Turn '/study/connect_me/' into 'study-connect-me'.
    """
    return (url
            .lower()
            .strip('/')
            .replace('/', '-')
            .replace('_', '-'))


def script_if_exists(slug):
    """
    Return a script tag if the given slug path exists.
    """
    fs_path = os.path.join(settings.BASE_DIR,
                           'build/js/bundle-{}.js'.format(slug))

    if os.path.exists(fs_path):
        return '<script src="{}js/bundle-{}.js"></script>'.format(
            settings.STATIC_URL, slug)


@register.simple_tag(takes_context=True)
def page_bundle(context):
    """
    Get the bundle path for a given page, first trying the view name and then
    the URL slug.
    """
    # for example, /study/connect/abc/ has a view_name of studies:connect
    name = context.request.resolver_match.view_name.replace(':', '-')
    script = script_if_exists(name)

    if script:
        return script

    path = slugify_url(context.request.path)
    script = script_if_exists(path)

    if script:
        return script

    return ''


@register.simple_tag(takes_context=True)
def page_body_id(context):
    """
    Get the CSS class for a given page.
    """
    path = slugify_url(context.request.path)

    if not path:
        path = 'home'

    page_body_id_tag = 'page-' + path

    return page_body_id_tag


@register.simple_tag(takes_context=True)
def active(context, pattern_or_urlname):
    """
    Return 'active' if the given URL or pattern is active.
    """
    try:
        pattern = '^' + reverse(pattern_or_urlname)
    except NoReverseMatch:
        pattern = pattern_or_urlname

    path = context.request.path

    if re.search(pattern, path):
        return 'active'

    return ''


@register.filter
def join_and(value):
    """
    Given a list of strings, format them with commas and spaces, but
    with 'and' at the end.

    >>> join_and(['apples', 'oranges', 'pears'])
    "apples, oranges, and pears"
    """
    # convert numbers to strings
    value = [str(item) for item in value]

    if len(value) == 1:
        return value[0]

    if len(value) == 2:
        return '{} and {}'.format(value[0], value[1])

    # join all but the last element
    all_but_last = ', '.join(value[:-1])
    return '{}, and {}'.format(all_but_last, value[-1])
