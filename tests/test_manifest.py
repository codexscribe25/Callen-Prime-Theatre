import unittest
from xml.etree import ElementTree
from .common import ADDON


class ManifestTests(unittest.TestCase):
    def test_manifest_is_omega_python_plugin_only(self):
        node = ElementTree.parse(ADDON / 'addon.xml').getroot()
        self.assertEqual(node.attrib['id'], 'plugin.video.callenprime')
        self.assertEqual(node.attrib['version'], '0.2.0')
        self.assertTrue(node.findall("./requires/import[@addon='xbmc.python'][@version='3.0.0']"))
        self.assertEqual(len(node.findall("./extension[@point='xbmc.python.pluginsource']")), 1)
        self.assertFalse(node.findall("./extension[@point='xbmc.service']"))
