
import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def json_script_tag(data):
    """
    Serializes a Python object to a JSON string and marks it as safe for rendering
    in a <script> tag.
    """
    return mark_safe(json.dumps(data))
