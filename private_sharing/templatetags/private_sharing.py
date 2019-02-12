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
