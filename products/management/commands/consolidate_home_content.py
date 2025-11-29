from django.core.management.base import BaseCommand
from products.models import TranslatableContent
import json

class Command(BaseCommand):
    help = 'Consolidates home page content into a single entry.'

    def handle(self, *args, **options):
        home_content = TranslatableContent.objects.filter(key__startswith='home_')

        if not home_content.exists():
            self.stdout.write(self.style.SUCCESS('No home page content to consolidate.'))
            return

        consolidated_content = {
            'ca': {}, 'en': {}, 'es': {}, 'fr': {}, 'pt': {}, 'de': {}, 'it': {}
        }

        for content in home_content:
            key = content.key.replace('home_', '')
            consolidated_content['ca'][key] = content.content_ca
            consolidated_content['en'][key] = content.content_en
            consolidated_content['es'][key] = content.content_es
            consolidated_content['fr'][key] = content.content_fr
            consolidated_content['pt'][key] = content.content_pt
            consolidated_content['de'][key] = content.content_de
            consolidated_content['it'][key] = content.content_it

        new_content, created = TranslatableContent.objects.update_or_create(
            key='home_content',
            defaults={
                'content_ca': json.dumps(consolidated_content['ca'], ensure_ascii=False, indent=2),
                'content_en': json.dumps(consolidated_content['en'], ensure_ascii=False, indent=2),
                'content_es': json.dumps(consolidated_content['es'], ensure_ascii=False, indent=2),
                'content_fr': json.dumps(consolidated_content['fr'], ensure_ascii=False, indent=2),
                'content_pt': json.dumps(consolidated_content['pt'], ensure_ascii=False, indent=2),
                'content_de': json.dumps(consolidated_content['de'], ensure_ascii=False, indent=2),
                'content_it': json.dumps(consolidated_content['it'], ensure_ascii=False, indent=2),
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS('Successfully created new home_content entry.'))
        else:
            self.stdout.write(self.style.SUCCESS('Successfully updated home_content entry.'))

        home_content.delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted old home page content entries.'))
