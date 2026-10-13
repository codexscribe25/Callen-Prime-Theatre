# Callen Prime Theatre 🎬

**CP04 v0.4.0 is an experimental Kodi playback bridge**, built for Kodi 21.3 Omega on the Fire TV Stick 4K Max (2nd generation).

The five CP02/CP03 home widget URLs, fictional Movies/Series/Anime browsing and profile-separated demo snapshots remain intact. Fictional catalogue entries **never play**. There is no background service, automatic source scraper, real Trakt history or dynamic recommendations.

## What's new

1. Open Add-ons → Video add-ons → Callen Prime Theatre (CP04 Prototype) → **Playback Tests**.
2. Choose **Play a local test video**. Use Kodi's file picker and explicitly approve playback. It accepts only files stored locally on the device.
3. If you already have **Umbrella 6.7.90** installed and enabled, you may optionally activate it in this Kodi profile for an experimental handoff. Enter a real title, TMDb ID and year (plus season/episode when applicable). Umbrella retains ownership of source selection and playback.
4. Fen and Seren are not enabled. No credentials, provider packages, third-party streams or full viewing histories are included.

**Status: BUILD-READY / DEVICE HOLD.** Forty-one off-device automated tests passed. Actual installation, local playback, Umbrella handoff, profile switching and navigation timings still require testing on the real Fire Stick.

## Install

Back up your Kodi/Nimbus settings, then install the provided Callen-Prime-Theatre_CP04_v0.4.0-test.zip using Kodi Settings → Add-ons → Install from zip file. Keep the CP03 ZIP for rollback.

## Development

Run these commands from repository root:

    python -m unittest discover -s tests -t . -v
    python scripts/build_zip.py

The installable ZIP contains only the addon/plugin.video.callenprime subtree. Widget URLs remain:

- plugin://plugin.video.callenprime/?row=continue
- plugin://plugin.video.callenprime/?row=new
- plugin://plugin.video.callenprime/?row=context-a
- plugin://plugin.video.callenprime/?row=context-b
- plugin://plugin.video.callenprime/?row=context-c

## Evidence

See docs/CP04-WORK-STATUS.md and CP04 device acceptance guide, source compatibility assessment and implementation report. Existing CP02/CP03 documentation remains applicable.

The repository is **public**. Do not commit local media paths, personal viewing history, Kodi backups, Trakt/Real-Debrid tokens, or unredacted provider logs. Project code is MIT. Kodi, Nimbus and provider sources are neither redistributed nor patched here.
