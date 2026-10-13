# CALLEN PRIME THEATRE 🎬

**Theatre Build 0.5.0** | A fullscreen, Kodi-native home theatre for Fire TV, built on the earlier CP02–CP04 plugin.

This build is fundamentally different from the earlier text-based test add-on. Choose **OPEN CALLEN PRIME THEATRE** and a custom full-screen interface opens with poster rows, featured artwork, film/series/anime sections, My List, Search, details and playback. It does **not** require you to switch Kodi skins or rebuild your streaming setup.

**Status:** source/test ZIP built and checked off-device; real Kodi 21.3/FIRE TV UI compatibility and speed are *not yet verified*. No misleading physical-device PASS.

## Install on your Fire TV Stick 4K Max (2nd Gen)

1. Keep your current Kodi skin and existing add-ons as they are. If this is your main Kodi setup, first back up its data or at least take a screenshot of your settings. You do **not** need a fresh Kodi install.
2. Copy `Callen-Prime-Theatre_Theatre_v0.5.0-test.zip` to your Fire Stick (for example, Download). **Do not unzip**.
3. In **Kodi → Settings → Add-ons → Install from zip file**, select the ZIP. This upgrades the previous `plugin.video.callenprime` add-on in place.
4. Open **Kodi → Add-ons → Video add-ons → Callen Prime Theatre**.
5. **Select the first item, `OPEN CALLEN PRIME THEATRE`.** This is the important difference: you should see the Callen Prime full-screen interface, **not** the directory of the older prototype.
6. Use your remote: left/right across posters, up/down between rows, top navigation for Movies / Series / Anime / My List / Search / Sources. Press Back to leave the theatre.
7. Optional: add Callen Prime to Kodi Favourites and pin that favourite to your existing skin's Home, if your skin supports shortcuts. This build deliberately does not overwrite the Kodi default skin or startup settings.

**If the full-screen theatre does not appear:** note the exact error or screen and return to Kodi. The underlying Kodi skin and media add-ons remain unchanged. You may reinstall the older CP04 ZIP to return to the previous add-on version. Do not reset Kodi.

## Where the content comes from

- **Films / TV / recently added / resume:** Kodi's own media library via local Kodi JSON-RPC, limited to a small number of records per category. Existing Kodi watch progress is reused. The theatre does not scrape websites in the background.
- **Suggestions:** deterministic, lightweight sorting by existing genres and recent Kodi watched activity. These are *local recommendations*, not Trakt-powered suggestions.
- **My List:** small, per-active-Kodi-profile saved list, with fail-closed identity checks. You and your dad should use **different Kodi profiles** and confirm whether Kodi is configured to share or separate media databases.
- **Anime:** animation/anime categorisation when present in Kodi metadata. A separate *English Audio Confirmed* row uses actual episode audio-stream metadata when available. **Unknown audio is not claimed to be dubbed.**
- **Sources:** browse the Umbrella, Fen, Fen Light or Seren add-on **already installed and enabled** on this Kodi device. The provider itself resolves and plays sources. Callen Prime does not read debrid credentials or change provider configuration.
- **Playing real media:** selecting a movie/episode that has a Kodi library path opens Kodi's player. If it doesn't have a playable path, the interface tells you rather than launching an arbitrary source.
- **Trakt:** this build does not implement new Trakt OAuth or import personal Trakt history. Continue using the authentication in your existing media add-ons. A direct Trakt per-viewer integration requires an explicit authorised login and further device verification.

**If your Kodi video library is empty:** Callen Prime shows the available source launchers. It will not create fake film listings and call them personalised recommendations. To populate recommendations, add the media you use to Kodi's library or connect an authorised catalogue integration in a later revision.

## Architecture

```text
Kodi 21.3 Omega / your existing skin
  ├── plugin.video.callenprime (same add-on id, upgrades CP04)
  │   ├── theatre.py        → custom WindowXMLDialog, fullscreen
  │   ├── resources/skins/Default/1080i/
  │   │   ├── CallenPrimeTheatre.xml → 9 top-level actions + 2 poster rows at a time
  │   │   └── CallenPrimeDetails.xml → item details / play / My List / back
  │   ├── resources/lib/library_home.py → bounded local Kodi JSON-RPC ingestion
  │   ├── resources/lib/theatre_window.py → Kodi remote + native playback
  │   ├── resources/lib/theatre_state.py → per-profile saved list
  │   └── CP02–CP04 demo and optional protected playback labs (unchanged)
  └── Existing Kodi / Umbrella / Fen / Seren playback paths remain separate
```

The two permanently visible poster rows show up to ten items each. Scrolling down pages through additional recommendation rows. No autoplay, no animated video hero, no SQLite/database server, no network requests from the visual renderer, and no recurring background tasks.

The GUI is an embedded Kodi-native **full-screen window**, not a separate Android APK or a replacement system skin. A major reason is to keep Kodi settings, add-ons and playback intact without requiring a giant skin fork.

## Developer verification

```bash
python -m unittest discover -s tests -t . -v
python scripts/build_zip.py
```

Artifacts: one reproducible Kodi ZIP with top-level `plugin.video.callenprime/`, plus `docs/THEATRE-IMPLEMENTATION.md` and `docs/THEATRE-DEVICE-TEST.md`.

## Safe rollback

Press Back to exit the theatre, use your existing Kodi skin normally, and disable Callen Prime in Kodi Add-ons if desired. For full version rollback, install the prior CP04 ZIP. Other Kodi add-ons and original skin settings are not modified.

Kodi, Trakt, Real-Debrid, Umbrella, Fen and Seren are not developed or hosted by this project. Use only media you have permission to access. No copyrighted movie art or personal tokens are included in the package.
