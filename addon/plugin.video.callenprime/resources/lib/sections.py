"""Small, non-resident catalogue sections for Kodi's native directory UI.

These lists intentionally contain fictional items only. They add no widgets,
read no account data and do not change the Kodi/Nimbus home configuration.
"""
from . import fixtures, presentation

SECTION_LABELS = {'movies': 'Movies', 'series': 'Series', 'anime': 'Anime'}


def listed_items(addon_path, section):
    if section not in SECTION_LABELS:
        return []
    try:
        catalogue = fixtures.load_catalog(addon_path)
        kind = {'movies': 'movie', 'series': 'series', 'anime': 'anime'}[section]
        return [item for item in catalogue.values() if presentation.media_kind(item) == kind][:fixtures.LIMIT]
    except (OSError, IOError, ValueError, KeyError, TypeError):
        return []


def find_item(addon_path, section, media_id):
    return next((item for item in listed_items(addon_path, section) if item['id'] == media_id), None)
