from django import template

from ..models import DataRequestProjectMember

register = template.Library()


@register.simple_tag
def project_is_connected(project_id, member):
    """
    Return True if the given project is connected (joined and authorized).
    """
    try:
        DataRequestProjectMember.objects.get(
            project_id=project_id,
            member=member,
            joined=True,
            authorized=True,
            revoked=False)

        return True
    except DataRequestProjectMember.DoesNotExist:
        return False
