# CP02 architecture: five stable widget paths, zero network

## Selected design (Architecture A)

```text
Stock Kodi 21.3 + stock Nimbus
    │ five user-configured plugin paths (no runtime XML edits)
    ▼
plugin.video.callenprime/default.py     [Kodi python pluginsource only]
    ├─ resources/lib/rows.py             [≤8 entries, no network]
    ├─ resources/lib/profile.py          [per-invocation Kodi scope check]
    └─ resources/lib/fixtures.py         [package fixtures / neutral fallback]
    │
    └─ special://profile/addon_data/plugin.video.callenprime/demo_snapshot.json
```

No worker thread, background service, SQLite DB, Trakt, source resolver, autoplay, external art or skin fork. User manually activates the fictional Andy/Dad preset in **each** Kodi profile. The optional snapshot is copied to that profile's effective `special://profile` directory by the explicit activation operation and atomically replaced there. Ordinary widget calls never write files.

## Contract

| Widget title (stable) | URI |
|---|---|
| Continue Watching | `plugin://plugin.video.callenprime/?row=continue` |
| What's New | `plugin://plugin.video.callenprime/?row=new` |
| Based on Your Watching | `plugin://plugin.video.callenprime/?row=context-a` |
| Fresh for You | `plugin://plugin.video.callenprime/?row=context-b` |
| Discover Something Different | `plugin://plugin.video.callenprime/?row=context-c` |

Each route returns four fictional, bounded folder items with `CP02 DEMO` labels and local 240×360 PNGs. Item selection opens a non-playing explanatory dialog. Unknown routes return empty directories. Content does not change on remote focus.

## Profile isolation

Kodi JSON-RPC supplies the current profile and configured profile labels. Its label is **not** used as the unique identity, because profile display names can collide. The effective `special://profile` directory is the scope anchor, fingerprinted locally with SHA-256. Snapshot values are bound to that path and the profile label, and duplicate configured labels fail closed. If the directory is shared but the label changes, the previous profile's snapshot is rejected and neutral fixtures are shown. If Kodi exposes no unambiguous scope, neutral fixtures are shown. Two genuinely indistinguishable Kodi profiles cannot be isolated by this mechanism and **must not be assigned private real data**; CP02 contains only fictional content. Device testing determines whether the selected Kodi profile setup has separate effective paths.

There is no user-supplied `profile` parameter for listing routes. The UI labels Andy/Dad are merely named test presets, not authentication. The selected preset is never pushed to GitHub.

## Performance and P0/P1

- P0: `?row=frozen` returns three identical static catalogue items, no scope lookup.
- P1: `?row=probe` looks up current Kodi scope and validates snapshot, then returns **exactly the same three items**. URI action differs only by `row=`, so compare list content rather than literal paths.
- Both incur Kodi's Python plugin startup and listing work; their difference approximates the cost of profile/snapshot validation, **not** overall Nimbus or artwork decoding cost.
- Actual B0 (Estuary), B1 (minimal Nimbus), B2 (five comparable static Nimbus rows) and B3 (five CP02 paths) are a physical-device experiment, not inferred from these tests.
- `xbmc.log` writes `[Callen Prime CP02] route=X local_ms=Y`. No paths, tokens, media URLs or profile names are logged. Times exclude Kodi external skin and artwork render time.

## Known boundaries

Nimbus widget *configuration* may reload the skin. CP02 does not perform reloads; Kodi/Nimbus may still reload on profile switching. Some Kodi skins may treat folder items differently from playable media; CP02 chooses safe, non-playable folder items instead of fake playable sources. Any resulting layout mismatch is measured and recorded, not silently altered to add playback.

All three neutral PNG poster tiles are original synthetic graphics from this commission. Project source, documentation and placeholder art distributed under MIT (see LICENSE). Neither Kodi nor Nimbus source is bundled.
