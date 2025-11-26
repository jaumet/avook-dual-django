import os
import django

def seed():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avook_site.settings')
    django.setup()
    from products.models import Title, TitleLanguage

    titles_to_create = [
        {
            'id': 1, 'machine_name': 'test-title-1', 'human_name': 'Test Title 1',
            'description': 'Description for test title 1', 'levels': 'A1', 'ages': '10-12',
            'collection': 'Collection A', 'duration': '00:02:30',
            'languages': ['EN', 'ES']
        },
        {
            'id': 2, 'machine_name': 'test-title-2', 'human_name': 'Test Title 2',
            'description': 'Description for test title 2', 'levels': 'A2', 'ages': '12-14',
            'collection': 'Collection B', 'duration': '00:05:00',
            'languages': ['FR', 'DE']
        },
        {
            'id': 3, 'machine_name': 'another-title', 'human_name': 'Another Title',
            'description': 'Another description', 'levels': 'A1', 'ages': '10-12',
            'collection': 'Collection A', 'duration': '00:03:15',
            'languages': ['EN', 'FR']
        }
    ]

    for title_data in titles_to_create:
        if not Title.objects.filter(id=title_data['id']).exists():
            title = Title.objects.create(
                id=title_data['id'],
                machine_name=title_data['machine_name'],
                human_name=title_data['human_name'],
                description=title_data['description'],
                levels=title_data['levels'],
                ages=title_data['ages'],
                collection=title_data['collection'],
                duration=title_data['duration']
            )
            for lang_code in title_data['languages']:
                TitleLanguage.objects.create(title=title, language=lang_code, directory=f'/{lang_code}/', json_file=f'{lang_code}.json')
            print(f"Title '{title.human_name}' seeded.")
        else:
            print(f"Title '{title_data['human_name']}' already exists.")

if __name__ == "__main__":
    seed()
