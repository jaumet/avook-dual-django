import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from products.models import Title
from products.utils import _normalize_languages


class Command(BaseCommand):
    help = "Importa títols des de static/audios.json cap a la base de dades"

    def handle(self, *args, **options):
        json_path = Path(settings.BASE_DIR) / "static" / "audios.json"
        if not json_path.exists():
            raise CommandError("No s'ha trobat l'arxiu static/audios.json")

        with json_path.open(encoding="utf-8") as fh:
            data = json.load(fh)

        created = 0
        updated = 0

        for slug, metadata in data.get("AUDIOS", {}).items():
            defaults = {
                "title_human": metadata.get("title-human", ""),
                "description": metadata.get("description", ""),
                "level": metadata.get("levels", ""),
                "languages": ", ".join(_normalize_languages(metadata.get("langs", ""))),
                "ages": metadata.get("ages", ""),
                "collection": metadata.get("colection", ""),
                "duration": metadata.get("duration", ""),
            }

            _, created_obj = Title.objects.update_or_create(
                slug=slug,
                defaults=defaults,
            )
            if created_obj:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Importació completada: {created} creats, {updated} actualitzats"
            )
        )
