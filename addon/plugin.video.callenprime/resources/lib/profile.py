"""Fail-closed, profile-scoped *fictional* fixture activation.

Kodi's profile name is not a globally unique identity. It is used only as an
additional guard against accidentally shared profile storage. Effective Kodi
special://profile path is the scope anchor; duplicate names fail closed.
"""
import hashlib
import json
import os

import xbmc
import xbmcvfs

from . import fixtures

SCHEMA = 'callenprime.cp02.snapshot.v1'
SNAPSHOT_FILE = 'demo_snapshot.json'
SNAPSHOT_LIMIT = 65536


def current_scope():
    """Return (resolved_profile_path, unique_label, digest) or None.

    Fail closed if Kodi profile metadata is not available, duplicate labels
    exist, or the effective path cannot be identified. No caller-supplied
    profile argument is used to select data.
    """
    try:
        path = xbmcvfs.translatePath('special://profile/')
        if not isinstance(path, str) or path.startswith('special://') or not os.path.isabs(path):
            return None
        path = os.path.normcase(os.path.normpath(os.path.realpath(path)))
        if not path or path == os.path.sep:
            return None
        current = json.loads(xbmc.executeJSONRPC(json.dumps({
            'jsonrpc': '2.0', 'method': 'Profiles.GetCurrentProfile', 'id': 1
        })))['result']
        all_profiles = json.loads(xbmc.executeJSONRPC(json.dumps({
            'jsonrpc': '2.0', 'method': 'Profiles.GetProfiles', 'id': 2
        })))['result']['profiles']
        label = current.get('label')
        labels = [p.get('label') for p in all_profiles]
        if not isinstance(label, str) or not label.strip() or labels.count(label) != 1:
            return None
        scope_id = hashlib.sha256(path.encode('utf-8')).hexdigest()
        return (path, label, scope_id)
    except (ValueError, KeyError, TypeError, OSError, AttributeError):
        return None


def _snapshot_path(scope):
    return os.path.join(scope[0], 'addon_data', 'plugin.video.callenprime', SNAPSHOT_FILE)


def read_snapshot():
    scope = current_scope()
    if scope is None:
        return None
    try:
        with xbmcvfs.File(_snapshot_path(scope), 'r') as handle:
            raw = handle.read(SNAPSHOT_LIMIT + 1)
            if len(raw) > SNAPSHOT_LIMIT:
                return None
            snapshot = json.loads(raw)
        if not isinstance(snapshot, dict) or snapshot.get('schema') != SCHEMA:
            return None
        if snapshot.get('scope_id') != scope[2] or snapshot.get('profile_label') != scope[1]:
            return None
        if snapshot.get('preset') not in ('andy', 'dad'):
            return None
        rows = snapshot.get('rows')
        if not isinstance(rows, dict) or set(rows) != set(fixtures.ROW_KEYS):
            return None
        for entries in rows.values():
            if not isinstance(entries, list) or len(entries) > fixtures.LIMIT:
                return None
            ids = []
            for item in entries:
                if not isinstance(item, dict) or not str(item.get('id', '')).startswith('demo:'):
                    return None
                if item.get('media_type') not in ('movie', 'episode') or not isinstance(item.get('title'), str):
                    return None
                if item.get('art') not in ('poster-a.png', 'poster-b.png', 'poster-c.png'):
                    return None
                ids.append(item['id'])
            if len(ids) != len(set(ids)):
                return None
        return snapshot
    except (OSError, IOError, ValueError, TypeError, AttributeError):
        return None


def activate(addon_path, preset):
    """One-time user-initiated fixture copy into *current* Kodi profile.

    No cached profile is retained across plugin invocations. No state is put in
    global special://userdata. A failed or ambiguous scope cannot activate.
    """
    if preset not in ('andy', 'dad'):
        return False
    scope = current_scope()
    if scope is None:
        return False
    try:
        rows = fixtures.load_rows(addon_path, preset)
        payload = {
            'schema': SCHEMA, 'scope_id': scope[2],
            'profile_label': scope[1], 'preset': preset, 'rows': rows
        }
        filename = _snapshot_path(scope)
        directory = os.path.dirname(filename)
        if not xbmcvfs.exists(directory) and not xbmcvfs.mkdirs(directory):
            return False
        temporary = filename + '.pending'
        with xbmcvfs.File(temporary, 'w') as handle:
            encoded = json.dumps(payload, sort_keys=True, separators=(',', ':'))
            if len(encoded) > SNAPSHOT_LIMIT:
                return False
            handle.write(encoded)
        # The translated special://profile path is local on supported Kodi
        # installations. Replace is atomic on the same filesystem.
        os.replace(temporary, filename)
        return True
    except (OSError, IOError, ValueError, TypeError, AttributeError):
        return False
