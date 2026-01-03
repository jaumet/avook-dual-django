from django.utils.translation import activate
from django.conf import settings

# The default value for LANGUAGE_SESSION_KEY is '_language'
LANGUAGE_SESSION_KEY = '_language'

class BrowserLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if LANGUAGE_SESSION_KEY not in request.session:
            accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE')
            if accept_language:
                browser_language = accept_language.split(',')[0].split('-')[0].lower()
                supported_languages = [lang[0] for lang in settings.LANGUAGES]
                if browser_language in supported_languages:
                    activate(browser_language)
                    request.session[LANGUAGE_SESSION_KEY] = browser_language

        response = self.get_response(request)
        return response
