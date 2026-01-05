
import os
import json
from django.conf import settings

class TitleContextMixin:
    def get_titles_with_status(self, titles):
        titles_with_status = []
        user = self.request.user if self.request.user.is_authenticated else None
        lang_code = self.request.LANGUAGE_CODE[:2].upper()

        # Load titles info from audios.json
        try:
            audios_json_path = os.path.join(settings.STATICFILES_DIRS[0], 'audios.json')
            with open(audios_json_path, 'r', encoding='utf-8') as f:
                audios_data = json.load(f).get("AUDIOS", {})
        except (FileNotFoundError, json.JSONDecodeError):
            audios_data = {}

        for title in titles:
            title_info = audios_data.get(title.machine_name, {})
            json_info = title_info.get('title', {}).get(lang_code) if title_info else None

            titles_with_status.append({
                'title': title,
                'status': title.get_user_status(user),
                'image_url': title.get_image_url(),
                'json_info': json_info,
            })
        return titles_with_status
