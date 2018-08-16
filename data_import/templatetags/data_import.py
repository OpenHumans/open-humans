from django import template
from django.apps import apps

from private_sharing.models import project_membership_visible

from ..models import is_public

register = template.Library()


@register.simple_tag
def source_is_connected(source, user):
    """
    Return True if the given source is connected (has the required data for
    retrieving the user's data, like a huID or an access token).
    """
    try:
        return getattr(user, source).is_connected
    except:  # pylint: disable=bare-except
        return False


@register.simple_tag
def source_is_individual_deletion(source):
    """
    Return True if the given source allows users to manage each file
    individually.
    """
    return apps.get_app_config(source).individual_deletion


@register.simple_tag(takes_context=True)
def source_is_public(context, source):
    """
    Return True if the given source is public for the user in the current
    request context.
    """
    return is_public(context.request.user.member, source)

@register.simple_tag(takes_context=True)
def source_is_visible(context, source):
    """
    Returns true if the given source is publicly visible.
    """
    return project_membership_visible(context.request.user.member, source)
