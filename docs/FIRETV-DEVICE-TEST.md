# Fire TV acceptance: CP02 on the actual 4K Max (2nd Gen)

**Status: PENDING**. Workstation unit tests do not establish device performance.

## Before installation

1. In Kodi, note its version/build and whether the installed APK is ARMV7A. Record Fire OS, available storage and display resolution (photos without account identifiers). Keep the same display and network connection across tests.
2. Back up Kodi's `.kodi/userdata` and Nimbus widget configuration using a trusted local method before changing widgets. Keep the backup **off GitHub**. If you cannot back up your existing setup, at least photograph every original widget source so restoration is possible.
3. Choose a harmless local video file you own for later playback regression testing. Do not include it or private URLs in reports.
4. Install the supplied ZIP and activate the fictional fixture set per Kodi profile as described in the [Nimbus setup guide](NIMBUS-WIDGET-SETUP.md).

## Four configurations

| ID | What to measure | Note |
|---|---|---|
| B0 | Stock Estuary / minimal | Broad Kodi overhead baseline; not equivalent to Nimbus |
| B1 | Stock Nimbus / minimal widgets | Nimbus idle/startup overhead |
| B2 | Stock Nimbus / five static rows | Use comparable item count, art and geometry; if can't match B3, mark inconclusive |
| B3 | Stock Nimbus / five Callen Prime widget URLs | Same profile, art, layout, network and cache state |

Do not claim a fair B2/B3 comparison if Kodi native library entries differ materially in art, playable status, widget overhead or count. Record the mismatch explicitly. You can still report separately measured B3 responsiveness.

## Repeatable sample process

1. Allow Kodi to settle for 60 seconds after any skin/widget edit. Do not time initial skin rebuilding as warm Home return.
2. For B2 and B3, make **at least ten** warm Home returns (30 preferred). Each trial: open a predetermined harmless page, press Back/Home to return, record time until rows are usable and the remote focus moves normally. Record durations in milliseconds, not an invented p95 from a handful of runs.
3. Measure ten deliberate left/right and up/down focus actions. Flag any repeated pause noticeably over 200 ms.
4. Record cold Kodi startup separately. Before and after startup, record whether posters/rows load while off-screen and how often plugin logs report `route=... local_ms=...`.
5. Disconnect Internet (leave Kodi running if practical), return Home and open every row; no network should be required to display CP02 content.
6. Switch Andy → Dad → Andy at least five cycles in Kodi. Check visible fixture differences and ensure no item from the previous profile leaks. Log whether **Nimbus itself** reloads; CP02 must not request it.
7. Play a local, authorised test video; pause/resume/return to Home. Check that the add-on doesn't interfere with playback. CP02 cannot start streams.
8. Restore your original widget layout. Disable CP02. Confirm original Home and add-ons work again.

### Diagnostic plugin comparator

In the same Nimbus widget slot, compare `?row=frozen` (P0) and `?row=probe` (P1). Both show the same three items and PNG assets. Use the `local_ms` log entries to compare on-device plugin runtime, not full skin latency. Ten samples minimum for a rough median, ideally thirty for reliable tail reporting.

### Recording evidence

Use [device-results-template.csv](device-results-template.csv) to record raw data. Note date, configuration, test ID, ms and conditions. Kodi logs may show plugin timing but might also include personal source URLs from unrelated add-ons: **never upload unredacted full logs**. A short phone video of remote navigation and profile switching is useful if it excludes account credentials.

### Acceptance gates

- Warm Home ≤500 ms (target, not prior observation).
- B3 median no more than 10% slower than an equivalent B2; if below measurement resolution or non-equivalent, mark **INCONCLUSIVE**.
- No recurring focus stalls >200 ms, no noticeable playback interruption, no content crossing profile boundaries, no unexpected Callen Prime network calls, and no repeated skin reloads caused by Callen Prime.
- If performance fails, reduce the number of widget rows or items **before** considering a Nimbus fork. If the setup fails, record the first unworkable step.
