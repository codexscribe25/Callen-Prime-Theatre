"""Real product-contract tests. These do not impersonate physical Fire TV acceptance."""
import importlib
import json
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from unittest.mock import patch

from .common import KodiHarness, ADDON


class TheatreProductTests(unittest.TestCase):
    def test_packaged_fullscreen_xml_and_texture_paths(self):
        skin = ADDON / 'resources/skins/Default'
        for name in ('CallenPrimeTheatre.xml', 'CallenPrimeDetails.xml'):
            root = ET.parse(skin / '1080i' / name).getroot()
            self.assertEqual(root.tag, 'window')
            self.assertIn('defaultcontrol', {x.tag for x in root})
            self.assertGreater(len(root.findall('.//control')), 8)
            text = (skin/'1080i'/name).read_text()
            self.assertIn('background.jpg', text)
            self.assertNotIn('ReloadSkin',text)
        for texture in ('background.jpg', 'hero-placeholder.jpg', 'focus.png', 'poster-library.jpg'):
            self.assertTrue((skin / 'media' / texture).is_file())

    def test_manifest_retains_original_plugin_and_adds_theatre_script(self):
        manifest = ET.parse(ADDON/'addon.xml').getroot()
        self.assertEqual(manifest.attrib['version'], '0.5.0')
        ext = {x.attrib['point']:x for x in manifest.findall('extension')}
        self.assertEqual(ext['xbmc.python.pluginsource'].attrib['library'],'default.py')
        self.assertEqual(ext['xbmc.python.script'].attrib['library'],'theatre.py')
        self.assertNotIn('xbmc.service',ext)

    def test_root_prominently_opens_theatre_without_playing(self):
        with KodiHarness() as k:
            entries = k.call('')
            self.assertEqual(entries[0][1].label,'OPEN CALLEN PRIME THEATRE')
            self.assertEqual(entries[0][1].properties['IsPlayable'],'false')
            self.assertIn('action=launch-theatre', entries[0][0])
            self.assertFalse(k.resolved)

    def test_real_media_normalisation(self):
        with KodiHarness():
            from resources.lib import library_home as l
            movie = l._entry({'movieid':3,'title':'A real Kodi title', 'year':2024,
                              'resume':{'position':15,'total':60},'genre':['Drama'],
                              'file':'/media/film.mkv','uniqueid':{'tmdb':'123'},
                              'dateadded':'2026-10-01'},'movie')
            self.assertEqual(movie['id'],'movie:3')
            self.assertEqual(movie['progress'],.25)
            self.assertEqual(movie['tmdb'],'123')
            self.assertTrue(movie['file'].endswith('.mkv'))
            self.assertIsNone(l._entry({'movieid':'unsafe','title':'Film'},'movie'))
            self.assertIsNone(l._entry({'movieid':1,'title':''},'movie'))
            self.assertIsNone(l._tmdb({'uniqueid':{'tmdb':'2&action=play'}}))

    def test_home_recommendations_bounded_and_not_fake(self):
        with KodiHarness():
            from resources.lib import library_home as l
            media=[]
            for n in range(28):
                item=l._entry({'movieid':n,'title':f'Film {n}', 'year':2025,
                               'genre':['Mystery' if n%3 else 'Comedy'],
                               'resume':{'position':7,'total':70} if n==2 else {},
                               'lastplayed':'2026-10-01' if n==2 else '',
                               'dateadded':'2026-10-%02d'%(n%27+1)}, 'movie')
                media.append(item)
            rows=l.build_rows(media,'home')
            self.assertEqual(rows[0][0],'Continue Watching')
            self.assertEqual(rows[0][1][0]['id'],'movie:2')
            self.assertTrue(all(len(r) <= 10 for _,r in rows))
            self.assertTrue(all(x['kind']=='movie' for title,ls in rows if title!='Your Sources' for x in ls))
            self.assertEqual(l.search(media,'FILM 12')[0]['id'],'movie:12')

    def test_no_library_still_has_real_navigation_targets(self):
        with KodiHarness():
            from resources.lib import library_home as l
            rows=l.build_rows([], 'home')
            self.assertEqual(rows[0][0], 'Start Watching')
            self.assertEqual(rows[0][1][0]['id'], 'source:umbrella')
            self.assertNotIn('demo:',str(rows))
            self.assertEqual(l.search([], 'anything'),[])

    def test_anime_not_falsely_claimed_dubbed(self):
        with KodiHarness():
            from resources.lib import library_home as l
            data=[l._entry({'tvshowid':2,'title':'Anime Show','genre':['Animation']},'series'),
                  l._entry({'tvshowid':3,'title':'Unrelated Show','genre':['Thriller']},'series')]
            rows=l.build_rows(data,'anime')
            self.assertEqual(rows[0][1][0]['id'],'series:2')
            self.assertNotIn('dubbed',str(rows).lower())

    def test_watchlists_scoped_and_ambiguous_profile_read_only(self):
        with KodiHarness() as k:
            from resources.lib import theatre_state as s
            self.assertEqual(s.read_list(),[])
            self.assertTrue(s.change('movie:25'))
            self.assertEqual(s.read_list(),['movie:25'])
            k.active='Dad'
            self.assertEqual(s.read_list(),[])
            self.assertTrue(s.change('episode:8'))
            self.assertEqual(s.read_list(),['episode:8'])
            k.active='Andy'
            self.assertEqual(s.read_list(),['movie:25'])
            k.duplicate_labels=True
            self.assertEqual(s.read_list(),[])
            self.assertIsNone(s.change('movie:13'))
            self.assertIsNone(s.change('source:umbrella'))
            k.duplicate_labels=False
            k.shared=True
            k.active='Andy'
            self.assertTrue(s.change('movie:11'))
            k.active='Dad'
            self.assertEqual(s.read_list(), [])
            self.assertTrue(s.change('movie:22'))
            k.active='Andy'
            self.assertEqual(s.read_list(), ['movie:11'])

    def test_no_remote_requests_in_initial_theatre_loading(self):
        with KodiHarness():
            from resources.lib import library_home as l
            with patch.object(l, 'rpc', side_effect=AssertionError('Kodi RPC allowed only from load_library')):
                rows=l.build_rows([], 'home')
                self.assertEqual(len(rows),2)

    def test_theatre_window_opens_with_kodi_doubles_and_no_skin_changes(self):
        with KodiHarness() as k:
            import xbmcgui
            from resources.lib import library_home
            source=library_home._entry({'movieid':12, 'title':'Film in my library',
                                        'plot':'A proper film','file':'/mnt/media/film.mkv',
                                        'resume':{'position':20,'total':100},
                                        'dateadded':'2026-10-10'},'movie')
            class FakeList:
                def __init__(self): self.items=[]
                def reset(self): self.items=[]
                def addItems(self,items): self.items.extend(items)
                def getSelectedItem(self): return self.items[0] if self.items else None
            class FakeWindow:
                def __init__(self,*args,**kwargs):
                    self.controls={301:FakeList(),302:FakeList()};self.props={};self.focus=None
                def getControl(self,k): return self.controls[k]
                def setProperty(self,k,v):self.props[k]=v
                def setFocusId(self,k):self.focus=k
                def getFocusId(self):return self.focus
                def close(self):pass
            native_item=xbmcgui.ListItem
            with patch.object(xbmcgui,'WindowXMLDialog',FakeWindow,create=True),patch.object(xbmcgui,'ListItem',lambda *args, **kwargs: native_item(*args,**{a:b for a,b in kwargs.items() if a!='offscreen'}), create=True),patch.object(library_home,'load_library',return_value=[source]):
                from resources.lib import theatre_window
                # Class definition must be made under the Kodi double.
                importlib.reload(theatre_window)
                win=theatre_window.TheatreWindow('CallenPrimeTheatre.xml','addon','Default','1080i')
                win.addonpath=str(ADDON)
                win.onInit()
                self.assertEqual(win.props['cp.title'],'FILM IN MY LIBRARY')
                self.assertEqual(win.focus,100)
                self.assertEqual(win.controls[301].items[0].label,'Film in my library')
                win._tab('movies')
                self.assertEqual(win.tab,'movies')
                self.assertTrue(len(win.controls[301].items)>0)
                self.assertFalse(win.exit_to_source)

if __name__=='__main__':unittest.main()
