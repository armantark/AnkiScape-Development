import copy
import json
import unittest
from pathlib import Path

from constants import (
    COMBAT_ENEMY_DATA,
    CRAFTING_DATA,
    EQUIPMENT_DATA,
    ITEM_DEFINITIONS,
    ORE_DATA,
)
from logic_pure import (
    apply_combat_burst_pure,
    charge_training_urn_pure,
    full_urn_teleport_info_pure,
    teleport_full_urn_pure,
)
from runtime_actions import (
    RuntimeActionContext,
    handle_cooking_answer,
    handle_hunter_answer,
    handle_mining_answer,
    handle_smithing_answer,
    run_answer_with_carried_overlay,
)
from storage_pure import CURRENT_CONFIG_VERSION, migrate_loaded_data
from tools.fetch_prayer_assets import asset_manifest
from urn_data import (
    URN_PHYSICAL_ITEM_NAMES,
    URN_STATE_ITEM_NAMES,
    URN_TIERS,
    URN_TIERS_BY_ID,
    sanitize_urn_state_pure,
)


ROOT = Path(__file__).resolve().parents[1]


def _context(player_data, random_values=()):
    calls = {"xp": [], "errors": [], "saves": 0}
    rolls = iter(random_values)

    def random_random():
        try:
            return next(rolls)
        except StopIteration:
            return 0.0

    def award_skill_exp(exp_key, amount):
        player_data[exp_key] = float(player_data.get(exp_key, 0.0) or 0.0) + float(amount)
        return float(amount)

    return RuntimeActionContext(
        player_data=player_data,
        random_random=random_random,
        show_error_message=lambda title, message: calls["errors"].append((title, message)),
        deactivate_current_skill=lambda: calls.setdefault("deactivated", True),
        award_skill_exp=award_skill_exp,
        award_hidden_skill_exp=lambda exp_key, _level_key, amount: player_data.__setitem__(
            exp_key, float(player_data.get(exp_key, 0.0) or 0.0) + float(amount)
        ),
        level_up_check=lambda _skill, _data: None,
        check_achievements=lambda _data: None,
        save_player_data=lambda: calls.__setitem__("saves", calls["saves"] + 1),
        refresh_skill_availability=lambda: None,
        refresh_skill_availability_partial=lambda *_args: None,
        can_smith_any=lambda: False,
        show_exp=lambda amount: calls["xp"].append(amount),
        show_activity_gain=lambda text: calls.setdefault("activity", []).append(text),
        implemented_exp_keys_snapshot=lambda: {},
        show_quest_exp_delta=lambda _before: None,
    )


class UrnDataAuthorityTest(unittest.TestCase):
    def test_all_26_tiers_have_five_certified_source_ids(self):
        self.assertEqual(len(URN_TIERS), 26)
        self.assertEqual(
            tuple(tier.source_item_ids[0] for tier in URN_TIERS),
            (
                20379, 20385, 20391, 20397, 20403,
                20349, 20355, 20361, 20367, 20373,
                20319, 20325, 20331, 20337, 20343,
                20295, 20301, 20307, 20313,
                20271, 20277, 20283, 20289,
                20409, 20415, 20421,
            ),
        )
        self.assertEqual(len(URN_PHYSICAL_ITEM_NAMES), 26 * 5)
        self.assertEqual(len({item_id for tier in URN_TIERS for item_id in tier.source_item_ids}), 26 * 5)

    def test_crafting_rows_are_exported_from_the_authority(self):
        urn_recipe_ids = []
        for tier in URN_TIERS:
            stable_item = tier.item_base.lower().replace(" ", "_")
            expected = (
                (f"form_{stable_item}_unf", tier.item_unf, tier.forming_xp, tier.source_item_ids[0]),
                (f"fire_{stable_item}_nr", tier.item_nr, tier.firing_xp, tier.source_item_ids[1]),
                (f"add_rune_{stable_item}", tier.item_r, 1.0, tier.source_item_ids[2]),
            )
            for recipe_id, output_item, xp, source_item_id in expected:
                urn_recipe_ids.append(recipe_id)
                row = CRAFTING_DATA[recipe_id]
                self.assertEqual(row["output_item"], output_item)
                self.assertEqual(row["exp"], xp)
                self.assertEqual(row["source_item_id"], source_item_id)
                self.assertEqual(row["source_enum"], tier.source_enum)
        self.assertEqual(len(urn_recipe_ids), 78)
        self.assertEqual(len(set(urn_recipe_ids)), 78)

    def test_all_physical_states_are_nonstackable_registry_items_with_source_ids(self):
        definitions = {item.storage_key: item for item in ITEM_DEFINITIONS}
        for tier in URN_TIERS:
            for item_name, source_item_id in zip(
                (tier.item_unf, tier.item_nr, tier.item_r, tier.item_active, tier.item_full),
                tier.source_item_ids,
            ):
                with self.subTest(item=item_name):
                    definition = definitions[item_name]
                    self.assertFalse(definition.stackable)
                    self.assertEqual(definition.source_item_id, source_item_id)

    def test_runtime_substitution_set_is_only_runed_active_and_full(self):
        expected = {
            item_name
            for tier in URN_TIERS
            for item_name in (tier.item_r, tier.item_active, tier.item_full)
        }
        self.assertEqual(URN_STATE_ITEM_NAMES, expected)


class UrnPureLifecycleTest(unittest.TestCase):
    def test_charging_requires_the_selected_carried_target_and_does_not_alias_input(self):
        bank_only = {"inventory": {"Cracked mining urn (r)": 1}}
        unchanged, info = charge_training_urn_pure(bank_only, "mining", "copper", 1, 17.5, "copper")
        self.assertFalse(info["charged"])
        self.assertEqual(unchanged["inventory"]["Cracked mining urn (r)"], 1)

        other_target = {
            "inventory": {"Cracked mining urn (r)": 1},
            "carried_inventory": {"tin": {"Cracked mining urn (r)": 1}},
        }
        unchanged, info = charge_training_urn_pure(other_target, "mining", "copper", 1, 17.5, "copper")
        self.assertFalse(info["charged"])
        self.assertEqual(unchanged["carried_inventory"], other_target["carried_inventory"])

        selected = {
            "inventory": {"Cracked mining urn (r)": 1},
            "carried_inventory": {"copper": {"Cracked mining urn (r)": 1}},
        }
        original = copy.deepcopy(selected)
        updated, info = charge_training_urn_pure(selected, "mining", "copper", 1, 17.5, "copper")
        self.assertTrue(info["charged"])
        self.assertEqual(selected, original)
        self.assertEqual(updated["inventory"]["Cracked mining urn (r)"], 0)
        self.assertEqual(updated["inventory"]["Cracked mining urn"], 1)
        self.assertEqual(updated["carried_inventory"]["copper"], {"Cracked mining urn": 1})

    def test_full_conversion_preserves_overflow_into_the_next_carried_urn(self):
        tier = URN_TIERS_BY_ID["mining_cracked_urn"]
        player = {
            "inventory": {tier.item_active: 1, tier.item_r: 1},
            "carried_inventory": {"copper": {tier.item_active: 1, tier.item_r: 1}},
            "active_urn_mining": tier.id,
            "urn_progress_mining": tier.capacity_base_xp - 7.5,
        }
        updated, info = charge_training_urn_pure(player, "mining", "copper", 1, 17.5, "copper")
        self.assertEqual(info["base_xp_charged"], 17.5)
        self.assertEqual(info["filled"], (tier.id,))
        self.assertEqual(info["activated"], (tier.id,))
        self.assertEqual(updated["inventory"][tier.item_full], 1)
        self.assertEqual(updated["inventory"][tier.item_active], 1)
        self.assertEqual(updated["urn_progress_mining"], 10.0)
        self.assertEqual(
            updated["carried_inventory"]["copper"],
            {tier.item_full: 1, tier.item_active: 1},
        )

    def test_no_charge_still_returns_repaired_pointer_state(self):
        player = {
            "inventory": {"Cracked mining urn (r)": 1},
            "active_urn_mining": "prayer_impious_urn",
            "urn_progress_mining": 999.0,
        }
        updated, info = charge_training_urn_pure(player, "mining", "copper", 1, 17.5, "copper")
        self.assertFalse(info["charged"])
        self.assertEqual(updated["active_urn_mining"], "")
        self.assertEqual(updated["urn_progress_mining"], 0.0)

    def test_full_urn_teleport_requires_the_current_target_carried_copy(self):
        tier = URN_TIERS_BY_ID["mining_cracked_urn"]
        bank_only = {
            "inventory": {tier.item_full: 1},
            "current_ore": "copper",
        }
        info = full_urn_teleport_info_pure(bank_only, tier.item_full)
        self.assertEqual(info["urn_id"], tier.id)
        self.assertFalse(info["eligible"])
        rejected, xp, ok, skill_id = teleport_full_urn_pure(bank_only, tier.id)
        self.assertFalse(ok)
        self.assertEqual((xp, skill_id), (0.0, "mining"))
        self.assertEqual(rejected, bank_only)

        wrong_target = {
            **bank_only,
            "carried_inventory": {"tin": {tier.item_full: 1}},
        }
        self.assertFalse(full_urn_teleport_info_pure(wrong_target, tier.item_full)["eligible"])

        carried = {
            **bank_only,
            "carried_inventory": {"copper": {tier.item_full: 1}},
        }
        original = copy.deepcopy(carried)
        updated, xp, ok, skill_id = teleport_full_urn_pure(carried, tier.id)
        self.assertTrue(ok)
        self.assertEqual((xp, skill_id), (tier.teleport_xp, "mining"))
        self.assertEqual(carried, original)
        self.assertEqual(updated["inventory"][tier.item_full], 0)
        self.assertNotIn("copper", updated["carried_inventory"])
        telemetry = updated["action_telemetry"]["actions"][f"mining:teleport_{tier.id}"]
        self.assertEqual((telemetry["attempts"], telemetry["successes"]), (1, 1))
        self.assertEqual(telemetry["expected_successes"], 1.0)

    def test_prayer_urn_teleport_updates_both_prayer_counters(self):
        tier = URN_TIERS_BY_ID["prayer_impious_urn"]
        player = {
            "inventory": {tier.item_full: 1},
            "current_combat_target": "ghost",
            "carried_inventory": {"ghost": {tier.item_full: 1}},
            "prayer_urns_teleported": 2,
            "prayer_actions_completed": 7,
        }
        updated, xp, ok, skill_id = teleport_full_urn_pure(player, tier.id)
        self.assertTrue(ok)
        self.assertEqual((xp, skill_id), (120.0, "prayer"))
        self.assertEqual(updated["prayer_urns_teleported"], 3)
        self.assertEqual(updated["prayer_actions_completed"], 8)

    def test_sanitizer_keeps_valid_banked_partial_and_clears_dangling_progress(self):
        tier = URN_TIERS_BY_ID["cooking_cracked_urn"]
        valid = sanitize_urn_state_pure(
            {
                "inventory": {tier.item_active: 1},
                "active_urn_cooking": tier.id,
                "urn_progress_cooking": 123.5,
            }
        )
        self.assertEqual(valid["active_urn_cooking"], tier.id)
        self.assertEqual(valid["urn_progress_cooking"], 123.5)

        invalid = sanitize_urn_state_pure(
            {
                "inventory": {},
                "active_urn_cooking": tier.id,
                "urn_progress_cooking": float("nan"),
            }
        )
        self.assertEqual(invalid["active_urn_cooking"], "")
        self.assertEqual(invalid["urn_progress_cooking"], 0.0)


class UrnRuntimeOverlayTest(unittest.TestCase):
    @staticmethod
    def _mining_player(drop=False):
        player = {
            "inventory": {"Cracked mining urn (r)": 1},
            "carried_inventory": {"copper": {"Cracked mining urn (r)": 1}},
            "mining_level": 1,
            "mining_exp": 0.0,
            "current_ore": "copper",
            "toolbelt": {"mining": ["bronze_pickaxe"]},
            "equipment": {},
            "quests": {},
            "completed_achievements": [],
        }
        if drop:
            player["carried_keep_drop"] = {"copper": "drop"}
        return player

    def test_gathering_keep_folds_product_but_not_urn_substitutions(self):
        player = self._mining_player()
        ok = run_answer_with_carried_overlay(
            _context(player, (0.0, 0.0, 1.0, 0.0)),
            "mining",
            handle_mining_answer,
        )
        self.assertTrue(ok)
        self.assertEqual(player["inventory"]["Copper ore"], 1)
        self.assertEqual(player["inventory"]["Cracked mining urn"], 1)
        self.assertEqual(
            player["carried_inventory"]["copper"],
            {"Cracked mining urn": 1, "Copper ore": 1},
        )
        self.assertEqual(player["carried_churn"]["copper"], 1)

    def test_gathering_drop_destroys_product_but_keeps_carried_urn_transition(self):
        player = self._mining_player(drop=True)
        ok = run_answer_with_carried_overlay(
            _context(player, (0.0, 0.0, 1.0, 0.0)),
            "mining",
            handle_mining_answer,
        )
        self.assertTrue(ok)
        self.assertNotIn("Copper ore", player["inventory"])
        self.assertEqual(player["inventory"]["Cracked mining urn"], 1)
        self.assertEqual(player["carried_inventory"]["copper"], {"Cracked mining urn": 1})
        self.assertNotIn("copper", player.get("carried_churn", {}))

    def test_active_urn_survives_custom_layout_bank_repack_and_keeps_charging(self):
        player = self._mining_player()
        player["carried_advanced_targets"] = {"copper": True}
        player["carried_layout"] = {"copper": {"Cracked mining urn (r)": 1}}

        self.assertTrue(
            run_answer_with_carried_overlay(
                _context(player, (0.0, 0.0, 1.0, 0.0)), "mining", handle_mining_answer
            )
        )
        first_progress = player["urn_progress_mining"]
        self.assertEqual(player["carried_inventory"]["copper"]["Cracked mining urn"], 1)

        player["carried_churn"]["copper"] = 28
        self.assertTrue(
            run_answer_with_carried_overlay(
                _context(player, (0.0, 0.0, 1.0, 0.0)), "mining", handle_mining_answer
            )
        )
        self.assertEqual(player["carried_inventory"]["copper"], {"Cracked mining urn": 1})

        self.assertTrue(
            run_answer_with_carried_overlay(
                _context(player, (0.0, 0.0, 1.0, 0.0)), "mining", handle_mining_answer
            )
        )
        self.assertGreater(player["urn_progress_mining"], first_progress)

    def test_cooking_and_smithing_use_post_handler_carried_views(self):
        cooking = {
            "inventory": {"Raw shrimps": 1, "Cracked cooking urn (r)": 1},
            "cooking_level": 99,
            "cooking_exp": 0.0,
            "current_cooking": "cook_shrimps",
            "completed_achievements": [],
            "carried_advanced_targets": {"cook_shrimps": True},
            "carried_layout": {"cook_shrimps": {"Raw shrimps": 1, "Cracked cooking urn (r)": 1}},
        }
        self.assertTrue(
            run_answer_with_carried_overlay(
                _context(cooking, (0.0,)), "cooking", handle_cooking_answer
            )
        )
        self.assertEqual(cooking["inventory"]["Shrimps"], 1)
        self.assertEqual(cooking["carried_inventory"]["cook_shrimps"], {"Cracked cooking urn": 1})
        self.assertEqual(cooking["urn_progress_cooking"], 30.0)
        self.assertEqual(cooking["carried_churn"]["cook_shrimps"], 1)

        smithing = {
            "inventory": {"Copper ore": 1, "Tin ore": 1, "Cracked smelting urn (r)": 1},
            "smithing_level": 99,
            "smithing_exp": 0.0,
            "current_smith": "smelt_bronze_bar",
            "completed_achievements": [],
            "quests": {},
            "carried_advanced_targets": {"smelt_bronze_bar": True},
            "carried_layout": {
                "smelt_bronze_bar": {"Copper ore": 1, "Tin ore": 1, "Cracked smelting urn (r)": 1}
            },
        }
        self.assertTrue(
            run_answer_with_carried_overlay(
                _context(smithing), "smithing", handle_smithing_answer
            )
        )
        self.assertEqual(smithing["inventory"]["Bronze bar"], 1)
        self.assertEqual(smithing["carried_inventory"]["smelt_bronze_bar"], {"Cracked smelting urn": 1})
        self.assertEqual(smithing["urn_progress_smithing"], 6.2)
        self.assertEqual(smithing["carried_churn"]["smelt_bronze_bar"], 2)

    def test_hunter_custom_layout_supplies_bonecrusher_on_the_first_trip(self):
        target = "catch_crimson_swift"
        player = {
            "inventory": {"Bonecrusher": 1, "Bird snare": 1},
            "hunter_level": 99,
            "hunter_exp": 0.0,
            "prayer_level": 1,
            "prayer_exp": 0.0,
            "current_hunter": target,
            "completed_achievements": [],
            "quests": {},
            "carried_advanced_targets": {target: True},
            "carried_layout": {target: {"Bonecrusher": 1, "Bird snare": 1}},
        }
        self.assertTrue(
            run_answer_with_carried_overlay(
                _context(player, (0.0,)), "hunter", handle_hunter_answer
            )
        )
        self.assertEqual(player["inventory"]["Bones"], 0)
        self.assertEqual(player["prayer_exp"], 4.5)
        self.assertEqual(player["prayer_bonecrusher_triggers"], 1)
        self.assertEqual(player["prayer_actions_completed"], 1)
        self.assertNotIn("Bones", player["carried_inventory"][target])
        self.assertEqual(player["carried_churn"][target], 2)


class UrnStorageAndCombatLayoutTest(unittest.TestCase):
    def test_current_schema_load_always_sanitizes_without_losing_valid_partial_or_unknown_keys(self):
        tier = URN_TIERS_BY_ID["mining_cracked_urn"]
        valid = migrate_loaded_data(
            {
                "config_version": CURRENT_CONFIG_VERSION,
                "inventory": {tier.item_active: 1},
                "active_urn_mining": tier.id,
                "urn_progress_mining": 42.5,
                "future_unknown": {"kept": True},
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(valid["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(valid["active_urn_mining"], tier.id)
        self.assertEqual(valid["urn_progress_mining"], 42.5)
        self.assertEqual(valid["future_unknown"], {"kept": True})

        dangling = migrate_loaded_data(
            {
                "config_version": CURRENT_CONFIG_VERSION,
                "inventory": {},
                "active_urn_mining": tier.id,
                "urn_progress_mining": 42.5,
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(dangling["active_urn_mining"], "")
        self.assertEqual(dangling["urn_progress_mining"], 0.0)

    def test_combat_custom_layout_repacked_after_loot_bank_run_without_loop(self):
        target = "chicken"
        player = {
            "inventory": {"Bonecrusher": 1, "Raw chicken": 1},
            "equipment": {},
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "prayer_level": 1,
            "current_combat_target": target,
            "combat_attack_style": "aggressive",
            "combat_lifepoints": 990,
            "combat_auto_eat_food": ["Shrimps"],
            "combat_supply_loadout": {
                "food": {"Shrimps": 26},
                "potions": {},
                "stat_potions": {},
                "ammo": {},
                "runes": {},
                "cannonballs": 0,
            },
            "combat_current_levels": {},
            "combat_status_effects": {},
            "combat_recovery_progress": {},
            "combat_encounter": {},
            "combat_kill_counts": {},
            "carried_inventory": {target: {"Bonecrusher": 1, "Raw chicken": 1}},
            "carried_advanced_targets": {target: True},
            "carried_layout": {target: {"Bonecrusher": 1}},
        }

        first, ok, result = apply_combat_burst_pure(player, COMBAT_ENEMY_DATA, EQUIPMENT_DATA, ticks=1, rng=lambda: 0.5)
        self.assertTrue(ok)
        self.assertEqual(result["reason"], "combat_bank_run")
        self.assertTrue(result["bank_run_started"])

        second, ok, result = apply_combat_burst_pure(first, COMBAT_ENEMY_DATA, EQUIPMENT_DATA, ticks=1, rng=lambda: 0.5)
        self.assertTrue(ok)
        self.assertTrue(result["bank_run_completed"])
        self.assertEqual(second["carried_inventory"][target], {"Bonecrusher": 1})

        third, ok, result = apply_combat_burst_pure(second, COMBAT_ENEMY_DATA, EQUIPMENT_DATA, ticks=1, rng=lambda: 0.5)
        self.assertTrue(ok)
        self.assertNotEqual(result["reason"], "combat_bank_run")
        self.assertEqual(third["carried_inventory"][target], {"Bonecrusher": 1})


class PrayerPassiveAssetTest(unittest.TestCase):
    def test_manifest_and_provenance_cover_only_the_new_passive_files_as_missing_outputs(self):
        requests = {request.item_name: request for request in asset_manifest()}
        provenance = json.loads((ROOT / "assets_provenance.json").read_text(encoding="utf-8"))
        for item_name, filename in (
            ("Bonecrusher", "bonecrusher.png"),
            ("Ectoplasmator", "ectoplasmator.png"),
        ):
            request = requests[item_name]
            self.assertEqual(request.output_path, ROOT / "prayeritems" / filename)
            self.assertTrue(request.output_path.is_file())
            row = provenance[f"prayeritems/{filename}"]
            self.assertEqual(row["source_wiki"], "rs3")
            self.assertTrue(row["file_page_url"].startswith("https://"))
            self.assertTrue(row["sha1"])


if __name__ == "__main__":
    unittest.main()
