"""Full-screen Kodi-native theatre UI. No skin fork, webview or background worker.

Built on WindowXMLDialog so ordinary Kodi skins, sources, subtitles and player
remain untouched. Work happens on open/explicit refresh only, not remote focus.
"""
import os

import xbmc
import xbmcgui

from . import library_home, theatre_state, providers, provider_prefs

TABS = {100: 'home', 101: 'movies', 102: 'series', 103: 'anime',
        104: 'my-list', 105: 'search', 106: 'sources', 107: 'settings'}
SOURCES = {
    'source:umbrella': ('plugin.video.umbrella', 'Umbrella'),
    'source:fen': ('plugin.video.fen', 'Fen'),
    'source:seren': ('plugin.video.seren', 'Seren'),
    'source:fenlight': ('plugin.video.fenlight', 'Fen Light'),
}
KEY_BACK = frozenset((9, 10, 92, 216, 247, 275))  # Kodi BACK / ESC / previous menu
KEY_DOWN = frozenset((4,))
KEY_UP = frozenset((3,))


def media_asset(addonpath, name):
    return os.path.join(addonpath, 'resources', 'skins', 'Default', 'media', name)


def art_for(addonpath, entry):
    if entry.get('poster'):
        return entry['poster']
    name = {'source:umbrella': 'poster-umbrella.jpg',
            'source:fen': 'poster-fen.jpg', 'source:seren': 'poster-seren.jpg',
            'source:fenlight': 'poster-fen.jpg',
            'action:library': 'poster-library.jpg'}.get(entry['id'], 'poster-default.jpg')
    return media_asset(addonpath, name)


def _subtitle(entry):
    kind = entry.get('kind', 'film')
    category = {'movie': 'FILM', 'series': 'SERIES', 'episode': 'EPISODE',
                'source': 'CONNECTED SOURCE', 'action': 'YOUR LIBRARY'}.get(kind, kind.upper())
    year = entry.get('year')
    if type(year) is int and year > 0:
        category += '  /  ' + str(year)
    progress = entry.get('progress', 0)
    if progress > 0:
        category += '  /  {}% WATCHED'.format(int(progress * 100))
    return category


def _safe_name(entry):
    return entry.get('title', 'Untitled')[:110]


class DetailsWindow(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entry = None
        self.saved = False
        self.choice = None

    def onInit(self):
        entry = self.entry or {}
        self.setProperty('cp.details.art', self.artwork)
        self.setProperty('cp.details.title', _safe_name(entry))
        self.setProperty('cp.details.meta', _subtitle(entry))
        self.setProperty('cp.details.plot', entry.get('plot') or 'Details are not available yet.')
        self.setProperty('cp.details.play', 'OPEN SOURCE' if entry.get('kind') in ('source', 'action') else 'PLAY / EPISODES')
        self.setProperty('cp.details.save', 'REMOVE FROM MY LIST' if self.saved else 'ADD TO MY LIST')
        if entry.get('kind') in ('source', 'action'):
            self.setProperty('cp.details.save', 'NOT AVAILABLE')
        self.setFocusId(501)

    def onClick(self, controlId):
        if controlId == 501:
            self.choice = 'play'
            self.close()
        elif controlId == 502:
            if self.entry and self.entry.get('kind') not in ('source', 'action'):
                self.choice = 'save'
                self.close()
        elif controlId == 503:
            self.close()

    def onAction(self, action):
        if action.getId() in KEY_BACK:
            self.close()


class TheatreWindow(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addonpath = ''
        self.catalogue = []
        self.rows = []
        self.page = 0
        self.tab = 'home'
        self.selection = {}
        self.exit_to_source = None
        self.hero = None
        self.search_text = ''

    def onInit(self):
        try:
            from . import profile
            scope = profile.current_scope()
            self.setProperty('cp.profile', 'PROFILE  /  ' + (scope[1].upper()[:25] if scope else 'KODI PROFILE'))
            self.setProperty('cp.mode', 'KODI LOCAL  /  NO AUTOPLAY')
            self.catalogue = library_home.load_library()
            self._tab('home', focus=False)
            self.setFocusId(100)
        except Exception as error:
            xbmc.log('[Callen Prime Theatre] start failure: ' + type(error).__name__, xbmc.LOGWARNING)
            self.setProperty('cp.title', 'CALLEN PRIME')
            self.setProperty('cp.plot', 'Library unavailable. Open SOURCES to find something to watch.')
            self._tab('sources', focus=False)

    def _tab(self, tab, focus=True):
        self.tab = tab
        self.page = 0
        if tab == 'search':
            self.rows = [('Search: ' + (self.search_text or 'No query'),
                          library_home.search(self.catalogue, self.search_text)),
                         ('Browse From Sources', library_home.source_tiles())]
        else:
            self.rows = library_home.build_rows(self.catalogue, tab, theatre_state.read_list())
        self._show_page()
        if focus:
            self.setFocusId(301)

    def _to_gui_item(self, entry):
        item = xbmcgui.ListItem(label=_safe_name(entry), offscreen=True)
        item.setArt({'poster': art_for(self.addonpath, entry),
                     'thumb': art_for(self.addonpath, entry),
                     'fanart': entry.get('fanart') or media_asset(self.addonpath, 'hero-placeholder.jpg')})
        item.setProperty('cp.identity', entry['id'])
        item.setProperty('cp.mediatype', entry.get('kind', ''))
        return item

    def _show_page(self):
        total = len(self.rows)
        self.selection = {}
        for slot, control_id in enumerate((301, 302)):
            index = self.page + slot
            title, items = self.rows[index] if index < total else ('', [])
            ctl = self.getControl(control_id)
            ctl.reset()
            if not items and title:
                items = [{'id': 'action:library', 'kind': 'action',
                          'title': 'Browse your Kodi library', 'plot': 'Your library has no entries for this row yet.'}]
            for item in items:
                self.selection[item['id']] = item
            if items:
                ctl.addItems([self._to_gui_item(x) for x in items])
            self.setProperty('cp.row{}'.format(slot), title)
        self.setProperty('cp.page', 'ROW {}-{} / {}'.format(min(self.page+1,total), min(self.page+2,total),total))
        first = next((x for _, items in self.rows[self.page:self.page+2] for x in items), None)
        if not first:
            first = library_home.source_tiles()[0]
        self._set_hero(first)

    def _set_hero(self, entry):
        self.hero = entry
        self.setProperty('cp.title', _safe_name(entry).upper())
        self.setProperty('cp.eyebrow', _subtitle(entry))
        self.setProperty('cp.plot', entry.get('plot') or 'Movies, series and anime in one place. Your own sources, your choice.')
        self.setProperty('cp.heroart', entry.get('fanart') or media_asset(self.addonpath,'hero-placeholder.jpg'))

    def _selected(self, control_id):
        try:
            item = self.getControl(control_id).getSelectedItem()
            return self.selection.get(item.getProperty('cp.identity')) if item else None
        except (AttributeError, RuntimeError, ValueError):
            return None

    def _details(self, entry):
        if not entry:
            return
        dialog = DetailsWindow('CallenPrimeDetails.xml', self.addonpath, 'Default', '1080i')
        dialog.entry = entry
        dialog.artwork = art_for(self.addonpath, entry)
        dialog.saved = entry['id'] in theatre_state.read_list()
        dialog.doModal()
        choice = dialog.choice
        del dialog
        if choice == 'save':
            change = theatre_state.change(entry['id'])
            if change is None:
                xbmcgui.Dialog().ok('My List unavailable', 'Use distinct Kodi profiles to keep personal lists separate.')
            self._tab(self.tab, focus=True)
        elif choice == 'play':
            self._play(entry)

    def _play(self, entry):
        if entry.get('kind') in ('source', 'action'):
            self._open_source(entry['id'])
            return
        if entry.get('kind') == 'series':
            episodes = library_home.episodes_for_series(entry['kodi_id'])
            if not episodes:
                xbmcgui.Dialog().ok('No episodes in Kodi library', 'Add the episodes to Kodi or browse an installed source.')
                return
            labels = ['S{:02d} E{:02d}  {}'.format(e.get('season') or 0, e.get('episode') or 0, e['title']) for e in episodes]
            index = xbmcgui.Dialog().select(entry['title'] + ' | Episodes', labels)
            if index < 0:
                return
            entry = episodes[index]
        location = entry.get('file')
        if isinstance(location, str) and location and len(location) < 2048:
            # Path comes directly from Kodi's own authorised VideoLibrary.
            xbmc.Player().play(location)
            return
        # Conditional fallback to the CP04 reviewed Umbrella contract, only on
        # explicit opt-in and with verified real TMDb identity.
        if entry.get('kind') == 'movie' and provider_prefs.is_umbrella_enabled() and providers.umbrella_available():
            url = providers.umbrella_url('movie', entry['title'], entry.get('tmdb'), str(entry.get('year', '')))
            if url and xbmcgui.Dialog().yesno('Play through Umbrella?', 'Let Umbrella find the source for this film?'):
                xbmc.Player().play(url)
                return
        xbmcgui.Dialog().ok('Playback not ready', 'This item does not have a playable Kodi library file. Try SOURCES to browse your installed add-ons.')

    def _open_source(self, identity):
        if identity == 'action:library':
            self.exit_to_source = 'kodi-library'
            self.close()
            return
        setting = SOURCES.get(identity)
        if not setting:
            return
        addon_id, name = setting
        try:
            result = library_home.rpc('Addons.GetAddonDetails', {'addonid': addon_id, 'properties': ['enabled', 'installed']})
            details = result.get('addon', {})
            if details.get('enabled') is not True or details.get('installed') is not True:
                xbmcgui.Dialog().ok(name + ' not installed', 'Install or enable it in Kodi Add-ons, then return here.')
                return
        except (AttributeError, ValueError, TypeError):
            xbmcgui.Dialog().ok('Source unavailable', 'Kodi could not confirm that this add-on is enabled.')
            return
        self.exit_to_source = identity
        self.close()

    def _settings(self):
        choices = ['Refresh my Kodi library', 'Play a local test video',
                   'Trakt and watch history', 'Switch Kodi profile',
                   'Make Callen Prime easy to launch', 'About this build']
        selected = xbmcgui.Dialog().select('Callen Prime | Settings', choices)
        if selected == 0:
            self.catalogue = library_home.load_library()
            self._tab(self.tab, focus=False)
        elif selected == 1:
            from .playback import select_local_video
            video = select_local_video(xbmcgui.Dialog())
            if video:
                xbmc.Player().play(video)
        elif selected == 2:
            xbmcgui.Dialog().ok('Trakt', 'Callen Prime can use the watched state in your Kodi library. Trakt authentication remains in your existing add-on. Direct Trakt login is not active in this build.')
        elif selected == 3:
            xbmcgui.Dialog().ok('Separate viewer profiles', 'Kodi Settings → Profiles controls viewer separation. Exit Callen Prime to switch. The theatre follows the active Kodi profile.')
        elif selected == 4:
            xbmcgui.Dialog().ok('Launch directly', 'Add Callen Prime Theatre to Kodi Favourites, then pin the favourite on your skin Home. Nothing will change your Kodi skin automatically.')
        elif selected == 5:
            xbmcgui.Dialog().ok('Callen Prime Theatre', 'Theatre Build 0.5.1 • fullscreen Kodi-native interface. Real Kodi library content, local recommendations, profile watchlists and your installed playback sources. Fire Stick testing pending.')

    def onClick(self, controlId):
        if controlId in TABS:
            tab = TABS[controlId]
            if tab == 'settings':
                self._settings()
            elif tab == 'search':
                typed = xbmcgui.Dialog().input('Search your Kodi library', self.search_text)
                if typed is not None:
                    self.search_text = typed[:70]
                    self._tab('search')
            else:
                self._tab(tab)
        elif controlId == 108:
            self.close()
        elif controlId == 120:
            self._details(self.hero)
        elif controlId == 121:
            self._tab('sources')
        elif controlId in (301, 302):
            self._details(self._selected(controlId))

    def onFocus(self, controlId):
        if controlId in (301, 302):
            chosen = self._selected(controlId)
            if chosen:
                self._set_hero(chosen)

    def onAction(self, action):
        key = action.getId()
        if key in KEY_BACK:
            self.close()
            return
        try:
            control = self.getFocusId()
        except (RuntimeError, AttributeError):
            return
        if key in KEY_DOWN and control == 302 and self.page+2 < len(self.rows):
            self.page += 2
            self._show_page()
            self.setFocusId(301)
        elif key in KEY_UP and control == 301 and self.page > 0:
            self.page = max(0, self.page - 2)
            self._show_page()
            self.setFocusId(302)
        elif control in (301, 302):
            chosen = self._selected(control)
            if chosen:
                self._set_hero(chosen)


def launch(addonpath):
    """Entry from Kodi Program add-on or the existing video add-on's first item."""
    window = TheatreWindow('CallenPrimeTheatre.xml', addonpath, 'Default', '1080i')
    window.addonpath = addonpath
    window.doModal()
    target = window.exit_to_source
    del window
    if target == 'kodi-library':
        xbmc.executebuiltin('ActivateWindow(Videos,library://video/,return)')
    elif target in SOURCES:
        # Static, validated addon IDs only; the user chooses the addon.
        addon_id = SOURCES[target][0]
        xbmc.executebuiltin('ActivateWindow(Videos,plugin://{}/,return)'.format(addon_id))
