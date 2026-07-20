# Desert goat Combat acquisition audit — 2026-07-20

## Decision

Ship one ordinary level-23 `Goat` Combat target as the canonical direct
acquisition route for Desert goat horn. It reuses the existing Combat loop,
carried-inventory banking, desert-heat hazard, drop handling, undo, and target
picker. No new interface or owner-facing design decision is introduced.

The period record and Darkan reconcile the level-23 Goat completely enough for
the current Combat schema. Billy Goat is not duplicated: it provides the same
guaranteed outputs but its period 320 LP conflicts with Darkan's 280 LP.

## Period authority

RuneScape Wiki `Goat`, oldid
[`5795580`](https://runescape.wiki/w/Goat?oldid=5795580), timestamp
`2012-06-21T10:33:02Z`, establishes:

- combat level 23 and 210 LP;
- passive, non-poisonous melee combat;
- a 47-LP maximum hit;
- guaranteed Bones and one Desert goat horn; and
- the Kharidian Desert habitat.

RuneScape Wiki `Desert goat horn`, oldid
[`6555637`](https://runescape.wiki/w/Desert_goat_horn?oldid=6555637),
timestamp `2012-11-14T21:01:13Z`, independently establishes:

- one horn always drops from a level-23 Goat;
- item ID 9735's non-stackable, tradeable item semantics;
- grinding with a pestle and mortar produces Goat horn dust;
- the Nardah banking route; and
- desert heat as a real carried-water risk while harvesting horns.

RuneScape Wiki `Goat horn dust`, oldid
[`6404814`](https://runescape.wiki/w/Goat_horn_dust?oldid=6404814),
timestamp `2012-10-14T17:11:32Z`, establishes the non-stackable, tradeable
output identity and its Combat-potion and Smoke-devil uses.

## Cache and implementation reconciliation

OpenRS2 revision 742 (`2012-11-07`) contains attackable Goat NPCs 4930, 4931,
4933, and 4934; item 9735 as `Desert goat horn` with `Grind`; and item 9736 as
`Goat horn dust`. These client definitions corroborate identity and interaction,
not server-side combat or drop behavior.

Darkan commit `0d1a8e4c404a12f0626a97c9038c7b09e571e9ff` contains:

- `data/npcs/combatdefs/uncategorized/goat.json`: 210 LP, 47 maximum,
  Attack/Strength/Defence 20, Magic/Ranged 1, passive melee, and a 59-tick
  respawn;
- `data/npcs/drops/goat.json`: separate always tables for Bones (526) and
  Desert goat horn (9735), quantity one; and
- `src/main/java/com/rs/utils/drop/DropList.java:43-68,98-146` plus
  `DropTable.java:87-97,147-149`: zero-denominator tables are unconditional and
  every `dropOne=false` member is emitted.

The server rows therefore reproduce both period-guaranteed outputs exactly.
The five executable combat levels and respawn are reconstruction evidence;
they do not conflict with the period page. Four attack ticks are the standard
bounded ordinary-Combat abstraction because the period page does not state the
interval.

## Player-facing translation

- One successful Combat review advances the existing live cadence loop.
- Goat participates in the existing Kharidian desert hazard: a filled
  waterskin is required and one dose is consumed per damaging Combat review.
- Every kill awards Bones and one Desert goat horn.
- The existing no-XP `Grind desert goat horn` action turns carried horns into
  Goat horn dust in batches capped at 28.
- The existing level-36 Combat-potion recipe now has a complete live
  acquisition chain.

The item registry now preserves source IDs 9735/9736, non-stackability,
tradeability, and real period-pinned art. Goat horn dust no longer inherits the
generic soft-clay fallback icon.

## Assets

- `combatenemies/goat.png`: `File:Desert Goat.png`, revision timestamp
  `2010-06-06T13:57:45Z`;
- `herbloreitems/desert_goat_horn.png`: `File:Desert goat horn.png`, revision
  timestamp `2010-07-23T21:54:03Z`; and
- `summoningitems/goat_horn_dust.png`: `File:Goat horn dust.png`, revision
  timestamp `2009-03-04T15:50:47Z`.

All three are RS3-wiki historical-file revisions fetched before the cutoff,
recorded in `assets_provenance.json`, and tight-alpha normalized. The global UI
asset audit reports no padded small sprites.

## Exclusions and unresolved evidence

- Billy Goat is not a second target because it adds no acquisition route and
  its LP conflict remains unresolved.
- Exact Goat attack speed is not period-proven. The ordinary four-tick Combat
  abstraction is disclosed in `source_status`.
- No Scabarite, Corporeal Beast, Soul Wars, or Familiarisation route is inferred
  from this slice.
- No owner-facing design gap emerged.

## Verification map

- `tests/test_combat_enemy_roster.py`: schema, target asset, provenance.
- `tests/test_combat_logic.py`: 210 LP / 47 maximum preview, guaranteed
  Bones-and-horn roll, desert context.
- `tests/test_skill_and_item_registry.py`: item IDs, non-stackability,
  tradeability, and real asset paths.
- `tests/test_herblore_assets.py`: period-pinned horn and dust provenance.
- `tests/test_item_reachability_audit.py`: `Desert goat horn -> combat:goat`.
- `tests/test_ui_asset_normalization.py`: repository-wide tight-alpha invariant.
- `tests/test_target_metadata.py`: missing-water lock, Animals grouping,
  guaranteed-horn tooltip, and enemy-image path.
- `tests/test_main_menu_widget.py`: rendered Qt row text, desert state, drop,
  and non-null icon.

The focused seven-module run passes 425 tests, and the focused offscreen Qt row
check passes. The complete non-Qt and offscreen Qt discoveries each pass all
1,903 tests (250 expected skips in the non-Qt runner; one platform skip in the
Qt runner). Documentation, test-quality, byte-compilation, diff-whitespace, and
worktree-safety gates pass.

A restarted native Anki smoke loaded one add-on menu and one disabled
`Goat (Lvl 23)` row under `Animals` with its real goat portrait on a live save
without a filled waterskin. The target was not selected and the save was not
mutated.

Reachability moves from 1,982 to 1,989 reachable items, 253 to 247 orphan inputs
(98/155 to 97/150 root/cascade), and 268 to 260 unresolved actions without
adding a fake seed or shop route.
