"""CP04: stable offline widgets plus explicit, guarded Kodi playback tests."""
import os
import sys
import time
from urllib.parse import parse_qs, urlencode

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from resources.lib import fixtures, playback, presentation, profile, provider_prefs, providers, rows, sections

ADDON = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')
ROW_KEYS = fixtures.ROW_KEYS


def _link(base, **query):
    return base + '?' + urlencode(query)


def _entry(handle, url, label, is_folder=True, art=None, info=None, media_kind=None, playable=False):
    item = xbmcgui.ListItem(label=label)
    item.setProperty('IsPlayable', 'true' if playable else 'false')
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
    _entry(handle, _link(base, action='my-list'), 'My List (not connected in CP04)')
    _entry(handle, _link(base, action='playback-lab'), 'Playback Tests (CP04)')
    _entry(handle, _link(base, action='setup', preset='andy'), 'Activate ANDY demo in THIS Kodi profile')
    _entry(handle, _link(base, action='setup', preset='dad'), 'Activate DAD demo in THIS Kodi profile')
    _entry(handle, _link(base, action='status'), 'Check current profile isolation')
    for row in ROW_KEYS:
        _entry(handle, _link(base, row=row), '[CP03 DEMO] ' + fixtures.ROW_LABELS[row])
    _entry(handle, _link(base, row='frozen'), '[DIAGNOSTIC P0] Frozen Python widget')
    _entry(handle, _link(base, row='probe'), '[DIAGNOSTIC P1] Profile-aware comparison')



def _playback_lab(handle, base):
    """The only place that probes provider installation, and only on request."""
    _entry(handle, _link(base, action='play-local'), 'Play a local test video',
           is_folder=False, playable=True)
    state = providers.installed_provider(providers.UMBRELLA_ID)
    if not state:
        _entry(handle, _link(base, action='provider-info'), 'Umbrella not installed or disabled')
    elif state['version'] != providers.UMBRELLA_VERIFIED_VERSION:
        _entry(handle, _link(base, action='provider-info'),
               'Umbrella version unsupported for CP04 (no automatic handoff)')
    elif provider_prefs.is_umbrella_enabled():
        _entry(handle, _link(base, action='play-umbrella'),
               'Play a title using Umbrella (manual media ID)', is_folder=False, playable=True)
        _entry(handle, _link(base, action='disable-umbrella'), 'Disable Umbrella in Callen Prime')
    else:
        _entry(handle, _link(base, action='enable-umbrella'),
               'Enable Umbrella for this Kodi profile (opt-in)')
    _entry(handle, _link(base, action='provider-info'), 'Fen and Seren: not enabled in CP04')


def _launch_guard():
    """Deter double presses without polling or holding a global player monitor."""
    scope = profile.current_scope()
    if scope is None:
        return False
    window = xbmcgui.Window(10000)
    key = 'CallenPrime.CP04.Launch.' + scope[2][:24]
    now = time.monotonic()
    try:
        last = float(window.getProperty(key) or '0')
        if 0 <= now - last < 2.5:
            return False
        window.setProperty(key, str(now))
        return True
    except (ValueError, TypeError, AttributeError):
        return False


def _playback_target(action):
    dialog = xbmcgui.Dialog()
    if action == 'play-local':
        chosen = playback.select_local_video(dialog)
        return chosen if chosen and _launch_guard() else None
    if action == 'play-umbrella':
        if not provider_prefs.is_umbrella_enabled() or not providers.umbrella_available():
            dialog.ok('Provider unavailable',
                      'Enable the verified Umbrella version for this Kodi profile in Playback Tests.')
            return None
        result = providers.choose_umbrella_target(dialog)
        if result is None:
            return None
        if not _launch_guard():
            return None
        return result
    return None

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
    query = parse_qs((argv[2] if len(argv) > 2 else '').lstrip('?'), keep_blank_values=True)
    action = query.get('action', [''])[0]
    row = query.get('row', [''])[0]
    section = query.get('section', [''])[0]
    is_playback = action in ('play-local', 'play-umbrella')
    playback_path = None
    try:
        if is_playback:
            route_name = 'playback'  # Never write selected paths/IDs to log.
            # No url, profile, item or hidden caller parameters can start playback.
            if set(query) == {'action'} and len(query['action']) == 1:
                playback_path = _playback_target(action)
        else:
            xbmcplugin.setContent(handle, 'videos')
            if row in ROW_KEYS + ('frozen', 'probe') and not action and not section:
                route_name = row
                _listing(handle, base, row)
            elif section in sections.SECTION_LABELS and not action and not row:
                route_name = 'section'
                _section(handle, base, section)
            elif action == 'playback-lab' and not row and not section and set(query) == {'action'}:
                route_name = 'playback-lab'
                _playback_lab(handle, base)
            elif action == 'enable-umbrella' and not row and not section and set(query) == {'action'}:
                route_name = 'provider-setting'
                if providers.umbrella_available() and xbmcgui.Dialog().yesno(
                        'Enable Umbrella?', 'Allow manual playback handoff for this Kodi profile?'):
                    result = provider_prefs.set_umbrella_enabled(True)
                    _message('Callen Prime CP04', 'Umbrella enabled.' if result else 'Profile scope unavailable.')
            elif action == 'disable-umbrella' and not row and not section and set(query) == {'action'}:
                route_name = 'provider-setting'
                _message('Callen Prime CP04', 'Umbrella disabled.' if provider_prefs.set_umbrella_enabled(False)
                         else 'Could not change preference for this Kodi profile.')
            elif action == 'provider-info' and not row and not section and set(query) == {'action'}:
                route_name = 'provider-info'
                _message('Provider status', 'Umbrella is the only conditional CP04 handoff. '
                         'Fen and Seren routes have not passed compatibility checks.')
            elif action == 'setup' and not row and not section:
                route_name = 'setup'
                preset = query.get('preset', [''])[0]
                success = profile.activate(ADDON_PATH, preset)
                _message('Callen Prime CP04',
                         'Demo activated for this Kodi profile.' if success else
                         'Profile scope ambiguous or unavailable. Neutral demo only. See setup guide.')
            elif action == 'status' and not row and not section:
                route_name = 'status'
                scope = profile.current_scope()
                snapshot = profile.read_snapshot()
                status = ('Profile scope: ' + ('verified' if scope else 'unavailable') +
                          '\nDemo preset: ' + (snapshot['preset'] if snapshot else 'neutral (safe fallback)'))
                _message('Callen Prime CP04', status)
            elif action == 'my-list' and not row and not section:
                route_name = 'my-list'
                _message('My List is not connected',
                         'CP04 still uses a fictional demo catalogue. Personal lists and Trakt are not active.')
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
        # No profile paths, user input or selected media identifiers in logs.
        xbmc.log('[Callen Prime CP04] local action failure: ' + type(exc).__name__, xbmc.LOGWARNING)
    finally:
        if is_playback:
            # These are resolvable items, *not* directory listings.
            item = xbmcgui.ListItem(path=playback_path or '')
            xbmcplugin.setResolvedUrl(handle, bool(playback_path), item)
        else:
            xbmcplugin.endOfDirectory(handle, succeeded=True, cacheToDisc=False)
        duration = (time.monotonic() - started) * 1000.0
        xbmc.log('[Callen Prime CP04] route=' + route_name + ' local_ms=' + ('%.2f' % duration), xbmc.LOGINFO)


if __name__ == '__main__':
    run()
