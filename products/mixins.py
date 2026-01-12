
import os
import json
from django.conf import settings

class TitleContextMixin:
    def get_titles_with_status(self, titles):
        titles_with_status = []
        user = self.request.user if self.request.user.is_authenticated else None
        lang_code = self.request.LANGUAGE_CODE[:2].upper()

        json_path = os.path.join(settings.BASE_DIR, 'static', 'AUDIOS', 'audios.json')
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                audios_data = json.load(f).get('AUDIOS', [])
        except (FileNotFoundError, json.JSONDecodeError):
            audios_data = []

        # Create a dictionary for quick lookup
        audios_map = {item['machine_name']: item for item in audios_data}

        for title in titles:
            translation = title.translations.filter(language_code=lang_code[:2]).first()
            if not translation:
                translation = title.translations.filter(language_code='en').first()
            if not translation:
                translation = title.translations.first()

            machine_name = title.machine_name
            title_data = audios_map.get(machine_name, {})
            text_versions = title_data.get('text_versions', [])
            title_info = None

            # Find the correct language version
            for version in text_versions:
                if version.get('lang', '').upper() == lang_code:
                    title_info = version
                    break

            # Fallback to English
            if not title_info:
                for version in text_versions:
                    if version.get('lang', '').upper() == 'EN':
                        title_info = version
                        break

            # Fallback to the first available language
            if not title_info and text_versions:
                title_info = text_versions[0]

            if not title_info:
                title_info = {'human-title': machine_name, 'description': ''}

            # Create a clean context dictionary
            context_data = {
                'machine_name': machine_name,
                'levels': title_data.get('levels', ''),
                'ages': title_info.get('ages', ''),
                'colection': title_info.get('colection', ''),
                'duration': title_info.get('duration', ''),
                'human_title': translation.human_name if translation else machine_name,
                'description': translation.description if translation else '',
                'json_file': title_info.get('json_file', ''),
                'languages': [v.get('lang') for v in text_versions if 'lang' in v]
            }

            titles_with_status.append({
                'title': title,
                'status': title.get_user_status(user),
                'image_url': title.get_image_url(),
                'json_info': context_data,
            })

        return titles_with_status
