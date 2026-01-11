from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.simple_tag
def get_product_translation(product, language_code):
    """
    Template tag to get the translation for a product for a specific language.
    """
    return product.get_translation(language_code)
