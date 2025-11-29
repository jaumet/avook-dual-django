import json
from django.core.management.base import BaseCommand
from django.conf import settings
from products.models import TranslatableContent

class Command(BaseCommand):
    help = 'Populates the database with translatable content from translations.json'

    def handle(self, *args, **options):
        translations_path = settings.BASE_DIR / 'static' / 'js' / 'translations.json'

        with open(translations_path, 'r', encoding='utf-8') as f:
            translations = json.load(f)

        for lang, trans_dict in translations.items():
            for key, value in trans_dict.items():
                if key.startswith('home.') or key == 'help_modal.html_content':
                    content_key = key.replace('.', '_')
                    obj, created = TranslatableContent.objects.get_or_create(key=content_key)

                    # We map the language from the JSON file to the corresponding model field
                    field_name = f'content_{lang}'
                    if hasattr(obj, field_name):
                        setattr(obj, field_name, value)
                        obj.save()
                        self.stdout.write(self.style.SUCCESS(f'Successfully updated {content_key} for language {lang}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Field {field_name} not found in model for key {content_key}'))

        self.stdout.write(self.style.SUCCESS('Finished populating translatable content.'))
