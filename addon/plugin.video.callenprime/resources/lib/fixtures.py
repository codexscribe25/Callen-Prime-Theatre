"""Small, immutable, clearly fictional demo catalogue (no external metadata)."""
import json
import os

ROW_KEYS = ('continue', 'new', 'context-a', 'context-b', 'context-c')
ROW_LABELS = {
    'continue': 'Continue Watching',
    'new': "What's New",
    'context-a': 'For You',
    'context-b': 'Worth Exploring',
    'context-c': 'Something Different',
}
LIMIT = 8


def _read_json(path):
    # All fixture files ship inside the installed addon; no HTTP, dynamic paths,
    # personal Kodi data or user-supplied filename is accepted here.
    with open(path, 'r', encoding='utf-8') as stream:
        return json.load(stream)


def load_catalog(addon_path):
    base = os.path.join(addon_path, 'resources', 'fixtures')
    raw = _read_json(os.path.join(base, 'catalog.json'))
    if not isinstance(raw, list) or len(raw) > 64:
        raise ValueError('Invalid catalogue')
    catalogue = {}
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError('Invalid item')
        media_id = item.get('id')
        if not isinstance(media_id, str) or not media_id.startswith('demo:') or media_id in catalogue:
            raise ValueError('Unstable or duplicate fixture ID')
        if item.get('media_type') not in ('movie', 'episode'):
            raise ValueError('Unsupported media type')
        if not isinstance(item.get('title'), str) or len(item['title']) > 80:
            raise ValueError('Invalid fixture title')
        if item.get('media_kind', 'series' if item['media_type'] == 'episode' else 'movie') not in ('movie', 'series', 'anime'):
            raise ValueError('Invalid fixture media kind')
        if item.get('media_type') == 'movie' and item.get('media_kind', 'movie') != 'movie':
            raise ValueError('Invalid media kind for movie')
        if item.get('media_type') == 'episode' and item.get('media_kind', 'series') not in ('series', 'anime'):
            raise ValueError('Invalid media kind for episode')
        duration = item.get('runtime_minutes')
        if duration is not None and (type(duration) is not int or duration < 1 or duration > 240):
            raise ValueError('Invalid demo runtime')
        if item.get('art') not in ('poster-a.png', 'poster-b.png', 'poster-c.png'):
            raise ValueError('Invalid local artwork')
        catalogue[media_id] = item
    return catalogue


def load_rows(addon_path, preset):
    if preset not in ('neutral', 'andy', 'dad'):
        raise ValueError('Unsupported demo preset')
    base = os.path.join(addon_path, 'resources', 'fixtures')
    definitions = _read_json(os.path.join(base, 'profiles.json'))
    selected = definitions[preset]
    if set(selected) != set(ROW_KEYS):
        raise ValueError('Fixture row mismatch')
    catalogue = load_catalog(addon_path)
    result = {}
    for row in ROW_KEYS:
        ids = selected[row]
        if not isinstance(ids, list) or len(ids) > LIMIT or len(ids) != len(set(ids)):
            raise ValueError('Invalid row size or duplicate IDs')
        result[row] = [dict(catalogue[media_id]) for media_id in ids]
    return result


def frozen_items(addon_path):
    # P0 fixture is deliberately stable and profile-independent.
    catalogue = load_catalog(addon_path)
    return [dict(catalogue[id_]) for id_ in ('demo:movie:quartz-harbour', 'demo:movie:ember-road', 'demo:episode:iron-lantern')]
