from django import template

register = template.Library()


@register.simple_tag
def project_is_connected(project, user):
    """
    Return True if the given project is connected (joined and authorized).
    """
    return project.is_joined(user)
