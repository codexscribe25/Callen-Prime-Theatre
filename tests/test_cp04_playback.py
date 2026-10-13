"""Playback tests use Kodi API doubles, not real media or provider accounts."""
import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from unittest.mock import patch

from .common import KodiHarness, ADDON


class CP04PlaybackTests(unittest.TestCase):
    def test_demo_rows_never_resolve_anything(self):
        with KodiHarness() as k:
            for row in k.fixtures.ROW_KEYS:
                items = k.call('?row=' + row)
                self.assertGreater(len(items), 0)
                self.assertTrue(all(not item.properties['IsPlayable'] == 'true' for _,item,_ in items))
                k.call('?' + urlsplit(items[0][0]).query)
                self.assertFalse(k.resolved)
                self.assertTrue(k.ended)

    def test_root_and_playback_lab_do_not_trigger_play(self):
        with KodiHarness() as k:
            root = k.call('')
            self.assertIn('Playback Tests (CP04)', [i.label for _, i, _ in root])
            lab = k.call('?action=playback-lab')
            self.assertEqual(len(k.ended), 1)
            self.assertEqual(len(k.resolved), 0)
            playable = [item for _, item, is_folder in lab if not is_folder]
            self.assertEqual(len(playable), 1)
            self.assertEqual(playable[0].properties['IsPlayable'], 'true')

    def test_local_cancel_never_resolves_a_video_or_ends_directory(self):
        with KodiHarness() as k:
            k.call('?action=play-local')
            self.assertEqual(k.resolved, [(7, False, '')])
            self.assertFalse(k.ended)
            with tempfile.TemporaryDirectory() as folder:
                movie = Path(folder) / 'mine.mp4'
                movie.write_bytes(b'FAKE MOVIE, NOT IN ZIP')
                k.browse_results.append(str(movie))
                k.confirmations.append(False)
                k.call('?action=play-local')
                self.assertEqual(k.resolved, [(7, False, '')])
                self.assertFalse(k.ended)

    def test_local_selected_file_resolves_only_after_confirmation(self):
        with KodiHarness() as k:
            with tempfile.TemporaryDirectory() as folder:
                movie = Path(folder) / 'mine.mp4'
                movie.write_bytes(b'FAKE TEST DATA')
                k.browse_results.append(str(movie))
                k.confirmations.append(True)
                k.call('?action=play-local')
                self.assertEqual(k.resolved, [(7, True, str(movie))])
                self.assertFalse(k.ended)
                self.assertNotIn(str(movie), str(k.logs))

    def test_reject_nonlocal_directory_url_and_query_injection(self):
        with KodiHarness() as k:
            with tempfile.TemporaryDirectory() as folder:
                import os
                paths = [folder, 'smb://server/video.mp4', 'https://site/x.mp4',
                         'plugin://plugin.video.umbrella/', 'file:///tmp/a.mp4',
                         '/tmp/file.mp4?secret=1', '/tmp/%2f.mkv']
                for item in paths:
                    self.assertIsNone(k.app.playback.local_video_path(item))
                k.call('?action=play-local&url=%2Fstorage%2Fmovies%2Ftest.mp4')
                self.assertEqual(k.resolved, [(7, False, '')])
                k.call('?action=play-local&row=continue')
                self.assertEqual(k.resolved, [(7, False, '')])
                self.assertFalse(k.ended)

    def test_umbrella_status_fails_closed(self):
        with KodiHarness() as k:
            self.assertIsNone(k.app.providers.installed_provider('evil.plugin'))
            self.assertIsNone(k.app.providers.installed_provider('plugin.video.umbrella'))
            k.provider_version = '6.7.90'
            k.provider_enabled = False
            self.assertFalse(k.app.providers.umbrella_available())
            k.provider_enabled = True
            self.assertTrue(k.app.providers.umbrella_available())
            k.provider_version = '6.7.91'
            self.assertFalse(k.app.providers.umbrella_available())

    def test_provider_optin_separate_per_kodi_profile(self):
        with KodiHarness() as k:
            k.provider_version = '6.7.90'
            k.provider_enabled = True
            self.assertFalse(k.app.provider_prefs.is_umbrella_enabled())
            k.confirmations.append(True)
            k.call('?action=enable-umbrella')
            self.assertTrue(k.app.provider_prefs.is_umbrella_enabled())
            k.active = 'Dad'
            self.assertFalse(k.app.provider_prefs.is_umbrella_enabled())
            k.call('?action=play-umbrella')
            self.assertEqual(k.resolved, [(7, False, '')])
            self.assertFalse(k.ended)
            k.active = 'Andy'
            self.assertTrue(k.app.provider_prefs.is_umbrella_enabled())
            k.call('?action=disable-umbrella')
            self.assertFalse(k.app.provider_prefs.is_umbrella_enabled())

    def test_corrupt_provider_preference_fails_closed(self):
        with KodiHarness() as k:
            self.assertTrue(k.app.provider_prefs.set_umbrella_enabled(True))
            scope = k.profile.current_scope()
            path = k.app.provider_prefs._file(scope)
            Path(path).write_text('{corrupt', encoding='utf8')
            self.assertFalse(k.app.provider_prefs.is_umbrella_enabled())
            self.assertTrue(k.app.provider_prefs.set_umbrella_enabled(False))
            self.assertFalse(k.app.provider_prefs.is_umbrella_enabled())

    def test_umbrella_movie_url_source_derived_and_encoded(self):
        with KodiHarness() as k:
            make = k.app.providers.umbrella_url
            u = make('movie', 'A & B', '246810', '2025')
            self.assertTrue(u.startswith('plugin://plugin.video.umbrella/?'))
            q = parse_qs(urlsplit(u).query)
            self.assertEqual(q['action'], ['play_Item'])
            self.assertEqual(q['title'], ['A & B'])
            self.assertEqual(q['tmdb'], ['246810'])
            self.assertEqual(q['year'], ['2025'])
            self.assertEqual(q['meta'][0], json.dumps({'title':'A & B','year':2025,'tmdb':'246810','mediatype':'movie'},separators=(',',':')))
            self.assertNotIn('token', u)

    def test_episode_requires_series_and_season_episode(self):
        with KodiHarness() as k:
            make = k.app.providers.umbrella_url
            self.assertIsNone(make('episode', 'Series', '123', '2020'))
            self.assertIsNone(make('episode', 'Series', '123', '2020', '1', '0'))
            url = make('episode', 'Series', '123', '2020', '1', '2')
            q = parse_qs(urlsplit(url).query)
            self.assertEqual((q['tvshowtitle'],q['season'],q['episode']), (['Series'],['1'],['2']))

    def test_provider_bad_ids_dont_launch(self):
        with KodiHarness() as k:
            make = k.app.providers.umbrella_url
            for kind, title, tmdb, year in [
                ('movie', 'Fake', 'demo:movie', '2025'),
                ('movie', 'Fake', '0', '2025'),
                ('movie', 'Fake', '123&action=evil', '2025'),
                ('movie', ' ', '123', '2025'),
                ('movie', 'A\nB', '123', '2025'),
                ('movie', 'A<evil>', '123', '2025'),
                ('video', 'Test', '123', '2025'),
                ('movie', 'Test', '123', 'notayear')]:
                self.assertIsNone(make(kind,title,tmdb,year))

    def test_manual_umbrella_handoff_is_one_resolve_not_directory(self):
        with KodiHarness() as k:
            k.provider_version = '6.7.90'; k.provider_enabled = True
            self.assertTrue(k.app.provider_prefs.set_umbrella_enabled(True))
            k.selections.append(0)
            k.inputs.extend(['Example Title','12345','2024'])
            k.confirmations.append(True)
            k.call('?action=play-umbrella')
            self.assertEqual(len(k.resolved),1)
            self.assertTrue(k.resolved[0][1])
            self.assertEqual(len(k.ended), 0)
            self.assertIn('plugin.video.umbrella', k.resolved[0][2])
            self.assertNotIn('12345', str(k.logs))
            # repeated command, even if interactive flow repeats, fails closed
            k.selections.append(0);k.inputs.extend(['Example Title','12345','2024']);k.confirmations.append(True)
            k.call('?action=play-umbrella')
            self.assertEqual(k.resolved, [(7, False, '')])

    def test_umbrella_cancel_unavailable_or_extra_query_never_launches(self):
        with KodiHarness() as k:
            k.provider_version='6.7.90'; k.provider_enabled=True
            self.assertTrue(k.app.provider_prefs.set_umbrella_enabled(True))
            k.selections.append(-1)
            k.call('?action=play-umbrella')
            self.assertEqual(k.resolved, [(7,False,'')])
            k.call('?action=play-umbrella&url=plugin%3A%2F%2Fevil')
            self.assertEqual(k.resolved, [(7,False,'')])
            k.provider_enabled=False
            k.call('?action=play-umbrella')
            self.assertEqual(k.resolved, [(7,False,'')])
            self.assertFalse(k.ended)

    def test_profile_ambiguous_cannot_enable_provider(self):
        with KodiHarness() as k:
            k.duplicate_labels = True
            self.assertFalse(k.app.provider_prefs.set_umbrella_enabled(True))
            self.assertFalse(k.app.provider_prefs.is_umbrella_enabled())
            k.duplicate_labels = False
            k.ambiguous_path = True
            self.assertFalse(k.app.provider_prefs.is_umbrella_enabled())

    def test_home_listing_does_not_probe_provider(self):
        with KodiHarness() as k:
            with patch.object(k.app.providers, 'installed_provider', side_effect=AssertionError('provider probed')):
                for row in k.fixtures.ROW_KEYS:
                    self.assertTrue(k.call('?row='+row))
                self.assertTrue(k.call('?section=movies'))
                self.assertTrue(k.call('?row=continue'))
                self.assertTrue(k.call(''))
                self.assertFalse(k.resolved)


if __name__ == '__main__':
    unittest.main()
