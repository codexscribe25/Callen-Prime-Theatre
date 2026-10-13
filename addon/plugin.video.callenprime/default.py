"""CP03: five offline, non-playing Kodi rows and a safe theatre demo shell."""
import os
import sys
import time
from urllib.parse import parse_qs, urlencode

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from resources.lib import fixtures, presentation, profile, rows, sections

ADDON = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')
ROW_KEYS = fixtures.ROW_KEYS


def _link(base, **query):
    return base + '?' + urlencode(query)


def _entry(handle, url, label, is_folder=True, art=None, info=None, media_kind=None):
    item = xbmcgui.ListItem(label=label)
    item.setProperty('IsPlayable', 'false')
    item.setProperty('CallenPrime.Demo', 'true')
    item.setProperty('CallenPrime.LanguageStatus', 'unknown')
    if media_kind:
        item.setProperty('CallenPrime.MediaKind', media_kind)
    if art:
        item.setArt({'poster': art, 'thumb': art, 'icon': art})
    if info:
        item.setInfo('video', info)
    xbmcplugin.addDirectoryItem(handle, url, item, isFolder=is_folder)


def _root(handle, base):
    # Each is a safe, ordinary Kodi folder. Stock Nimbus owns the real Home UI.
    for section, label in sections.SECTION_LABELS.items():
        _entry(handle, _link(base, section=section), label + ' (fictional demo)')
    _entry(handle, _link(base, action='my-list'), 'My List (not connected in CP03)')
    _entry(handle, _link(base, action='setup', preset='andy'), 'Activate ANDY demo in THIS Kodi profile')
    _entry(handle, _link(base, action='setup', preset='dad'), 'Activate DAD demo in THIS Kodi profile')
    _entry(handle, _link(base, action='status'), 'Check current profile isolation')
    for row in ROW_KEYS:
        _entry(handle, _link(base, row=row), '[CP03 DEMO] ' + fixtures.ROW_LABELS[row])
    _entry(handle, _link(base, row='frozen'), '[DIAGNOSTIC P0] Frozen Python widget')
    _entry(handle, _link(base, row='probe'), '[DIAGNOSTIC P1] Profile-aware comparison')


def _render_items(handle, base, items, *, row=None, section=None):
    # Keep order unchanged so the native Kodi widget can preserve its focus.
    for item in items[:fixtures.LIMIT]:
        art = os.path.join(ADDON_PATH, 'resources', 'media', item['art'])
        query = {'action': 'details', 'item': item['id']}
        if row is not None:
            query['row'] = row
        else:
            query['section'] = section
        _entry(handle, _link(base, **query), '[CP03 DEMO] ' + item['title'],
               art=art, info=presentation.kodi_video_info(item),
               media_kind=presentation.media_kind(item))


def _listing(handle, base, row):
    _render_items(handle, base, rows.listed_items(ADDON_PATH, row), row=row)


def _section(handle, base, section):
    _render_items(handle, base, sections.listed_items(ADDON_PATH, section), section=section)


def _message(title, message):
    # A Kodi modal keeps the current item visible underneath on supported skins;
    # exact focus restoration still requires a real remote acceptance test.
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
        section = query.get('section', [''])[0]
        if row in ROW_KEYS + ('frozen', 'probe') and not action and not section:
            route_name = row
            _listing(handle, base, row)
        elif section in sections.SECTION_LABELS and not action and not row:
            route_name = 'section'
            _section(handle, base, section)
        elif action == 'setup' and not row and not section:
            route_name = 'setup'
            preset = query.get('preset', [''])[0]
            success = profile.activate(ADDON_PATH, preset)
            _message('Callen Prime CP03',
                     'Demo activated for this Kodi profile.' if success else
                     'Profile scope ambiguous or unavailable. Neutral demo only. See setup guide.')
        elif action == 'status' and not row and not section:
            route_name = 'status'
            scope = profile.current_scope()
            snapshot = profile.read_snapshot()
            status = ('Profile scope: ' + ('verified' if scope else 'unavailable') +
                      '\nDemo preset: ' + (snapshot['preset'] if snapshot else 'neutral (safe fallback)'))
            _message('Callen Prime CP03', status)
        elif action == 'my-list' and not row and not section:
            route_name = 'my-list'
            _message('My List is not connected',
                     'CP03 is an offline, fictional demo. Personal lists and Trakt are not active.')
        elif action == 'details':
            route_name = 'details'
            media_id = query.get('item', [''])[0]
            item = (rows.find_item(ADDON_PATH, row, media_id) if row in ROW_KEYS + ('frozen', 'probe') and not section
                    else sections.find_item(ADDON_PATH, section, media_id) if section in sections.SECTION_LABELS and not row
                    else None)
            _message('Callen Prime | Title Details (No Playback)', presentation.detail_lines(item))
        elif not action and not row and not section:
            _root(handle, base)
        # Unknown queries intentionally yield an empty successfully closed directory.
    except Exception as exc:
        # No user information or request arguments in logs.
        xbmc.log('[Callen Prime CP03] local listing failure: ' + type(exc).__name__, xbmc.LOGWARNING)
    finally:
        xbmcplugin.endOfDirectory(handle, succeeded=True, cacheToDisc=False)
        duration = (time.monotonic() - started) * 1000.0
        xbmc.log('[Callen Prime CP03] route=' + route_name + ' local_ms=' + ('%.2f' % duration), xbmc.LOGINFO)


if __name__ == '__main__':
    run()
