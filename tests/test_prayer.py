import os
import unittest

from constants import ITEM_DEFINITIONS, ORE_DATA, PRAYER_DATA, PRAYER_ITEM_IMAGES, UTILITY_ACTIVITY_DATA
from logic_pure import (
    apply_combat_burst_pure,
    apply_combat_preset_pure,
    apply_prayer_action_pure,
    apply_utility_activity_pure,
    curse_expected_ramp_pure,
    prayer_drain_for_ticks_pure,
    sanitize_prayer_selection_pure,
    save_combat_preset_pure,
)
from prayer_data import COMBAT_PRAYERS_BY_ID, PRAYER_MATERIALS, PRAYER_TARGETS
from storage_pure import CURRENT_CONFIG_VERSION, migrate_loaded_data
from target_metadata import prayer_target_rows


class PrayerDataAndMechanicsTest(unittest.TestCase):
    def test_complete_books_and_training_tables_have_stable_unique_ids(self):
        self.assertEqual(len([row for row in COMBAT_PRAYERS_BY_ID.values() if row.book == "standard"]), 30)
        self.assertEqual(len([row for row in COMBAT_PRAYERS_BY_ID.values() if row.book == "curses"]), 20)
        self.assertEqual(len(PRAYER_MATERIALS), 21)
        self.assertEqual(len(PRAYER_TARGETS), 62)
        self.assertEqual(len(PRAYER_TARGETS), len(set(PRAYER_TARGETS)))
        self.assertNotIn("ectofuntus_ancient_bones", PRAYER_TARGETS)

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

    def test_sap_and_leech_ramps_use_proc_steps_and_five_stack_cap(self):
        self.assertEqual(curse_expected_ramp_pure(100, "sap")["enemy_drain"], .20)
        leech = curse_expected_ramp_pure(100, "leech")
        self.assertEqual(leech["enemy_drain"], .25)
        self.assertEqual(leech["self_boost"], .10)

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
