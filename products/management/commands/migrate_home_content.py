import json
from django.core.management.base import BaseCommand
from products.models import TranslatableContent, HomePageContent

class Command(BaseCommand):
    help = 'Migrates content from the old TranslatableContent home_content to the new HomePageContent model.'

    def handle(self, *args, **options):
        try:
            old_content = TranslatableContent.objects.get(key='home_content')
        except TranslatableContent.DoesNotExist:
            self.stdout.write(self.style.WARNING('No old home_content found to migrate.'))
            return

        new_content, created = HomePageContent.objects.get_or_create()

        for lang in ['ca', 'en']:
            field_name = f'content_{lang}'
            content_json = getattr(old_content, field_name, '{}')

            try:
                content_dict = json.loads(content_json)
            except json.JSONDecodeError:
                self.stdout.write(self.style.ERROR(f'Could not decode JSON for language {lang}. Skipping.'))
                continue

            for key, value in content_dict.items():
                new_field_name = f'{key}_{lang}'
                if hasattr(new_content, new_field_name):
                    setattr(new_content, new_field_name, value)

        new_content.save()
        self.stdout.write(self.style.SUCCESS('Successfully migrated content to HomePageContent.'))
