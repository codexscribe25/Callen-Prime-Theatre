"""Build deterministic Kodi install ZIP from tracked addon folder.

Usage: python scripts/build_zip.py
"""
import hashlib
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / 'addon' / 'plugin.video.callenprime'
DEFAULT_OUTPUT = ROOT / 'dist' / 'Callen-Prime-Theatre_CP02_v0.2.0-test.zip'
FIXED_TIME = (2020, 1, 1, 0, 0, 0)


def build(output=DEFAULT_OUTPUT):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for file in sorted(ADDON.rglob('*')):
            if not file.is_file() or '__pycache__' in file.parts or file.suffix in ('.pyc', '.pyo'):
                continue
            entry = zipfile.ZipInfo('plugin.video.callenprime/' + file.relative_to(ADDON).as_posix(), FIXED_TIME)
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = (0o100644 << 16)
            archive.writestr(entry, file.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return hashlib.sha256(output.read_bytes()).hexdigest()


if __name__ == '__main__':
    digest = build()
    print(str(DEFAULT_OUTPUT))
    print('SHA-256:', digest)
