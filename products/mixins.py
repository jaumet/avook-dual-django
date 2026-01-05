
import os
import json
from django.conf import settings
from .models import TitleTranslation

class TitleContextMixin:
    def get_titles_with_status(self, titles):
        titles_with_status = []
        user = self.request.user if self.request.user.is_authenticated else None
        lang_code = self.request.LANGUAGE_CODE[:2]

        for title in titles:
            try:
                translation = TitleTranslation.objects.get(title=title, language_code=lang_code)
                json_info = {
                    'human-title': translation.human_name,
                    'description': translation.description
                }
            except TitleTranslation.DoesNotExist:
                json_info = None

            titles_with_status.append({
                'title': title,
                'status': title.get_user_status(user),
                'image_url': title.get_image_url(),
                'json_info': json_info,
            })
        return titles_with_status
