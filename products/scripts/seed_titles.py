import json
from pathlib import Path
from django.conf import settings
from products.models import Title, TitleTranslation

def run():
    """
    Seeds the database with titles from the new audios.json format.
    """
    json_path = Path(settings.STATICFILES_DIRS[0]) / "AUDIOS" / "audios.json"
    if not json_path.exists():
        print(f"audios.json not found at {json_path}")
        return

    try:
        with json_path.open(encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError:
        print("Error decoding JSON from audios.json")
        return

    created_count = 0
    updated_count = 0

    audios_list = data.get('AUDIOS', [])
    if not isinstance(audios_list, list):
        print("AUDIOS should be a list in audios.json")
        return

    for title_data in audios_list:
        machine_name = title_data.get('machine_name')
        if not machine_name:
            continue

        title, created = Title.objects.update_or_create(
            machine_name=machine_name,
            defaults={
                'level': title_data.get('levels', ''),
            }
        )

        if created:
            created_count += 1
        else:
            updated_count += 1

        for lang_data in title_data.get("text_versions", []):
            lang_code = lang_data.get('lang')
            if not lang_code:
                continue

            TitleTranslation.objects.update_or_create(
                title=title,
                language_code=lang_code.lower(),
                defaults={
                    "human_name": lang_data.get("human-title", ""),
                    "description": lang_data.get("description", ""),
                },
            )

    print(f"Created titles: {created_count}")
    print(f"Updated titles: {updated_count}")
