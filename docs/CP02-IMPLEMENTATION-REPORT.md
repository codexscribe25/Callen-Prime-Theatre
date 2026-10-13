# CP02 implementation report

**Date:** 13 October 2026  
**Build:** 0.2.0 offline fixture demonstrator  
**Scope:** add-on source, five fixed routes, profiles, tests, deterministic ZIP and device instructions.

## Evidence

- Kodi plugin entrypoint: `addon/plugin.video.callenprime/default.py`. Five row URLs, two P0/P1 diagnostic routes, manual activation and non-playing details.
- Profile scope: `resources/lib/profile.py`; uses active Kodi `special://profile/` (resolved by Kodi), unique profile label guard and a profile-bound snapshot. `special://userdata` not used for per-profile fixture data.
- Fixtures: `resources/fixtures/catalog.json`, `profiles.json`; all titles and summaries invented for CP02. Three original local 240×360 PNG tiles.
- No services, players, Trakt, debrid, artwork URLs, remote calls or Nimbus source changes.
- Data updates require explicit user activation. No automatic row rotation or XML rewrite.

## Local automated tests

Run `python -m unittest discover -s tests -t . -v` from repository root. Tests cover manifest, six/seven routes, safe end-of-directory, neutral fallback, corrupted snapshots, ambiguity, cross-profile switches, offline execution and reproducible ZIP. Record the actual result from the execution environment here at release time.

Run `python scripts/build_zip.py`. A deterministic SHA-256 is produced and must be captured alongside the delivered test ZIP.

## Outstanding gates

1. Kodi 21.3 plugin loader compatibility (not executable in this environment).
2. Nimbus UI's exact add-on widget-picker workflow on the user's device.
3. Profile isolation under the user's actual profile configuration.
4. B0/B1/B2/B3/P0/P1 performance measurements.
5. Reversibility and stable playback with an authorised local video.

**Disposition: provisional BUILD-READY, hold final CP02 acceptance pending device evidence.** If the plugin's folder items are rendered poorly in Nimbus, record that mismatch before changing the non-playable safety contract.
