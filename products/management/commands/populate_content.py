import json
from django.core.management.base import BaseCommand
from django.conf import settings
from products.models import TranslatableContent

class Command(BaseCommand):
    help = 'Populates the database with translatable content from translations.json'

    def handle(self, *args, **options):

        self.stdout.write(self.style.WARNING('This command is now deprecated and will be removed in a future version.'))
        self.stdout.write(self.style.SUCCESS('Finished populating translatable content.'))
