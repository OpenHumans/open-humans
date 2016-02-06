from django import template

from ..models import is_public
from ..utils import app_name_to_app_config, app_name_to_user_data_model

register = template.Library()


@register.simple_tag
def source_is_connected(source, user):
    """
    Return True if the given source is connected (has the required data for
    retrieving the user's data, like a huID or an access token).
    """
    try:
        user_data_model = app_name_to_user_data_model(source)

        user_data = user_data_model.objects.get(user=user)

        return user_data.is_connected
    except:  # pylint: disable=bare-except
        return False


@register.simple_tag
def source_is_disconnectable(source):
    """
    Return True if the given source allows disconnection by the user.
    """
    return app_name_to_app_config(source).disconnectable


@register.simple_tag
def source_is_individual_deletion(source):
    """
    Return True if the given source allows users to manage each file
    individually.
    """
    return app_name_to_app_config(source).individual_deletion


@register.simple_tag(takes_context=True)
def source_is_public(context, source):
    """
    Return True if the given source is public for the user in the current
    request context.
    """
    return is_public(context.request.user.member, source)
