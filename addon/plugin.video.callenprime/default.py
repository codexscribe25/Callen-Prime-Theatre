"""CP02: offline, non-playable Kodi widget demonstrator."""
import os
import sys
import time
from urllib.parse import parse_qs, urlencode

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from resources.lib import fixtures, profile, rows

ADDON = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')
ROW_KEYS = fixtures.ROW_KEYS


def _link(base, **query):
    return base + '?' + urlencode(query)


def _entry(handle, url, label, is_folder=True, art=None, info=None):
    item = xbmcgui.ListItem(label=label)
    item.setProperty('IsPlayable', 'false')
    item.setProperty('CallenPrime.Demo', 'true')
    if art:
        item.setArt({'poster': art, 'thumb': art, 'icon': art})
    if info:
        item.setInfo('video', info)
    xbmcplugin.addDirectoryItem(handle, url, item, isFolder=is_folder)


def _root(handle, base):
    _entry(handle, _link(base, action='setup', preset='andy'), 'Activate ANDY demo in THIS Kodi profile')
    _entry(handle, _link(base, action='setup', preset='dad'), 'Activate DAD demo in THIS Kodi profile')
    _entry(handle, _link(base, action='status'), 'Check current profile isolation')
    for row in ROW_KEYS:
        _entry(handle, _link(base, row=row), '[CP02 DEMO] ' + fixtures.ROW_LABELS[row])
    _entry(handle, _link(base, row='frozen'), '[DIAGNOSTIC P0] Frozen Python widget')
    _entry(handle, _link(base, row='probe'), '[DIAGNOSTIC P1] Profile-aware comparison')


def _listing(handle, base, row):
    items = rows.listed_items(ADDON_PATH, row)
    for item in items[:fixtures.LIMIT]:
        art = os.path.join(ADDON_PATH, 'resources', 'media', item['art'])
        media_id = item['id']
        info = {
            'title': '[CP02 DEMO] ' + item['title'],
            'plot': '[CP02 DEMO: fictional content, no playback] ' + item.get('plot', ''),
            'mediatype': item['media_type'],
        }
        if isinstance(item.get('year'), int):
            info['year'] = item['year']
        _entry(handle, _link(base, action='details', row=row, item=media_id),
               '[CP02 DEMO] ' + item['title'], art=art, info=info)


def _message(title, message):
    xbmcgui.Dialog().ok(title, message)


def run(argv=None):
    argv = argv if argv is not None else sys.argv
    try:
        handle = int(argv[1])
        base = argv[0]
    except (IndexError, ValueError, TypeError):
        return
    started = time.monotonic()
    route_name = 'root'
    try:
        xbmcplugin.setContent(handle, 'videos')
        query = parse_qs((argv[2] if len(argv) > 2 else '').lstrip('?'), keep_blank_values=False)
        action = query.get('action', [''])[0]
        row = query.get('row', [''])[0]
        if row in ROW_KEYS + ('frozen', 'probe') and not action:
            route_name = row
            _listing(handle, base, row)
        elif action == 'setup':
            route_name = 'setup'
            preset = query.get('preset', [''])[0]
            success = profile.activate(ADDON_PATH, preset)
            _message('Callen Prime CP02',
                     'Demo activated for this Kodi profile.' if success else
                     'Profile scope ambiguous or unavailable. Neutral demo only. See setup guide.')
        elif action == 'status':
            route_name = 'status'
            scope = profile.current_scope()
            snapshot = profile.read_snapshot()
            # Never reveal profile paths in UI or logs.
            status = ('Profile scope: ' + ('verified' if scope else 'unavailable') +
                      '\nDemo preset: ' + (snapshot['preset'] if snapshot else 'neutral (safe fallback)'))
            _message('Callen Prime CP02', status)
        elif action == 'details':
            route_name = 'details'
            item = rows.find_item(ADDON_PATH, row, query.get('item', [''])[0])
            _message('CP02 DEMO: no playback',
                     (item['title'] + '\n' + item.get('plot', '') if item else 'Item unavailable in this profile.') +
                     '\nThis is fictional content. Nothing will play.')
        elif not action and not row:
            _root(handle, base)
        # Unknown queries intentionally yield an empty, successfully closed directory.
    except Exception as exc:
        # No user information or request arguments in logs.
        xbmc.log('[Callen Prime CP02] local listing failure: ' + type(exc).__name__, xbmc.LOGWARNING)
    finally:
        xbmcplugin.endOfDirectory(handle, succeeded=True, cacheToDisc=False)
        duration = (time.monotonic() - started) * 1000.0
        xbmc.log('[Callen Prime CP02] route=' + route_name + ' local_ms=' + ('%.2f' % duration), xbmc.LOGINFO)


if __name__ == '__main__':
    run()
