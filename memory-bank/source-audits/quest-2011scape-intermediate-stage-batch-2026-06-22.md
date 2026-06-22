# 2011Scape Intermediate Quest Stage Batch - 2026-06-22

## Scope

Backend and frontend continuation for the active all-quest stage-gate goal. This
pass does not claim every quest is complete. It upgrades three high-impact quest
flows from broad generated blockers into local 2011Scape-backed stage data:
The Restless Ghost, Rune Mysteries, and Lost City.

## Sources

- The Restless Ghost:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/quests/impl/TheRestlessGhost.kt`
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/lumbridge/father_urhney.plugin.kts`
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/lumbridge/restless_ghost.plugin.kts`
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/lumbridge/rock_with_skull.plugin.kts`
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/lumbridge/ghost_coffin.plugin.kts`
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/undeads/skeleton_warlock_lvl_11.plugin.kts`
- Rune Mysteries:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/quests/impl/RuneMysteries.kt`
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/lumbridge/duke_horacio.plugin.kts`
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/draynor/sedridor.plugin.kts`
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/varrock/aubury.plugin.kts`
- Lost City:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/quests/impl/LostCity.kt`
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/lumbridge/warrior.plugin.kts`
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/lumbridge/lostcity_tree.plugin.kts`
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/lumbridge/shamus.plugin.kts`
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/entrana/entrana.plugin.kts`
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/lumbridge/lostcity_shed.plugin.kts`
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/undeads/tree_spirit_lv_101.plugin.kts`

## Backend

- Added quest `start_inventory` support so source-granted quest items can enter
  the flat inventory at quest start without becoming start requirements.
- Changed stage advancement to advance from the computed current stage. This
  prevents a started quest at progress `0` from reprocessing stage 1 after the
  first successful stage transition.
- The Restless Ghost now models Father Urhney producing a Ghostspeak amulet,
  the ghost conversation requiring that amulet, the skull search producing
  Muddy skull, and the coffin handoff consuming Muddy skull only after the
  Skeleton warlock gate is resolved.
- Rune Mysteries now models Duke Horacio giving Air talisman at start, Sedridor
  consuming it to produce Research package, Aubury consuming the package to
  produce Research notes, and the final Sedridor handoff consuming the notes
  before the Air talisman reward. The old generated Magic/Runecrafting XP is
  removed because local 2011Scape does not award it.
- Lost City now models Find Shamus, Shamus/Entrana route state, Tree spirit
  combat with local stats, Dramen branch production with a hatchet, and Dramen
  staff production with a knife. Dramen staff is no longer duplicated as a final
  quest reward.
- Tree spirit is now resolver-ready from local 2011Scape NPC stats while still
  retaining quest text level 63 for the blocker.

## Frontend

- No new widget contract was needed. The existing Quests tab continues to show
  `blocked_at_stage` and receives compact blocker reasons from the pure backend.
- Qt/offscreen coverage now proves the Restless Ghost combat button is enabled
  only at the real muddy-skull/coffin stage with the resolver enabled.
- Runtime and integration tests now complete Rune Mysteries from the sourced
  Research notes stage and assert that no false XP is awarded.

## Current Audit Counts

`python3 tools/audit_quest_stage_gate_coverage.py` after this slice:

```text
quests: 194
quests_with_stage_requirements: 194
stage_requirement_rows: 396
quests_with_item_or_tool_blockers: 174
quests_with_combat_blockers: 119
combat_encounter_rows: 283
combat_encounters_with_any_stats: 176
combat_encounters_with_resolver_stats: 175
requirement_row_kinds:
  consumed_inventory: 19
  consumed_inventory_options: 1
  inventory: 210
  inventory_options: 60
  produced_inventory: 10
  tools: 91
quests_without_stage_requirements:
```

Computed from live `quest_data.py` override/addition maps: 73 focused stage
rows and 323 generated rows remain in the 396-row stage requirement set.

`python3 tools/audit_quest_combat_stat_gaps.py` after this slice:

```text
statless_combat_encounters: 108
classifications:
  darkan_hitpoints_only_metadata: 51
  darkan_missing_resolver_stats: 18
  darkan_same_name_wrong_level: 7
  no_local_source_match: 13
  parser_or_variant_level: 19
```

## Verification

Focused checks:

```bash
python3 -m unittest tests.test_quest_catalog tests.test_logic
python3 -m unittest tests.test_runtime_actions tests.test_integration_smoke
QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget
```

Required full suites:

```bash
python3 run_tests.py
QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests
```

Results:

```text
python3 run_tests.py: Ran 463 tests in 4.461s - OK (skipped=108)
QT offscreen discover: Ran 463 tests in 99.979s - OK
```

## Manual Anki Test Instructions

1. Restart Anki with this add-on enabled and open AnkiScape.
2. Set current skill to Quests.
3. Start Rune Mysteries and confirm the inventory receives `Air talisman x1`.
   Progress the Sedridor stage with the matching action flag and confirm the
   talisman is consumed and `Research package x1` appears.
4. Progress Rune Mysteries through Aubury and back to Sedridor. Confirm
   `Research package` becomes `Research notes`, the notes are consumed on
   completion, `Air talisman x1` is awarded once, and no Magic or Runecrafting
   XP is awarded.
5. Start The Restless Ghost and confirm stage 1 blocks on Father Urhney's
   action until the Ghostspeak amulet is produced. Confirm the muddy skull
   appears after the skull search, and the coffin stage blocks on Skeleton
   warlock combat while the global combat resolver is disabled.
6. Enable `player_data["quest_combat_config"]["resolver_enabled"]`, provide
   sufficient player combat stats, resolve Skeleton warlock, then answer one
   Quest review and confirm `Muddy skull` is consumed and completion parks 125
   Prayer XP in `pending_skill_exp_rewards`.
7. Start Lost City with Crafting 31 and Woodcutting 36. Confirm Shamus and
   Entrana route blockers appear before Tree spirit, Tree spirit is combat
   locked by default, resolving it does not auto-complete the quest, Dramen
   branch is produced from the hatchet stage, and Dramen staff is produced once
   from the knife/staff/shed stage.

## Remaining Gaps

- Full all-quest minute-detail parity remains open. The plugin has 323
  generated stage rows that need source-backed per-stage extraction or explicit
  blocker notes.
- Combat remains globally locked by default and 108 statless combat rows remain
  blocked pending a new source class or full combat simulation.
- Route/location flags, branch state, puzzle state, partner/follower state, and
  quest-specific minigame mechanics are still broad quest-system backlog items.
- Doric's Quest exists in local 2011Scape, but the generated pre-EOC catalog
  intentionally contains the 2012 replacement `What's Mine is Yours`; do not
  silently add Doric's without deciding the catalog-era policy.
