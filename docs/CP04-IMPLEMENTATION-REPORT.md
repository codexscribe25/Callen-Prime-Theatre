# CP04 Implementation Report

**13 October 2026 | CP04 0.4.0 test build | Branch: cp04/playback-bridge**

Base source: cp03/theatre-shell at 815b9cf6830a9e651672f20ae5aa765712316004.

## Implemented

- Existing five synthetic Home widget routes and fictional demo title details unchanged.
- Explicit Playback Tests directory, separate from all Home widgets.
- User-selected local file (Kodi browseSingle), path/type validation, explicit confirmation and setResolvedUrl callback for Kodi-owned player.
- Optional Umbrella 6.7.90 source-derived handoff with manual real title and media identifiers; installed/enabled metadata checked only on deliberate user interactions.
- Per-profile provider opt-in, fail-closed on ambiguous Kodi profile, missing installation, wrong provider version, malformed ID or user cancellation.
- No Trakt/Real-Debrid credentials, direct source scraping, automatic provider fallback, background service, player monitor, Nimbus XML edit or autoplay.
- Corrected a pre-existing test stub bug: FakeVFSFile.read now accepts a size argument, matching production Kodi usage.

## Automated verification

From repository root: python -m unittest discover -s tests -t . -v

**41 local tests passed**, including 26 baseline CP02/CP03 checks and 15 new playback checks. These are mocks of Kodi's API; no actual Kodi binary or Fire Stick was available.

Package: python scripts/build_zip.py

Output: Callen-Prime-Theatre_CP04_v0.4.0-test.zip

SHA-256: 09854d64f4c32b7f7257eed3096c2d0258515277993e5a9db77b9ccd6c31f54c

Deterministic 17-entry ZIP with the correct plugin.video.callenprime top-level directory, and no bundled streaming providers or private user media.

## Red-team

- Kept demo IDs and rows nonplayable.
- No query parameter may specify arbitrary playback URLs, provider names, profile selection or hidden source commands.
- Kodi playable routes call setResolvedUrl once, and directory routes call endOfDirectory.
- Manual numeric TMDb inputs are structurally validated, not independently checked against catalogue data; wrong IDs may yield no result.
- Umbrella play_Item was inspected in source, but actual provider execution remains unverified and is not a public stability promise.
- Cancellation never falls through to Fen or Seren; second immediate provider launch is debounced.
- Device/profile and Nimbus performance benchmarks from earlier commissions are still open, not silently approved.

## Release decision

**BUILD-READY / DEVICE HOLD.** Installability, actual playback, Kodi remote navigation, profile switching, Umbrella handoff and warm Home timings need physical testing. No merges to main are authorised by this report.
