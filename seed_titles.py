import os
import django
import json

def seed_titles():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avook_site.settings')
    django.setup()
    from products.models import Title

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
                'level': details.get('levels', ''),
            }
        )
        if created:
            print(f"Created title: {machine_name}")
            next_id += 1
        else:
            print(f"Title already exists: {machine_name}")

if __name__ == "__main__":
    seed_titles()
