# Callen Prime Theatre Build v0.5.0 | Engineering record

**Source parent:** CP04 `cp04/playback-bridge`, commit `2412b939` as reported in prior release session. No direct Kodi installation was observed in the build environment.

## Why the architecture changed

The initial CP02–CP04 releases only exposed Kodi directory listings under the user's existing skin. Passing those tests did not deliver the requested modern TV interface. Rather than require the user to configure Nimbus manually or risk replacing the entire Kodi skin, this release adds a real full-screen Kodi WindowXMLDialog that the video add-on can launch directly, preserving the host Kodi skin and existing media add-ons.

## What's implemented

- One native full-screen window with branded background, featured content, two horizontal poster lists at a time, five+ rows by navigation and nine TV-remote top actions.
- Dedicated title-details window with Play / My List / Back, episodic picker for series.
- JSON-RPC Kodi movie/series/episode ingestion from the *current Kodi library*, rather than fake titles. Reuses local resume/watched state and Kodi artwork.
- Stable profile-scoped My List with SHA-256 effective path binding and unique Kodi profile-label binding. No storage write during passive browsing.
- Simple deterministic recommendations based on genre overlap and recent library watch activity. No external AI calls or aggressive ranking algorithms.
- Anime/animation sorting with verified English audio row when episode audio stream metadata is supplied.
- Installed provider browsing for Umbrella, Fen, Fen Light and Seren. Sources are opened by explicit user action; no token reads or automated scraping. CP04 Umbrella direct-play verification remains restricted to pinned version and explicit opt-in.
- Source/empty-state cards; no fake watched progress masquerading as real content.
- All CP02–CP04 routes and tests retained, with an upgraded add-on manifest and launcher route first in the menu.

## Risk register and mitigations

1. **Kodi runtime unverified:** XML and Python source checks pass, but no Fire Stick GUI is available to execute it here. Deliver test ZIP only, device HOLD.
2. **Provider handoff:** browsing installed addons is supported in Kodi, but Focus/Back after switching apps is a physical test. No arbitrary plugin command injection.
3. **Profile sharing:** Kodi databases may be shared; My List uses scope and profile-label guards. If the profile identity isn't unambiguous, My List is read-only/empty.
4. **External Trakt:** OAuth requires the viewer's authentication. No account secrets, API key or watch history are packaged; direct Trakt is not represented as finished.
5. **Dubbed anime:** language varies by media stream; the UI only marks English confirmed where Kodi actually reports stream language metadata.
6. **Performance:** content ingestion occurs once on opening or explicit refresh, not on focus; bounded listing; no background worker; local image/skin assets. Real focus latency not measurable off-device.
7. **Rollback:** add-on upgrade preserves Kodi skin. Old CP04 installer can be reinstalled without deleting other media addons.

## Acceptance disposition

**OFF-DEVICE BUILD VERIFIED; KODI/FIRE TV DEVICE ACCEPTANCE PENDING.** This package should be tested on the real 4K Max before describing it as a finished, fast, compatible home theatre.
