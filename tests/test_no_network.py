import socket
import unittest
from unittest.mock import patch
from .common import KodiHarness, ADDON


class NoNetworkTests(unittest.TestCase):
    def test_all_widget_invocations_are_offline(self):
        with KodiHarness() as k:
            with patch.object(socket, 'socket', side_effect=AssertionError('network invoked')):
                for row in k.fixtures.ROW_KEYS + ('frozen', 'probe'):
                    self.assertTrue(k.call('?row=' + row))
                self.assertTrue(k.profile.activate(str(ADDON), 'andy'))
                for row in k.fixtures.ROW_KEYS:
                    self.assertTrue(k.call('?row=' + row))
                self.assertEqual(len(k.ended), 1)

    def test_widget_modules_have_no_skin_reload_or_playback_calls(self):
        from pathlib import Path
        source = '\n'.join((ADDON / 'resources/lib' / x).read_text()
                           for x in ('fixtures.py', 'profile.py', 'rows.py', 'sections.py', 'presentation.py'))
        for banned in ('ReloadSkin', 'RunPlugin(', 'PlayMedia(', 'setResolvedUrl', 'xbmc.Player(', 'requests.get(', 'urllib.request', 'https://', 'http://'):
            self.assertNotIn(banned, source)
