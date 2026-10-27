# Witch's House Stage Detail Audit - 2026-06-22

## Scope

Focused backend/frontend slice for Witch's House. The goal was to replace the
earlier two-row item/combat proof with source-backed current-stage gates across
the whole quest, without turning in-quest requirements into start locks.

This is not an all-quest completion marker. The active all-quest goal still has
generated-row cleanup, route/location state, quest-item transformations, combat
simulation, optional/branch handling, and remaining combat-stat enrichment gaps.

## Source Tiers Used

- Local 2011Scape item identity: `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml` confirms the item identities used here. Darkan names item id 2411 generically as `Key`; AnkiScape stores that as `Backroom key` to avoid colliding with unrelated generic key items.
- Local 2011Scape quest implementation: no complete Witch's House quest mechanics were found in the local 2011Scape checkout, so it was not used for stage ordering.
- Darkan/2012scape quest implementation: `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/witchshouse/WitchsHouse.java`.
- Darkan dialogues and sentry logic: `BoyWitchsHouseD.java`, `WitchsDiary.java`, and `WitchSentry.java` under the same `witchshouse` package.
- Darkan combat definitions: `data/npcs/combatdefs/uncategorized/witch's_experiment/witch's_experiment_(19) (noanims).json`, plus the matching level 30, 42, and 53 files.
- Pinned historical wiki row: `https://runescape.wiki/w/Witch's_House?oldid=6474931` is retained for catalog metadata and human-readable cross-checking.
- OSRS/Fandom pages were used only to identify item sprite file titles for asset fetching. They are not mechanics sources for this slice.

## Implemented Data Model

- Witch's House is now a 12-stage focused override in `quest_data.py`.
- The quest remains startable without Cheese, Leather gloves, keys, Magnet, or Ball. Those are current-stage gates, tools, produced quest items, or consumed quest items.
- Stage 1 produces `Door key` from the potted plant outside the house.
- Stage 2 requires `Door key` as a tool plus the door-entry action.
- Stage 3 produces `Magnet` from the cupboard.
- Stage 4 requires `Magnet`, consumes `Cheese x1`, and requires the mouse-hole/magnet action.
- Stage 5 requires the route flag for avoiding the witch's patrol through the house.
- Stage 6 requires `Leather gloves` as a reusable tool for the electric gate.
- Stage 7 produces `Backroom key` from the fountain.
- Stage 8 requires `Backroom key` and the shed-door unlock action.
- Stage 9 gates all four Witch's experiment forms: Skavid level 19, Spider level 30, Bear level 42, and Wolf level 53. Each form remains resolver-ready with Darkan-backed stats, and the combat resolver still resolves one form per Quest review.
- Stage 10 produces Harvey's `Ball` from the shed.
- Stage 11 consumes `Ball` and requires the Harvey hand-in action.
- Completion keeps the sourced `4` quest points and `6,325 Constitution XP`. Constitution is not an implemented AnkiScape skill yet, so the reward is stored in `pending_skill_exp_rewards["constitution_exp"]`.
- The diary is used as source evidence for the mouse/magnet and fountain clues, but reading the diary is not modeled as a hard gate because the Darkan mechanics do not require it before the puzzle actions.

## Frontend And Assets

- Existing Quests-tab state handling is reused: started Witch's House can surface `blocked_at_stage` without making Cheese or gloves start locks.
- A Qt/offscreen test verifies the mouse-hole stage shows compact missing item/action blocker text and keeps the Quest button disabled.
- A Qt/offscreen test verifies the experiment stage is selectable when the global resolver is enabled and player combat level is high enough.
- Quest item icons were fetched into `questitems/` and recorded in `assets_provenance.json` for `Door key`, `Magnet`, `Backroom key`, and `Ball`. OSRS/Fandom sprites are treated as visual assets only; mechanics come from the local source hierarchy above.

## Verification Snapshot

- Targeted pure/catalog/registry/integration/runtime tests passed:
  `python3 -m unittest tests.test_quest_catalog.TestQuestCatalog tests.test_logic.TestLogic.test_witchs_house_stage_gates_items_route_combat_and_reward tests.test_logic.TestLogic.test_witchs_house_experiment_forms_are_resolver_ready tests.test_integration_smoke.TestIntegrationSmoke.test_quest_answer_blocks_witchs_house_mouse_puzzle_without_stage_item tests.test_runtime_actions.TestRuntimeActions.test_quest_answer_blocks_witchs_house_mouse_puzzle_without_stage_item tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_quest_stage_items_resolve_icons` ran 18 tests.
- Targeted Qt tests passed:
  `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_witchs_house_mouse_stage_blocker tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_allows_witchs_house_form_combat_gate_selection`.
- Post-slice stage audit:
  `python3 tools/audit_quest_stage_gate_coverage.py` reports 194/194 quests with stage requirements, 458 stage requirement rows, 174 quests with item/tool blockers, 120 quests with combat blockers, 285 combat rows, 180 rows with any stats, 177 resolver-ready combat rows, and 42 produced-inventory rows.
- Required full suites passed:
  `python3 run_tests.py` ran 485 tests with 114 skips, and
  `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
  ran 485 tests.

## Manual Anki Test Instructions

1. Start Anki with this add-on checkout active and open AnkiScape -> Quests.
2. Start Witch's House from the Quests tab. Confirm it can start without Cheese, Leather gloves, Door key, Magnet, Backroom key, or Ball.
3. Answer one Quest review. Confirm the quest advances to the door-key stage, Bank inventory gains `Door key x1`, and no quest points or quest XP are awarded.
4. At progress 2, confirm the quest is blocked until the door-entry action is present. Add `Enter the Witch's house with the door key`, then answer one Quest review.
5. Confirm stage 3 produces `Magnet x1`.
6. At progress 4, confirm the quest blocks without `Cheese x1` and the mouse-hole/magnet action. Add Cheese and `Use cheese on the mouse hole and attach the magnet to the mouse`, then answer one Quest review. Confirm Cheese is consumed and Magnet remains.
7. At progress 5, confirm the route blocker says to avoid the witch's patrol. Add `quest_route_states["witchs_house"] = ["Avoid the witch's patrol through the house"]`, then answer one Quest review.
8. At progress 6, confirm `Leather gloves` are required as a tool. Add or wear Leather gloves, then answer one Quest review.
9. Confirm stage 7 produces `Backroom key x1`, and stage 8 blocks until `Unlock the Witch's shed door with the backroom key` is present.
10. At stage 9 with `quest_combat_config.resolver_enabled = False`, confirm the experiment forms show global combat-locked blockers.
11. Enable the resolver and set combat levels high enough for level 53. Confirm Quest reviews resolve Skavid, Spider, Bear, and Wolf forms one review at a time while progress remains 9 until all forms are recorded.
12. Answer a Quest review after all four forms are resolved and confirm the quest advances to stage 10, then answer another review to pick up `Ball x1`.
13. Confirm progress 11 blocks until `Return the ball to Harvey` is present. Add that action, answer one Quest review, and confirm the quest completes with 4 quest points, `Ball` consumed, and pending `constitution_exp: 6325.0`.
14. Answer another Quest review after completion and confirm the reward does not duplicate.

## Remaining Gaps

- Full all-quest parity is still open. This slice proves one more focused quest replacement, not the entire catalog.
- The current action and route blockers use the existing flat `quest_stage_actions` and `quest_route_states` save model. There is still no player-facing UI for recording arbitrary dialogue/action/route flags.
- Real combat simulation is still out of scope. The four experiment forms are resolver-ready because Darkan supplies sufficient stats; other quests still have no-stats combat rows that must remain blocked.
- Diary reading is not modeled as an optional clue state.
- Broad generated-row cleanup, route/location modeling, optional steps, and quest-item transformations remain future work.
