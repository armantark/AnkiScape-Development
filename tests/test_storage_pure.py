import unittest

from storage_pure import (
    default_player_data,
    migrate_loaded_data,
    CURRENT_CONFIG_VERSION,
)
from inventory_pure import DEFAULT_LOOT_VALUE_THRESHOLD
from constants import (
    BAR_DATA,
    CRAFTING_DATA,
    FIREMAKING_DATA,
    FIREMAKING_LOG_ITEMS,
    FIREMAKING_OUTPUT_ITEMS,
    FISHING_DATA,
    FISHING_OUTPUT_ITEMS,
    COOKING_DATA,
    COOKING_OUTPUT_ITEMS,
    FLETCHING_DATA,
    GEM_DATA,
    HUNTER_DATA,
    HUNTER_OUTPUT_ITEMS,
    ITEM_DEFINITIONS,
    MINING_OUTPUT_ITEMS,
    ORE_DATA,
    RUNECRAFTING_ACCESS_ITEMS,
    RUNECRAFTING_EXTRA_ITEM_DATA,
    RUNECRAFTING_OUTPUT_ITEMS,
    UTILITY_ACTIVITY_DATA,
    WOODCUTTING_LOG_ITEMS,
)


class TestStoragePure(unittest.TestCase):
    def test_default_player_data_has_expected_keys(self):
        data = default_player_data(ORE_DATA)
        # Core keys
        for key in [
            "config_version",
            "mining_level",
            "woodcutting_level",
            "smithing_level",
            "crafting_level",
            "fletching_level",
            "firemaking_level",
            "fishing_level",
            "cooking_level",
            "runecrafting_level",
            "hunter_level",
            "mining_exp",
            "woodcutting_exp",
            "smithing_exp",
            "crafting_exp",
            "fletching_exp",
            "firemaking_exp",
            "fishing_exp",
            "cooking_exp",
            "runecrafting_exp",
            "hunter_exp",
            "current_craft",
            "current_fletch",
            "current_firemaking",
            "current_fishing",
            "current_cooking",
            "current_runecrafting",
            "current_hunter",
            "current_utility",
            "current_quest",
            "current_combat_target",
            "combat_attack_style",
            "current_combat_spell",
            "combat_lifepoints",
            "combat_auto_eat_threshold_percent",
            "combat_auto_eat_food",
            "combat_supply_loadout",
            "combat_special_attack_energy",
            "combat_current_levels",
            "combat_status_effects",
            "combat_recovery_progress",
            "combat_encounter",
            "combat_kill_counts",
            "combat_last_result",
            "combat_grave",
            "death_office",
            "current_ore",
            "current_tree",
            "current_smith",
            "inventory",
            "progress_to_next",
            "completed_achievements",
            "toolbelt",
            "equipment",
            "attack_level",
            "defense_level",
            "ranged_level",
            "strength_level",
            "agility_level",
            "agility_exp",
            "constitution_level",
            "cooking_success_count",
            "cooking_burn_count",
            "hunter_success_count",
            "action_telemetry",
            "quests",
            "quest_points",
            "quest_combat_config",
            "quest_combat_encounters",
            "quest_combat_encounter_counts",
            "quest_stage_actions",
            "quest_route_states",
            "pending_skill_exp_rewards",
            "claims",
            "wicked_hood",
            "runecrafting_pouches",
            "item_charges",
            "unlocked_abilities",
            "carried_inventory",
            "loot_value_threshold",
            "shop_data_version",
            "shop_market_clock",
            "shop_stock_state",
            "shop_events",
            "shop_next_event_id",
        ]:
            self.assertIn(key, data)
        # Inventory uses real item names; Mining targets use stable IDs.
        for ore in MINING_OUTPUT_ITEMS:
            self.assertIn(ore, data["inventory"])  # zero by default
        self.assertEqual(data["config_version"], CURRENT_CONFIG_VERSION)
        self.assertIn("bronze_pickaxe", data["toolbelt"]["mining"])
        self.assertEqual(data["equipment"], {})
        self.assertEqual(data["attack_level"], 1)
        self.assertEqual(data["defense_level"], 1)
        self.assertEqual(data["agility_level"], 1)
        self.assertEqual(data["agility_exp"], 0)
        self.assertEqual(data["constitution_level"], 10)
        self.assertEqual(data["current_runecrafting"], "craft_air_runes")
        self.assertEqual(data["current_hunter"], "catch_crimson_swift")
        self.assertEqual(data["hunter_success_count"], 0)
        self.assertEqual(data["action_telemetry"], {"version": 1, "actions": {}})
        self.assertEqual(data["current_combat_target"], "chicken")
        self.assertEqual(data["combat_attack_style"], "accurate")
        self.assertEqual(data["current_combat_spell"], "wind_strike")
        self.assertEqual(data["combat_lifepoints"], 100)
        self.assertEqual(data["combat_auto_eat_threshold_percent"], 40)
        self.assertIn("Shrimps", data["combat_auto_eat_food"])
        self.assertEqual(data["combat_supply_loadout"], {"food": {}, "potions": {}, "stat_potions": {}, "ammo": {}, "runes": {}, "cannonballs": 0})
        self.assertEqual(data["combat_special_attack_energy"], 100)
        self.assertEqual(data["combat_current_levels"], {})
        self.assertEqual(data["combat_status_effects"], {})
        self.assertEqual(data["combat_recovery_progress"], {})
        self.assertEqual(data["combat_encounter"], {})
        self.assertEqual(data["combat_kill_counts"], {})
        self.assertEqual(data["combat_last_result"], {})
        self.assertEqual(data["combat_grave"], {})
        self.assertEqual(data["death_office"], {})
        self.assertEqual(data["current_quest"], "rune_mysteries")
        self.assertEqual(data["quest_points"], 0)
        self.assertEqual(data["quests"]["rune_mysteries"], {"started": False, "progress": 0, "completed": False})
        self.assertIn("lost_city", data["quests"])
        self.assertIn("lunar_diplomacy", data["quests"])
        self.assertEqual(data["quest_combat_config"], {"version": 1, "resolver_enabled": False})
        self.assertEqual(data["quest_combat_encounters"], {})
        self.assertEqual(data["quest_combat_encounter_counts"], {})
        self.assertEqual(data["quest_stage_actions"], {})
        self.assertEqual(data["quest_route_states"], {})
        self.assertEqual(data["pending_skill_exp_rewards"], {})
        self.assertEqual(data["claims"]["wicked_hood"], {"claimed": False})
        self.assertEqual(data["claims"]["tutorial_island_starter_kit"], {"claimed": False})
        self.assertEqual(data["wicked_hood"], {"fed_altars": []})
        self.assertEqual(data["runecrafting_pouches"], {})
        self.assertEqual(data["item_charges"], {})
        self.assertEqual(data["unlocked_abilities"], [])
        self.assertEqual(data["carried_inventory"], {})
        self.assertEqual(data["loot_value_threshold"], DEFAULT_LOOT_VALUE_THRESHOLD)
        self.assertEqual(data["shop_market_clock"], {"version": 1, "answered_cards": 0, "market_tick": 0})
        self.assertEqual(data["shop_stock_state"], {})
        self.assertEqual(data["shop_events"], [])
        self.assertEqual(data["shop_next_event_id"], 1)

    def test_default_player_data_can_seed_registered_items(self):
        data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        fletching_outputs = [spec["output_item"] for spec in FLETCHING_DATA.values()]
        fletching_materials = [
            material
            for spec in FLETCHING_DATA.values()
            for material in spec.get("requirements", {})
            if material not in WOODCUTTING_LOG_ITEMS
        ]
        utility_outputs = [spec["output_item"] for spec in UTILITY_ACTIVITY_DATA.values() if "output_item" in spec]
        utility_bundle_outputs = [
            item_name
            for spec in UTILITY_ACTIVITY_DATA.values()
            if isinstance(spec.get("outputs"), dict)
            for item_name in spec.get("outputs", {})
        ]
        hunter_materials = [
            material
            for spec in HUNTER_DATA.values()
            for material in spec.get("requirements", {})
        ]
        for item_name in (
            list(MINING_OUTPUT_ITEMS)
            + list(WOODCUTTING_LOG_ITEMS)
            + list(FIREMAKING_LOG_ITEMS)
            + list(BAR_DATA)
            + list(GEM_DATA)
            + [spec["output_item"] for spec in CRAFTING_DATA.values()]
            + fletching_outputs
            + fletching_materials
            + list(FIREMAKING_OUTPUT_ITEMS)
            + list(FISHING_OUTPUT_ITEMS)
            + list(COOKING_OUTPUT_ITEMS)
            + utility_outputs
            + utility_bundle_outputs
            + list(RUNECRAFTING_OUTPUT_ITEMS)
            + list(RUNECRAFTING_ACCESS_ITEMS)
            + list(RUNECRAFTING_EXTRA_ITEM_DATA)
            + list(HUNTER_OUTPUT_ITEMS)
            + hunter_materials
            + ["Beer", "Silk", "Newspaper", "Cowhide", "Leather", "Oak plank"]
        ):
            self.assertIn(item_name, data["inventory"])
            self.assertEqual(data["inventory"][item_name], 0)

    def test_migrate_from_old_schema_total_exp(self):
        old = {
            "total_exp": 123,
            "inventory": {"Copper ore": 2},
            # missing many keys on purpose
        }
        migrated = migrate_loaded_data(old, ORE_DATA)
        # total_exp -> mining_exp, and other exp fields defaulted
        self.assertEqual(migrated["mining_exp"], 123)
        self.assertIn("woodcutting_exp", migrated)
        self.assertIn("smithing_exp", migrated)
        self.assertIn("crafting_exp", migrated)
        self.assertIn("hunter_exp", migrated)
        # Ensure smithing/crafting defaults
        self.assertEqual(migrated["smithing_level"], 1)
        self.assertEqual(migrated["crafting_level"], 1)
        self.assertEqual(migrated["current_smith"], "smelt_bronze_bar")
        self.assertEqual(migrated["current_craft"], "form_pot_unfired")
        self.assertEqual(migrated["current_firemaking"], "logs")
        self.assertEqual(migrated["current_fishing"], "catch_crayfish")
        self.assertEqual(migrated["current_cooking"], "cook_shrimps")
        self.assertEqual(migrated["current_runecrafting"], "craft_air_runes")
        self.assertEqual(migrated["current_hunter"], "catch_crimson_swift")
        self.assertEqual(migrated["hunter_success_count"], 0)
        self.assertEqual(migrated["action_telemetry"], {"version": 1, "actions": {}})
        self.assertEqual(migrated["current_combat_target"], "chicken")
        self.assertEqual(migrated["combat_attack_style"], "accurate")
        self.assertEqual(migrated["current_combat_spell"], "wind_strike")
        self.assertEqual(migrated["combat_lifepoints"], 100)
        self.assertEqual(migrated["combat_supply_loadout"], {"food": {}, "potions": {}, "stat_potions": {}, "ammo": {}, "runes": {}, "cannonballs": 0})
        self.assertEqual(migrated["combat_special_attack_energy"], 100)
        self.assertEqual(migrated["combat_current_levels"], {})
        self.assertNotIn("combat_stat_drains", migrated)
        self.assertEqual(migrated["combat_status_effects"], {})
        self.assertEqual(migrated["combat_recovery_progress"], {})
        self.assertEqual(migrated["combat_encounter"], {})
        self.assertEqual(migrated["combat_kill_counts"], {})
        self.assertEqual(migrated["current_quest"], "rune_mysteries")
        self.assertEqual(migrated["quests"]["rune_mysteries"], {"started": False, "progress": 0, "completed": False})
        self.assertIn("swan_song", migrated["quests"])
        self.assertEqual(migrated["claims"]["wicked_hood"], {"claimed": False})
        self.assertEqual(migrated["claims"]["tutorial_island_starter_kit"], {"claimed": False})
        self.assertEqual(migrated["wicked_hood"], {"fed_altars": []})
        self.assertEqual(migrated["runecrafting_pouches"], {})
        self.assertEqual(migrated["item_charges"], {})
        self.assertEqual(migrated["current_utility"], "make_soft_clay")
        self.assertEqual(migrated["shop_market_clock"], {"version": 1, "answered_cards": 0, "market_tick": 0})
        self.assertEqual(migrated["shop_stock_state"], {})
        self.assertEqual(migrated["shop_events"], [])
        self.assertEqual(migrated["carried_inventory"], {})
        self.assertEqual(migrated["loot_value_threshold"], DEFAULT_LOOT_VALUE_THRESHOLD)
        # Inventory preserved and completed with ore keys
        self.assertEqual(migrated["inventory"]["Copper ore"], 2)
        for ore in MINING_OUTPUT_ITEMS:
            self.assertIn(ore, migrated["inventory"])  # completed
        # Version bumped
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)

    def test_future_schema_version_is_preserved(self):
        migrated = migrate_loaded_data(
            {
                "config_version": CURRENT_CONFIG_VERSION + 7,
                "inventory": {"Future item": 1},
                "farming_exp": float("inf"),
                "farming_level": float("nan"),
                "farm_clock_minutes": float("nan"),
                "farm_patches": {"future_patch": {"future": True}},
                "pending_skill_exp_rewards": {"farming_exp": float("nan"), "summoning_exp": 250},
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION + 7)
        self.assertEqual(migrated["inventory"]["Future item"], 1)
        self.assertEqual(migrated["farming_exp"], 0.0)
        self.assertEqual(migrated["farming_level"], 1)
        self.assertEqual(migrated["farm_clock_minutes"], 0)
        self.assertEqual(migrated["farm_patches"]["future_patch"], {"future": True})
        self.assertEqual(migrated["pending_skill_exp_rewards"], {"summoning_exp": 250.0})

    def test_load_cleans_only_above_base_stale_prayer_current_level(self):
        cleaned = migrate_loaded_data(
            {
                "config_version": CURRENT_CONFIG_VERSION,
                "prayer_level": 70,
                "combat_current_levels": {"prayer": 80, "attack": 65, "future_skill": 123},
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(cleaned["combat_current_levels"], {"attack": 65, "future_skill": 123})

        drained = migrate_loaded_data(
            {
                "config_version": CURRENT_CONFIG_VERSION,
                "prayer_level": 70,
                "combat_current_levels": {"prayer": 60, "attack": 65},
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(drained["combat_current_levels"], {"prayer": 60, "attack": 65})

    def test_migrate_preserves_existing_action_telemetry_rows(self):
        migrated = migrate_loaded_data(
            {
                "action_telemetry": {
                    "version": 1,
                    "actions": {
                        "fishing:catch_mackerel_cod_bass": {
                            "skill_id": "fishing",
                            "action_id": "catch_mackerel_cod_bass",
                            "attempts": 3,
                            "successes": 1,
                            "failures": 2,
                            "expected_successes": 1.2,
                            "current_dry_streak": 2,
                            "longest_dry_streak": 2,
                            "outputs": {"Raw mackerel": 1},
                            "failure_kinds": {"dry": 2},
                        }
                    },
                }
            },
            ORE_DATA,
        )

        telemetry = migrated["action_telemetry"]["actions"]["fishing:catch_mackerel_cod_bass"]
        self.assertEqual(telemetry["attempts"], 3)
        self.assertEqual(telemetry["successes"], 1)
        self.assertEqual(telemetry["outputs"], {"Raw mackerel": 1})

    def test_migrate_sanitizes_quest_stage_side_state(self):
        migrated = migrate_loaded_data(
            {
                "quest_combat_config": {"resolver_enabled": True},
                "quest_combat_encounters": {"dragon_slayer": {"elvarg": True, "unused": False}},
                "quest_combat_encounter_counts": {"toktz_ket_dill": {"lava_monster": "1", "bad": 0, 123: 1}},
                "quest_stage_actions": {"the_knights_sword": "Mine blurite ore"},
                "quest_route_states": {"heroes_quest": ["member_route", 123]},
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["quest_combat_config"], {"version": 1, "resolver_enabled": True})
        self.assertEqual(migrated["quest_combat_encounters"], {"dragon_slayer": ["elvarg"]})
        self.assertEqual(migrated["quest_combat_encounter_counts"], {"toktz_ket_dill": {"lava_monster": 1}})
        self.assertEqual(migrated["quest_stage_actions"], {"the_knights_sword": ["Mine blurite ore"]})
        self.assertEqual(migrated["quest_route_states"], {"heroes_quest": ["member_route"]})

    def test_migrate_can_seed_registered_items_without_losing_custom_entries(self):
        migrated = migrate_loaded_data(
            {"inventory": {"Mystery item": 7, "Oak": 3}},
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["inventory"]["Mystery item"], 7)
        self.assertNotIn("Oak", migrated["inventory"])
        self.assertEqual(migrated["inventory"]["Oak logs"], 3)
        self.assertIn("Bronze bar", migrated["inventory"])
        self.assertIn("Uncut sapphire", migrated["inventory"])
        self.assertIn("Arrow shafts", migrated["inventory"])
        self.assertIn("Feather", migrated["inventory"])
        self.assertIn("Fishing bait", migrated["inventory"])
        self.assertIn("Raw crayfish", migrated["inventory"])
        self.assertIn("Shrimps", migrated["inventory"])
        self.assertIn("Burnt fish", migrated["inventory"])
        self.assertIn("Air rune", migrated["inventory"])
        self.assertIn("Air talisman", migrated["inventory"])
        self.assertIn("Binding necklace", migrated["inventory"])
        self.assertIn("Wicked hood", migrated["inventory"])
        self.assertIn("Dramen staff", migrated["inventory"])
        self.assertIn("Red feather", migrated["inventory"])
        self.assertIn("Impling jar", migrated["inventory"])
        self.assertIn("Imp-in-a-box (2)", migrated["inventory"])
        self.assertIn("Coins", migrated["inventory"])
        self.assertIn("Soft clay", migrated["inventory"])
        self.assertIn("Ashes", migrated["inventory"])
        self.assertIn("Arctic pine logs", migrated["inventory"])
        self.assertIn("Wool", migrated["inventory"])
        self.assertIn("Flax", migrated["inventory"])
        self.assertIn("bronze_hatchet", migrated["toolbelt"]["woodcutting"])
        self.assertIn("bronze_pickaxe", migrated["toolbelt"]["mining"])
        self.assertEqual(migrated["equipment"], {})
        self.assertNotIn("owned_equipment", migrated)

    def test_migrate_pending_skill_exp_rewards_applies_trainable_keys_once(self):
        migrated = migrate_loaded_data(
            {
                "runecrafting_exp": 100,
                "attack_exp": 25,
                "pending_skill_exp_rewards": {
                    "runecrafting_exp": 5000,
                    "attack_exp": 1000,
                    "farming_exp": 250,
                },
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["runecrafting_exp"], 5100.0)
        self.assertEqual(migrated["attack_exp"], 1025.0)
        self.assertGreater(migrated["attack_level"], 1)
        self.assertEqual(migrated["farming_exp"], 250.0)
        self.assertGreater(migrated["farming_level"], 1)
        self.assertEqual(migrated["pending_skill_exp_rewards"], {})

    def test_migrate_equipment_state_and_removes_owned_equipment(self):
        migrated = migrate_loaded_data(
            {
                "equipment": {"body": "Bronze platebody", "bad_slot": "Mystery"},
                "owned_equipment": ["amulet_of_glory_4"],
                "inventory": {"Bronze platebody": 0},
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["equipment"], {"body": "Bronze platebody"})
        self.assertNotIn("owned_equipment", migrated)

    def test_migrate_combat_grave_state_is_sanitized(self):
        malformed = migrate_loaded_data(
            {"combat_grave": "not a grave"},
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(malformed["combat_grave"], {})

        clamped = migrate_loaded_data(
            {
                "combat_grave": {
                    "items": ["Iron sword", "", 123],
                    "reviews_remaining": 99,
                    "source": "",
                }
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(
            clamped["combat_grave"],
            {"items": ["Iron sword"], "reviews_remaining": 5, "source": "combat_death"},
        )

    def test_migrate_legacy_mining_target_names(self):
        migrated = migrate_loaded_data(
            {"current_ore": "Iron ore", "inventory": {"Iron ore": 2}},
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["current_ore"], "iron")
        self.assertEqual(migrated["inventory"]["Iron ore"], 2)

    def test_migrate_unknown_mining_target_to_default(self):
        migrated = migrate_loaded_data(
            {"current_ore": "Not a rock", "inventory": {}},
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["current_ore"], "rune_essence")

    def test_migrate_firemaking_target_to_stable_default(self):
        migrated = migrate_loaded_data(
            {"current_firemaking": "Not a log", "inventory": {"Mystery ash": 3}},
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["current_firemaking"], "logs")
        self.assertEqual(migrated["inventory"]["Mystery ash"], 3)
        self.assertIn("Cursed magic logs", migrated["inventory"])
        self.assertEqual(FIREMAKING_DATA["logs"]["output_item"], "Ashes")

    def test_migrate_fishing_target_to_stable_default_and_seeds_items(self):
        migrated = migrate_loaded_data(
            {"current_fishing": "Not a fish", "inventory": {"Mystery fish": 3}},
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["current_fishing"], "catch_crayfish")
        self.assertEqual(migrated["inventory"]["Mystery fish"], 3)
        self.assertIn("Raw crayfish", migrated["inventory"])
        self.assertIn("Fishing bait", migrated["inventory"])
        self.assertEqual(FISHING_DATA["catch_crayfish"]["fish"][0]["output_item"], "Raw crayfish")

    def test_migrate_cooking_target_to_stable_default_and_seeds_items(self):
        migrated = migrate_loaded_data(
            {"current_cooking": "Not food", "inventory": {"Mystery food": 3}},
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["current_cooking"], "cook_shrimps")
        self.assertEqual(migrated["inventory"]["Mystery food"], 3)
        self.assertIn("Raw shrimps", migrated["inventory"])
        self.assertIn("Shrimps", migrated["inventory"])
        self.assertIn("Burnt shrimp", migrated["inventory"])
        self.assertEqual(COOKING_DATA["cook_shrimps"]["output_item"], "Shrimps")

    def test_migrate_deferred_daemonheim_herblore_target_without_losing_items(self):
        migrated = migrate_loaded_data(
            {
                "current_herblore": "clean_sagawort",
                "inventory": {
                    "Grimy sagewort": 2,
                    "Clean sagewort": 1,
                    "Strong survivalist's potion": 3,
                },
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["current_herblore"], "clean_guam")
        self.assertEqual(migrated["inventory"]["Grimy sagewort"], 2)
        self.assertEqual(migrated["inventory"]["Clean sagewort"], 1)
        self.assertEqual(migrated["inventory"]["Strong survivalist's potion"], 3)

    def test_migrate_hunter_target_to_stable_default_and_seeds_items(self):
        migrated = migrate_loaded_data(
            {"current_hunter": "Not a creature", "inventory": {"Mystery catch": 3}},
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["current_hunter"], "catch_crimson_swift")
        self.assertEqual(migrated["inventory"]["Mystery catch"], 3)
        self.assertIn("Red feather", migrated["inventory"])
        self.assertIn("Butterfly jar", migrated["inventory"])
        self.assertIn("Impling jar", migrated["inventory"])
        self.assertIn("Imp-in-a-box (2)", migrated["inventory"])
        self.assertEqual(HUNTER_DATA["catch_crimson_swift"]["output_item"], "Red feather")

    def test_migrate_legacy_woodcutting_target_and_logs(self):
        migrated = migrate_loaded_data(
            {
                "current_tree": "Magic",
                "inventory": {"Tree": 2, "Magic": 4, "Redwood": 99, "Mystery item": 1},
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["current_tree"], "magic")
        self.assertEqual(migrated["inventory"]["Logs"], 2)
        self.assertEqual(migrated["inventory"]["Magic logs"], 4)
        self.assertNotIn("Tree", migrated["inventory"])
        self.assertNotIn("Magic", migrated["inventory"])
        self.assertNotIn("Redwood", migrated["inventory"])
        self.assertEqual(migrated["inventory"]["Mystery item"], 1)

    def test_migrate_legacy_smithing_target_and_bar_names(self):
        migrated = migrate_loaded_data(
            {
                "current_bar": "Runite bar",
                "inventory": {"Runite bar": 3, "Adamantite bar": 2, "Mystery bar": 1},
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["current_smith"], "smelt_rune_bar")
        self.assertEqual(migrated["inventory"]["Rune bar"], 3)
        self.assertEqual(migrated["inventory"]["Adamant bar"], 2)
        self.assertNotIn("Runite bar", migrated["inventory"])
        self.assertNotIn("Adamantite bar", migrated["inventory"])
        self.assertEqual(migrated["inventory"]["Mystery bar"], 1)

    def test_migrate_moves_legacy_soft_clay_target_to_utility(self):
        migrated = migrate_loaded_data(
            {"current_craft": "Soft clay", "inventory": {"Clay": 4}},
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["current_craft"], "")
        self.assertEqual(migrated["current_utility"], "make_soft_clay")
        self.assertEqual(migrated["inventory"]["Clay"], 4)

    def test_migrate_legacy_crafting_target_names(self):
        migrated = migrate_loaded_data(
            {"current_craft": "Bow string", "inventory": {"Flax": 3}},
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["current_craft"], "spin_flax_to_bow_string")
        self.assertEqual(migrated["inventory"]["Flax"], 3)

    def test_migrate_legacy_crafting_inventory_names(self):
        migrated = migrate_loaded_data(
            {
                "inventory": {
                    "Unfired pot": 120,
                    "Pot": 4,
                    "Unfired pie dish": 3,
                    "Pot (unfired)": 2,
                }
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["inventory"]["Pot (unfired)"], 122)
        self.assertEqual(migrated["inventory"]["Empty pot"], 4)
        self.assertEqual(migrated["inventory"]["Pie dish (unfired)"], 3)
        self.assertNotIn("Unfired pot", migrated["inventory"])
        self.assertNotIn("Pot", migrated["inventory"])
        self.assertNotIn("Unfired pie dish", migrated["inventory"])

    def test_migrate_idempotent(self):
        base = {"mining_exp": 10, "inventory": {}}
        first = migrate_loaded_data(base, ORE_DATA)
        second = migrate_loaded_data(first, ORE_DATA)
        self.assertEqual(first, second)

    def test_migrate_handles_bad_inventory(self):
        base = {"mining_exp": 10, "inventory": 5}  # not a dict
        migrated = migrate_loaded_data(base, ORE_DATA)
        self.assertIsInstance(migrated["inventory"], dict)
        for ore in MINING_OUTPUT_ITEMS:
            self.assertIn(ore, migrated["inventory"])  # seeded


if __name__ == "__main__":
    unittest.main()
