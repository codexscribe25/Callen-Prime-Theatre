# CP05 conditional handoff | Viewer profiles and Trakt

CP05 must start from the CP04 branch only after actual Kodi installation and critical playback behaviour have been observed. CP02/CP03 UI and performance gates remain unverified on the Fire Stick.

## Candidate scope

- Establish that Kodi profiles on the target Fire TV isolate the add-on data directories and installed provider credentials as intended.
- Connect independent viewers to individual Trakt accounts using official, profile-scoped OAuth only; no shared tokens, repository copies or cross-profile history.
- Select exactly **one owner of watched progress and scrobbling**. The same viewing event must not be written twice by Callen Prime and Umbrella/Fen/Seren.
- Treat playback providers as owners of source discovery, account authorisation and their own internal continuation.
- Use cached Trakt results and bounded refresh work. Passive Home and widget navigation must never block on network or refresh artwork unnecessarily.
- Handle expired tokens, unavailable Trakt, incomplete progress and user logout with safe, profile-local fallbacks.
- Preserve five fixed widget paths. Contextual content should update only at safe navigation boundaries without Nimbus XML regeneration.

## Release gates

CP02/CP03 five-row responsiveness and actual CP04 local playback/Back behaviour must be tested on Fire Stick. An unverified Umbrella route must stay separately held, not silently accepted. No account connection on an ambiguous/shared profile storage path.

## Security

The repository is public. Never write personal watch histories, Trakt OAuth credentials, provider API keys, raw Kodi logs or playable source links to GitHub.
