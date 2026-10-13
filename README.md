# Callen Prime Theatre 🎬

**CP02 test build (v0.2.0): five offline Kodi widget rows for a performance experiment.** This is not yet a streaming build. It contains fictional demo titles only and **cannot play movies, access Trakt, use Real-Debrid, or resolve sources**.

Target: Kodi 21.3 Omega / Fire TV Stick 4K Max (2nd Generation). Stock Nimbus is the initial candidate skin, but real-device compatibility remains **unverified**.

## What is included

- One Kodi plugin, `plugin.video.callenprime`, no service or background job.
- Five stable routes: `?row=continue`, `?row=new`, `?row=context-a`, `?row=context-b`, `?row=context-c`.
- Two explicitly selectable *fictional* fixture sets and a neutral fail-safe set.
- Local poster placeholders; no network activity on widget calls.
- P0 (`?row=frozen`) / P1 (`?row=probe`) diagnostic routes for comparing a frozen plugin with profile-aware lookup of identical items.
- Deterministic ZIP build and off-device unit tests.

## Get started

1. **Back up your existing Kodi configuration** before installing or changing Nimbus widgets. See [the Fire TV guide](docs/FIRETV-DEVICE-TEST.md).
2. Build via `python scripts/build_zip.py`, or install the supplied `Callen-Prime-Theatre_CP02_v0.2.0-test.zip` into Kodi using *Settings → Add-ons → Install from zip file* (enable Unknown sources only if prompted and only after trusting the file).
3. Open *Add-ons → Video add-ons → Callen Prime Theatre (CP02 Demo)*. From the **currently active Kodi profile**, choose `Activate ANDY demo in THIS Kodi profile`. Switch Kodi profiles and choose the Dad preset separately. If profile storage is ambiguous, the add-on stays neutral.
4. In stock Nimbus, set up five widget paths using the exact URLs in [NIMBUS-WIDGET-SETUP.md](docs/NIMBUS-WIDGET-SETUP.md). Configuration is user-initiated; CP02 never edits the skin.
5. Complete [the device checklist](docs/FIRETV-DEVICE-TEST.md) and [acceptance record](docs/CP02-ACCEPTANCE.md).

**Careful:** source tests passing does not prove the Fire Stick ZIP installs successfully or that five widget rows are fast on device. Treat this as an experimental Kodi add-on.

## Development

```bash
python -m unittest discover -s tests -t . -v
python scripts/build_zip.py
```

`addon/plugin.video.callenprime/` is the only folder packaged into the installation ZIP. No third-party Kodi add-ons, credentials, user media or copyrighted film art are packaged.

## Safety and rollback

- Kodi, Nimbus, Umbrella, Fen, Seren and existing authorisations are **not changed** by this plugin.
- All widget titles contain `CP02 DEMO`. Selecting one opens an explanatory dialog, not playback.
- Restoring the original widget settings removes Callen Prime from the home screen. Then disable or uninstall the addon.
- Data is written *only when selecting an activation command*, under the active Kodi profile's addon-data path. Unknown or ambiguous profile scopes fall back to neutral content.
- The repo is public. Do **not** commit real watch history, Trakt/Real-Debrid tokens, logs containing private URLs or personal Kodi backups.

See [architecture](docs/CP02-ARCHITECTURE.md), [implementation report](docs/CP02-IMPLEMENTATION-REPORT.md), [source baseline](docs/CP01-SOURCE-BASELINE.md) and [MIT license](LICENSE).