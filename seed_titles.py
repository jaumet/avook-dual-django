import os
import django
import json

def seed_titles():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avook_site.settings')
    django.setup()
    from products.models import Title, TitleLanguage

    with open('samples/audios.json') as f:
        data = json.load(f)

    # Clear existing titles and languages to ensure a clean slate
    Title.objects.all().delete()
    TitleLanguage.objects.all().delete()

    for machine_name, details in data['AUDIOS'].items():
        title, created = Title.objects.get_or_create(
            machine_name=machine_name,
            defaults={
                'description': details.get('description', ''),
                'levels': details.get('levels', ''),
                'ages': details.get('ages', ''),
                'collection': details.get('collection', ''),
                'duration': details.get('duration', ''),
            }
        )
        if created:
            print(f"Created title: {title.machine_name}")
        else:
            print(f"Title already exists: {title.machine_name}")

        if 'text_versions' in details:
            for lang_code, lang_details in details['text_versions'].items():
                TitleLanguage.objects.update_or_create(
                    title=title,
                    language=lang_code.upper(),
                    defaults={
                        'human_name': lang_details.get('human_name', ''),
                        'directory': lang_details.get('directory', ''),
                        'json_file': lang_details.get('json_file', '')
                    }
                )
                print(f"  - Added/Updated language: {lang_code.upper()}")

if __name__ == "__main__":
    seed_titles()
