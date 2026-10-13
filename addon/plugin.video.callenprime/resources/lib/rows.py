"""Bounded local row output; no network, background tasks or playback calls."""
from . import fixtures, profile


def listed_items(addon_path, row):
    if row == 'frozen':  # P0: minimal Python plugin comparator
        return fixtures.frozen_items(addon_path)
    if row == 'probe':   # P1: same items, with profile-scope/cache validation
        profile.read_snapshot()
        return fixtures.frozen_items(addon_path)
    if row not in fixtures.ROW_KEYS:
        return []
    snapshot = profile.read_snapshot()
    if snapshot is not None:
        entries = snapshot['rows'].get(row, [])
        return [dict(item) for item in entries[:fixtures.LIMIT]]
    try:
        return fixtures.load_rows(addon_path, 'neutral')[row]
    except (OSError, IOError, KeyError, ValueError, TypeError):
        return []


def find_item(addon_path, row, media_id):
    if row not in fixtures.ROW_KEYS and row not in ('frozen', 'probe'):
        return None
    for item in listed_items(addon_path, row):
        if item['id'] == media_id:
            return item
    return None
