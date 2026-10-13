# CP01 locked baseline for CP02

CP02 implementation date: 13 October 2026. These are **upstream source snapshots inspected**, not a claim that the user's Fire Stick has the same versions installed.

| Component | Repository and inspected revision | Evidence |
|---|---|---|
| Kodi | 21.3 Omega selected | https://kodi.tv/download/android/ |
| Nimbus | `ivarbrandt/skin.nimbus`, `8b5071b8cd0db3a8e813eb00e9a821d3efad2454` (0.1.43) | `xml/Home.xml`, `xml/Includes_Home.xml`, `addon.xml` |
| Nimbus Helper | `ivarbrandt/script.nimbus.helper`, `e42d2ffffbccaa58386ef2e4a054049e5fcb7664` (0.0.52) | `resources/lib/modules/cpath_maker.py`, `version_monitor.py`, `xmls.py` |
| Umbrella | `umbrellaplug/umbrellaplug.github.io`, `3baead15cc75e6a17a708e1a4f884342d2e58295` (6.7.90) | `omega/plugin.video.umbrella/addon.xml` and router |
| Fen | `Tikipeter/Tikipeter.github.io`, `e5c183e771e477762ca0e9222b9c188584bf3dd0` (4.0.46 distribution) | `packages/`, `README.md`; internals **not inspected** |
| Seren | `nixgates/plugin.video.seren`, `b4f4b63bf59b38b93bd565a8503e121f64c91e30` (3.0.1) | `addon.xml` and router; older upstream code |
| Up Next | `im85288/service.upnext`, `592c7db536d12ace81ebfc64df85699012fc58b2` | future integration only |

**Implementation-critical Nimbus evidence**

- `xml/Includes_Home.xml`: widget list includes have `content_path`, `widget_header` and bounded `<content limit=...>` definitions.
- Nimbus Helper `cpath_maker.py`: builds generated widget XML under `special://skin/xml/` and can call `reload_skin()`; `version_monitor.py` can rebuild widgets on Kodi profile change.
- Therefore, configure the five widget paths once. Never regenerate Nimbus XML merely to rotate recommendations.
- Nimbus `addon.xml` lists GPL-2.0 and CC BY-SA 4.0. We distribute **no Nimbus files** or artwork.

**Unverified:** Kodi 21.3 runtime installation, actual profile storage choices, Nimbus settings UI flow and five-row performance on target hardware. The current repository began empty and public. No remote tokens or media are required for CP02.
