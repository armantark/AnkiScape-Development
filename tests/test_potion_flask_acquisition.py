import os
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import (
    CRAFTED_ITEM_IMAGES,
    CRAFTING_DATA,
    DEFAULT_MINING_TARGET,
    DEFAULT_UTILITY_ACTIVITY,
    GEM_IMAGES,
    ITEM_DEFINITIONS,
    MINING_PICKAXE_DATA,
    ORE_DATA,
    ORE_IMAGES,
    QUEST_UNLOCK_RULES,
    UTILITY_ACTIVITY_DATA,
    UTILITY_ITEM_IMAGES,
)
from ankiscape.core.item_registry import item_definitions_by_storage_key
from ankiscape.logic_pure.logic_pure import (
    apply_crafting_pure,
    apply_utility_activity_pure,
    mining_target_locked_reasons_pure,
    red_sandstone_daily_remaining_pure,
)
from ankiscape.data.mining_data import (
    MINING_REVIEW_DAY_CARDS,
    RED_SANDSTONE_DAILY_CAP,
)
from ankiscape.runtime.runtime_actions import (
    handle_crafting_answer,
    handle_mining_answer,
    handle_utility_answer,
)
from ankiscape.core.storage_pure import CURRENT_CONFIG_VERSION, migrate_loaded_data
from ankiscape.core.target_metadata import (
    crafting_target_rows,
    mining_target_rows,
    utility_activity_rows,
)
from tests.test_runtime_actions import _context
from tests.reachability.live_report import live_reachability_report


class TestPotionFlaskAcquisition(unittest.TestCase):
    def test_period_chain_data_and_item_identity_are_exact(self):
        sandstone = ORE_DATA["red_sandstone"]
        self.assertEqual(
            (
                sandstone["level"],
                sandstone["exp"],
                sandstone["source_item_id"],
                sandstone["low_chance"],
                sandstone["high_chance"],
            ),
            (81, 70.0, 23194, 30, 145),
        )
        self.assertFalse(sandstone["output_tradeable"])
        self.assertFalse(sandstone["output_stackable"])
        self.assertFalse(sandstone["allows_random_gems"])

        robust = UTILITY_ACTIVITY_DATA["make_robust_glass"]
        self.assertEqual(robust["requirements"], {"Red sandstone": 1})
        self.assertEqual(robust["output_item"], "Robust glass")
        self.assertEqual(robust["batch_size"], 28)

        flask = CRAFTING_DATA["glass_potion_flask"]
        self.assertEqual(flask["level"], 89)
        self.assertEqual(flask["exp"], 100.0)
        self.assertEqual(flask["requirements"], {"Robust glass": 1})
        self.assertEqual(flask["required_items"], {"Glassblowing pipe": 1})
        self.assertEqual(flask["source_item_id"], 23191)

        items = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        for name, item_id, tradeable in (
            ("Red sandstone", 23194, False),
            ("Robust glass", 23193, False),
            ("Potion flask", 23191, True),
        ):
            with self.subTest(name=name):
                self.assertEqual(items[name].source_item_id, item_id)
                self.assertFalse(items[name].stackable)
                self.assertEqual(items[name].tradeable, tradeable)
        self.assertFalse(items["Glassblowing pipe"].stackable)

    def test_quest_gate_and_review_day_cap_are_enforced_without_wall_clock(self):
        player = {
            "mining_level": 99,
            "inventory": {},
            "toolbelt": {"mining": ["bronze_pickaxe"]},
            "quests": {"as_a_first_resort": {"completed": False}},
            "shop_market_clock": {"answered_cards": 239},
            "red_sandstone_daily": {"review_day": 0, "mined": 50},
        }
        reasons = mining_target_locked_reasons_pure(
            player,
            "red_sandstone",
            ORE_DATA,
            {"bronze_pickaxe": {"level": 1, "item_id": 1265}},
            QUEST_UNLOCK_RULES,
        )
        self.assertIn("As a First Resort", reasons)
        self.assertIn("50 Red sandstone already mined this review day", reasons)

        player["quests"]["as_a_first_resort"]["completed"] = True
        self.assertEqual(red_sandstone_daily_remaining_pure(player), 0)
        player["shop_market_clock"]["answered_cards"] = MINING_REVIEW_DAY_CARDS
        self.assertEqual(
            red_sandstone_daily_remaining_pure(player),
            RED_SANDSTONE_DAILY_CAP,
        )

    def test_runtime_mining_records_only_successful_blocks_and_stops_at_cap(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player = {
            "mining_level": 99,
            "mining_exp": 0.0,
            "current_ore": "red_sandstone",
            "inventory": {},
            "toolbelt": {"mining": ["bronze_pickaxe"]},
            "quests": {"as_a_first_resort": {"completed": True}},
            "shop_market_clock": {"answered_cards": 239},
            "red_sandstone_daily": {"review_day": 0, "mined": 49},
            "completed_achievements": [],
        }

        self.assertTrue(
            handle_mining_answer(
                _context(player, calls, random_values=(0.0, 0.0, 1.0, 0.0))
            )
        )
        self.assertEqual(player["inventory"]["Red sandstone"], 1)
        self.assertEqual(player["red_sandstone_daily"], {"review_day": 0, "mined": 50})
        self.assertEqual(player["mining_exp"], 70.0)

        self.assertFalse(handle_mining_answer(_context(player, calls)))
        self.assertTrue(calls["deactivated"])
        self.assertIn("50 Red sandstone", calls["errors"][-1][1])

    def test_machine_and_glassblowing_actions_preserve_tools_and_award_exact_xp(self):
        converted, exp, ok, processed = apply_utility_activity_pure(
            "make_robust_glass",
            {"Red sandstone": 10},
            UTILITY_ACTIVITY_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual((processed, exp), (10, 0))
        self.assertEqual(converted, {"Red sandstone": 0, "Robust glass": 10})

        crafted, exp, ok = apply_crafting_pure(
            "glass_potion_flask",
            {"Robust glass": 1, "Glassblowing pipe": 1},
            CRAFTING_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual(exp, 100.0)
        self.assertEqual(
            crafted,
            {"Robust glass": 0, "Glassblowing pipe": 1, "Potion flask": 1},
        )

    def test_runtime_chain_respects_quest_gate_and_standard_handlers(self):
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player = {
            "current_utility": "make_robust_glass",
            "inventory": {"Red sandstone": 2},
            "quests": {"as_a_first_resort": {"completed": False}},
            "completed_achievements": [],
        }
        self.assertFalse(handle_utility_answer(_context(player, calls)))
        self.assertIn("As a First Resort", calls["errors"][-1][1])

        player["quests"]["as_a_first_resort"]["completed"] = True
        calls["errors"].clear()
        self.assertTrue(handle_utility_answer(_context(player, calls)))
        self.assertEqual(player["inventory"]["Robust glass"], 2)

        player.update(
            {
                "current_craft": "glass_potion_flask",
                "crafting_level": 89,
                "crafting_exp": 0.0,
            }
        )
        player["inventory"]["Glassblowing pipe"] = 1
        self.assertTrue(handle_crafting_answer(_context(player, calls)))
        self.assertEqual(player["inventory"]["Robust glass"], 1)
        self.assertEqual(player["inventory"]["Potion flask"], 1)
        self.assertEqual(player["inventory"]["Glassblowing pipe"], 1)
        self.assertEqual(player["crafting_exp"], 100.0)

    def test_assets_exist_but_reachability_preserves_the_quest_gate(self):
        self.assertTrue(os.path.exists(ORE_IMAGES["Red sandstone"]))
        self.assertTrue(os.path.exists(CRAFTED_ITEM_IMAGES["Robust glass"]))
        self.assertTrue(os.path.exists(CRAFTED_ITEM_IMAGES["Potion flask"]))

        report = live_reachability_report()
        gated_items = {"Red sandstone", "Robust glass", "Potion flask"}
        self.assertTrue(gated_items.isdisjoint(report["routes"]))
        self.assertTrue(
            gated_items <= {row["item"] for row in report["orphan_inputs"]}
        )
        unresolved = {row["id"]: row for row in report["unresolved_actions"]}
        self.assertEqual(unresolved["Mining:red_sandstone"]["missing"], [])
        self.assertEqual(
            unresolved["Utility:make_robust_glass"]["missing"],
            ["Red sandstone"],
        )
        self.assertEqual(
            unresolved["Crafting:glass_potion_flask"]["missing"],
            ["Robust glass"],
        )

    def test_existing_skill_lists_expose_icons_gates_and_daily_allowance(self):
        player = {
            "mining_level": 99,
            "crafting_level": 89,
            "inventory": {"Red sandstone": 1, "Robust glass": 1, "Glassblowing pipe": 1},
            "toolbelt": {"mining": ["bronze_pickaxe"]},
            "quests": {"as_a_first_resort": {"completed": True}},
            "shop_market_clock": {"answered_cards": 1},
            "red_sandstone_daily": {"review_day": 0, "mined": 17},
            "current_ore": "red_sandstone",
            "current_utility": "make_robust_glass",
            "current_craft": "glass_potion_flask",
        }
        mining = next(
            row
            for row in mining_target_rows(
                player,
                ORE_DATA,
                ORE_IMAGES,
                GEM_IMAGES,
                MINING_PICKAXE_DATA,
                DEFAULT_MINING_TARGET,
                quest_unlock_rules=QUEST_UNLOCK_RULES,
            )
            if row.target_id == "red_sandstone"
        )
        self.assertTrue(mining.enabled)
        self.assertTrue(mining.icon_path)
        self.assertIn("33 of 50 remaining", mining.tooltip)

        utility = next(
            row
            for row in utility_activity_rows(
                player,
                UTILITY_ACTIVITY_DATA,
                UTILITY_ITEM_IMAGES,
                {},
                DEFAULT_UTILITY_ACTIVITY,
                QUEST_UNLOCK_RULES,
            )
            if row.target_id == "make_robust_glass"
        )
        self.assertTrue(utility.enabled)
        self.assertTrue(utility.icon_path)
        self.assertIn("Processes up to 28", utility.tooltip)

        crafting = next(
            row
            for row in crafting_target_rows(
                player,
                CRAFTING_DATA,
                CRAFTED_ITEM_IMAGES,
                QUEST_UNLOCK_RULES,
            )
            if row.target_id == "glass_potion_flask"
        )
        self.assertTrue(crafting.enabled)
        self.assertTrue(crafting.icon_path)
        self.assertIn("Base XP: 100", crafting.tooltip)

    def test_save_migration_repairs_daily_state_against_current_review_day(self):
        loaded = {
            "config_version": 50,
            "shop_market_clock": {
                "version": 1,
                "answered_cards": 480,
                "market_tick": 480,
            },
            "red_sandstone_daily": {"review_day": 1, "mined": 50},
        }
        migrated = migrate_loaded_data(loaded, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(
            migrated["red_sandstone_daily"],
            {"review_day": 2, "mined": 0},
        )


if __name__ == "__main__":
    unittest.main()
