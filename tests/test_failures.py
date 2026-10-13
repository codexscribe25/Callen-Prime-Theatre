import os
import unittest
from unittest.mock import patch
from .common import KodiHarness, ADDON


class FailureTests(unittest.TestCase):
    def test_corrupt_missing_snapshot_falls_back_neutral(self):
        with KodiHarness() as k:
            assert k.profile.activate(str(ADDON), 'andy')
            path = k.profile._snapshot_path(k.profile.current_scope())
            neutral = k.fixtures.load_rows(str(ADDON), 'neutral')['continue']
            for payload in ('{broken', '{"schema":"other"}', '{"preset":"dad"}'):
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(payload)
                self.assertEqual(k.rows.listed_items(str(ADDON), 'continue'), neutral)
            os.remove(path)
            self.assertEqual(k.rows.listed_items(str(ADDON), 'continue'), neutral)

    def test_bad_rpc_neutral_and_no_stale_state(self):
        with KodiHarness() as k:
            assert k.profile.activate(str(ADDON), 'dad')
            k.bad_rpc = True
            self.assertIsNone(k.profile.read_snapshot())
            self.assertEqual(len(k.call('?row=context-b')), 4)
            self.assertEqual(len(k.ended), 1)

    def test_missing_packaged_fixture_returns_empty_and_closes(self):
        with KodiHarness() as k:
            with patch.object(k.fixtures, 'load_rows', side_effect=FileNotFoundError):
                self.assertEqual(k.call('?row=context-b'), [])
                self.assertEqual(len(k.ended), 1)

    def test_exception_always_closes_directory(self):
        with KodiHarness() as k:
            with patch.object(k.app, '_listing', side_effect=RuntimeError('synthetic failure')):
                self.assertEqual(k.call('?row=continue'), [])
                self.assertEqual(len(k.ended), 1)
