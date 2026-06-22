# Quest Stage Detail Audit: Sheep Herder

Date: 2026-06-22

## Scope

Backend-focused quest-stage replacement for Sheep Herder. This replaces the generated 7-stage quick-guide placeholder with a local Darkan-backed 4-stage chain that preserves startability versus finishability.

Frontend change is limited to test coverage of the existing Quests tab blocked-at-stage display. No UI behavior was redesigned in this slice.

## Sources

- Local 2011Scape: `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml` for item identity cross-checks.
- Local Darkan quest handler:
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/sheep_herder/SheepHerder.kt`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/sheep_herder/dialogues/CouncillorHalgrivesD.kt`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/sheep_herder/dialogues/DoctorOrbonD.kt`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/sheep_herder/dialogues/FarmerBrumtyD.kt`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/sheep_herder/utils/SheepHerderConstants.kt`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/sheep_herder/utils/SheepHerderUtils.kt`
- Asset practical fallback: OSRS wiki item images for unchanged legacy quest item sprites. Colored bones resolve as `Sheep bones (1)` through `Sheep bones (4)`.

## Captured Rows

| Stage | Gate | Inventory/tool mutation |
| --- | --- | --- |
| 1 | Accept poisoned sheep feed from Councillor Halgrive. | Produces `Sheep feed x1`. |
| 2 | Buy protective clothing from Doctor Orbon. | Consumes `Coins x100`; produces `Plague jacket x1` and `Plague trousers x1`. |
| 3 | Herd, poison, incinerate, and report all four infected sheep. | Requires `Sheep feed x1`; requires tools/equipment `Plague jacket`, `Plague trousers`, `Cattleprod`; consumes `Red sheep bones`, `Green sheep bones`, `Blue sheep bones`, and `Yellow sheep bones`; requires the Ardougne sheep enclosure route plus per-colour sheep action flags and the Halgrive report action. |

`Sheep feed` is required but not consumed because the local Darkan implementation does not delete it when used on sheep. The cattleprod is modeled as a required tool, not a produced quest item, because Darkan points the player to the barn through Farmer Brumty dialogue instead of granting it through quest dialogue.

## Assets

Fetched to `questitems/` with provenance:

- `sheep_feed.png`
- `plague_jacket.png`
- `plague_trousers.png`
- `cattleprod.png`
- `red_sheep_bones.png`
- `green_sheep_bones.png`
- `blue_sheep_bones.png`
- `yellow_sheep_bones.png`

## Verification

Targeted tests added or updated:

- `tests.test_quest_catalog.TestQuestCatalog.test_local_source_batch_quest_stage_replacements_are_structured`
- `tests.test_logic.TestLogic.test_sheep_herder_stage_gates_clothing_tools_and_all_four_bones`
- `tests.test_runtime_actions.TestRuntimeActions.test_quest_answer_blocks_and_progresses_sheep_herder_feed_gate`
- `tests.test_integration_smoke.TestIntegrationSmoke.test_quest_answer_progresses_sheep_herder_feed_gate`
- `tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_sheep_herder_current_stage_blocker`
- `tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_quest_stage_items_resolve_icons`

Audit after this slice:

- quests: 194
- quests_with_stage_requirements: 194
- stage_requirement_rows: 501
- quests_with_item_or_tool_blockers: 174
- quests_with_combat_blockers: 120
- combat_encounter_rows: 285
- combat_encounters_with_resolver_stats: 180
- produced_inventory rows: 58
- statless_combat_encounters: 105

## Remaining Quest-Parity Gap

This slice updates Sheep Herder only. The all-quest goal remains active: 168 quests still lack explicit source-backed `QUEST_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID` rows and continue to rely on generated catalog blockers or focused combat additions until audited.
