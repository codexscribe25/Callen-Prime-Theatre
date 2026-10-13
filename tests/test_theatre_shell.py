"""CP03 behaviour-level checks; not a substitute for remote-controller testing."""
import copy
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from .common import KodiHarness, ADDON


class TheatreShellTests(unittest.TestCase):
    def test_root_has_catalogue_sections_and_stable_widget_routes(self):
        with KodiHarness() as k:
            entries = k.call('')
            params = [parse_qs(urlsplit(url).query) for url, _, _ in entries]
            self.assertEqual([p['section'][0] for p in params if 'section' in p],
                             ['movies', 'series', 'anime'])
            self.assertEqual([p['row'][0] for p in params if 'row' in p][:5], list(k.fixtures.ROW_KEYS))
            self.assertTrue(all(item.properties['IsPlayable'] == 'false' for _, item, _ in entries))

    def test_movies_series_anime_are_bounded_and_nonplaying(self):
        with KodiHarness() as k:
            seen_kinds = set()
            for section in ('movies', 'series', 'anime'):
                entries = k.call('?section=' + section)
                self.assertGreater(len(entries), 0, section)
                self.assertLessEqual(len(entries), k.fixtures.LIMIT)
                self.assertTrue(all(folder for _, _, folder in entries))
                self.assertTrue(all('[CP03 DEMO]' in item.label for _, item, _ in entries))
                kinds = {item.properties['CallenPrime.MediaKind'] for _, item, _ in entries}
                self.assertEqual(kinds, {section[:-1] if section == 'movies' else section})
                seen_kinds.update(kinds)
                url, item, _ = entries[0]
                k.call('?' + urlsplit(url).query)
                self.assertIn('No playback in this test build.', k.dialogs[-1][1])
            self.assertEqual(seen_kinds, {'movie', 'series', 'anime'})

    def test_runtimes_present_only_if_fixture_provides_them(self):
        with KodiHarness() as k:
            entries = k.call('?section=movies')
            self.assertTrue(any(item.info.get('duration') == 6240 for _, item, _ in entries))
            self.assertTrue(any('duration' not in item.info for _, item, _ in entries))
            self.assertTrue(all(item.properties['CallenPrime.LanguageStatus'] == 'unknown'
                                for _, item, _ in entries))
            self.assertTrue(all('rating' not in item.info for _, item, _ in entries))
            self.assertEqual(k.app.ROW_KEYS, k.fixtures.ROW_KEYS)

    def test_details_show_kind_year_runtime_and_unknown_language(self):
        with KodiHarness() as k:
            items = k.call('?section=anime')
            self.assertEqual(len(items), 1)
            url = items[0][0]
            k.call('?' + urlsplit(url).query)
            title, message = k.dialogs[-1]
            self.assertIn('Details', title)
            for expected in ('[CP03 DEMO:', 'Anime episode', '2026', '24m',
                             'Audio and dub information: Unknown', 'No playback'):
                self.assertIn(expected, message)
            self.assertEqual(len(k.ended), 1)

    def test_old_cp02_snapshot_metadata_stays_safe(self):
        with KodiHarness() as k:
            assert k.profile.activate(str(ADDON), 'andy')
            source = k.rows.listed_items(str(ADDON), 'continue')[0]
            old = {key: val for key, val in source.items() if key not in ('media_kind', 'runtime_minutes')}
            message = k.app.presentation.detail_lines(old)
            self.assertIn('Unknown', message)
            self.assertIn('No playback', message)

    def test_details_do_not_leak_prior_profile_row_item(self):
        with KodiHarness() as k:
            assert k.profile.activate(str(ADDON), 'andy')
            self.assertIsNotNone(k.rows.find_item(str(ADDON), 'continue', 'demo:movie:stone-comet'))
            k.active = 'Dad'
            assert k.profile.activate(str(ADDON), 'dad')
            k.call('?action=details&row=continue&item=demo%3Amovie%3Astone-comet')
            self.assertIn('unavailable in this profile', k.dialogs[-1][1])

    def test_stray_query_cannot_override_profile_or_section(self):
        with KodiHarness() as k:
            for query in ('?row=continue&section=anime', '?action=details&row=continue&section=anime&item=demo%3Aepisode%3Apaper-dragons',
                          '?section=not-real', '?action=search&query=someone'):
                self.assertFalse(k.call(query))
                self.assertEqual(len(k.ended), 1)
            self.assertIn('unavailable', k.dialogs[-1][1])

    def test_my_list_not_misrepresented_as_connected(self):
        with KodiHarness() as k:
            self.assertFalse(k.call('?action=my-list'))
            self.assertIn('not connected', k.dialogs[-1][0])
            self.assertIn('fictional demo', k.dialogs[-1][1])

    def test_missing_fixture_returns_empty_sections(self):
        with KodiHarness() as k:
            with patch.object(k.fixtures, 'load_catalog', side_effect=FileNotFoundError()):
                self.assertFalse(k.call('?section=anime'))
                self.assertEqual(len(k.ended), 1)

    def test_invalid_fixture_metadata_rejected(self):
        with KodiHarness() as k:
            catalog = k.fixtures.load_catalog(str(ADDON))
            a = copy.deepcopy(next(iter(catalog.values())))
            a['runtime_minutes'] = 0
            self.assertEqual(k.app.presentation.runtime_label(a), 'Unknown')
            a['runtime_minutes'] = True
            self.assertEqual(k.app.presentation.runtime_label(a), 'Unknown')
