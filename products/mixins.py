
from django.conf import settings
from django.utils import translation

class TitleContextMixin:
    def get_titles_with_status(self, titles):
        titles_with_status = []
        user = self.request.user if self.request.user.is_authenticated else None
        current_lang = translation.get_language()
        lang_map = dict(settings.LANGUAGES)

        for title in titles.prefetch_related('languages'):
            language_names = [lang_map.get(lang.language.upper(), lang.language) for lang in title.languages.all()]

            # Get the human_name for the current language
            title_lang = title.languages.filter(language=current_lang.upper()).first()
            if not title_lang and title.languages.exists():
                title_lang = title.languages.first()

            human_name = title_lang.human_name if title_lang else title.machine_name

            titles_with_status.append({
                'title': title,
                'human_name': human_name,
                'status': title.get_user_status(user),
                'image_url': title.get_image_url(),
                'language_names': language_names
            })
        return titles_with_status
