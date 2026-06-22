# Quest Stage Gates Source Audit - 2026-06-22

## Status

This slice makes the quest stage-gate model real, but it does not claim full
catalog parity. The implemented proof case is The Knight's Sword, because it
was the live failure mode: the old review-driven model could complete the quest
without Redberry pie and immediately award 12,725 Smithing XP.

## Source Policy

- Prefer local 2011Scape behavior source when it exists.
- Use Darkan/2012scape only when local 2011Scape lacks the behavior.
- Use pinned historical RuneScape Wiki revisions through 2012-11-20 when local
  sources do not expose a requirement or stage action.
- Use OSRS wiki only as a cross-check, not as primary pre-EOC evidence.
- Do not hand-edit `quest_catalog_generated.py`; add generator support in
  `tools/build_pre_eoc_quest_catalog.py` or focused source-backed overrides in
  `quest_data.py`.

## The Knight's Sword Local Evidence

- Quest definition: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/quests/impl/TheKnightsSword.kt`
- Thurgo interaction: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/asgarnia/thurgo.plugin.kts`
- Squire interaction: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/falador/squire.plugin.kts`

Local facts used:

- The quest has 7 stages, a Mining 10 requirement, 1 quest point, and 12,725
  Smithing XP on completion.
- The quest's required-items prose names Redberry pie, 2 Iron bars, and a
  Pickaxe. The local quest prose also calls out evading level 54 Ice Warriors
  and level 53 Ice Giants.
- The Squire start path enforces `canStartQuest`; the local failure message is
  Mining 10 when the player cannot start.
- Thurgo stage 2 requires and removes `REDBERRY_PIE`, then advances the quest.
- Thurgo later consumes `BLURITE_ORE` plus two `IRON_BAR` at the replica-sword
  materials step.
- Final completion happens through the Squire and awards the 12,725 Smithing XP.

## Implemented Backend Contract

- `QuestDefinition.stage_requirements` stores machine-readable stage blockers
  in the `quest_data.py` override layer.
- `QuestStageRequirement` can express `required_inventory`,
  `consumed_inventory`, `required_tools`, `required_actions`,
  `required_routes`, and `combat_encounters`.
- `QuestCombatEncounter` gives future combat-aware stages a structured row
  instead of relying on prose-only `combat` text.
- `logic_pure.quest_current_stage_blockers_pure()` returns structured blocker
  rows, and `quest_current_stage_blocker_reasons_pure()` returns compact
  player-facing reasons.
- `logic_pure.can_progress_quest_pure()` keeps startability separate from
  finishability.
- `logic_pure.apply_quest_progress_pure()` refuses blocked current stages
  without marking the quest complete, consuming items, or awarding quest XP.
- Stage-local `consumed_inventory` is consumed at the current stage advance,
  not at quest start.

The Knight's Sword override keeps `required_items` empty, so Redberry pie,
Blurite ore, and Iron bars are not start locks. Its `requirements` line lists
them as `Used during quest` so the player can see the whole material commitment
before starting.

## Implemented Frontend Contract

- The Quests tab still uses the existing filters.
- Hide unable to start continues to hide only `locked` quests.
- Started quests with current-stage blockers remain visible and show
  `Blocked: <reason>`.
- Blocked quest action buttons are disabled and carry the same compact tooltip.
- The The Knight's Sword card lists `Mining 10, Used during quest: Redberry pie
  x1, Blurite ore x1, Iron bar x2` before the quest starts.

## Asset Notes

No new assets were needed. Redberry pie, Blurite ore, and Iron bar already have
registered item definitions and asset paths. The new registry test spot-checks
those quest-stage item assets.

## Deferred Parity Work

This slice is intentionally not full quest parity. Future quest-stage work
should proceed in source-backed batches:

1. Add generator or override support for catalog-wide stage items where source
   data says they are used mid-quest rather than required to start.
2. Convert prose-only enemy and boss text into `QuestCombatEncounter` rows, then
   either implement a combat resolver or leave those stages blocked with clear
   player-facing reasons.
3. Add explicit `required_actions` only when an AnkiScape action exists or when
   a source-backed blocker should intentionally stop progress until that action
   is implemented.
4. Add explicit `required_routes` only when route state exists or when the
   source evidence is strong enough to block progression rather than silently
   inventing travel access.
5. Revisit The Knight's Sword if quest-only intermediate items become visible in
   inventory. This slice consumes Blurite ore and Iron bars at Thurgo's
   materials stage; a deeper itemized model could create a Blurite sword and
   consume that on Squire completion.

## Manual Anki Test Instructions

Use a throwaway profile or back up the current AnkiScape save first.

1. Start Anki with the add-on enabled and open AnkiScape's main menu.
2. In the Quests tab, find The Knight's Sword with Mining 10 available and no
   quest materials. Confirm the Requirements line says `Mining 10, Used during
   quest: Redberry pie x1, Blurite ore x1, Iron bar x2`.
3. Start The Knight's Sword and answer quest reviews until it reaches the
   Thurgo stage. Confirm the quest card shows `Blocked: Needs Redberry pie x1`,
   the action button is disabled, and Hide unable to start does not hide the
   in-progress blocked quest.
4. Trigger one more quest review while missing Redberry pie. Confirm a `Quest
   blocked` dialog appears, questing switches off, progress does not advance,
   and Smithing XP remains unchanged.
5. Add one Redberry pie, resume the quest, and answer a quest review. Confirm
   Redberry pie drops to zero and progress advances.
6. Continue to the later Thurgo materials stage without Blurite ore or Iron
   bars. Confirm the blocker lists `Needs Blurite ore x1` and `Needs Iron bar
   x2`.
7. Add one Blurite ore and two Iron bars, resume the quest, and complete it.
   Confirm the items are consumed, the quest is completed once, quest points
   increase by 1, and Smithing XP increases by exactly 12,725.

## Verification

- `python3 -m unittest tests.test_logic.TestLogic.test_knights_sword_blocks_and_consumes_redberry_pie_at_thurgo_stage tests.test_logic.TestLogic.test_knights_sword_requires_later_materials_before_completion_reward tests.test_logic.TestLogic.test_stage_requirement_model_exposes_tool_action_route_and_combat_blockers`
- `python3 -m unittest tests.test_runtime_actions.TestRuntimeActions.test_quest_stage_blocker_deactivates_without_progress_or_reward tests.test_integration_smoke.TestIntegrationSmoke.test_quest_answer_blocks_knights_sword_without_stage_item tests.test_quest_catalog.TestQuestCatalog.test_knights_sword_stage_requirements_are_machine_readable_override_data tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_every_cooking_item_resolves_an_icon`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_stage_blockers_without_hiding_started_quests tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_lists_stage_items_before_knights_sword_start`
- `python3 run_tests.py` passed with 396 tests and 91 skipped.
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests` passed with 396 tests.
