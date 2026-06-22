# Priest in Peril Stage Detail Audit - 2026-06-22

## Scope

Backend and frontend slice for Priest in Peril as the next source-backed quest
stage replacement after the generic catalog-wide quest-stage layer.

This is not a claim that every quest is complete. After this slice, the catalog
still has broad generated quest-stage rows that need the same source-backed
replacement pass.

## Sources

- Primary local 2011Scape quest object:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/quests/impl/PriestInPeril.kt`
- Secondary Darkan quest implementation:
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/priestinperil/PriestInPeril.java`
- Secondary Darkan combat implementation:
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/priestinperil/Cerberus.java`
- Secondary Darkan Drezel/key/coffin/essence dialogues:
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/priestinperil/DrezelInJailD.java`
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/priestinperil/DrezelMausoleumD.java`
- Secondary Darkan combat definitions:
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/combatdefs/areas/paterdomus/cerberus (noanims).json`
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/combatdefs/areas/paterdomus/monk_of_zamorak/monk_of_zamorak_(30).json`
- Historical wiki catalog source retained as conflict context:
  `https://runescape.wiki/w/Priest_in_Peril?oldid=6487728`

## Backend

- Added `consumed_inventory_options` to the quest-stage requirement contract so
  a stage can require and consume one satisfied alternative group. This is used
  for the Salve purification step without flattening Rune essence and Pure
  essence into start locks.
- Replaced Priest in Peril's generated stage rows through `quest_data.py`, not
  `quest_catalog_generated.py`.
- Corrected the playable stage count from generated stage `61` to a 9-stage
  focused quest definition. The generated value was a journal completion marker,
  not sixty-one Anki review steps.
- Corrected rewards to Wolfbane dagger plus the existing 1 Quest Point and
  1,406 Prayer XP reward. Prayer is not an implemented skill yet, so AnkiScape
  stores that XP in `pending_skill_exp_rewards["prayer_exp"]`.
- Preserved startability: Priest in Peril has no start item locks. Bucket and
  essence are current-stage blockers only.
- Added source-backed stage blockers:
  - Speak through the Paterdomus temple door.
  - Defeat the Temple guardian dog.
  - Report the dead guard dog to King Roald.
  - Find Drezel imprisoned in the Paterdomus cell.
  - Defeat a Monk of Zamorak for the key route.
  - Swap the golden key at the monument and unlock Drezel's cell.
  - Use a bucket, bless Salve water with Drezel, and pour it over the coffin.
  - Give Drezel 50 Rune essence or 25 Pure essence to purify the Salve.
- Kept combat fail-closed behind `player_data["quest_combat_config"]["resolver_enabled"]`.
  The Temple guardian dog carries Darkan hitpoints/max-hit/magic-immunity
  metadata, but its Darkan combatdef has zero combat levels, so it remains
  `combat_missing_stats` if the global resolver is enabled before battle support
  knows how to handle that payload.

## Frontend

- The existing Quest UI state model did not need a new widget path for this
  slice. It now receives the focused Priest in Peril blocker reasons through the
  same `quest_current_stage_blocker_reasons_pure` contract.
- Added offscreen Qt coverage proving the Quests tab shows
  `Blocked: Needs Rune essence x50 or Pure essence x25` and disables the quest
  action when the player is in progress at the Salve purification stage without
  enough essence.

## Source Conflicts

- 2011Scape names the dog fight `Temple guardian dog (level 30)` and says Magic
  cannot be used.
- Darkan names the NPC class `Cerberus`, includes ids `7711` and `15255`, and
  zeroes magic damage in code.
- The generated historical wiki row had `Cerberus (level 29)` and `Monk of
  Zamorak (level 30)` at generated stage 60. The focused replacement uses the
  2011Scape player-facing dog name and level, keeps Darkan combat metadata, and
  moves the Monk of Zamorak fight to the key stage.
- 2011Scape required items say `50 rune essence or 25 pure essence`; Darkan's
  later implementation counts rune and pure essence one-for-one toward 50. The
  focused replacement follows 2011Scape because local 2011Scape has priority.

## Verification

Targeted checks run during the slice:

```bash
python3 -m unittest tests.test_quest_catalog.TestQuestCatalog tests.test_logic.TestLogic.test_consumed_inventory_options_block_and_consume_selected_alternative tests.test_logic.TestLogic.test_priest_in_peril_blocks_on_source_backed_stage_gates_and_consumes_essence
python3 -m unittest tests.test_runtime_actions.TestRuntimeActions.test_quest_answer_completes_priest_in_peril_only_after_essence_gate tests.test_integration_smoke.TestIntegrationSmoke.test_quest_answer_consumes_priest_in_peril_essence_at_completion_gate
QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_priest_in_peril_essence_stage_blocker
```

Required full suites passed after the final audit-count update:

```bash
python3 run_tests.py
QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests
```

Results:

```text
python3 run_tests.py: Ran 459 tests in 5.307s - OK (skipped=107)
QT offscreen discover: Ran 459 tests in 93.025s - OK
```

Post-slice audit:

```bash
python3 tools/audit_quest_stage_gate_coverage.py
```

Output after this slice:

```text
quests: 194
quests_with_stage_requirements: 194
stage_requirement_rows: 389
quests_with_item_or_tool_blockers: 173
quests_with_combat_blockers: 119
combat_encounter_rows: 283
combat_encounters_with_any_stats: 175
combat_encounters_with_resolver_stats: 174
requirement_row_kinds:
  consumed_inventory: 7
  consumed_inventory_options: 1
  inventory: 212
  inventory_options: 62
  tools: 91
```

Manual Anki test instructions:

1. Restart Anki with this add-on enabled and open AnkiScape.
2. Set current skill to Quests and start Priest in Peril.
3. At the first in-progress stage, confirm the Quests tab shows the current
   action blocker instead of treating the quest as completed or locked at start.
4. Move the save to Priest in Peril progress `2` with no combat config enabled.
   Confirm the UI shows the Temple guardian dog combat as globally locked.
5. Move the save to progress `8` with only `Pure essence x24`. Answer a Quest
   review and confirm it blocks with `Needs Rune essence x50 or Pure essence x25`,
   does not award Wolfbane, and does not add quest points.
6. Add `Pure essence x25` or `Rune essence x50`, answer a Quest review, and
   confirm the selected essence is consumed, Wolfbane dagger is awarded once,
   quest points increase by one, and Prayer XP is recorded in pending skill XP.

## Remaining Gaps

- Full minute-detail replacement is still open for the rest of the pre-EOC
  catalog. Current broad generated rows are useful blockers, not completion
  evidence.
- The Temple guardian dog is still not resolver-ready because Darkan provides
  hitpoints/max-hit/magic immunity but no nonzero attack/strength/defence stats.
- Quest-item transformations such as golden key, iron key, blessed water, and
  empty bucket are represented as action flags in this slice to avoid adding
  unproven bank/icon items. A future quest-item state pass should model those
  transformations explicitly if the broader quest item inventory surface exists.
- Route/location gates, follower/partner state, puzzle state, and branch state
  remain global quest-system backlog items.
