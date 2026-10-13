# Theatre 0.5.1 | Fire Stick first-run acceptance

**Device:** Fire TV Stick 4K Max (2nd generation), Kodi 21.3 Omega

**All checks below require observation on the actual device. None is marked PASS by workstation tests.**

## First-run in five minutes

1. Install the v0.5.1 ZIP and open Video add-ons → Callen Prime Theatre.
2. Select the FIRST item: **OPEN CALLEN PRIME THEATRE**. You should leave the ordinary directory and see a full-screen dark theatre with CALLEN PRIME heading, navigation and two horizontal rows. If it stays a file list, report that exact behaviour; it is an installation/launcher blocker.
3. Use Left/Right on a poster row and Up/Down between rows. At the bottom row, Down should reveal the next two rows if more exist. Back should return to Kodi.
4. Select Movies / Series / Anime / My List / Search / Sources on the top navigation. Observe that the layout remains consistent and no Kodi skin reload occurs.
5. If the Kodi media library contains a film, select it → DETAILS → PLAY. Kodi should play the existing library file. If the library is empty, open SOURCES → UMBRELLA (or your installed provider) instead; provider browsing intentionally uses that provider's normal interface.
6. If your dad has a separate Kodi profile, switch profiles through Kodi, launch Callen Prime again and check My List and content. Do not assume your media databases are private if Kodi is configured to share them.
7. Check Back / Pause / Resume / Stop, plus playback interruption and picture decoding on the TV. No autoplay or trailer should launch without a selection.
8. Press Back, inspect original Kodi Home and open an existing addon to verify no regression.

## Performance record

Record at least 10 warm theatre openings from Kodi and 10 horizontal/vertical remote moves. When possible compare with the CP04 addon and Kodi Home. Rough targets: no repeat focus stall above 200ms, no background network triggered by poster selection and no playback interruption. **Do not claim a 500ms warm home target from source-level test timings.** Record free RAM/storage and the number of movies/episodes in your Kodi database because large libraries can affect initial JSON-RPC calls. The renderer caps its initial reads at 65 movies, 45 series and 45 episodes, but Kodi's core may still do internal database work.

## Known limitations to investigate on-device

- Kodi `WindowXMLDialog` screen and custom skin texture fallback must be validated on the actual skin and Android build.
- Kodi skins differ in font declarations; fallbacks should prevent complete text loss, but alignment needs visual inspection.
- Player may not return focus exactly to the theatre after stopping in every Kodi configuration.
- Exiting to another provider may return to the Kodi browser rather than directly to the Callen Prime overlay.
- Direct Trakt login and provider-fed integrated discovery are not implemented.
- Real artwork depends on your Kodi metadata. Empty libraries show source tiles.
- The new fullscreen screen does not automatically replace Kodi's system Home. Pin it as a favourite if desired.

If the window crashes or cannot load, do not remove Kodi. Capture the last relevant `[Callen Prime]` log lines without credentials or private source URLs, and restore CP04 if necessary.
