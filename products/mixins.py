
import os
import json
from django.conf import settings

class TitleContextMixin:
    def get_titles_with_status(self, titles):
        titles_with_status = []
        user = self.request.user if self.request.user.is_authenticated else None
        lang_code = self.request.LANGUAGE_CODE[:2].upper()

        json_path = os.path.join(settings.BASE_DIR, 'static', 'audios.json')
        try:
            with open(json_path, 'r') as f:
                audios_data = json.load(f).get('AUDIOS', {})
        except (FileNotFoundError, json.JSONDecodeError):
            audios_data = {}

        for title in titles:
            machine_name = title.machine_name
            title_data = audios_data.get(machine_name, {})
            title_info = title_data.get('title', {}).get(lang_code)

            if not title_info:
                # Fallback to English if the current language is not available
                fallback_lang = 'EN'
                title_info = title_data.get('title', {}).get(fallback_lang, {})
                if not title_info:
                    # If no EN translation, get the first one available
                    available_langs = title_data.get('title', {})
                    if available_langs:
                        first_lang_code = next(iter(available_langs))
                        title_info = available_langs[first_lang_code]
                    else:
                        title_info = {'human-title': machine_name, 'description': ''}

            context_data = title_data.copy()
            context_data.update(title_info)

            titles_with_status.append({
                'title': title,
                'status': title.get_user_status(user),
                'image_url': title.get_image_url(),
                'json_info': context_data,
            })

        return titles_with_status
