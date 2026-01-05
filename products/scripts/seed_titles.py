import json
from pathlib import Path
from django.conf import settings
from products.models import Title, TitleTranslation

def run():
    json_path = Path(settings.BASE_DIR) / "static" / "audios.json"
    if not json_path.exists():
        print("audios.json not found")
        return

    with json_path.open(encoding="utf-8") as fh:
        data = json.load(fh)

    created_count = 0
    updated_count = 0

    for machine_name, details in data['AUDIOS'].items():
        title, created = Title.objects.update_or_create(
            machine_name=machine_name,
            defaults={
                'level': details.get('levels', ''),
            }
        )

        if created:
            created_count += 1
        else:
            updated_count += 1

        for lang_code, lang_data in details.get("title", {}).items():
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
