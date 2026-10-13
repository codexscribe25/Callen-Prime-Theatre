"""Provider status and guarded, explicitly initiated Umbrella handoff.

Provider routes are source-derived, not Kodi public APIs. Only the pinned
Umbrella version was inspected for CP04. Never import another add-on's modules,
read its tokens, fetch sources, or silently switch providers.
"""
import json
import re
from urllib.parse import urlencode

import xbmc

UMBRELLA_ID = 'plugin.video.umbrella'
UMBRELLA_VERIFIED_VERSION = '6.7.90'
PENDING = {'fen': 'Version-specific contract unverified',
           'seren': 'Version-specific contract unverified'}


def installed_provider(addon_id):
    """Read only Kodi metadata. Fail closed if enabled/version is unknown."""
    if addon_id not in (UMBRELLA_ID, 'plugin.video.fen', 'plugin.video.seren'):
        return None
    request = {'jsonrpc': '2.0', 'id': 4,
               'method': 'Addons.GetAddonDetails',
               'params': {'addonid': addon_id, 'properties': ['version', 'enabled', 'installed']}}
    try:
        payload = json.loads(xbmc.executeJSONRPC(json.dumps(request)))
        data = payload.get('result', {}).get('addon', {})
        if data.get('addonid') != addon_id or data.get('enabled') is not True or data.get('installed') is not True:
            return None
        version = data.get('version')
        if not isinstance(version, str) or not re.fullmatch(r'[0-9A-Za-z._+-]{1,40}', version):
            return None
        return {'id': addon_id, 'version': version}
    except (ValueError, TypeError, AttributeError, KeyError):
        return None


def umbrella_available():
    info = installed_provider(UMBRELLA_ID)
    return info is not None and info['version'] == UMBRELLA_VERIFIED_VERSION


def validate_title(title):
    if not isinstance(title, str) or not 1 <= len(title.strip()) <= 100:
        return None
    title = title.strip()
    # Kodi input can be arbitrary; restrict control characters and url syntax.
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in title) or any(x in title for x in ('<', '>', '{', '}', '|', '\\')):
        return None
    return title


def validate_tmdb(value):
    if not isinstance(value, str) or not re.fullmatch(r'[1-9][0-9]{0,8}', value):
        return None
    return value


def validate_year(value):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9]{4}', value):
        return None
    n = int(value)
    return str(n) if 1888 <= n <= 2100 else None


def validate_episode_num(value, start):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9]{1,3}', value):
        return None
    n = int(value)
    return str(n) if start <= n <= 999 else None


def umbrella_url(kind, title, tmdb, year, season=None, episode=None):
    """Construct exactly one whitelisted URL from manually supplied catalogue metadata.

    This matches Umbrella 6.7.90 router.py `action=play_Item` field names.
    Actual nested resolution is DEVICE-PENDING until witnessed on Kodi 21.3.
    """
    if kind not in ('movie', 'episode'):
        return None
    title = validate_title(title)
    tmdb = validate_tmdb(tmdb)
    year = validate_year(year)
    if not all((title, tmdb, year)):
        return None
    parts = {'action': 'play_Item', 'title': title, 'year': year,
             'tmdb': tmdb, 'meta': json.dumps({
                 'title': title, 'year': int(year), 'tmdb': tmdb,
                 'mediatype': kind}, separators=(',', ':'))}
    if kind == 'episode':
        season = validate_episode_num(season, 0)
        episode = validate_episode_num(episode, 1)
        if season is None or episode is None:
            return None
        parts.update({'tvshowtitle': title, 'season': season, 'episode': episode})
    return 'plugin://' + UMBRELLA_ID + '/?' + urlencode(parts)


def choose_umbrella_target(dialog):
    """User must manually enter a real media identity; no fake/demo IDs."""
    kind_index = dialog.select('What would you like to play?', ['Movie', 'Episode'])
    if kind_index not in (0, 1):
        return None
    kind = ('movie', 'episode')[kind_index]
    title = dialog.input('Film title' if kind == 'movie' else 'Series title')
    if not validate_title(title):
        return None
    tmdb = dialog.input('TMDb film ID' if kind == 'movie' else 'TMDb series ID')
    if not validate_tmdb(tmdb):
        dialog.ok('Unsupported identifier', 'Enter an actual numeric TMDb ID for the selected title.')
        return None
    year = dialog.input('Release year (four digits)')
    if not validate_year(year):
        return None
    season = episode = None
    if kind == 'episode':
        season = dialog.input('Season number')
        episode = dialog.input('Episode number')
    url = umbrella_url(kind, title, tmdb, year, season, episode)
    if not url:
        dialog.ok('Playback not available', 'Required media details are invalid or incomplete.')
        return None
    if not dialog.yesno('Hand off to Umbrella?',
                        'Umbrella will choose sources and handle playback. Continue?'):
        return None
    return url
