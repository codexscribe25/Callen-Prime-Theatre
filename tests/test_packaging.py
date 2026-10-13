import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path
from scripts.build_zip import build
from .common import ADDON


class PackagingTests(unittest.TestCase):
    def test_deterministic_valid_root_and_no_secrets(self):
        with tempfile.TemporaryDirectory() as folder:
            first = Path(folder) / 'a.zip'
            second = Path(folder) / 'b.zip'
            build(first)
            build(second)
            self.assertEqual(hashlib.sha256(first.read_bytes()).digest(),
                             hashlib.sha256(second.read_bytes()).digest())
            with zipfile.ZipFile(first) as archive:
                names = archive.namelist()
                self.assertTrue(all(n.startswith('plugin.video.callenprime/') for n in names))
                self.assertIn('plugin.video.callenprime/addon.xml', names)
                self.assertIn('plugin.video.callenprime/resources/media/poster-a.png', names)
                self.assertFalse(any('__pycache__' in n or n.endswith('.pyc') for n in names))
                self.assertTrue(all(i.date_time == (2020, 1, 1, 0, 0, 0) for i in archive.infolist()))
                for name in names:
                    self.assertNotIn('token', name.lower())
