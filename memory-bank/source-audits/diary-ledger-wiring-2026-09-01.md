# Achievement Diary ledger wiring source audit — 2026-09-01

## Authority and boundary

Base commit: `345579c6c6c143232f98b53766b7956e6207b683`.

The gate-1 review is `memory-bank/diary-curation-ledger/cross-lineage-review.md`; gate 2 is the 2026-08-31 owner ruling recorded in the ledger README. This slice consumes only repository-pinned evidence. It fetches no newer source and changes no permanent citation.

No user interface code changed. The existing Achievement Cabinet receives live progress for the reviewed rows. The 247 dormant rows remain the ledger's only trigger record and keep `conditions == ()`.

## Catalog result

| Measure | Before | After |
| --- | ---: | ---: |
| Named tasks | 474 | 474 |
| Tasks with empty conditions | 320 | 247 |
| Structurally claimable tiers | 0 | 0 |
| Active ledger rows | 43 | 43 |
| Translated ledger rows | 30 | 30 |
| Dormant ledger rows | 247 | 247 |

No row stopped at the expressibility gate.

## Generator and runtime wiring

Active and translated `designed_trigger` values carry one structured `Wiring:` clause. The generator compiles that clause into existing condition kinds and refuses unresolved action, output, state, encounter, Farming, and direct-event identities. Dormant rows have no clause and generate no condition.

Durable writers continue to use existing `ledger_action`, `ledger_output`, `counter`, `combat_kill`, `state_equals`, `equipped_item`, `any_of`, and `derived_value` conditions. Same-frame deeds use encoded `counter` keys backed by strict generated event rules. The runtime records only fields already present at the reviewed seams. Event conditions are indexed once by event type rather than rescanning the catalog on every review.

The save adds sanitized event-count and sequence-stage maps. They are forward-only deed evidence; completed tasks remain sticky through the existing diary state.

## Ledger identifier corrections

- `ardougne_hard_a_taste_of_the_exotic`: the shipped Coconut crop identity is `palm`, not `coconut`.
- `morytania_easy_wurt_a_bundle`: the exact patch identity is `phasmatys_flower`, not location shorthand `phasmatys`.
- `morytania_hard_detarnation`: the exact encounter identity is `lair_of_tarn_razorlor_tarn_ghost`.
- `varrock_elite_red_red_pies_of_summer`: the three no-XP preparation steps are recorded under telemetry owner `utility`; only the final cook is owned by `cooking`.
- `karamja_elite_the_power_of_lava`: the canonical trigger now states the owner-selected closer candidate — Fire cape equipped in the active TzHaar Fight Pit context — rather than the rejected win requirement.

These are exact-writer corrections in the canonical ledger, followed by regeneration. No generated catalog row was hand-edited.

## Same-frame boundary

Rows 53, 94, 128, 165, and 274 inspect one action's output map. Cumulative telemetry cannot satisfy them. Output-qualified one-item deeds also inspect the post-replacement same-frame output map, so a Shattered Heart replacement cannot credit an item the action did not produce. Skipped Farming steps emit no deed event.

## Real-kernel execution

```text
lumbridge_easy_iron_on: before=False
lumbridge_easy_iron_on: handler_result=True after=True same_frame_iron_ore=1
lumbridge_easy_camping_trip: before=False
lumbridge_easy_camping_trip: handler_result=True after=True action_successes=1
falador_hard_mass_production: before=False
falador_hard_mass_production: handler_result=True after=True same_frame_mind_runes=144
ardougne_easy_yoink: before=False
ardougne_easy_yoink: handler_result=False after=True guard_attempts=1
```

The Mining and Firemaking rows are translated; the Runecrafting batch and guard-attempt row are active. Each path uses its real review handler and the real achievement refresh hook.

## Reproducible generation

```text
wrote /tmp/achievement_diary_catalog.refactor-first.py
wrote /tmp/achievement_diary_catalog.refactor-second.py
5e8f434fbbbf24551f0217db917bf6e72275518d6c29cddf2a7b7986f2752bbb  /tmp/achievement_diary_catalog.refactor-first.py
5e8f434fbbbf24551f0217db917bf6e72275518d6c29cddf2a7b7986f2752bbb  /tmp/achievement_diary_catalog.refactor-second.py
5e8f434fbbbf24551f0217db917bf6e72275518d6c29cddf2a7b7986f2752bbb  data/achievement_diary_catalog.py
generator reproducibility: byte-identical
```

## Verification

### Plain lane under the promotion-gate exception

```text
/opt/homebrew/bin/python3 run_tests.py
Ran 4623 tests in 852.760s
OK (skipped=515)
```

The offscreen Qt lane was not run on this branch. The orchestrator reruns both lanes on the merged tree as the promotion gate.

### `python3 tools/audit_docs.py` (exit 0)

```text
Audited 624 Markdown and 441 HTML files.
Documentation audit passed.
```

### `python3 tools/audit_test_quality.py` (exit 0)

```text
4588 tests across 233 files
hard issues: 0
structural clone candidates: 31 groups
- tests/test_write_through_barbarian_assault.py:228:BarbarianAssaultWriteThroughTest.test_the_probe_itself_catches_a_write_through | tests/test_write_through_castle_wars.py:189:CastleWarsWriteThroughTest.test_the_probe_itself_catches_a_write_through | tests/test_write_through_fight_caves.py:170:FightCavesWriteThroughTest.test_the_probe_itself_catches_a_write_through | tests/test_write_through_great_orb_project.py:223:GreatOrbProjectWriteThroughTest.test_the_probe_itself_catches_a_write_through | tests/test_write_through_pest_control.py:239:PestControlWriteThroughProbeTest.test_the_probe_itself_catches_a_write_through | tests/test_write_through_phoenix_lair.py:182:PhoenixLairWriteThroughTest.test_the_probe_itself_catches_a_write_through | tests/test_write_through_probe.py:169:WriteThroughProbeTest.test_the_probe_itself_catches_a_write_through | tests/test_write_through_shades_of_mortton.py:192:ShadesOfMorttonWriteThroughTest.test_the_probe_itself_catches_a_write_through | tests/test_write_through_soul_wars.py:226:SoulWarsWriteThroughProbeTest.test_the_probe_itself_catches_a_write_through | tests/test_write_through_stealing_creation.py:253:StealingCreationWriteThroughTest.test_the_probe_itself_catches_a_write_through | tests/test_write_through_tzhaar_fight_pit.py:187:FightPitWriteThroughTest.test_the_probe_itself_catches_a_write_through
- tests/test_single_valued_route_steps.py:254:TestSingleValuedRoutesAreRecordedSteps.test_kenniths_concerns_shrine_tunnels_are_recorded | tests/test_single_valued_route_steps.py:260:TestSingleValuedRoutesAreRecordedSteps.test_lost_city_entrana_travel_is_recorded | tests/test_single_valued_route_steps.py:266:TestSingleValuedRoutesAreRecordedSteps.test_merlins_crystal_crate_delivery_is_recorded | tests/test_single_valued_route_steps.py:300:TestSingleValuedRoutesAreRecordedSteps.test_gertrudes_cat_lumber_yard_route_is_recorded | tests/test_single_valued_route_steps.py:306:TestSingleValuedRoutesAreRecordedSteps.test_tribal_totem_rpdt_route_is_recorded | tests/test_single_valued_route_steps.py:332:TestSingleValuedRoutesAreRecordedSteps.test_plague_city_sewer_route_is_recorded | tests/test_single_valued_route_steps.py:338:TestSingleValuedRoutesAreRecordedSteps.test_waterfall_quest_golrie_route_is_recorded | tests/test_single_valued_route_steps.py:353:TestSingleValuedRoutesAreRecordedSteps.test_witchs_house_patrol_avoidance_is_recorded | tests/test_single_valued_route_steps.py:359:TestSingleValuedRoutesAreRecordedSteps.test_myths_of_the_white_lands_ice_cave_route_is_recorded
- tests/test_logic.py:857:TestLogic.test_blue_dragon_scale_trip_gathers_the_seven_ordinary_spawns | tests/test_logic.py:868:TestLogic.test_potato_cactus_trip_gathers_only_the_three_first_level_spawns | tests/test_logic.py:879:TestLogic.test_black_mushroom_pickup_gathers_one_ground_spawn_without_xp | tests/test_logic.py:890:TestLogic.test_doogle_leaves_trip_gathers_the_two_quest_spawns_without_xp
- tests/test_main_menu_widget.py:9749:MainMenuWidgetTest.test_quests_tab_allows_merlins_crystal_mordred_combat_gate_selection | tests/test_main_menu_widget.py:9799:MainMenuWidgetTest.test_quests_tab_allows_beast_fallback_ranged_combat_gate_selection | tests/test_main_menu_widget.py:9914:MainMenuWidgetTest.test_quests_tab_allows_witchs_house_form_combat_gate_selection | tests/test_main_menu_widget.py:9969:MainMenuWidgetTest.test_quests_tab_shows_split_golem_combat_gates
- tests/test_item_reachability_audit.py:607:TestItemReachabilityAudit.test_lost_city_shamus_action_has_a_runtime_emitter | tests/test_item_reachability_audit.py:657:TestItemReachabilityAudit.test_a_souls_bane_rage_action_has_a_runtime_emitter | tests/test_item_reachability_audit.py:668:TestItemReachabilityAudit.test_dealing_with_scabaras_bronze_action_has_a_runtime_emitter
- tests/test_single_valued_route_steps.py:272:TestSingleValuedRoutesAreRecordedSteps.test_heroes_quest_travel_steps_are_recorded | tests/test_single_valued_route_steps.py:312:TestSingleValuedRoutesAreRecordedSteps.test_scorpion_catcher_room_routes_are_recorded | tests/test_single_valued_route_steps.py:322:TestSingleValuedRoutesAreRecordedSteps.test_sheep_herder_enclosure_routes_are_recorded
- tests/test_single_valued_route_steps.py:282:TestSingleValuedRoutesAreRecordedSteps.test_family_crest_dungeon_routes_are_recorded | tests/test_single_valued_route_steps.py:291:TestSingleValuedRoutesAreRecordedSteps.test_temple_of_ikov_travel_steps_are_recorded | tests/test_single_valued_route_steps.py:344:TestSingleValuedRoutesAreRecordedSteps.test_tree_gnome_village_battlefield_routes_are_recorded
- tests/test_achievement_diaries.py:864:NewConditionDegradationTest.test_combat_kill_degrades_on_absent_or_wrong_typed_state | tests/test_achievement_diaries.py:874:NewConditionDegradationTest.test_shop_transaction_degrades_on_absent_or_wrong_typed_state
- tests/test_achievement_diaries.py:915:NewConditionDegradationTest.test_ledger_action_family_degrades_on_absent_or_wrong_typed_state | tests/test_achievement_diaries.py:923:NewConditionDegradationTest.test_equipped_item_degrades_on_absent_or_wrong_typed_state
- tests/test_achievement_diaries.py:962:StageOneRealPathTest.test_vial_deeds_completes_through_aemads_shop | tests/test_achievement_diaries.py:1205:StageTwoRealPathTest.test_grand_candle_completes_through_the_candle_maker_shop
- tests/test_cadence_live.py:98:TestCadenceLiveCoverage.test_big_chinchompa_declares_grouped_jar_and_world_boundary | tests/test_cadence_live.py:150:TestCadenceLiveCoverage.test_barbarian_assault_declares_one_duty_or_persistent_queen_beat
- tests/test_combat_enemy_roster.py:790:CombatEnemyRosterDataTest.test_bronze_dragon_preserves_cutoff_metal_dragon_contract | tests/test_combat_enemy_roster.py:834:CombatEnemyRosterDataTest.test_iron_dragon_preserves_cutoff_metal_dragon_contract
- tests/test_combat_logic.py:2640:CombatLogicTest.test_citizen_quantity_range_and_tertiary_drop_rolls | tests/test_combat_logic.py:3599:CombatLogicTest.test_black_knight_drop_rolls_nested_seed_table_and_charms
- tests/test_dialog_lifecycle.py:186:DialogLifecycleTest.test_level_up_dialog_names_the_exact_level_transition | tests/test_dialog_lifecycle.py:209:DialogLifecycleTest.test_combat_level_popup_uses_the_shared_level_up_dialog
- tests/test_dominion_tower.py:430:DominionTowerFactorTest.test_climber_pays_a_hundred_times_the_arena_level_total | tests/test_dominion_tower.py:434:DominionTowerFactorTest.test_endurance_pays_a_tenth_of_that
- tests/test_dominion_tower.py:876:DominionTowerRunTest.test_freestyle_refuses_a_boss_that_was_never_beaten | tests/test_dominion_tower.py:887:DominionTowerRunTest.test_special_mode_waits_for_climber_exposure
- tests/test_item_reachability_audit.py:618:TestItemReachabilityAudit.test_waterfall_quest_dialogue_and_tomb_actions_have_runtime_emitters | tests/test_item_reachability_audit.py:642:TestItemReachabilityAudit.test_gertrudes_cat_dialogue_actions_have_runtime_emitters
- tests/test_logic.py:2857:TestLogic.test_polar_kebbit_tracking_preserves_noose_wand_and_awards_sourced_outputs | tests/test_logic.py:2953:TestLogic.test_razor_backed_kebbit_tracking_preserves_noose_wand_and_awards_chain_inputs
- tests/test_main_menu_widget.py:9439:MainMenuWidgetTest.test_quests_tab_shows_demon_slayer_item_stage_blocker | tests/test_main_menu_widget.py:9454:MainMenuWidgetTest.test_quests_tab_shows_ernest_machine_part_stage_blocker
- tests/test_main_menu_widget.py:9489:MainMenuWidgetTest.test_quests_tab_shows_fishing_contest_current_stage_blocker | tests/test_main_menu_widget.py:9733:MainMenuWidgetTest.test_quests_tab_shows_merlins_crystal_wax_stage_blocker
- tests/test_papercut_tools.py:77:PapercutToolTests.test_focused_runner_refuses_a_fuzzy_module_substitution | tests/test_papercut_tools.py:88:PapercutToolTests.test_focused_runner_refuses_ambiguous_fuzzy_methods
- tests/test_phoenix_lair.py:344:PhoenixLairPersistenceAndRuntimeTests.test_runtime_routes_only_selected_active_phoenix_lair_reviews | tests/test_skeletal_horror.py:390:SkeletalHorrorPersistenceRuntimeAndAssetTests.test_runtime_routes_selected_active_reviews_and_persists
- tests/test_promotion_gate.py:609:PromotionGateTest.test_reachability_content_addition_with_updated_pins_passes | tests/test_promotion_gate.py:621:PromotionGateTest.test_reachability_content_addition_without_updated_pins_fails
- tests/test_single_valued_route_steps.py:424:TestSingleValuedRoutesAreRecordedSteps.test_enlightened_journey_reach_auguste_is_a_recorded_step | tests/test_single_valued_route_steps.py:454:TestSingleValuedRoutesAreRecordedSteps.test_in_pyre_need_phoenix_lair_is_a_recorded_step
- tests/test_single_valued_route_steps.py:443:TestSingleValuedRoutesAreRecordedSteps.test_cabin_fever_charter_route_is_a_recorded_step | tests/test_single_valued_route_steps.py:460:TestSingleValuedRoutesAreRecordedSteps.test_back_to_my_roots_karamja_route_is_a_recorded_step
- tests/test_write_through_big_chinchompa.py:200:BigChinchompaWriteThroughTest.test_the_probe_itself_catches_a_write_through | tests/test_write_through_pet.py:204:PetWriteThroughTest.test_the_probe_itself_catches_a_write_through
- tests/test_write_through_castle_wars.py:197:CastleWarsWriteThroughTest.test_frozen_save_is_equal_to_the_plain_one | tests/test_write_through_tzhaar_fight_pit.py:195:FightPitWriteThroughTest.test_frozen_save_is_equal_to_the_plain_one
- tests/test_write_through_fight_caves.py:178:FightCavesWriteThroughTest.test_frozen_save_is_equal_to_the_plain_one | tests/test_write_through_phoenix_lair.py:190:PhoenixLairWriteThroughTest.test_frozen_save_is_equal_to_the_plain_one
- tests/test_write_through_pest_control.py:247:PestControlWriteThroughProbeTest.test_frozen_save_is_equal_to_the_plain_one | tests/test_write_through_soul_wars.py:234:SoulWarsWriteThroughProbeTest.test_frozen_save_is_equal_to_the_plain_one
- tests/test_write_through_pest_control.py:352:PestControlWriteThroughProbeTest.test_assault_with_the_real_combat_engine_never_writes_through | tests/test_write_through_pest_control.py:381:PestControlWriteThroughProbeTest.test_defend_review_never_writes_through
- tests/test_write_through_shades_of_mortton.py:200:ShadesOfMorttonWriteThroughTest.test_frozen_save_is_equal_to_the_plain_one | tests/test_write_through_stealing_creation.py:261:StealingCreationWriteThroughTest.test_frozen_save_is_equal_to_the_plain_one
```

### `python3 tools/audit_item_reachability.py` (exit 1 by its documented orphan-input contract)

```text
1663 actions; 2343 reachable items; 163 orphan inputs; 249 blocked actions
- Agility mix (1): Item action:consume:Agility mix (1)
- Agility mix (2): Item action:consume:Agility mix (2)
- Antifire flask (1): Item action:consume:Antifire flask (1)
- Antifire flask (2): Item action:consume:Antifire flask (2)
- Antifire flask (3): Item action:consume:Antifire flask (3), Shop service:teplin_decant_flasks_to_vials:Antifire
- Antifire flask (4): Item action:consume:Antifire flask (4)
- Antifire flask (5): Item action:consume:Antifire flask (5)
- Antifire flask (6): Item action:consume:Antifire flask (6)
- Astral rune shards: Utility:grind_astral_rune_shards
- Attack flask (1): Item action:consume:Attack flask (1)
- Attack flask (2): Item action:consume:Attack flask (2)
- Attack flask (3): Item action:consume:Attack flask (3), Shop service:teplin_decant_flasks_to_vials:Attack potion
- Attack flask (4): Item action:consume:Attack flask (4)
- Attack flask (5): Item action:consume:Attack flask (5)
- Attack flask (6): Item action:consume:Attack flask (6)
- Blood talisman: Runecrafting:bind_blood_talisman_staff, Runecrafting:bind_blood_tiara
- Caviar: Fishing:catch_leaping_fish, Herblore:finished_agility_mix, Herblore:finished_antifire_mix, Herblore:finished_antip_supermix
- Chain link mould: Crafting:silver_silvthrill_chain
- Combat flask (1): Item action:consume:Combat flask (1)
- Combat flask (2): Item action:consume:Combat flask (2)
- Combat flask (3): Item action:consume:Combat flask (3), Shop service:teplin_decant_flasks_to_vials:Combat potion
- Combat flask (4): Item action:consume:Combat flask (4)
- Combat flask (5): Item action:consume:Combat flask (5)
- Combat flask (6): Item action:consume:Combat flask (6)
- Conductor mould: Crafting:silver_conductor
- Crab meat: Utility:grind_crab_meat
- Crafting flask (1): Item action:consume:Crafting flask (1)
- Crafting flask (2): Item action:consume:Crafting flask (2)
- Crafting flask (3): Item action:consume:Crafting flask (3), Shop service:teplin_decant_flasks_to_vials:Crafting potion
- Crafting flask (4): Item action:consume:Crafting flask (4)
- Crafting flask (5): Item action:consume:Crafting flask (5)
- Crafting flask (6): Item action:consume:Crafting flask (6)
- Cured yak-hide: Crafting:leather_yakhide_armour, Crafting:leather_yakhide_armour_10824
- Cursed magic logs: Firemaking:cursed_magic_logs
- Defence flask (1): Item action:consume:Defence flask (1)
- Defence flask (2): Item action:consume:Defence flask (2)
- Defence flask (3): Item action:consume:Defence flask (3), Shop service:teplin_decant_flasks_to_vials:Defence potion
- Defence flask (4): Item action:consume:Defence flask (4)
- Defence flask (5): Item action:consume:Defence flask (5)
- Defence flask (6): Item action:consume:Defence flask (6)
- Demonic sigil mould: Crafting:silver_demonic_sigil
- Diamond root: Utility:grind_diamond_root
- Dried thistle: Utility:grind_dried_thistle
- Emerald lantern (lit): Utility:extinguish_emerald_lantern
- Emerald lantern (unlit): Utility:light_emerald_lantern
- Emerald lens: Crafting:combine_bullseye_emerald_lantern
- Fish offcuts: Fishing:catch_leaping_fish
- Fletching flask (1): Item action:consume:Fletching flask (1)
- Fletching flask (2): Item action:consume:Fletching flask (2)
- Fletching flask (3): Item action:consume:Fletching flask (3), Shop service:teplin_decant_flasks_to_vials:Fletching potion
- Fletching flask (4): Item action:consume:Fletching flask (4)
- Fletching flask (5): Item action:consume:Fletching flask (5)
- Fletching flask (6): Item action:consume:Fletching flask (6)
- Fletching potion (1): Item action:consume:Fletching potion (1)
- Fletching potion (2): Item action:consume:Fletching potion (2)
- Fletching potion (3): Item action:consume:Fletching potion (3), Shop service:bob_barter_decant_four:Fletching potion, Shop service:teplin_fill_potion_flasks:Fletching potion
- Fletching potion (4): Item action:consume:Fletching potion (4)
- Fresh crab claw: Crafting:chisel_crab_claw
- Fresh crab shell: Crafting:chisel_crab_helmet
- Gorak claws: Utility:grind_gorak_claws
- Inferno adze: Farming:clear:magic, Farming:clear:maple, Farming:clear:oak, Farming:clear:willow
- Jade vine seed: Farming:jade_vine
- Kelp: Utility:grind_kelp
- Leaping salmon: Cooking:gut_leaping_salmon
- Leaping sturgeon: Cooking:gut_leaping_sturgeon
- Leaping trout: Cooking:gut_leaping_trout
- Magic essence (2): Herblore:finished_magic_essence_mix
- Magic flask (1): Item action:consume:Magic flask (1)
- Magic flask (2): Item action:consume:Magic flask (2)
- Magic flask (3): Item action:consume:Magic flask (3), Shop service:teplin_decant_flasks_to_vials:Magic potion
- Magic flask (4): Item action:consume:Magic flask (4)
- Magic flask (5): Item action:consume:Magic flask (5)
- Magic flask (6): Item action:consume:Magic flask (6)
- Mining helmet (lit): Utility:extinguish_mining_helmet
- Mining helmet (unlit): Utility:light_mining_helmet
- Mushroom spore: Farming:bittercap
- Orb of armadyl: Crafting:combine_armadyl_battlestaff
- Phoenix feather: Herblore:finished_super_antifire
- Potion flask: Shop service:teplin_fill_potion_flasks:Antifire, Shop service:teplin_fill_potion_flasks:Attack potion, Shop service:teplin_fill_potion_flasks:Combat potion, Shop service:teplin_fill_potion_flasks:Crafting potion
- Prayer flask (1): Item action:consume:Prayer flask (1)
- Prayer flask (2): Item action:consume:Prayer flask (2)
- Prayer flask (3): Item action:consume:Prayer flask (3), Shop service:teplin_decant_flasks_to_vials:Prayer potion
- Prayer flask (4): Item action:consume:Prayer flask (4)
- Prayer flask (5): Item action:consume:Prayer flask (5)
- Prayer flask (6): Item action:consume:Prayer flask (6)
- Ranging flask (1): Item action:consume:Ranging flask (1)
- Ranging flask (2): Item action:consume:Ranging flask (2)
- Ranging flask (3): Item action:consume:Ranging flask (3), Shop service:teplin_decant_flasks_to_vials:Ranging potion
- Ranging flask (4): Item action:consume:Ranging flask (4)
- Ranging flask (5): Item action:consume:Ranging flask (5)
- Ranging flask (6): Item action:consume:Ranging flask (6)
- Raw monkfish: Cooking:cook_monkfish
- Raw spider on stick: Cooking:cook_spider_on_a_stick
- Red sandstone: Utility:make_robust_glass
- Relicym's balm (2): Herblore:finished_relicyms_mix
- Robust glass: Crafting:glass_potion_flask
- Rod clay mould: Crafting:silver_silvthrill_rod
- Roe: Fishing:catch_leaping_fish, Herblore:finished_relicyms_mix, Herblore:finished_restore_mix
- Shaikahan bonemeal: Prayer:ectofuntus_shaikahan_bones
- Shaikahan bones: Utility:grind_prayer_shaikahan_bones
- Shards of armadyl: Utility:grind_shards_of_armadyl
- Shield right half: Smithing:repair_dragon_sq_shield
- Shrunk ogleroot: Herblore:finished_shrink_me_quick
- Skewer stick: Utility:skewer_spider_on_a_stick
- Spider carcass: Utility:skewer_spider_on_a_stick
- Spirit roots: Crafting:spin_spirit_roots_to_crossbow_string
- Strength flask (1): Item action:consume:Strength flask (1)
- Strength flask (2): Item action:consume:Strength flask (2)
- Strength flask (3): Item action:consume:Strength flask (3), Shop service:teplin_decant_flasks_to_vials:Strength potion
- Strength flask (4): Item action:consume:Strength flask (4)
- Strength flask (5): Item action:consume:Strength flask (5)
- Strength flask (6): Item action:consume:Strength flask (6)
- Summoning flask (1): Item action:consume:Summoning flask (1)
- Summoning flask (2): Item action:consume:Summoning flask (2)
- Summoning flask (3): Item action:consume:Summoning flask (3), Shop service:teplin_decant_flasks_to_vials:Summoning potion
- Summoning flask (4): Item action:consume:Summoning flask (4)
- Summoning flask (5): Item action:consume:Summoning flask (5)
- Summoning flask (6): Item action:consume:Summoning flask (6)
- Super antifire (1): Item action:consume:Super antifire (1)
- Super antifire (2): Item action:consume:Super antifire (2)
- Super antifire (3): Item action:consume:Super antifire (3), Shop service:bob_barter_decant_four:Super antifire, Shop service:teplin_fill_potion_flasks:Super antifire
- Super antifire (4): Item action:consume:Super antifire (4)
- Super antifire flask (1): Item action:consume:Super antifire flask (1)
- Super antifire flask (2): Item action:consume:Super antifire flask (2)
- Super antifire flask (3): Item action:consume:Super antifire flask (3), Shop service:teplin_decant_flasks_to_vials:Super antifire
- Super antifire flask (4): Item action:consume:Super antifire flask (4)
- Super antifire flask (5): Item action:consume:Super antifire flask (5)
- Super antifire flask (6): Item action:consume:Super antifire flask (6)
- Super attack flask (1): Item action:consume:Super attack flask (1)
- Super attack flask (2): Item action:consume:Super attack flask (2)
- Super attack flask (3): Item action:consume:Super attack flask (3), Shop service:teplin_decant_flasks_to_vials:Super attack
- Super attack flask (4): Item action:consume:Super attack flask (4)
- Super attack flask (5): Item action:consume:Super attack flask (5)
- Super attack flask (6): Item action:consume:Super attack flask (6)
- Super defence flask (1): Item action:consume:Super defence flask (1)
- Super defence flask (2): Item action:consume:Super defence flask (2)
- Super defence flask (3): Item action:consume:Super defence flask (3), Shop service:teplin_decant_flasks_to_vials:Super defence
- Super defence flask (4): Item action:consume:Super defence flask (4)
- Super defence flask (5): Item action:consume:Super defence flask (5)
- Super defence flask (6): Item action:consume:Super defence flask (6)
- Super prayer flask (1): Item action:consume:Super prayer flask (1)
- Super prayer flask (2): Item action:consume:Super prayer flask (2)
- Super prayer flask (3): Item action:consume:Super prayer flask (3), Shop service:teplin_decant_flasks_to_vials:Super prayer
- Super prayer flask (4): Item action:consume:Super prayer flask (4)
- Super prayer flask (5): Item action:consume:Super prayer flask (5)
- Super prayer flask (6): Item action:consume:Super prayer flask (6)
- Super restore flask (1): Item action:consume:Super restore flask (1)
- Super restore flask (2): Item action:consume:Super restore flask (2)
- Super restore flask (3): Item action:consume:Super restore flask (3), Shop service:teplin_decant_flasks_to_vials:Super restore
- Super restore flask (4): Item action:consume:Super restore flask (4)
- Super restore flask (5): Item action:consume:Super restore flask (5)
- Super restore flask (6): Item action:consume:Super restore flask (6)
- Super strength flask (1): Item action:consume:Super strength flask (1)
- Super strength flask (2): Item action:consume:Super strength flask (2)
- Super strength flask (3): Item action:consume:Super strength flask (3), Shop service:teplin_decant_flasks_to_vials:Super strength
- Super strength flask (4): Item action:consume:Super strength flask (4)
- Super strength flask (5): Item action:consume:Super strength flask (5)
- Super strength flask (6): Item action:consume:Super strength flask (6)
- Suqah tooth: Utility:grind_suqah_tooth
- Tchiki monkey nuts: Utility:grind_tchiki_monkey_nuts
- White lily seed: Farming:white_lily
- White tree sapling: Farming:white_tree
- Wimpy feather: Herblore:finished_fletching_potion
```

### `python3 tools/worktree_guard.py audit` (exit 0)

```text
Worktree layout safe: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork
Linked worktree root: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees
```

### `git diff --check` (exit 0)

```text
(no output)
```

## Not done

- The 247 dormant rows were not wired, demoted, or copied into generated data.
- No diary tier was made claimable.
- The Beefy Bill banking service was not built, stubbed, or anticipated.
- No quest, combat, or Slayer data file was edited.
- No newer source was fetched and no permanent link was replaced.
- No offscreen Qt lane was run on this branch. The brief invokes the promotion-gate exception: the orchestrator reruns both lanes after merge, so this branch runs the plain lane only.
- No user interface code changed.
- No remote was pushed.
