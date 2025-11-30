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

        home_content_by_lang = {lang: {} for lang in translations.keys()}
        other_content = {}

        for lang, trans_dict in translations.items():
            other_content[lang] = {}
            for key, value in trans_dict.items():
                if key.startswith('home.'):
                    simple_key = key.replace('home.', '').replace('.', '_')
                    home_content_by_lang[lang][simple_key] = value
                elif key == 'help_modal.html_content':
                    other_content[lang][key.replace('.', '_')] = value

        # Create the single home_content entry only if it does not exist
        if not TranslatableContent.objects.filter(key='home_content').exists():
            home_content_defaults = {
                f'content_{lang}': json.dumps(content, ensure_ascii=False, indent=2)
                for lang, content in home_content_by_lang.items()
            }
            TranslatableContent.objects.create(
                key='home_content',
                **home_content_defaults
            )
            self.stdout.write(self.style.SUCCESS('Successfully populated home_content.'))
        else:
            self.stdout.write(self.style.WARNING('home_content already exists, skipping.'))

        # Create other content entries only if they do not exist
        for lang, content_dict in other_content.items():
            for key, value in content_dict.items():
                if not TranslatableContent.objects.filter(key=key).exists():
                    obj = TranslatableContent.objects.create(key=key)
                    field_name = f'content_{lang}'
                    if hasattr(obj, field_name):
                        setattr(obj, field_name, value)
                        obj.save()
                        self.stdout.write(self.style.SUCCESS(f'Successfully created {key} for language {lang}'))
                else:
                    self.stdout.write(self.style.WARNING(f'{key} already exists, skipping.'))


        self.stdout.write(self.style.SUCCESS('Finished populating translatable content.'))
