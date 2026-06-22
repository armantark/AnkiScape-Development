# Quest Stage Detail Audit: Sheep Herder

Date: 2026-06-22

## Scope

Backend-focused quest-stage replacement for Sheep Herder. This replaces the generated 7-stage quick-guide placeholder with a local Darkan-backed 6-stage chain that preserves startability versus finishability.

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
| 3 | Find the cattleprod at the Ardougne sheep enclosure. | Produces `Cattleprod x1` through a route/action gate. |
| 4 | Herd and poison all four infected sheep. | Requires `Sheep feed x1`; requires tools/equipment `Plague jacket`, `Plague trousers`, and `Cattleprod`; produces `Red sheep bones`, `Green sheep bones`, `Blue sheep bones`, and `Yellow sheep bones`; requires the Ardougne sheep enclosure route plus per-colour sheep action flags. |
| 5 | Incinerate all four sets of sheep bones and report back. | Consumes `Red sheep bones`, `Green sheep bones`, `Blue sheep bones`, and `Yellow sheep bones`; requires the Halgrive report action. |

`Sheep feed` is required but not consumed because the local Darkan implementation does not delete it when used on sheep. The cattleprod and coloured sheep bones are quest-route products, so they are produced before the later stages require or consume them rather than being treated as bank requirements.

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

## Quest-Only Item Follow-Up

A later same-day correction split the old all-in-one herding/incineration row
into route production and hand-in stages. The player should not be blocked on
pre-owning `Cattleprod` or coloured sheep bones: the quest creates those items
before the disposal stage consumes them.

Current audit after this follow-up:

- stage_requirement_rows: 1,119
- produced_inventory rows: 116
- combat_encounter_rows: 288
- combat_encounters_with_resolver_stats: 185
- statless_combat_encounters: 103

## Remaining Quest-Parity Gap

This slice updates Sheep Herder only. The all-quest goal remains active: broad
generated rows still need minute-detail source reconciliation even though every
quest now has at least one machine-readable current-stage blocker.
