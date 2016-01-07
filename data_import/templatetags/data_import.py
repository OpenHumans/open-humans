from django import template

from ..utils import app_name_to_user_data_model

register = template.Library()


@register.simple_tag
def source_is_connected(source, user):
    """
    Given 'go_viral', return True or False.
    """
    try:
        user_data_model = app_name_to_user_data_model(source)

        user_data = user_data_model.objects.get(user=user)

        return user_data.is_connected
    except:  # pylint: disable=bare-except
        return False
