import os
import django
import json

def seed_titles():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avook_site.settings')
    django.setup()
    from products.models import Title, TitleLanguage

    with open('samples/audios.json') as f:
        data = json.load(f)

    last_title = Title.objects.order_by('-id').first()
    next_id = 10001
    if last_title:
        try:
            next_id = int(last_title.id) + 1
        except (ValueError, TypeError):
            pass

    for machine_name, details in data['AUDIOS'].items():
        title, created = Title.objects.get_or_create(
            machine_name=machine_name,
            defaults={
                'id': str(next_id),
                'human_name': details.get('title-human', machine_name),
                'description': details.get('description', ''),
                'levels': details.get('levels', ''),
                'ages': details.get('ages', ''),
                'collection': details.get('collection', ''),
                'duration': details.get('duration', ''),
            }
        )
        if created:
            print(f"Created title: {title.human_name}")
            next_id += 1
            langs = details.get('langs', '').split(',')
            for lang in langs:
                lang = lang.strip().upper()
                if lang:
                    TitleLanguage.objects.get_or_create(
                        title=title,
                        language=lang,
                        defaults={
                            'directory': f"/AUDIOS/{machine_name}/{lang}/",
                            'json_file': f"{lang}-{machine_name}.json"
                        }
                    )
                    print(f"  - Added language: {lang}")
        else:
            print(f"Title already exists: {title.human_name}")

if __name__ == "__main__":
    seed_titles()
