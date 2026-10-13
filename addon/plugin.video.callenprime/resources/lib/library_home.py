"""Small, synchronous, local-only Kodi library adapter for Callen Prime Theatre.

We never fetch recommendations from a server while moving between tiles. Kodi
owns all artwork and playable paths; Callen Prime owns presentation only.
"""
import json
import re

MAX_PER_LIBRARY = 80
MAX_RENDER = 10


def rpc(method, params=None):
    import xbmc
    request = {'jsonrpc': '2.0', 'method': method, 'id': 17}
    if params is not None:
        request['params'] = params
    try:
        response = json.loads(xbmc.executeJSONRPC(json.dumps(request)))
        result = response.get('result')
        return result if isinstance(result, dict) else {}
    except (ValueError, TypeError, AttributeError, RuntimeError):
        return {}


def _fetch(method, key, fields, limit):
    result = rpc(method, {'properties': fields,
                          'limits': {'start': 0, 'end': min(limit, MAX_PER_LIBRARY)}})
    items = result.get(key, [])
    return items if isinstance(items, list) else []


def _text(value, max_chars=220):
    return value[:max_chars].strip() if isinstance(value, str) else ''


def _poster(raw):
    art = raw.get('art') if isinstance(raw.get('art'), dict) else {}
    for key in ('poster', 'thumb', 'fanart'):
        value = art.get(key)
        if isinstance(value, str) and len(value) < 2048:
            return value
    thumb = raw.get('thumbnail')
    return thumb if isinstance(thumb, str) and len(thumb) < 2048 else ''


def _fanart(raw):
    art = raw.get('art') if isinstance(raw.get('art'), dict) else {}
    result = art.get('fanart')
    return result if isinstance(result, str) and len(result) < 2048 else _poster(raw)


def _tmdb(raw):
    ids = raw.get('uniqueid', {})
    value = ids.get('tmdb') if isinstance(ids, dict) else None
    if isinstance(value, (int, str)) and re.fullmatch(r'[1-9][0-9]{0,8}', str(value)):
        return str(value)
    return None


def _progress(raw):
    resume = raw.get('resume')
    if isinstance(resume, dict):
        try:
            position, total = float(resume.get('position', 0)), float(resume.get('total', 0))
            return max(0.0, min(1.0, position / total)) if total > 0 and position > 0 else 0.0
        except (ValueError, TypeError, ZeroDivisionError):
            pass
    return 0.0


def _entry(raw, kind):
    if not isinstance(raw, dict):
        return None
    id_key = {'movie': 'movieid', 'series': 'tvshowid', 'episode': 'episodeid'}[kind]
    identity = raw.get(id_key)
    if type(identity) is not int or identity < 0:
        return None
    title = _text(raw.get('title'), 110)
    if not title:
        return None
    genres = [x.strip() for x in raw.get('genre', []) if isinstance(x, str)] if isinstance(raw.get('genre'), list) else []
    details = raw.get('streamdetails') or {}
    tracks = details.get('audio', []) if isinstance(details, dict) else []
    languages = sorted({str(x.get('language','')).lower() for x in tracks if isinstance(x,dict) and x.get('language')}) if isinstance(tracks,list) else []
    return {'id': '{}:{}'.format(kind, identity), 'kodi_id': identity, 'kind': kind,
            'title': title, 'year': raw.get('year') if isinstance(raw.get('year'), int) else 0,
            'plot': _text(raw.get('plot'), 600), 'poster': _poster(raw), 'fanart': _fanart(raw),
            'file': _text(raw.get('file'), 2048), 'progress': _progress(raw),
            'watched': bool(raw.get('playcount', 0)), 'lastplayed': _text(raw.get('lastplayed'), 40),
            'dateadded': _text(raw.get('dateadded'), 40), 'genres': genres,
            'tmdb': _tmdb(raw), 'audio_languages': languages,
            'tvshowid': raw.get('tvshowid'), 'season': raw.get('season') if isinstance(raw.get('season'), int) else None,
            'episode': raw.get('episode') if isinstance(raw.get('episode'), int) else None}


def load_library():
    movie_fields = ['title', 'year', 'plot', 'art', 'thumbnail', 'genre', 'file',
                    'uniqueid', 'resume', 'playcount', 'lastplayed', 'dateadded']
    show_fields = ['title', 'year', 'plot', 'art', 'thumbnail', 'genre',
                   'uniqueid', 'playcount', 'lastplayed', 'dateadded']
    episode_fields = ['title', 'showtitle', 'year', 'plot', 'art', 'thumbnail',
                      'file', 'resume', 'playcount', 'lastplayed', 'dateadded', 'season', 'episode', 'tvshowid', 'streamdetails']
    movies = [_entry(x, 'movie') for x in _fetch('VideoLibrary.GetMovies', 'movies', movie_fields, 65)]
    shows = [_entry(x, 'series') for x in _fetch('VideoLibrary.GetTVShows', 'tvshows', show_fields, 45)]
    episodes = [_entry(x, 'episode') for x in _fetch('VideoLibrary.GetEpisodes', 'episodes', episode_fields, 45)]
    present_shows = {x['kodi_id']:x for x in shows if x}
    for ep in episodes:
        if ep and ep.get('tvshowid') in present_shows:
            show = present_shows[ep['tvshowid']]
            ep['genres'] = list(show['genres'])
    return [x for x in movies + shows + episodes if x]


def source_tiles():
    return [
        {'id': 'source:umbrella', 'kind': 'source', 'title': 'Umbrella', 'plot': 'Browse your installed Umbrella add-on.', 'poster': '', 'fanart': ''},
        {'id': 'source:fen', 'kind': 'source', 'title': 'Fen', 'plot': 'Browse your installed Fen add-on.', 'poster': '', 'fanart': ''},
        {'id': 'source:seren', 'kind': 'source', 'title': 'Seren', 'plot': 'Browse your installed Seren add-on.', 'poster': '', 'fanart': ''},
        {'id': 'action:library', 'kind': 'action', 'title': 'Your Kodi Library', 'plot': 'Add your films and programmes to the Kodi library for personalised rows.', 'poster': '', 'fanart': ''},
    ]


def unique(items, limit=MAX_RENDER):
    result, seen = [], set()
    for item in items:
        if item and item['id'] not in seen:
            seen.add(item['id'])
            result.append(item)
            if len(result) >= limit:
                break
    return result


def _recent(item):
    return item.get('dateadded') or ''


def _lastplayed(item):
    return item.get('lastplayed') or ''


def _unseen(items):
    return [x for x in items if not x['watched'] and x.get('progress', 0) <= 0]


def _genres(items):
    recent = sorted([x for x in items if x['lastplayed']], key=_lastplayed, reverse=True)[:8]
    favored = {}
    for x in recent:
        for genre in x.get('genres', []):
            name = genre.lower()
            if name:
                favored[name] = favored.get(name, 0) + 1
    return favored


def _anime(item):
    return any(('anime' in g.lower() or 'animation' in g.lower()) for g in item.get('genres', []))


def build_rows(items, tab='home', saved_ids=None):
    """Prepare stable, bounded rows once on opening/tab change, never per focus move."""
    saved_ids = set(saved_ids or [])
    movies = [x for x in items if x['kind'] == 'movie']
    series = [x for x in items if x['kind'] == 'series']
    episodes = [x for x in items if x['kind'] == 'episode']
    playable = movies + episodes
    genre_votes = _genres(items)
    based = sorted(_unseen(items), key=lambda x: (sum(genre_votes.get(g.lower(), 0) for g in x.get('genres', [])), _recent(x)), reverse=True)
    surprises = sorted(_unseen(items), key=lambda x: (sum(genre_votes.get(g.lower(), 0) for g in x.get('genres', [])), _recent(x)))
    latest = sorted(items, key=_recent, reverse=True)
    continuing = sorted([x for x in playable if x.get('progress', 0) > 0], key=_lastplayed, reverse=True)
    sources = source_tiles()
    if tab == 'home':
        rows = [('Continue Watching', continuing), ('What\'s New', latest),
                ('Because You Watched', based), ('Fresh for You', _unseen(latest)),
                ('Something Different', surprises), ('Your Sources', sources)]
    elif tab == 'movies':
        rows = [('Recently Added Films', sorted(movies, key=_recent, reverse=True)),
                ('Films You Haven\'t Seen', _unseen(movies)), ('Find a Film', sources)]
    elif tab == 'series':
        rows = [('Pick Up Your Episodes', [x for x in continuing if x['kind'] == 'episode']),
                ('Your Series', sorted(series, key=_recent, reverse=True)),
                ('Latest Episodes', sorted(episodes, key=_recent, reverse=True)),
                ('Find a Series', sources)]
    elif tab == 'anime':
        anime = [x for x in series + episodes if _anime(x)]
        dubbed = [x for x in anime if x['kind'] == 'episode' and
                  any(language in ('eng', 'en', 'english') for language in x.get('audio_languages', []))]
        rows = [('Anime in Your Library', anime),
                ('English Audio Confirmed', dubbed),
                ('Anime Episodes', [x for x in anime if x['kind'] == 'episode']),
                ('Browse Anime From a Source', sources)]
    elif tab == 'my-list':
        rows = [('Saved for Later', [x for x in items if x['id'] in saved_ids]),
                ('Explore', sources)]
    elif tab == 'sources':
        rows = [('Choose Your Provider', sources)]
    else:
        rows = [('Search Results', []), ('Browse Sources', sources)]
    populated = []
    for title, row_items in rows:
        content = unique(row_items)
        if content or title in ('Continue Watching', 'Saved for Later', 'Anime in Your Library'):
            populated.append((title, content))
    if not items and tab == 'home':
        populated = [('Start Watching', sources), ('Bring Your Library to Life', sources)]
    elif not populated:
        populated = [('Browse Your Sources', sources)]
    return populated


def search(items, phrase):
    words = _text(phrase, 70).lower().split()
    return unique([x for x in items if words and all(w in x['title'].lower() for w in words)], 30)


def episodes_for_series(tvshowid):
    if type(tvshowid) is not int or tvshowid < 0:
        return []
    response = rpc('VideoLibrary.GetEpisodes', {
        'tvshowid': tvshowid,
        'properties': ['title', 'file', 'resume', 'playcount', 'season', 'episode', 'art', 'thumbnail'],
        'limits': {'start': 0, 'end': 80},
        'sort': {'method': 'episode', 'order': 'ascending'}})
    return [entry for entry in (_entry(x, 'episode') for x in response.get('episodes', [])) if entry]
