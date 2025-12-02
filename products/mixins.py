
from django.conf import settings

class TitleContextMixin:
    def get_titles_with_status(self, titles):
        titles_with_status = []
        user = self.request.user if self.request.user.is_authenticated else None
        lang_map = dict(settings.LANGUAGES)

        for title in titles:
            language_names = [lang_map.get(lang.language.upper(), lang.language) for lang in title.languages.all()]
            titles_with_status.append({
                'title': title,
                'status': title.get_user_status(user),
                'image_url': title.get_image_url(),
                'language_names': language_names
            })
        return titles_with_status
