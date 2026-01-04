
from django.conf import settings

class TitleContextMixin:
    def get_titles_with_status(self, titles):
        titles_with_status = []
        user = self.request.user if self.request.user.is_authenticated else None
        # Since all titles include all languages, get the list from settings.
        language_names = [name for code, name in settings.LANGUAGES]

        for title in titles:
            titles_with_status.append({
                'title': title,
                'status': title.get_user_status(user),
                'image_url': title.get_image_url(),
                'language_names': language_names
            })
        return titles_with_status
