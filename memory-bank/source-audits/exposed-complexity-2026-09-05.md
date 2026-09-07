# Exposed function complexity: measured scope and remaining work

Accepted source snapshot: `4fd93b0b481c4308f5654e813b5bd738714fdbd0`. Shop logic was then accepted at `0005e1cb42530706ab9ceb85e5be80ce3a0685f9`; all four shop-family source files are byte-identical to measured candidate `12850beed2aa644b0d051f6e1e4a90d9154a9b69`. Later main movement does not change the captured snapshot.

The installed gate loaded CCN 15, cognitive complexity 15, and Halstead difficulty 80, with no environment overrides. Its source hash and loaded limits matched after measurement. Lizard 1.24.0, Complexipy 7.0.1, and Radon 6.0.1 supplied the measurements. Exact executable paths, hashes, source snapshots, move matches, and raw metric dictionaries are retained in [the evidence manifest](../evidence/exposed-complexity-2026-09-05/manifest.json).

The measurement reads immutable Git blobs and calls the installed gate APIs. It does not import product code, run tests, change the gate, or establish behavior preservation. Raw measurements are retained before the gate suppresses inherited moves. A passing regression gate does not mean that every function is below its limit.

## Scope

Owner rulings in `handoffs/design-to-impl-rulings-2026-08-13.md` define the original ten sources at 34.2, carried as file eleven at 48, and the promotion tool as file twelve at 51.1. Section 48.1 also requires the activities and diary-generator splits. The table records all fourteen source families.

| Family source | Exact split or candidate | Status at the accepted snapshot |
| --- | --- | --- |
| `__init__.py` | No accepted move | Unsplit obligation |
| `core/constants.py` | `bbb79d4d`, `0246e1fc`, `9f54377b` | Accepted |
| `data/quest_data.py` | `5c87ba05` | Provisional |
| `data/combat_data.py` | `2f5949b7` | Accepted |
| `data/slayer_data.py` | `50e5cbdb` | Accepted |
| `logic_pure/logic_pure_combat_engine.py` | `0af0b0d5` | Explicit target; candidate simplifies in place |
| `tests/test_combat_enemy_roster.py` | `4d3bd18b` | Provisional |
| `logic/shop_logic.py` | `12850bee` | Accepted later at 0005; source identity verified |
| `ui/ui_tab_shop.py` | No accepted move | Unsplit obligation |
| `data/achievement_diary_catalog.py` | `a0e22ade` | Accepted |
| `runtime/runtime_actions_carried.py` | `89f2666e` | Accepted |
| `tools/promotion_gate.py` | `6bfeafe4` | Accepted |
| `runtime/runtime_actions_activities.py` | `3d3ed9d9` | Accepted |
| `tools/generate_achievement_diary_data.py` | `a0e22ade` | Accepted |

The root state conversion is a prerequisite, not the dispatcher relocation. Rejected root split `a8bb0fa70947d3602b917091aaba15ebf5cd1f54` is not accepted evidence. The latest shop-UI file-history change is `7a5a43976fbd0e725dc61780bd6dc9d367d50da9` on 2026-08-07; shop-logic candidate `12850bee` does not change `ui/ui_tab_shop.py`. These exact Git query results are retained in `scope-history.json`. The UI-family obligation is separate from shop logic. This audit authorizes no UI implementation or redesign; any later source move must preserve every visible behavior. Native approval remains pending separately.

## Confirmed exposed or explicitly named functions

20 distinct functions remain above at least one loaded limit. This includes the owner-named combat burst and root answer dispatcher before their moves, plus the accepted shop reconciliation. The ordering below is descending CCN, then cognitive complexity.

| Function at measured source | CCN | Cognitive | Halstead |
| --- | ---: | ---: | ---: |
| `logic_pure/logic_pure_combat_engine.py:1020::apply_combat_burst_pure` | 348 | 690 | 16.59811320754717 |
| `runtime/runtime_actions_carried_overlay.py:145::run_answer_with_carried_overlay` | 189 | 267 | 11.831521739130435 |
| `__init__.py:5700::on_answer_card` | 93 | 84 | 3.664285714285714 |
| `runtime/runtime_actions_activities_training.py:638::handle_agility_answer` | 61 | 80 | 5.6911764705882355 |
| `runtime/runtime_actions_carried_overlay.py:53::_try_pack_yak_winter_storage_overlay` | 34 | 20 | 7.838709677419355 |
| `logic/shop/state.py:170::shop_access_lock_reason_pure` | 29 | 42 | 3.9705882352941178 |
| `runtime/runtime_actions_carried_requirements.py:108::_processing_requirements_for` | 26 | 42 | 5.516129032258065 |
| `runtime/runtime_actions_carried_requirements.py:239::_agility_casual_layout_for` | 24 | 33 | 4.5 |
| `runtime/runtime_actions_activities_distractions.py:58::_handle_evil_tree_answer` | 24 | 22 | 3.369565217391304 |
| `tools/promotion/lane_execution.py:140::_read_reachability_pins` | 22 | 17 | 5.256410256410256 |
| `logic/shop/state.py:45::sanitize_shop_state_pure` | 21 | 42 | 3.652173913043478 |
| `runtime/runtime_actions_activities_training.py:168::_handle_livid_farm_answer` | 21 | 19 | 2.0952380952380953 |
| `runtime/runtime_actions_activities_competitions.py:408::handle_troll_invasion_answer` | 21 | 16 | 5.370967741935484 |
| `runtime/runtime_actions_activities_distractions.py:208::_handle_shooting_star_answer` | 20 | 25 | 3.3823529411764706 |
| `runtime/runtime_actions_carried_requirements.py:275::_agility_carried_requirement_gaps` | 16 | 16 | 3.6923076923076925 |
| `runtime/runtime_actions_activities_competitions.py:135::handle_pest_control_answer` | 16 | 10 | 4.277777777777778 |
| `logic/shop/services.py:167::_decant_potions_delta` | 11 | 17 | 3.4 |
| `logic/shop/state.py:461::_item_tradeable` | 10 | 18 | 2.727272727272727 |
| `tools/promotion/lane_execution.py:256::_run_gate_checks` | 10 | 17 | 3.75 |
| `logic/shop/services.py:454::_decant_flasks_to_vials_delta` | 9 | 16 | 2.3076923076923075 |

## Provisional candidate functions

5 distinct functions remain provisional. Combat candidate `0af0b0d5` reduces the same explicit target; it is not an additional accepted function. Quest `5c87ba05` and roster `4d3bd18b` are separate unlanded source measurements.

| Function at candidate source | CCN | Cognitive | Halstead |
| --- | ---: | ---: | ---: |
| `logic_pure/logic_pure_combat_engine.py:1042::apply_combat_burst_pure` | 342 | 674 | 16.593090211132438 |
| `data/quest/catalog.py:203::_quest_from_catalog` | 35 | 35 | 2.1176470588235294 |
| `tests/combat_roster/test_roster_contract.py:40::CombatEnemyRosterDataTest.test_new_enemies_have_required_schema` | 20 | 42 | 3.787878787878788 |
| `data/quest/catalog.py:79::_catalog_item_pairs` | 15 | 33 | 2.6923076923076925 |
| `tests/combat_roster/contract.py:153::_assert_slots_well_formed` | 11 | 23 | 2.4 |

## Functions retained in accepted split-family aggregators

12 further functions exceed a loaded limit but did not change file in the recovered moves. These are measured remainders of the accepted activities, diary-generator, and shop families. Keep them visible when defining completion of the family; do not call them exact moved-definition matches or silently discard them as unrelated repository debt.

| Function at measured source | CCN | Cognitive | Halstead |
| --- | ---: | ---: | ---: |
| `tools/generate_achievement_diary_data.py:243::resolve_condition_key` | 35 | 50 | 6.938775510204081 |
| `tools/generate_achievement_diary_data.py:1217::_regional_roster` | 30 | 47 | 4.9655172413793105 |
| `logic/shop_logic.py:430::rollback_shop_event_pure` | 21 | 48 | 3.4285714285714284 |
| `runtime/runtime_actions_activities.py:777::handle_temple_trekking_answer` | 20 | 16 | 1.5 |
| `logic/shop_logic.py:553::_preview_sell_from_state` | 16 | 17 | 7.5 |
| `runtime/runtime_actions_activities.py:647::handle_castle_wars_answer` | 16 | 10 | 4.277777777777778 |
| `logic/shop_logic.py:174::search_shop_catalog_pure` | 15 | 19 | 3.5454545454545454 |
| `tools/generate_achievement_diary_data.py:1076::_condition_src` | 14 | 16 | 3.8333333333333335 |
| `tools/generate_achievement_diary_data.py:127::_emitted_ledger_actions` | 11 | 24 | 2.5 |
| `tools/generate_achievement_diary_data.py:1333::build` | 11 | 24 | 2.5 |
| `tools/generate_achievement_diary_data.py:92::_module_level_strings` | 11 | 23 | 1.5 |
| `tools/generate_achievement_diary_data.py:1121::_equipment_rows` | 10 | 27 | 2.25 |

## Complete snapshot inventory and unsplit-family remainders

The recovered snapshot has 56 unique above-threshold functions across the fourteen scoped families: 20 moved or explicitly named functions, 12 retained accepted-family functions, and 24 unsplit-family remainders below. The 5 provisional candidate rows describe alternative source states and must not be added to this snapshot count. Raw names, source hashes, AST hashes and spans are retained in `complete-function-inventory.json.gz`. This completes the inventory, not the source moves or complexity reduction.

| Function at captured source | CCN | Cognitive | Halstead |
| --- | ---: | ---: | ---: |
| `logic_pure/logic_pure_combat_engine.py:510::combat_target_preview_pure` | 54 | 58 | 7.930232558139535 |
| `ui/ui_tab_shop.py:1131::build_shop_tab._refresh_service_preview` | 45 | None | None |
| `ui/ui_tab_shop.py:1582::build_shop_tab._populate_shop_selector` | 40 | None | None |
| `data/quest_data.py:10182::_quest_from_catalog` | 35 | 35 | 2.1176470588235294 |
| `__init__.py:4881::_set_combat_prayer_config` | 26 | 37 | 3.0172413793103448 |
| `__init__.py:5614::on_good_answer` | 24 | 39 | 6.111111111111111 |
| `ui/ui_tab_shop.py:715::build_shop_tab._preview_denial_text` | 24 | None | None |
| `tests/test_combat_enemy_roster.py:362::CombatEnemyRosterDataTest.test_new_slayer_family_assets_are_present_and_provenanced` | 22 | 41 | 1.8333333333333333 |
| `tests/test_combat_enemy_roster.py:178::CombatEnemyRosterDataTest.test_new_enemies_have_required_schema` | 20 | 42 | 3.787878787878788 |
| `ui/ui_tab_shop.py:1476::build_shop_tab._render_shop_detail` | 20 | None | None |
| `logic_pure/logic_pure_combat_engine.py:2952::combat_hud_state_pure` | 18 | 22 | 4.34 |
| `__init__.py:1073::resolve_review_context_action` | 18 | 21 | 5.173913043478261 |
| `ui/ui_tab_shop.py:59::build_shop_tab` | 17 | 653 | 9.028409090909092 |
| `__init__.py:575::_combine_activity_feedback` | 17 | 29 | 6.868421052631579 |
| `__init__.py:808::_skill_availability_fingerprint` | 16 | 13 | 1.0 |
| `ui/ui_tab_shop.py:956::build_shop_tab._refresh_transaction_panel` | 16 | None | None |
| `data/quest_data.py:10058::_catalog_item_pairs` | 15 | 33 | 2.6923076923076925 |
| `__init__.py:986::commit_direct_action` | 14 | 16 | 3.142857142857143 |
| `data/quest_data.py:11456::quest_reward_items_as_dict` | 12 | 19 | 1.1 |
| `__init__.py:705::_catalog_requirement_item_names` | 11 | 36 | 0.5 |
| `__init__.py:5244::on_equip_item` | 9 | 18 | 2.0 |
| `__init__.py:5297::on_unequip_slot` | 9 | 17 | 2.0 |
| `__init__.py:1871::_on_main_menu` | 1 | 982 | 7.092485549132948 |
| `tests/test_combat_enemy_roster.py:1699::CombatEnemyRosterDataTest._assert_slots_well_formed` | None | 23 | None |

## Completion limits

The exact historical above-threshold moved keys have 0 unresolved current path/name lineages. The raw inventory also retains above-threshold functions in the still-unsplit root, shop-UI, combat, quest and roster source files; they are not presented as completed moves. Farming is outside this scope. The generated diary catalog is excluded by the installed gate filter, and its generator is measured separately. No complete-program claim is possible while source moves and the provisional candidates remain unaccepted.

The installed matcher returns moved keys, origin maps and spans. Its stale two-value return annotation was not used. Raw Lizard and Complexipy names for the same roster method differ; the human table joins them only through the uniquely identified source AST function. The retained raw dictionaries preserve each tool name unchanged.
