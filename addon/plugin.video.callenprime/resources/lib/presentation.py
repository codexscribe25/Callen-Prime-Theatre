"""Minimal, offline ten-foot metadata projection for CP03 demo entries.

All catalogue information is invented test data; nothing here asserts real audio,
ratings, availability or viewing history. No Kodi imports or network calls.
"""

KINDS = {'movie': 'Film', 'series': 'Series episode', 'anime': 'Anime episode'}


def media_kind(item):
    default = 'series' if item.get('media_type') == 'episode' else 'movie'
    value = item.get('media_kind', default)
    return value if value in KINDS else default


def runtime_label(item):
    value = item.get('runtime_minutes')
    if type(value) is not int or not 1 <= value <= 240:
        return 'Unknown'
    if value >= 60:
        hours, minutes = divmod(value, 60)
        return f'{hours}h {minutes}m' if minutes else f'{hours}h'
    return f'{value}m'


def detail_lines(item):
    if not item:
        return 'Item unavailable in this profile.\nNo playback is available.'
    year = item.get('year')
    year_text = str(year) if type(year) is int and 1900 <= year <= 2100 else 'Unknown'
    title = item.get('title', 'Untitled')
    kind = KINDS[media_kind(item)]
    return ('[CP03 DEMO: fictional metadata]\n' + str(title) + '\n' +
            f'{kind}  |  {year_text}  |  {runtime_label(item)}\n' +
            'Audio and dub information: Unknown (not verified)\n\n' +
            str(item.get('plot') or 'Description unavailable.') + '\n\nNo playback in this test build.')


def kodi_video_info(item):
    kind = media_kind(item)
    info = {
        'title': '[CP03 DEMO] ' + str(item.get('title', 'Untitled')),
        'plot': '[CP03 DEMO: fictional title and metadata, no playback] ' + str(item.get('plot') or 'Description unavailable.'),
        'mediatype': item.get('media_type', 'movie'),
        'genre': KINDS[kind] + ' (DEMO)',
    }
    year = item.get('year')
    if type(year) is int and 1900 <= year <= 2100:
        info['year'] = year
    runtime = item.get('runtime_minutes')
    if type(runtime) is int and 1 <= runtime <= 240:
        info['duration'] = runtime * 60
    return info
