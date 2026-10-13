# CP04 Fire TV Device Acceptance

**Not yet performed. Do not label DEVICE-PASS without physical evidence.**

## Before installing

1. Record Kodi version (target 21.3 Omega), current profile and Nimbus configuration. Back up or photograph your existing widgets; do not reset Kodi.
2. Keep the previous CP03 test ZIP for rollback.
3. Install Callen-Prime-Theatre_CP04_v0.4.0-test.zip through Kodi Settings → Add-ons → Install from zip file.
4. Open Add-ons → Video add-ons → Callen Prime Theatre (CP04 Prototype). Confirm Movies, Series, Anime and the original five offline demo rows remain available.

## Local playback test

1. Prepare a short original local video file you own on Fire TV storage.
2. Open Playback Tests → Play a local test video.
3. Cancel once. No playback should begin.
4. Select the video but decline the confirmation. Nothing should play.
5. Select it again and confirm. Verify Kodi starts playing; test Pause, Seek, Resume, Stop and Back to the prior menu.
6. Note any perpetual spinner, focus loss or unexpected playback. Network paths and arbitrary URLs are intentionally rejected.

## Umbrella test (optional)

1. Do not install or upgrade a provider just for this test. Only installed/enabled Umbrella **6.7.90** is supported by the CP04 prototype.
2. In the current Kodi profile open Playback Tests and explicitly enable Umbrella for Callen Prime.
3. Choose Play using Umbrella. Manually enter a real title, TMDb ID and release year, plus season/episode if appropriate. Confirm the final handoff.
4. Record whether Umbrella takes control of sources and playback or displays an error. If cancelled, verify no duplicate resolver and no fallback provider begins.
5. Switch to another Kodi profile. Confirm no Umbrella opt-in was inherited. Disable opt-in on the first profile if desired.

Do not share private media paths, source URLs, account IDs or unredacted Kodi logs.

## Performance and rollback

Compare warm Home return with CP03 on the same Kodi setup, same five rows and artwork, and similar device conditions. Target warm Home at or below 500 ms and no repeat remote-focus stalls above 200 ms; report actual samples rather than guesses. Confirm zero Callen Prime network requests on passive widget navigation. Test briefly with Internet disconnected.

Restore existing widget settings or reinstall CP03 to roll back. Uninstalling/disabling Callen Prime must not modify Kodi, Nimbus or another provider's authorisation.

## Return these results

- Kodi installed CP04 ZIP: Yes / No.
- Local video selection cancellation: Safe / Not safe.
- Local video playback, pause/seek/stop/back: Pass / Fail / Not tested.
- Umbrella version and handoff result: Pass / Fail / Not available / Not tested.
- Andy/Dad profile separation: Pass / Fail / Not tested.
- Navigation observations, rough timing or short video without account details.

**Acceptance stays HOLD until these tests are actually observed.**
