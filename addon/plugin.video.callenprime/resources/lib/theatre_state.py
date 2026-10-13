"""Tiny per-Kodi-profile watchlist, separate from demo fixtures and provider tokens."""
import json
import os
import re
import hashlib

import xbmcvfs

from . import profile

_MAX_BYTES = 16384
_KEY = 'callenprime.theatre.watchlist.v1'
_ID = re.compile(r'^(movie|series|episode):[0-9]{1,9}$')


def _location():
    scope = profile.current_scope()
    if not scope:
        return None
    # Distinguish labels even if two Kodi profiles mistakenly share userdata.
    # The saved payload is also bound to BOTH real resolved scope and label.
    label_tag = hashlib.sha256(scope[1].encode('utf-8')).hexdigest()[:16]
    location = os.path.join(scope[0], 'addon_data', 'plugin.video.callenprime',
                            'theatre_list_' + label_tag + '.json')
    return location, scope



def read_list():
    location = _location()
    if not location:
        return []
    path, scope = location
    try:
        with xbmcvfs.File(path, 'r') as stream:
            raw = stream.read(_MAX_BYTES + 1)
        if len(raw) > _MAX_BYTES:
            return []
        payload = json.loads(raw)
        if (not isinstance(payload, dict) or payload.get('schema') != _KEY
                or payload.get('scope_id') != scope[2] or payload.get('profile_label') != scope[1]
                or not isinstance(payload.get('items'), list)):
            return []
        items = payload['items']
        return items if len(items) <= 200 and all(isinstance(x, str) and _ID.fullmatch(x) for x in items) else []
    except (OSError, IOError, ValueError, TypeError, AttributeError):
        return []


def change(item_id):
    """Toggle one real Kodi-library identifier. No writes if identity is unclear."""
    if not isinstance(item_id, str) or not _ID.fullmatch(item_id):
        return None
    location = _location()
    if not location:
        return None
    path, scope = location
    items = read_list()
    if item_id in items:
        items.remove(item_id)
    elif len(items) < 200:
        items.append(item_id)
    else:
        return None
    temp = path + '.pending'
    try:
        folder = os.path.dirname(path)
        if not xbmcvfs.exists(folder) and not xbmcvfs.mkdirs(folder):
            return None
        with xbmcvfs.File(temp, 'w') as out:
            out.write(json.dumps({'schema': _KEY, 'scope_id': scope[2],
                                  'profile_label': scope[1], 'items': items}, separators=(',', ':')))
        os.replace(temp, path)
        return item_id in items
    except (OSError, IOError, ValueError, AttributeError):
        return None
