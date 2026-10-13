import unittest
from urllib.parse import unquote
from .common import KodiHarness, ADDON


class RouteTests(unittest.TestCase):
    def test_all_five_routes_are_bounded_synthetic_and_local(self):
        with KodiHarness() as k:
            for row in k.fixtures.ROW_KEYS:
                items = k.call('?row=' + row)
                self.assertTrue(items)
                self.assertLessEqual(len(items), 8)
                self.assertEqual(len(k.ended), 1)
                ids = []
                for url, item, folder in items:
                    self.assertTrue(folder)
                    self.assertIn('CP03 DEMO', item.label)
                    self.assertIn('demo:', unquote(url))
                    self.assertEqual(item.properties['IsPlayable'], 'false')
                    self.assertEqual(item.properties['CallenPrime.Demo'], 'true')
                    self.assertIn(item.info['mediatype'], ('movie', 'episode'))
                    self.assertTrue(item.art['poster'].startswith(str(ADDON)))
                    ids.append(url)
                self.assertEqual(len(ids), len(set(ids)))

    def test_p0_and_p1_produce_same_items(self):
        with KodiHarness() as k:
            p0 = [(u, i.label, i.art, i.info) for u, i, _ in k.call('?row=frozen')]
            p1 = [(u.replace('row=probe', 'row=frozen'), i.label, i.art, i.info) for u, i, _ in k.call('?row=probe')]
            self.assertEqual(p0, p1)

    def test_details_never_play(self):
        with KodiHarness() as k:
            items = k.call('?row=continue')
            self.assertTrue(items)
            k.call('?' + items[0][0].split('?', 1)[1])
            self.assertEqual(len(k.ended), 1)
            self.assertEqual(k.entries, [])
            self.assertIn('no playback', k.dialogs[-1][0].lower())

    def test_unknown_queries_terminate_empty(self):
        with KodiHarness() as k:
            for query in ('?row=unknown', '?action=play', '?row=continue&action=play'):
                self.assertFalse(k.call(query))
                self.assertEqual(len(k.ended), 1)
