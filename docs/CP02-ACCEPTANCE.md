# CP02 acceptance record

## Source/build gates (off-device)

- [x] Five stable offline routes, eight-item cap, safe unknown route.
- [x] Synthetic catalogue, distinct demo presets, neutral fallback.
- [x] Player never invoked, no service extension, no network dependencies.
- [x] Profile-scope binding tests, duplicate-label guard, shared-path fail-closed behaviour.
- [x] Deterministic top-level Kodi ZIP packaging; SHA-256 recorded in report.
- [x] Safe optional setup and rollback guidance.
- [ ] **Installable on real Kodi 21.3 verified:** device evidence required.

## Device acceptance (not yet observed)

- [ ] Kodi accepts ZIP and opens Video add-on.
- [ ] Nimbus exposes five independently configured rows with the intended labels.
- [ ] No repeated skin XML regeneration on ordinary navigation.
- [ ] Andy/Dad profile switching exposes only current-profile demo snapshot or neutral fallback.
- [ ] Offline five-row navigation works.
- [ ] Fair B2/B3 baseline captured, results satisfy target or honestly marked inconclusive.
- [ ] Local player experiences no regression.
- [ ] Original widgets restored and add-on disabled/removed cleanly.

**Current disposition: BUILD-READY only; DEVICE ACCEPTANCE PENDING.** Do not promote CP03 on source tests alone.
