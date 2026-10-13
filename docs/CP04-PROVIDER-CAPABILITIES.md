# CP04 Provider Capability Review

Date: 13 October 2026. Source investigation only; not a Fire TV runtime result.

| Provider | Add-on ID | Source / version | Route | CP04 decision |
| --- | --- | --- | --- | --- |
| Umbrella | plugin.video.umbrella | 6.7.90 | action=play_Item | Opt-in prototype, exact-version gated |
| Fen | plugin.video.fen | Package 4.0.46; current internals not verified | Unverified | Disabled |
| Seren | plugin.video.seren | 3.0.1; older upstream source | action=getSources with action_args | Disabled |

Umbrella route evidence: https://github.com/umbrellaplug/umbrellaplug.github.io/blob/master/omega/plugin.video.umbrella/resources/lib/modules/router.py

Seren route evidence: https://github.com/nixgates/plugin.video.seren/blob/master/resources/lib/modules/router.py

Kodi documents xbmcplugin.setResolvedUrl for playable plugin entries, and its PluginDirectory supports bounded recursion for nested plugin:// URLs. That makes an Umbrella URL handoff plausible; it does NOT prove actual source resolution or provider interoperability.

Kodi documentation: https://xbmc.github.io/docs.kodi.tv/master/kodi-dev-kit/group__python__xbmcplugin.html

The CP04 adapter requires a real manually supplied title, numeric TMDb movie/series ID and year, with season and episode for series. It strictly encodes parameters, refuses demo IDs and refuses unknown addon versions. The source-derived play_Item action is not a public stable Umbrella API. The handoff may still fail for missing metadata, invalid manual IDs, absent account authorisation or no available provider source.

Provider discovery uses Kodi Addons.GetAddonDetails with only installed/enabled/version and runs only when the user opens Playback Tests or explicitly requests a provider action. It never reads addon tokens or uses Real-Debrid directly.

A Callen Prime per-profile opt-in flag is required in addition to the provider being installed. Kodi/profile ambiguity, malformed IDs, missing provider, version mismatch and cancelled dialogs fail closed. No automatic switch to Fen or Seren is permitted.

### Known unverified behaviour

- Whether the nested plugin resolver and Umbrella playlist semantics succeed on Kodi 21.3.
- Whether Umbrella's current source code requires richer metadata or other identifiers.
- Whether provider cancellation cleanly restores native focus on Nimbus.
- Whether Kodi profiles truly isolate the corresponding third-party add-on authorisation in the target device configuration.

No player monitor, external API polling, skin XML rewriting or auto-scrobble writer was introduced. CP04 remains DEVICE HOLD until a physical test.

Project source is MIT. Third-party Kodi, Nimbus and provider packages are not bundled or modified.
