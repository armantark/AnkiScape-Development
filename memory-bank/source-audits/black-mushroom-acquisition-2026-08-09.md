# Black mushroom acquisition audit — 2026-08-09

## Scope and verdict

This slice closes the ordinary acquisition route for `Black mushroom` and
corrects its existing grinding action. `Black mushroom ink` was registered but
blocked because no player could obtain its source item.

**Verdict:** one Utility action picks up one Black mushroom from the ground near
Uzer or in the Goblin Cave. Grinding one mushroom consumes one empty Vial and
produces one Black mushroom ink. Both items are non-stackable and
non-exchangeable. No placeholder is necessary.

## Period evidence

### Ground source and recipe

- RuneScape Wiki `Black mushroom`, oldid `5513228`, timestamp
  `2012-04-19T18:18:44Z`:
  <https://runescape.wiki/w/Black_mushroom?oldid=5513228>.
- The cutoff page says that Black mushrooms grow in shaded areas around Uzer
  and in the Goblin Cave. It also says that using a pestle and mortar while an
  empty Vial is in the inventory produces Black mushroom ink.
- RuneScape Wiki `Black mushroom ink`, oldid `6084503`, timestamp
  `2012-08-13T06:25:15Z`:
  <https://runescape.wiki/w/Black_mushroom_ink?oldid=6084503>.
- The ink page independently states the same one-mushroom plus one-empty-Vial
  recipe. Without the Vial, the source says that no ink is obtained.

### Item identity

OpenRS2 revision 742, dated 2012-11-07, pins both definitions:

| ID | Item | Model | Stackable | Exchangeable | Relevant option |
| ---: | --- | ---: | --- | --- | --- |
| 4620 | Black mushroom | 6151 | No | No | `Grind` |
| 4622 | Black mushroom ink | 2789 | No | No | `Empty` |

The exact query was:

```text
tools/query_openrs2_cache.sh '/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/742-2012-11-07/cache' --id 4620 4622
```

## Product translation

- `gather_black_mushrooms` is a zero-XP Utility gathering action. Each answered
  card collects one ground item. World travel and respawn waiting stay outside
  the review model, as they do for the existing source-gathering rows.
- `grind_black_mushroom` now requires both one Black mushroom and one Vial.
  It consumes both and produces one Black mushroom ink. The old mushroom-only
  action was a concrete parity defect.
- Both source-period sprites are normalized to their tight alpha bounds and
  registered for the Utility row, grinding row, Bank, and item registry.
- The graph changes from 1,550 actions / 2,423 reachable items / 111 orphan
  inputs / 111 blocked actions to 1,551 / 2,425 / 110 / 110.

## Asset provenance

| Asset | Upload timestamp | SHA-1 | Dimensions |
| --- | --- | --- | --- |
| `herbloreitems/black_mushroom.png` | `2011-11-18T02:55:42Z` | `04372b1c2a83176147a56fe413a061479f94069d` | 15×31 |
| `herbloreitems/black_mushroom_ink.png` | `2010-04-25T12:56:24Z` | `f5cde78fd6a21412f11e34fc01d91db4ccb30952` | 21×30 |

## Explicit omissions

- This slice does not recreate travel, ground-spawn timers, or the quest uses
  of the ink.
- It does not claim that one review equals one complete trip. One review is one
  source pickup.
- Quest-specific dye and program actions remain owned by their quest lanes.

## Acceptance contract

- The gathering action must add one Black mushroom and no XP.
- The grinding action must fail without an empty Vial and must consume one Vial
  on success.
- Review undo must restore the gathered item state.
- Utility metadata and the real Qt selector must show the period mushroom icon.
- Reachability must name both Utility routes.
- Item identities, trade rules, asset timestamps, hashes, and dimensions must
  remain pinned by tests.
