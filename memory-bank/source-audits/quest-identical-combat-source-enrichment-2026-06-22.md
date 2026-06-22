# Quest Identical Combat Source Enrichment - 2026-06-22

## Scope

Backend and contract-test follow-up for the remaining quest combat stat gap.
This slice only accepts exact local Darkan/2012scape duplicate candidates when
their captured battle stats/configs are identical. It does not weaken the
global combat lock or make conflicting source rows completable.

Frontend impact is limited to the existing Quests tab contract: newly
resolver-ready encounters show `Battle required` when the resolver is enabled,
and still use the same disabled/blocker state otherwise.

## Sources Used

- Generated catalog input: `tools/build_pre_eoc_quest_catalog.py`
- Darkan NPC list:
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/developer-information/npcList.txt`
- Darkan combatdefs:
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/combatdefs`
- Focused override layer: `quest_data.py`

## Implemented

- The generated catalog builder now groups Darkan exact name+combat-level
  candidates by captured `npc_stats` and `npc_configs`, ignoring source path.
- If exactly one stats/config group exists, the row is safe to enrich and
  `npc_stats_source` records every contributing source path separated by `; `.
- If more than one stats/config group exists, the row stays statless and the
  resolver continues to block it as `combat_missing_stats`.
- The focused `quest_data.py` override layer now carries Darkan stats for:
  - Tai Bwo Wannai Trio: Jogre level 53 from
    `uncategorized/jogre/jogre_(53).json`.
  - Swan Song: Sea Troll Queen level 170 from
    `uncategorized/sea_troll_queen (noanims).json`.

## Proof Cases

- Elemental Workshop I/II/III/IV: Earth Elemental level 35 now carries shared
  Darkan stats from both `earth_elemental.json` and `earth_elemental_rock.json`
  because captured battle stats/configs match.
- Tai Bwo Wannai Trio: Jogre level 53 now carries 600 hitpoints, 43 attack,
  43 strength, and 43 defence.
- Swan Song: Sea Troll Queen level 170 now carries 2000 hitpoints, 100 attack,
  70 strength, 100 defence, and 150 magic.

## Preserved Blocks

- Priest in Peril: Monk of Zamorak level 30 remains statless because exact
  Darkan candidates disagree.
- Troll Stronghold: Dad level 101 remains statless because exact Darkan
  candidates disagree.
- Lost City: Tree spirit level 63 remains statless because local exact
  name+level stats are still missing.
- Level 0 prose/group rows remain statless.

## Current Coverage

`python3 tools/audit_quest_stage_gate_coverage.py` after this slice:

```text
quests: 194
quests_with_stage_requirements: 194
stage_requirement_rows: 382
quests_with_item_or_tool_blockers: 171
quests_with_combat_blockers: 119
combat_encounter_rows: 286
combat_encounters_with_local_stats: 147
```

This is not all-quest combat parity. The remaining 139 statless combat rows are
explicit source reconciliation debt.

## Tests Added

- Catalog tests assert Earth Elemental, Jogre, and Sea Troll Queen stats and
  assert Monk of Zamorak plus Dad remain statless.
- Pure logic tests prove Elemental Workshop I's Earth Elemental gate is
  resolver-ready and writes `elemental_workshop_i_earth_elemental_35`.
- Runtime and integration smoke tests prove Quest review resolves the
  identical-source generated fight without advancing the quest stage on the same
  review.
- Qt/offscreen tests prove the Quests tab shows `Blocked: Battle required:
  Earth Elemental level 35` and leaves the Elemental Workshop action selectable
  when resolver and player combat state allow it.

## Remaining Gaps

- 139/286 combat encounters still lack safe source-backed stats.
- Full combat simulation remains future work: hit chance, equipment, food,
  prayer, death, poison, multi-phase mechanics, and scripted quest rules are not
  implemented by this stat gate.
- Generated stage rows remain broad quest-detail gates, not exact
  minute-by-minute walkthrough parity.
