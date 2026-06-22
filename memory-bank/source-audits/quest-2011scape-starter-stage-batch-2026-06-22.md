# 2011Scape Starter Quest Stage Batch - 2026-06-22

## Scope

Backend and frontend slice for the active all-quest stage-gate goal. This pass
does not claim every quest is complete. It replaces another set of broad or
wrong generated quest-stage rows with local 2011Scape-backed stage data:
Cook's Assistant, Imp Catcher, Druidic Ritual, Pirate's Treasure, and Vampyre
Slayer.

## Sources

- Cook's Assistant:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/quests/impl/CooksAssistant.kt`
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/lumbridge/lumbridge_cook.plugin.kts`
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/lumbridge/prized_dairy_cow.plugin.kts`
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/lumbridge/millie_miller.plugin.kts`
- Imp Catcher:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/quests/impl/ImpCatcher.kt`
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/draynor/mizgog.plugin.kts`
- Druidic Ritual:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/quests/impl/DruidicRitual.kt`
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/taverley/sanfew.plugin.kts`
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/taverley/kaqemeex.plugin.kts`
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/objs/cauldron_of_thunder.plugin.kts`
- Pirate's Treasure:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/quests/impl/PiratesTreasure.kt`
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/portsarim/redbeard_frank.plugin.kts`
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/varrock/pirate_chest.plugin.kts`
- Vampyre Slayer:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/quests/impl/VampyreSlayer.kt`
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/varrock/dr_harlow.plugin.kts`
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/draynor/draynor_manor.plugin.kts`
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/draynor/morgan.plugin.kts`
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/undeads/count_draynor_level_37.plugin.kts`

## Backend

- Added `produced_inventory` to `QuestStageRequirement` and the catalog
  serialization/deserialization path.
- Extended the pure progression helper so a successful current-stage advance can
  consume stage-local inventory and create produced quest items in one save
  mutation.
- Replaced generated rows through `quest_data.py`, not
  `quest_catalog_generated.py`.
- Cook's Assistant now consumes `Top-quality milk`, `Extra fine flour`, and
  `Super large egg` at the finish gate. The old generated `Bucket` and
  `Empty pot` blocker is gone.
- Imp Catcher now consumes the four beads and awards only the Amulet of
  accuracy plus 875 Magic XP. The generated 5,000 coin reward is gone.
- Druidic Ritual now models the Sanfew action, raw meat to enchanted meat
  transformation, Sanfew turn-in, and Kaqemeex completion. The generated coins,
  chisel, fishing rod, and note reward are gone.
- Pirate's Treasure now models `Karamja rum -> Chest key -> Pirate message ->
  Spade/dig -> Casket`, with the optional gardener left out of hard combat
  blockers.
- Vampyre Slayer now models Dr Harlow, beer consumption, stake/stake hammer
  production, Count Draynor combat, stake consumption, and Morgan report. Garlic
  is documented as optional and is not a hard inventory blocker.
- Count Draynor remains resolver-ready from local 2011Scape stats. The global
  combat lock still fails closed until `quest_combat_config.resolver_enabled`
  is true.

## Frontend

- No new widget path was required. The existing Quests tab consumes the same
  blocker reasons from `quest_current_stage_blocker_reasons_pure`.
- Added offscreen Qt coverage for Cook's Assistant showing the combined
  source-backed missing ingredient blocker while keeping the quest in progress
  rather than start-locked.
- Updated existing Vampyre Slayer UI/runtime/integration tests to use the new
  combat stage 3 and the source-backed stake/stake hammer gate.

## Current Audit Counts

`python3 tools/audit_quest_stage_gate_coverage.py` after this slice:

```text
quests: 194
quests_with_stage_requirements: 194
stage_requirement_rows: 395
quests_with_item_or_tool_blockers: 173
quests_with_combat_blockers: 119
combat_encounter_rows: 283
combat_encounters_with_any_stats: 175
combat_encounters_with_resolver_stats: 174
requirement_row_kinds:
  consumed_inventory: 15
  consumed_inventory_options: 1
  inventory: 208
  inventory_options: 60
  produced_inventory: 4
  tools: 92
quests_without_stage_requirements:
```

Computed from live `quest_data.py` override/addition maps: 70 focused stage
rows and 325 generated rows remain in the 395-row stage requirement set.

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
python3 run_tests.py: Ran 463 tests in 5.239s - OK (skipped=108)
QT offscreen discover: Ran 463 tests in 93.919s - OK
```

## Manual Anki Test Instructions

1. Restart Anki with this add-on enabled and open AnkiScape.
2. Set current skill to Quests.
3. Start Cook's Assistant, leave all three special ingredients missing, and
   confirm the Quests tab shows `Blocked: Needs Top-quality milk x1, Needs
   Extra fine flour x1, Needs Super large egg x1`.
4. Add the three ingredients to `player_data["inventory"]`, answer a Quest
   review, and confirm they are consumed, `Coins x500` and `Sardine x20` are
   awarded, 1 quest point is added, and Cooking XP increases by 300.
5. For Druidic Ritual, move the save through stages with the matching
   `quest_stage_actions` flags. Confirm raw meats are consumed and enchanted
   meats are produced at the Cauldron stage, then enchanted meats are consumed
   before completion.
6. For Pirate's Treasure, confirm Karamja rum produces Chest key, Chest key
   produces Pirate message, and the final Spade/message dig awards only the
   casket and 2 quest points.
7. For Vampyre Slayer, confirm stage 2 consumes Beer and produces Stake plus
   Stake hammer; stage 3 blocks on combat while the global resolver is disabled;
   enabling the resolver with sufficient combat stats resolves Count Draynor
   without completing the quest; a later review consumes Stake and advances to
   Morgan; Morgan's action gate completes the quest and parks Attack XP in
   pending skill XP.

## Remaining Gaps

- Full all-quest minute-detail parity remains open. The plugin still has 325
  generated stage rows that need source-backed per-stage extraction or explicit
  blocker notes.
- Route/location gates, follower/partner state, puzzle state, and branch state
  are still broad quest-system backlog items.
- Many quests still have generated item buckets that are useful blockers but not
  exact current-stage source evidence.
- Combat remains globally locked by default and 109 statless combat rows remain
  blocked pending a new source class or full combat simulation.
