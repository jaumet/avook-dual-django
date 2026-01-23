
import os
import json
from django.conf import settings

class TitleContextMixin:
    def get_titles_with_status(self, titles):
        titles_with_status = []
        user = self.request.user if self.request.user.is_authenticated else None

        # Language codes for DB (lowercase) and JSON (uppercase)
        request_lang = self.request.LANGUAGE_CODE.lower() # e.g., 'en-us'
        primary_lang = request_lang.split('-')[0] # e.g., 'en'
        json_lang_code = primary_lang.upper() # e.g., 'EN'

        json_path = os.path.join(settings.AUDIOS_ROOT, 'audios.json')
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                audios_data = json.load(f).get('AUDIOS', [])
        except (FileNotFoundError, json.JSONDecodeError):
            audios_data = []

        audios_map = {item['machine_name']: item for item in audios_data}

        for title in titles:
            # 1. Get DB translation with proper fallback
            translation = title.translations.filter(language_code=request_lang).first()
            if not translation:
                translation = title.translations.filter(language_code=primary_lang).first()
            if not translation:
                translation = title.translations.filter(language_code='en').first()
            if not translation:
                translation = title.translations.first()

            machine_name = title.machine_name
            title_data_from_json = audios_map.get(machine_name, {})
            text_versions = title_data_from_json.get('text_versions', [])

            # 2. Get JSON metadata with proper fallback
            lang_version_from_json = None
            # Find the correct language version from JSON
            for version in text_versions:
                if version.get('lang', '').upper() == json_lang_code:
                    lang_version_from_json = version
                    break

            # Fallback to English in JSON
            if not lang_version_from_json:
                for version in text_versions:
                    if version.get('lang', '').upper() == 'EN':
                        lang_version_from_json = version
                        break

            # Fallback to the first available language in JSON
            if not lang_version_from_json and text_versions:
                lang_version_from_json = text_versions[0]

            if not lang_version_from_json:
                lang_version_from_json = {}

            # 3. Combine data, prioritizing DB for translatable text
            context_data = {
                'machine_name': machine_name,
                'levels': title.level,
                'ages': title_data_from_json.get('ages', ''),
                'colection': title_data_from_json.get('colection', ''),
                'duration': title_data_from_json.get('duration', ''),
                'human_title': translation.human_name if translation else machine_name,
                'description': translation.description if translation else '',
                'json_file': lang_version_from_json.get('json_file', ''),
                'languages': [v.get('lang') for v in text_versions if 'lang' in v]
            }

            titles_with_status.append({
                'title': title,
                'status': title.get_user_status(user),
                'image_url': title.get_image_url(),
                'json_info': context_data,
            })

        return titles_with_status
