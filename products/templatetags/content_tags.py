from django import template
from products.models import TranslatableContent
from django.utils.translation import get_language

register = template.Library()

from django.utils.translation import gettext_lazy as _

@register.simple_tag
def get_translatable_content(key):
    lang = get_language()
    try:
        content_obj = TranslatableContent.objects.get(key=key)
        field_name = f'content_{lang}'
        # Fallback to English if the specific language content is empty
        content = getattr(content_obj, field_name, '') or getattr(content_obj, 'content_en', '')
        return content
    except TranslatableContent.DoesNotExist:
        return _(f"Contingut no trobat per a la clau: '{key}'")
