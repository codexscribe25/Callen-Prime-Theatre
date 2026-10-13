"""Small per-Kodi-profile opt-in state; never contains secrets or watch history."""
import json
import os

import xbmcvfs
from . import profile

PREF_FILE = 'cp04_provider_optin.json'
SCHEMA = 'callenprime.cp04.provider_optin.v1'
MAX_BYTES = 2048


def _file(scope):
    return os.path.join(scope[0], 'addon_data', 'plugin.video.callenprime', PREF_FILE)


def is_umbrella_enabled():
    scope = profile.current_scope()
    if not scope:
        return False
    try:
        with xbmcvfs.File(_file(scope), 'r') as file:
            raw = file.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            return False
        data = json.loads(raw)
        return (data.get('schema') == SCHEMA and data.get('scope_id') == scope[2]
                and data.get('profile_label') == scope[1] and data.get('umbrella') is True)
    except (ValueError, TypeError, OSError, IOError, AttributeError):
        return False


def set_umbrella_enabled(enabled):
    scope = profile.current_scope()
    if scope is None or not isinstance(enabled, bool):
        return False
    path = _file(scope)
    try:
        parent = os.path.dirname(path)
        if not xbmcvfs.exists(parent) and not xbmcvfs.mkdirs(parent):
            return False
        if not enabled:
            # Explicitly revoke opt-in, preserving no previous state.
            if xbmcvfs.exists(path):
                xbmcvfs.delete(path)
            return True
        payload = json.dumps({'schema': SCHEMA, 'scope_id': scope[2],
                              'profile_label': scope[1], 'umbrella': True},
                             separators=(',', ':'), sort_keys=True)
        if len(payload) > MAX_BYTES:
            return False
        # Never log contents. This is only a source-free opt-in flag.
        temp = path + '.pending'
        with xbmcvfs.File(temp, 'w') as file:
            file.write(payload)
        os.replace(temp, path)
        return True
    except (ValueError, TypeError, OSError, IOError, AttributeError):
        return False
