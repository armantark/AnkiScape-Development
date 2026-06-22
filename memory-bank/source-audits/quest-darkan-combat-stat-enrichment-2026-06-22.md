# Quest Darkan Combat Stat Enrichment - 2026-06-22

## Scope

Backend slice for generated quest combat encounters. The goal was to broaden
machine-readable NPC combat stats without hand-editing
`quest_catalog_generated.py` and without turning unsafe prose rows into
completable combat.

Frontend impact is contract-level only: the existing Quests tab already renders
`combat_locked`, `combat_missing_stats`, `combat_underpowered`, and
`combat_encounter` blockers. New frontend tests prove a generated Darkan-backed
fight can be selected when the global resolver is enabled and player combat
level is high enough.

## Sources Used

Primary local source precedence:

- Local 2011Scape NPC combat definitions:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions`
- Local Darkan/2012scape NPC combat definitions:
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/combatdefs`
- Local Darkan/2012scape NPC id/name/level list:
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/developer-information/npcList.txt`

The generator keeps 2011Scape first. Darkan is only a fallback for exact,
unambiguous normalized NPC name plus combat level matches. Ambiguous duplicate
combatdef sources and wrong-level rows stay statless.

## Implemented

- `tools/build_pre_eoc_quest_catalog.py` now loads Darkan combatdef JSON rows
  with hitpoints, attack, strength, defence, optional magic/ranged, max hit,
  attack style, attack range, attack bonus, and aggressiveness metadata.
- Darkan rows are keyed through `npcList.txt` by normalized display name plus
  combat level. Rows with missing core stats, level 0, ambiguous duplicate
  source candidates, or non-exact levels are not emitted.
- `parse_combat_encounters()` now asks a source-stat matcher that returns local
  2011Scape matches first and Darkan matches second.
- The generated catalog was regenerated through the builder.

## Proof Cases

- Demon Slayer: Delrith level 27 now carries Darkan stats from
  `uncategorized/delrith (nostats).json`: 70 hitpoints, 11 attack, 10 strength,
  5 defence, max hit 30, melee/passive config.
- Dragon Slayer: Elvarg level 83 now carries Darkan stats from
  `uncategorized/elvarg.json`: 800 hitpoints, 70 attack, 70 strength,
  70 defence, max hit 100, melee/aggressive config.
- Existing local 2011Scape matches still win, for example Count Draynor and
  Lesser demon rows keep their `.plugin.kts` sources.

## Safety Checks

- Lost City's generated level 63 Tree spirit stays statless. Darkan only has
  local level 14/101 Tree spirit rows in the available list, and those must not
  be forced onto the quest's level 63 encounter.
- Elemental Workshop's level 35 Earth Elemental stays statless because the local
  Darkan combatdefs have duplicate exact-match sources. The safer behavior is
  to keep it blocked until a focused source decision is made.
- Level 0 or source-unknown encounters remain blocked as missing stats even
  when the global combat resolver is enabled.

## Current Coverage

`python3 tools/audit_quest_stage_gate_coverage.py` after this slice:

```text
quests: 194
quests_with_stage_requirements: 194
stage_requirement_rows: 382
quests_with_item_or_tool_blockers: 171
quests_with_combat_blockers: 119
combat_encounter_rows: 286
combat_encounters_with_local_stats: 141
```

This is not all-quest combat parity. The remaining 145 statless generated
encounters are explicit source reconciliation debt, not completed content.

## Tests Added

- Catalog tests assert Delrith and Elvarg Darkan stats, preserve local
  2011Scape Count Draynor/Lesser demon precedence, and assert Tree spirit 63
  plus Earth Elemental 35 remain statless.
- Pure logic tests prove Demon Slayer's generated Darkan-backed Delrith gate is
  resolver-ready and writes `demon_slayer_delrith_27`.
- Runtime and integration smoke tests prove Quest review resolves the generated
  Darkan-backed fight before stage progression.
- Qt/offscreen tests prove the Quests tab shows `Blocked: Battle required:
  Delrith level 27` and leaves the Demon Slayer action selectable when the
  resolver and player stats allow it.

## Remaining Gaps

- 145/286 generated combat encounters still lack safe source-backed stats.
- The resolver is still a threshold gate, not a full combat simulation. Hit
  chance, equipment, food, prayer, poison, death handling, scripted boss
  mechanics, multi-phase fights, and encounter-specific route constraints remain
  future work.
- Broad stage parity remains open: generated rows still represent broad
  quest-detail blockers, not exact per-stage walkthrough mechanics for every
  quest.
