from django import template
from django.utils.safestring import mark_safe

from private_sharing.models import DataRequestProject

register = template.Library()


@register.simple_tag
def project_is_connected(project, user):
    """
    Return True if the given project is connected (joined and authorized).
    """
    return project.is_joined(user)


@register.simple_tag()
def erasure_requested_checkbox():
    """
    If a Data Request Project supports member data erasure, then return the
    html to produce a checkbox to request this.
    """
    html = """
           <div class="checkbox">
             <label>
               <input type="checkbox" name="erasure_requested">

               Request that {{ object.project.name }} deletes my data
             </label>
           </div>
    """
    erasure_supported = True
    return mark_safe(html)
