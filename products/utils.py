import json
from pathlib import Path
from typing import Dict, List

from django.conf import settings


def _normalize_languages(raw_langs: str) -> List[str]:
    return [lang.strip() for lang in raw_langs.split(',') if lang.strip()]


def load_titles_grouped_by_level() -> Dict[str, List[dict]]:
    """Return titles grouped by level from static/audios.json."""

    json_path = Path(settings.BASE_DIR) / 'static' / 'audios.json'
    if not json_path.exists():
        return {}

    with json_path.open(encoding='utf-8') as fh:
        data = json.load(fh)

    titles_by_level: Dict[str, List[dict]] = {}
    for slug, metadata in data.get('AUDIOS', {}).items():
        level = metadata.get('levels', '').strip() or 'Sense nivell'
        title = {
            'slug': slug,
            'title': metadata.get('title-human', ''),
            'description': metadata.get('description', ''),
            'langs': _normalize_languages(metadata.get('langs', '')),
            'ages': metadata.get('ages', ''),
            'collection': metadata.get('colection', ''),
            'duration': metadata.get('duration', ''),
            'level': level,
        }
        titles_by_level.setdefault(level, []).append(title)

    for level_titles in titles_by_level.values():
        level_titles.sort(key=lambda item: item['title'])

    return titles_by_level
