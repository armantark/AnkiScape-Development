# Quest Auto-Action Gates - 2026-06-24

## Scope

This follow-up covers the behavior gap left after removing misleading broad
quest-local requirement text. Some local quest steps are not meaningful player
preconditions in AnkiScape: they are deterministic actions performed as part of
the quest review, such as speaking to Dr Harlow at the Blue Moon Inn and buying
his beer before receiving the Vampyre Slayer stake gear.

Backend scope: add a structured stage requirement field for deterministic
actions that should be recorded automatically during successful quest
progression.

Frontend scope: no widget logic change. The Quests tab already renders
`quest_current_stage_blockers_pure()` results, so removing these steps from hard
blockers corrects the card state.

## Implementation Notes

- Added `QuestStageRequirement.auto_actions` to the quest data contract,
  generated-catalog deserialization, and `quests_as_dict()` serialization.
- `apply_quest_progress_pure()` now records selected-stage `auto_actions` when a
  stage advances. It still blocks on inventory, tools, routes, combat, and
  manual `required_actions`.
- Vampyre Slayer stages 1 and 2 now use `auto_actions` for the Dr Harlow talk and
  Blue Moon Inn beer steps. Stage 2 still produces Stake and Stake hammer, and it
  still does not require Beer in inventory.

## Verification

- `python3 -m unittest tests.test_quest_catalog`
- `python3 -m unittest tests.test_logic.TestLogic.test_source_backed_starter_quests_progress_through_stage_gates tests.test_logic.TestLogic.test_early_darkan_quests_progress_through_source_backed_stage_gates`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_vampyre_slayer_easy_items_are_not_prestart_requirements`
- `python3 tools/audit_quest_local_item_gates.py`
- `python3 run_tests.py` (713 passed, 133 skipped)
