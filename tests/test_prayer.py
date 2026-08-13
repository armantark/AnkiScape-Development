import os
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, PRAYER_DATA, PRAYER_ITEM_IMAGES, UTILITY_ACTIVITY_DATA
from ankiscape.logic_pure.logic_pure import (
    apply_combat_burst_pure,
    apply_combat_preset_pure,
    apply_combat_target_overrides_pure,
    apply_prayer_action_pure,
    apply_prayer_selection_pure,
    apply_utility_activity_pure,
    curse_expected_ramp_pure,
    effective_gilded_altar_multiplier_pure,
    owned_gilded_altar_access_reasons_pure,
    derive_casual_combat_magic_pure,
    prayer_drain_for_ticks_pure,
    prayer_effect_state_pure,
    sanitize_prayer_selection_pure,
    save_combat_preset_pure,
)
from ankiscape.data.prayer_data import COMBAT_PRAYERS_BY_ID, PRAYER_MATERIALS, PRAYER_TARGETS
from ankiscape.core.storage_pure import CURRENT_CONFIG_VERSION, migrate_loaded_data
from ankiscape.core.target_metadata import prayer_target_rows


class PrayerDataAndMechanicsTest(unittest.TestCase):
    def test_complete_books_and_training_tables_have_stable_unique_ids(self):
        self.assertEqual(len([row for row in COMBAT_PRAYERS_BY_ID.values() if row.book == "standard"]), 30)
        self.assertEqual(len([row for row in COMBAT_PRAYERS_BY_ID.values() if row.book == "curses"]), 20)
        self.assertEqual(len(PRAYER_MATERIALS), 21)
        self.assertEqual(len(PRAYER_TARGETS), 61)
        self.assertEqual(len(PRAYER_TARGETS), len(set(PRAYER_TARGETS)))
        self.assertIn("ancient_bones", {material.id for material in PRAYER_MATERIALS})
        self.assertIn("bury_ancient_bones", PRAYER_TARGETS)
        self.assertEqual(PRAYER_TARGETS["bury_ancient_bones"]["exp"], 200.0)
        self.assertNotIn("ectofuntus_ancient_bones", PRAYER_TARGETS)
        self.assertNotIn("gilded_altar_ancient_bones", PRAYER_TARGETS)

    def test_owned_gilded_altar_accepts_zero_one_or_two_burners_at_exact_rates(self):
        target_id = "gilded_altar_dragon_bones"
        for burner_flags, herbs, expected in (
            ({}, 0, 2.5),
            ({"marble_burner": True}, 1, 3.0),
            ({"marble_burner": True, "mahogany_burner": True}, 2, 3.5),
        ):
            with self.subTest(expected=expected):
                state = {
                    "house_owned": True,
                    "house_rooms_bought": {"chapel": True},
                    "house_built_flags": {"guilded_altar": True, **burner_flags},
                    "inventory": {"Dragon bones": 1, "Clean marrentill": herbs},
                    "prayer_owned_altar_stint": {},
                }
                self.assertEqual(owned_gilded_altar_access_reasons_pure(state, target_id), ())
                self.assertEqual(effective_gilded_altar_multiplier_pure(state, "owned", target_id), expected)
        self.assertEqual(effective_gilded_altar_multiplier_pure({}, "hosted", target_id), 3.5)

    def test_composite_prayer_selection_clears_only_changed_search_and_stint_state(self):
        target_id = "gilded_altar_dragon_bones"
        state = {
            "prayer_level": 99,
            "current_prayer": target_id,
            "prayer_gilded_mode": "owned",
            "prayer_gilded_house_search": {"target_id": target_id, "reviews_remaining": 3},
            "prayer_owned_altar_stint": {"target_id": target_id, "burners_lit": 1},
            "house_owned": True,
            "house_rooms_bought": {"chapel": True},
            "house_built_flags": {"guilded_altar": True, "marble_burner": True},
            "inventory": {"Dragon bones": 2},
        }
        reselected, ok, reasons = apply_prayer_selection_pure(
            state, "dragon_bones", "gilded_owned", PRAYER_DATA
        )
        self.assertTrue(ok)
        self.assertEqual(reasons, ())
        self.assertEqual(reselected["prayer_owned_altar_stint"], state["prayer_owned_altar_stint"])
        self.assertEqual(reselected["prayer_gilded_house_search"], state["prayer_gilded_house_search"])

        hosted, ok, reasons = apply_prayer_selection_pure(
            state, "dragon_bones", "gilded_hosted", PRAYER_DATA
        )
        self.assertTrue(ok)
        self.assertEqual(reasons, ())
        self.assertEqual(hosted["prayer_gilded_mode"], "hosted")
        self.assertEqual(hosted["prayer_owned_altar_stint"], {})
        self.assertEqual(hosted["prayer_gilded_house_search"], {})

        rejected, ok, reasons = apply_prayer_selection_pure(
            {"prayer_level": 99, "inventory": {"Dragon bones": 1}},
            "dragon_bones",
            "gilded_owned",
            PRAYER_DATA,
        )
        self.assertFalse(ok)
        self.assertIn("a player-owned house", reasons)
        self.assertNotIn("current_prayer", rejected)

    def test_ectofuntus_consumes_inputs_and_returns_containers_and_tokens(self):
        inventory, xp, ok, outputs = apply_prayer_action_pure(
            "ectofuntus_dragon_bones",
            {"Dragon bonemeal": 1, "Bucket of slime": 1},
            PRAYER_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual(xp, 288.0)
        self.assertEqual(inventory["Dragon bonemeal"], 0)
        self.assertEqual(inventory["Bucket of slime"], 0)
        self.assertEqual(outputs, {"Bucket": 1, "Empty pot": 1, "Ecto-token": 5})

    def test_decoded_bonemeals_keep_exact_ids_and_generated_ectofuntus_contracts(self):
        cases = (
            ("burnt_bones", "Burnt bones", "Burnt bonemeal", 4258, 4.5),
            ("zogre_bones", "Zogre bones", "Zogre bonemeal", 4852, 22.5),
            ("jogre_bones", "Jogre bones", "Jogre bonemeal", 4271, 15.0),
            ("shaikahan_bones", "Shaikahan bones", "Shaikahan bonemeal", 5615, 25.0),
            ("fayrg_bones", "Fayrg bones", "Fayrg bonemeal", 4853, 84.0),
            ("raurg_bones", "Raurg bones", "Raurg bonemeal", 4854, 96.0),
            ("ourg_bones", "Ourg bones", "Ourg bonemeal", 4855, 140.0),
            ("frost_dragon_bones", "Frost dragon bones", "Frost dragon bonemeal", 18834, 180.0),
        )
        item_definitions = {definition.storage_key: definition for definition in ITEM_DEFINITIONS}
        for material_id, bone, bonemeal, item_id, base_xp in cases:
            with self.subTest(material_id=material_id):
                self.assertEqual(item_definitions[bonemeal].source_item_id, item_id)
                self.assertEqual(PRAYER_DATA[f"bury_{material_id}"]["exp"], base_xp)
                grind = UTILITY_ACTIVITY_DATA[f"grind_prayer_{material_id}"]
                self.assertEqual(grind["requirements"], {bone: 1, "Empty pot": 1})
                self.assertEqual(grind["output_item"], bonemeal)
                self.assertEqual(grind["output_qty"], 1)
                self.assertEqual(grind["batch_size"], 9)

                ectofuntus = PRAYER_DATA[f"ectofuntus_{material_id}"]
                self.assertEqual(ectofuntus["requirements"], {bonemeal: 1, "Bucket of slime": 1})
                self.assertEqual(ectofuntus["byproducts"], {"Bucket": 1, "Empty pot": 1})
                self.assertEqual(ectofuntus["outputs"], {"Ecto-token": 5})
                self.assertEqual(ectofuntus["exp"], base_xp * 4.0)

        self.assertEqual(item_definitions["Wyvern bonemeal"].source_item_id, 6810)
        self.assertEqual(PRAYER_DATA["ectofuntus_wyvern_bones"]["exp"], 200.0)

    def test_manual_burial_consumes_one_bone_per_review_action(self):
        inventory, xp, ok, outputs = apply_prayer_action_pure(
            "bury_bones",
            {"Bones": 3},
            PRAYER_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual(xp, 4.5)
        self.assertEqual(inventory["Bones"], 2)
        self.assertEqual(outputs, {})

    def test_prayer_preparation_batches_cap_at_nine_and_twenty_eight(self):
        ground, _xp, ok, processed = apply_utility_activity_pure(
            "grind_prayer_dragon_bones",
            {"Dragon bones": 20, "Empty pot": 20},
            UTILITY_ACTIVITY_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual(processed, 9)
        self.assertEqual(ground["Dragon bonemeal"], 9)
        slime, _xp, ok, processed = apply_utility_activity_pure(
            "collect_ectofuntus_slime",
            {"Bucket": 40},
            UTILITY_ACTIVITY_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual(processed, 28)
        self.assertEqual(slime["Bucket of slime"], 28)

    def test_drain_counter_uses_two_tick_timer_and_prayer_bonus_resistance(self):
        no_bonus = prayer_drain_for_ticks_pure(100, 0, ("thick_skin",), 0, 4, 1.0)
        bonus = prayer_drain_for_ticks_pure(100, 0, ("thick_skin",), 15, 4, 1.0)
        self.assertEqual(no_bonus, (99, 0.0))
        self.assertEqual(bonus, (100, 60.0))

    def test_curse_drain_matches_pinned_displayed_point_cadence(self):
        points, counter = prayer_drain_for_ticks_pure(990, 0, ("soul_split",), 0, 1, 1.0)
        self.assertEqual((points, counter), (960, 0.0))

    def test_conflicts_keep_latest_valid_family_member_order(self):
        standard = {"prayer_level": 99, "combat_prayer_book": "standard", "knight_waves": {"completed": True}}
        self.assertEqual(
            sanitize_prayer_selection_pure(standard, ("clarity_of_thought", "burst_of_strength", "eagle_eye")),
            ("clarity_of_thought", "burst_of_strength"),
        )
        curses = {
            "prayer_level": 99,
            "combat_prayer_book": "curses",
            "quests": {"the_temple_at_senntisten": {"completed": True}},
        }
        self.assertEqual(
            sanitize_prayer_selection_pure(curses, ("sap_warrior", "sap_ranger", "leech_attack", "turmoil")),
            ("sap_warrior", "sap_ranger"),
        )
        self.assertEqual(
            sanitize_prayer_selection_pure(curses, ("deflect_melee", "soul_split", "wrath")),
            ("deflect_melee",),
        )

    def test_conflict_matrix_matches_standard_and_curse_activation_rules(self):
        standard = {
            "prayer_level": 99,
            "defense_level": 99,
            "combat_prayer_book": "standard",
            "knight_waves": {"completed": True},
        }
        matrix = {
            ("steel_skin", "eagle_eye"): ("steel_skin", "eagle_eye"),
            ("steel_skin", "mystic_might"): ("steel_skin", "mystic_might"),
            ("steel_skin", "rigour"): ("steel_skin",),
            ("rigour", "steel_skin"): ("rigour",),
            ("rapid_restore", "rapid_heal"): ("rapid_restore", "rapid_heal"),
            ("rapid_restore", "rapid_renewal"): ("rapid_restore", "rapid_renewal"),
            ("rapid_heal", "rapid_renewal"): ("rapid_heal",),
            ("protect_from_summoning", "protect_from_melee"): ("protect_from_summoning", "protect_from_melee"),
            ("protect_from_melee", "redemption"): ("protect_from_melee",),
        }
        for selected, expected in matrix.items():
            with self.subTest(selected=selected):
                self.assertEqual(sanitize_prayer_selection_pure(standard, selected), expected)

        curses = {
            "prayer_level": 99,
            "defense_level": 99,
            "combat_prayer_book": "curses",
            "quests": {"the_temple_at_senntisten": {"completed": True}},
        }
        self.assertEqual(
            sanitize_prayer_selection_pure(curses, ("deflect_summoning", "deflect_melee")),
            ("deflect_summoning", "deflect_melee"),
        )
        self.assertEqual(
            sanitize_prayer_selection_pure(curses, ("deflect_melee", "soul_split")),
            ("deflect_melee",),
        )

    def test_piety_requires_defence_70_and_valid_combined_prayers_drain_in_aggregate(self):
        state = {
            "prayer_level": 99,
            "defense_level": 69,
            "combat_prayer_book": "standard",
            "knight_waves": {"completed": True},
        }
        self.assertEqual(sanitize_prayer_selection_pure(state, ("piety",)), ())
        state["defense_level"] = 70
        self.assertEqual(sanitize_prayer_selection_pure(state, ("piety",)), ("piety",))

        selected = sanitize_prayer_selection_pure(state, ("steel_skin", "eagle_eye", "protect_item"))
        self.assertEqual(selected, ("steel_skin", "eagle_eye", "protect_item"))
        self.assertEqual(prayer_drain_for_ticks_pure(100, 0, selected, 0, 1, 1.0), (98, 10.0))

    def test_high_tier_standard_prayers_enforce_their_defence_requirements(self):
        state = {
            "prayer_level": 99,
            "defense_level": 64,
            "combat_prayer_book": "standard",
            "knight_waves": {"completed": True},
        }
        self.assertEqual(sanitize_prayer_selection_pure(state, ("chivalry",)), ())
        state["defense_level"] = 65
        self.assertEqual(sanitize_prayer_selection_pure(state, ("chivalry",)), ("chivalry",))
        self.assertEqual(sanitize_prayer_selection_pure(state, ("rigour", "augury")), ())
        state["defense_level"] = 70
        self.assertEqual(sanitize_prayer_selection_pure(state, ("rigour",)), ("rigour",))
        self.assertEqual(sanitize_prayer_selection_pure(state, ("augury",)), ("augury",))

    def test_master_off_masks_effects_without_erasing_configured_fields(self):
        state = {
            "prayer_level": 99,
            "defense_level": 99,
            "combat_prayer_book": "standard",
            "combat_selected_prayers": ["protect_item", "steel_skin"],
            "combat_prayer_uptime": "100",
            "combat_prayer_points": 990,
            "combat_prayers_enabled": False,
        }
        effects = prayer_effect_state_pure(state)
        self.assertEqual(effects["uptime"], 0.0)
        self.assertEqual(effects["selected"], ())
        self.assertNotIn("protect_item", effects)
        self.assertEqual(state["combat_selected_prayers"], ["protect_item", "steel_skin"])
        self.assertEqual(state["combat_prayer_uptime"], "100")

        burst_state = {
            **state,
            "current_combat_target": "chicken",
            "attack_level": 99,
            "strength_level": 99,
            "constitution_level": 99,
            "combat_lifepoints": 990,
            "inventory": {},
        }
        after, ok, result = apply_combat_burst_pure(burst_state, ticks=8, rng=lambda: .5)
        self.assertTrue(ok)
        self.assertEqual(result["prayer_uptime"], 0.0)
        self.assertEqual(after["combat_prayer_points"], 990)
        self.assertEqual(after["combat_selected_prayers"], ["protect_item", "steel_skin"])
        self.assertEqual(after["combat_prayer_uptime"], "100")

    def test_sap_and_leech_ramps_use_proc_steps_and_five_stack_cap(self):
        self.assertEqual(curse_expected_ramp_pure(100, "sap")["enemy_drain"], .20)
        leech = curse_expected_ramp_pure(100, "leech")
        self.assertEqual(leech["enemy_drain"], .25)
        self.assertEqual(leech["self_boost"], .10)

    def test_ancient_gilded_target_migrates_to_existing_bury_target(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 28,
                "current_prayer": "gilded_altar_ancient_bones",
                "inventory": {"Ancient bones": 5},
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["current_prayer"], "bury_ancient_bones")
        self.assertIn(migrated["current_prayer"], PRAYER_TARGETS)
        self.assertEqual(migrated["inventory"]["Ancient bones"], 5)

    def test_named_preset_migration_and_target_override(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 28,
                "combat_pack_mode": "compact",
                "combat_auto_eat_threshold_percent": 55,
                "combat_selected_prayers": [],
                "pending_skill_exp_rewards": {"prayer_exp": 125.0},
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["prayer_exp"], 125.0)
        self.assertNotIn("prayer_exp", migrated["pending_skill_exp_rewards"])
        self.assertEqual(migrated["combat_presets"]["Default"]["combat_pack_mode"], "compact")

        configured = dict(migrated)
        configured["combat_prayer_uptime"] = "70"
        saved, ok = save_combat_preset_pure(configured, "Bossing")
        self.assertTrue(ok)
        saved["combat_target_overrides"] = {"chicken": {"combat_prayer_uptime": "40"}}
        applied, ok = apply_combat_preset_pure(saved, "Bossing", "chicken")
        self.assertTrue(ok)
        self.assertEqual(applied["combat_prayer_uptime"], "40")

    def test_combat_presets_never_snapshot_or_restore_finite_supplies(self):
        loaded = {
            "combat_supply_loadout": {
                "food": {"Lobster": 3},
                "potions": {},
                "stat_potions": {},
                "ammo": {},
                "runes": {},
                "cannonballs": 0,
            },
            "combat_prayer_uptime": "70",
        }
        saved, ok = save_combat_preset_pure(loaded, "Bossing")
        self.assertTrue(ok)
        self.assertNotIn("combat_supply_loadout", saved["combat_presets"]["Bossing"])

        # Old saves may already contain the bad field. Applying that preset must
        # leave the currently owned pack alone rather than minting its snapshot.
        saved["combat_presets"]["Bossing"]["combat_supply_loadout"] = {
            "food": {"Lobster": 99}
        }
        saved["combat_supply_loadout"]["food"] = {"Lobster": 1}
        applied, ok = apply_combat_preset_pure(saved, "Bossing")
        self.assertTrue(ok)
        self.assertEqual(applied["combat_supply_loadout"]["food"], {"Lobster": 1})

    def test_target_override_applies_without_pin_and_pinned_precedence_is_preset_then_override(self):
        state = {
            "prayer_level": 99,
            "defense_level": 99,
            "combat_prayer_book": "standard",
            "combat_selected_prayers": ["steel_skin"],
            "combat_prayer_uptime": "off",
            "combat_presets": {
                "Bossing": {
                    "combat_selected_prayers": ["protect_from_melee"],
                    "combat_prayer_uptime": "100",
                }
            },
            "combat_target_overrides": {
                "chicken": {
                    "combat_selected_prayers": ["eagle_eye"],
                    "combat_prayer_uptime": "40",
                }
            },
        }
        standalone = apply_combat_target_overrides_pure(state, "chicken")
        self.assertEqual(standalone["combat_selected_prayers"], ["eagle_eye"])
        self.assertEqual(standalone["combat_prayer_uptime"], "40")

        runtime_state = {
            **state,
            "current_combat_target": "chicken",
            "attack_level": 99,
            "strength_level": 99,
            "constitution_level": 99,
            "combat_lifepoints": 990,
            "combat_prayer_points": 990,
            "combat_prayers_enabled": True,
            "inventory": {},
        }
        runtime, runtime_ok, runtime_result = apply_combat_burst_pure(runtime_state, ticks=1, rng=lambda: .5)
        self.assertTrue(runtime_ok)
        self.assertEqual(runtime["combat_selected_prayers"], ["eagle_eye"])
        self.assertEqual(runtime_result["prayer_uptime"], .4)

        pinned, ok = apply_combat_preset_pure(state, "Bossing", "chicken")
        self.assertTrue(ok)
        self.assertEqual(pinned["combat_selected_prayers"], ["eagle_eye"])
        self.assertEqual(pinned["combat_prayer_uptime"], "40")

    def test_casual_pack_mode_preserves_disabled_config_and_falls_back_to_highest_legal_prayer(self):
        disabled = {
            "combat_pack_mode": "max_safety",
            "combat_prayers_enabled": False,
            "combat_selected_prayers": ["protect_item"],
            "combat_prayer_uptime": "70",
            "prayer_level": 99,
            "defense_level": 99,
        }
        preserved = derive_casual_combat_magic_pure(disabled)
        self.assertEqual(preserved["combat_selected_prayers"], ["protect_item"])
        self.assertEqual(preserved["combat_prayer_uptime"], "70")

        fallback = derive_casual_combat_magic_pure({
            "combat_pack_mode": "max_output",
            "combat_prayers_enabled": True,
            "combat_prayer_book": "standard",
            "combat_selected_prayers": [],
            "combat_prayer_uptime": "off",
            "current_combat_target": "chicken",
            "equipment": {},
            "prayer_level": 70,
            "defense_level": 69,
            "knight_waves": {"completed": True},
        })
        self.assertEqual(fallback["combat_selected_prayers"], ["chivalry"])

    def test_locked_curses_normalization_is_idempotent_and_preserves_nested_unknown_data(self):
        payload = {
            "config_version": CURRENT_CONFIG_VERSION,
            "inventory": {"Bonemeal": 4, "Wyvern bonemeal": 2},
            "combat_prayer_book": "curses",
            "combat_selected_prayers": ["turmoil"],
            "combat_presets": {
                "Future": {
                    "combat_prayer_book": "curses",
                    "combat_selected_prayers": ["turmoil"],
                    "future_preset_key": {"kept": True},
                }
            },
            "combat_active_preset": "Future",
            "combat_target_overrides": {
                "chicken": {
                    "combat_prayer_book": "curses",
                    "future_override_key": 17,
                }
            },
            "future_top_level_key": {"kept": True},
        }
        normalized = migrate_loaded_data(payload, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(normalized["combat_prayer_book"], "standard")
        self.assertEqual(normalized["combat_selected_prayers"], [])
        self.assertEqual(normalized["combat_presets"]["Future"]["combat_prayer_book"], "curses")
        self.assertEqual(normalized["combat_presets"]["Future"]["future_preset_key"], {"kept": True})
        self.assertEqual(normalized["combat_target_overrides"]["chicken"]["future_override_key"], 17)
        self.assertEqual(normalized["future_top_level_key"], {"kept": True})
        self.assertEqual(normalized["inventory"]["Bonemeal"], 4)
        self.assertEqual(normalized["inventory"]["Wyvern bonemeal"], 2)
        self.assertEqual(migrate_loaded_data(normalized, ORE_DATA, ITEM_DEFINITIONS), normalized)

    def test_protection_overlay_removes_matching_enemy_damage(self):
        base = {
            "current_combat_target": "chicken",
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "prayer_level": 99,
            "combat_lifepoints": 990,
            "combat_prayer_points": 990,
            "combat_prayer_uptime": "100",
            "combat_prayer_book": "standard",
            "inventory": {},
        }
        unprotected, ok, unprotected_result = apply_combat_burst_pure(base, ticks=8, rng=lambda: .5)
        protected_data = dict(base, combat_selected_prayers=["protect_from_melee"])
        protected, ok2, protected_result = apply_combat_burst_pure(protected_data, ticks=8, rng=lambda: .5)
        self.assertTrue(ok and ok2)
        self.assertGreaterEqual(unprotected_result["enemy_damage"], protected_result["enemy_damage"])
        self.assertEqual(protected_result["enemy_damage"], 0)
        self.assertLess(protected["combat_prayer_points"], 990)

    def test_rows_gate_missing_materials_and_all_asset_paths_exist(self):
        rows = prayer_target_rows({"prayer_level": 99, "inventory": {}}, PRAYER_DATA, PRAYER_ITEM_IMAGES, "bury_bones")
        self.assertTrue(rows)
        self.assertTrue(all(not row.enabled for row in rows))
        for path in PRAYER_ITEM_IMAGES.values():
            self.assertTrue(os.path.exists(path), path)


if __name__ == "__main__":
    unittest.main()
