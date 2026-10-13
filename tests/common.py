"""Tiny Kodi API doubles for off-device tests; not a Kodi runtime emulator."""
import importlib.util
import json
import os
import sys
import tempfile
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / 'addon' / 'plugin.video.callenprime'


class FakeVFSFile:
    def __init__(self, path, mode='r'):
        self.file = open(path, mode, encoding='utf-8')

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.file.close()

    def read(self, size=-1):
        return self.file.read(size)

    def write(self, content):
        return self.file.write(content)


class KodiHarness:
    def __init__(self):
        self.root = tempfile.TemporaryDirectory()
        self.home = Path(self.root.name)
        self.active = 'Andy'
        self.shared = False
        self.duplicate_labels = False
        self.bad_rpc = False
        self.ambiguous_path = False
        self.entries = []
        self.ended = []
        self.logs = []
        self.dialogs = []
        self._original = {}

    def __enter__(self):
        for name in ('xbmc', 'xbmcgui', 'xbmcplugin', 'xbmcaddon', 'xbmcvfs'):
            self._original[name] = sys.modules.get(name)
        xbmc = types.ModuleType('xbmc')
        xbmc.LOGWARNING, xbmc.LOGINFO = 2, 1
        xbmc.log = lambda message, level: self.logs.append((message, level))
        xbmc.executeJSONRPC = self.json_rpc
        gui = types.ModuleType('xbmcgui')
        harness = self

        class Item:
            def __init__(self, label):
                self.label = label
                self.properties = {}
                self.art = {}
                self.info = {}

            def setProperty(self, key, value):
                self.properties[key] = value

            def setArt(self, art):
                self.art = art

            def setInfo(self, category, info):
                self.info = info

        class Dialog:
            def ok(self, title, message):
                harness.dialogs.append((title, message))

        gui.ListItem, gui.Dialog = Item, Dialog
        plugin = types.ModuleType('xbmcplugin')
        plugin.setContent = lambda handle, content: None
        plugin.addDirectoryItem = lambda handle, url, item, isFolder: self.entries.append((url, item, isFolder))
        plugin.endOfDirectory = lambda handle, **kw: self.ended.append((handle, kw))
        addon = types.ModuleType('xbmcaddon')
        addon.Addon = lambda: types.SimpleNamespace(getAddonInfo=lambda key: str(ADDON) if key == 'path' else 'plugin.video.callenprime')
        vfs = types.ModuleType('xbmcvfs')
        vfs.translatePath = self.translate_path
        vfs.File = FakeVFSFile
        vfs.exists = lambda path: os.path.exists(path)
        vfs.mkdirs = lambda path: (os.makedirs(path, exist_ok=True) or True)
        for name, module in [('xbmc', xbmc), ('xbmcgui', gui), ('xbmcplugin', plugin), ('xbmcaddon', addon), ('xbmcvfs', vfs)]:
            sys.modules[name] = module
        sys.path.insert(0, str(ADDON))
        from resources.lib import profile, rows, fixtures
        self.profile = profile
        self.rows = rows
        self.fixtures = fixtures
        spec = importlib.util.spec_from_file_location('cp02_default', ADDON / 'default.py')
        self.app = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.app)
        return self

    def __exit__(self, *_):
        sys.path.remove(str(ADDON))
        for name, value in self._original.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value
        for name in list(sys.modules):
            if name == 'resources' or name.startswith('resources.') or name == 'cp02_default':
                sys.modules.pop(name, None)
        self.root.cleanup()

    def translate_path(self, path):
        if self.ambiguous_path:
            return 'special://profile/'
        if path == 'special://profile/':
            return str(self.home / ('shared' if self.shared else self.active.lower()))
        raise ValueError(path)

    def json_rpc(self, request):
        if self.bad_rpc:
            return '{'
        method = json.loads(request)['method']
        if method == 'Profiles.GetCurrentProfile':
            return json.dumps({'result': {'label': self.active}})
        if method == 'Profiles.GetProfiles':
            labels = [self.active, self.active] if self.duplicate_labels else ['Andy', 'Dad']
            return json.dumps({'result': {'profiles': [{'label': x} for x in labels]}})
        raise AssertionError(method)

    def call(self, query=''):
        self.entries.clear()
        self.ended.clear()
        self.app.run(['plugin://plugin.video.callenprime/', '7', query])
        return self.entries[:]
