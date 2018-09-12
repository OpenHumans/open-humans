from django import template
from django.utils.safestring import mark_safe

from private_sharing.models import DataRequestProject

register = template.Library()


@register.simple_tag()
def erasure_requested_checkbox(object):
    """
    If a Data Request Project supports member data erasure, then return the
    html to produce a checkbox to request this.
    """
    html = """
           <div class="checkbox">
             <label>
               <input type="checkbox" name="erasure_requested">

               Request that {0} deletes my data
             </label>
           </div>
    """
    erasure_supported = object.project.erasure_supported
    if erasure_supported == True:
        return mark_safe(str(html).format(object.project.name))
    else:
        return ''


@register.simple_tag
def project_is_connected(project, user):
    """
    Return True if the given project is connected (joined and authorized).
    """
    return project.is_joined(user)


@register.simple_tag
def erasure_requested_txt(erasure_requested):
    """
    Returns text requesting that a project erase a member's data.
    """

    erasure_text = ("""In addition, they have requested erasure of their data.  We have\n"""
    """deleted the data on our end, and hereby request that you do the same.""")

    if erasure_requested:
        return erasure_text
    else:
        return "The member has not requested that you erase their data"
