from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.simple_tag
def get_product_translation(product, language_code):
    """
    Template tag to get the translation for a product for a specific language.
    This tag will prioritize the selected language and handle fallbacks gracefully.
    """
    # First, try to get the exact translation
    translation = product.translations.filter(language_code=language_code).first()
    if translation:
        return translation

    # If no exact match, try to get the primary language (e.g., 'en' from 'en-us')
    if '-' in language_code:
        primary_language = language_code.split('-')[0]
        translation = product.translations.filter(language_code=primary_language).first()
        if translation:
            return translation

    # If still no match, return the first available translation as a fallback
    return product.translations.first()
