# Summoning point-restoration source audit (2026-07-17)

Scope: close the ordinary pre-EOC Summoning-potion and super-restore effects,
including vial/flask identity and the separate familiar special-move pool.
Cutoff: 2012-11-20.

## Pinned period sources

- **Summoning potion**, oldid
  [6462617](https://runescape.wiki/w/Summoning_potion?oldid=6462617),
  2012-10-24 05:25:05 UTC.
- **Super restore**, oldid
  [6387712](https://runescape.wiki/w/Super_restore?oldid=6387712),
  2012-10-12 08:09:02 UTC.
- **Summoning points**, oldid
  [6542597](https://runescape.wiki/w/Summoning_points?oldid=6542597),
  2012-11-08 06:20:13 UTC.

The pinned pages distinguish ordinary Summoning points from familiar
special-move points. A Summoning potion restores `floor(base Summoning / 4) +
7` ordinary points and 15 familiar special-move points. A super restore
restores lowered stats, Prayer, and Summoning by `floor(base / 4) + 8`, capped
at each base value, but does not restore familiar special-move points.

## Emulator corroboration

Darkan commit `e488619ada8c40eb1f066eb49f5b50485b16b6af`,
`darkan-world-server/src/main/java/com/rs/game/content/Potions.kt:239-245`,
implements the super-restore `8 + 25%` stat restoration for both vials and
flasks. Lines `398-407` implement Summoning potion `7 + 25%` restoration plus
15 familiar special points.

The same rows pin the supported item IDs:

| Family | Vial IDs, four doses to one | Flask IDs, six doses to one |
| --- | --- | --- |
| Summoning potion | 12140, 12142, 12144, 12146 | 23621, 23623, 23625, 23627, 23629, 23631 |
| Super restore | 3024, 3026, 3028, 3030 | 23399, 23401, 23403, 23405, 23407, 23409 |

## Implemented boundary

`potion_data.py` registers both complete dose families. `logic_pure.py`
restores only state AnkiScape actually models: drained Combat levels, Prayer,
ordinary Summoning points, and the separate familiar special pool. Restoration
is capped at the corresponding base value and consumes exactly one dose.
Bob Barter's existing dose-preserving service handles the new vial families.

This is a fully source-shaped consumable transaction. It does not invent
wall-clock recovery or merge ordinary Summoning and special-move points.
