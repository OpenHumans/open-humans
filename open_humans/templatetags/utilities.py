import logging
import os
import re

import bleach
import markdown as markdown_library

from django import template
from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse, NoReverseMatch
from django.template.defaultfilters import stringfilter
from django.template.loader_tags import do_include
from django.utils.safestring import mark_safe

from common.utils import full_url as full_url_method
from private_sharing.models import (
    DataRequestProjectMember,
    app_label_to_verbose_name_including_dynamic,
    project_membership_visible,
)
from private_sharing.utilities import source_to_url_slug as source_to_url_slug_method
from public_data.models import Participant

logger = logging.getLogger(__name__)

register = template.Library()


@register.filter
@stringfilter
def startswith(string, substring):
    """
    Return True if string starts with substring, otherwise false.
    """
    return string.startswith(substring)


@register.filter
def source_to_name(source):
    """
    Given 'american_gut', return 'American Gut'
    """
    try:
        return app_label_to_verbose_name_including_dynamic(source)
    except:  # pylint: disable=bare-except
        return source


@register.filter
@stringfilter
def source_to_url_slug(source):
    """
    Return url_slug for an "app" activity, or slug for "project" activity.
    """
    return source_to_url_slug_method(source)


@register.filter
def lookup(dictionary, key):
    """
    Get a dictionary value by key within a template.
    """
    return dictionary.get(key)


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
            return ""


@register.tag
def try_include(parser, token):
    """
    Include the specified template but only if it exists.
    """
    return TryIncludeNode(parser, token)


@register.filter
def markdown(value):
    """
    Translate markdown to a safe subset of HTML.
    """
    cleaned = bleach.clean(
        markdown_library.markdown(value),
        tags=bleach.ALLOWED_TAGS + ["p", "h1", "h2", "h3", "h4", "h5", "h6"],
    )

    linkified = bleach.linkify(cleaned)

    return mark_safe(linkified)


@register.simple_tag(takes_context=True)
def next_page(context):
    """
    Get the next page for signup or login.

    The query string takes priority over the template variable and the default
    is an empty string.
    """
    if "next" in context.request.GET:
        return context.request.GET["next"]

    if "next" in context.request.POST:
        return context.request.POST["next"]

    if "next" in context:
        return context["next"]

    return ""


def slugify_url(url):
    """
    Turn '/study/connect_me/' into 'study-connect-me'.
    """
    return url.lower().strip("/").replace(":", "-").replace("/", "-").replace("_", "-")


def script_if_exists(slug):
    """
    Return a script tag if the given slug path exists.
    """
    # don't try to add scripts with unicode characters
    if isinstance(slug, str):

        fs_path = os.path.join(settings.BASE_DIR, "build/js/{}.js".format(slug))

        if os.path.exists(fs_path):
            return '<script src="{}js/{}.js"></script>'.format(
                settings.STATIC_URL, slug
            )


@register.simple_tag(takes_context=True)
def page_bundle(context):
    """
    Get the bundle path for a given page, first trying the view name and then
    the URL slug.
    """
    # for example, /study/connect/abc/ has a view_name of studies:connect
    try:
        name = slugify_url(context.request.resolver_match.view_name)
    except AttributeError:
        name = "404"

    script = script_if_exists(name)

    if script:
        return mark_safe(script)

    path = slugify_url(context.request.path)
    script = script_if_exists(path)

    if script:
        return mark_safe(script)

    if settings.DEBUG:
        return mark_safe('<!-- DEBUG: not found: "{}", "{}" -->'.format(name, path))

    return ""


@register.simple_tag(takes_context=True)
def page_body_id(context):
    """
    Get the CSS class for a given page.
    """
    path = slugify_url(context.request.path)

    if not path:
        path = "home"

    return "page-{}".format(path)


@register.simple_tag(takes_context=True)
def page_body_class(context):
    """
    Get the CSS class for a given resolved URL.
    """
    try:
        return "url-{}".format(context.request.resolver_match.url_name)
    except AttributeError:
        return "404"


@register.simple_tag(takes_context=True)
def active(context, pattern_or_urlname):
    """
    Return 'active' if the given URL or pattern is active.
    """
    try:
        pattern = "^" + reverse(pattern_or_urlname)
    except NoReverseMatch:
        pattern = pattern_or_urlname

    path = context.request.path

    if re.search(pattern, path):
        return "active"

    return ""


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

    if len(value) == 0:
        return ""

    if len(value) == 1:
        return value[0]

    if len(value) == 2:
        return "{} and {}".format(value[0], value[1])

    # join all but the last element
    all_but_last = ", ".join(value[:-1])
    return "{}, and {}".format(all_but_last, value[-1])


@register.filter
def full_url(value):
    """
    Given a fragment, return that fragment joined to the full Open Humans URL.
    """
    return full_url_method(value)


@register.filter
def add_string(a, b):
    """
    Like `add` but coerces to strings instead of integers.
    """
    return str(a) + str(b)


@register.tag
def render_if_visible(parser, token):
    """
    Is a member publicly sharing data but wishes that membership to not be public?
    """
    try:
        tag, member_t, source_label_t = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("is_visible requires exactly two arguments")

    nodelist = parser.parse(("end_render_if_visible",))
    parser.delete_first_token()
    member = parser.compile_filter(member_t)
    source = parser.compile_filter(source_label_t)

    return VisibleNode(nodelist, member, source)


class VisibleNode(template.Node):
    def __init__(self, nodelist, member, source):
        self.nodelist = nodelist
        self.member = member
        self.source = source

    def render(self, context):
        member = self.member.resolve(context)
        source = self.source.resolve(context)
        if project_membership_visible(member, source):
            return self.nodelist.render(context)
        else:
            return ""


@register.simple_tag()
def render_user_badges(member, badge_class="mini-badge"):
    """
    Returns the html to render all of a member's badges.
    """
    projects = DataRequestProjectMember.objects.select_related("project").filter(
        visible=True,
        project__approved=True,
        member=member,
        authorized=True,
        revoked=False,
    )
    html = ""
    for project in projects:
        html += make_badge(project.project, badge_class=badge_class)

    try:
        participant = Participant.objects.get(member_id=member.id)
        if participant.enrolled:
            html += make_badge("public_data", badge_class=badge_class)
    except Participant.DoesNotExist:
        pass

    return mark_safe(html)


@register.simple_tag()
def make_badge(project, badge_class="oh-badge"):
    """
    Return HTML for a badge.
    """
    if project == "public_data":
        badge_data = {
            "name": "Public Data Sharing",
            "static_url": static("images/public-data-sharing-badge.png"),
            "badge_class": badge_class,
            "href": reverse("public-data:home"),
        }
    else:
        try:
            badge_url = project.badge_image.url
        except ValueError:
            badge_url = static("images/default-badge.png")
        badge_data = {
            "name": project.name,
            "badge_class": badge_class,
            "static_url": badge_url,
            "href": reverse("activity", kwargs={"slug": project.slug}),
        }

    return mark_safe(
        """<a href="{href}" class="{badge_class}">
            <img class="{badge_class}"
              src="{static_url}" alt="{name}" title="{name}">
           </a>""".format(
            **badge_data
        )
    )


@register.simple_tag()
def template_bool(item):
    return bool(item)


@register.simple_tag()
def project_is_connected(project, user):
    """
    Return True if the given project is connected (joined and authorized).
    """
    return project.is_joined(user)


@register.simple_tag(takes_context=True)
def get_download_url(context, data_file):
    """
    Returns the download url
    """
    return data_file.download_url(context.request)
