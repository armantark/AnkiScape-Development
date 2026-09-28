"""Combination rune reviews spend the target's carried materials."""

import copy
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import RUNECRAFTING_DATA
from ankiscape.runtime.runtime_actions import (
    handle_runecrafting_answer,
    run_answer_with_carried_overlay,
)
from tests.test_runtime_actions import _context


def _player(target="combo_mist_at_air", *, layout=None, imbued=False):
    recipe = RUNECRAFTING_DATA[target]
    player = {
        "inventory": {
            "Pure essence": 100,
            recipe["component_rune"]: 100,
            recipe["consumed_talisman"]: 10,
        },
        "equipment": {
            "head": recipe["altar_id"].capitalize() + " tiara",
            "neck": "Binding necklace",
        },
        "quests": {"rune_mysteries": {"completed": True}},
        "current_runecrafting": target,
        "runecrafting_level": 99,
        "runecrafting_exp": 0,
        "magic_imbue_active": imbued,
        "completed_achievements": [],
    }
    if layout is not None:
        player["carried_advanced_targets"] = {target: True}
        player["carried_layout"] = {target: layout}
    return player


def _review(player):
    return run_answer_with_carried_overlay(
        _context(player), "runecrafting", handle_runecrafting_answer,
    )


class TestCombinationRunecraftingPack(unittest.TestCase):
    def test_empty_custom_pack_cannot_spend_bank_materials(self):
        for target, recipe in RUNECRAFTING_DATA.items():
            if recipe.get("kind") != "combination":
                continue
            with self.subTest(target=target):
                player = _player(target, layout={})
                bank = copy.deepcopy(player["inventory"])

                _review(player)

                self.assertEqual(player["inventory"], bank)
                self.assertEqual(player["runecrafting_exp"], 0)
                self.assertEqual(player.get("item_charges", {}), {})

    def test_incomplete_custom_pack_never_borrows_missing_materials(self):
        complete = {"Pure essence": 3, "Water rune": 5, "Water talisman": 2}
        for missing in complete:
            for bank_stock in (0, 100):
                with self.subTest(missing=missing, bank_stock=bank_stock):
                    layout = {item: count for item, count in complete.items() if item != missing}
                    player = _player(layout=layout)
                    player["inventory"][missing] = bank_stock
                    bank = copy.deepcopy(player["inventory"])

                    _review(player)

                    self.assertEqual(player["inventory"], bank)
                    self.assertEqual(player["runecrafting_exp"], 0)

    def test_custom_pack_limits_every_combination_to_carried_materials(self):
        for target, recipe in RUNECRAFTING_DATA.items():
            if recipe.get("kind") != "combination":
                continue
            with self.subTest(target=target):
                rune, talisman = recipe["component_rune"], recipe["consumed_talisman"]
                player = _player(target, layout={"Pure essence": 3, rune: 5, talisman: 2})

                self.assertTrue(_review(player))

                self.assertEqual(player["inventory"], {
                    "Pure essence": 97, rune: 97, talisman: 9, recipe["output_item"]: 3,
                })
                self.assertEqual(player["carried_inventory"][target], {rune: 2, talisman: 1})
                self.assertAlmostEqual(player["runecrafting_exp"], 3 * recipe["base_exp"])
                self.assertEqual(player["item_charges"]["Binding necklace"], 14)

    def test_casual_pack_reserves_one_talisman_for_a_full_batch(self):
        player = _player()

        self.assertTrue(_review(player))

        self.assertEqual(player["inventory"], {
            "Pure essence": 74, "Water rune": 74, "Water talisman": 9, "Mist rune": 26,
        })
        self.assertNotIn("combo_mist_at_air", player["carried_inventory"])

    def test_magic_imbue_waives_talisman_until_the_next_custom_batch(self):
        player = _player(layout={"Pure essence": 27, "Water rune": 30}, imbued=True)

        self.assertTrue(_review(player))

        self.assertEqual(player["inventory"], {
            "Pure essence": 74, "Water rune": 74, "Water talisman": 10, "Mist rune": 26,
        })
        self.assertFalse(player["magic_imbue_active"])
        self.assertEqual(player["carried_inventory"]["combo_mist_at_air"], {
            "Pure essence": 1, "Water rune": 4,
        })
        bank = copy.deepcopy(player["inventory"])
        self.assertTrue(_review(player))
        self.assertEqual(player["inventory"], bank)
        self.assertEqual(player["item_charges"]["Binding necklace"], 14)
        self.assertTrue(player["skilling_bank_run"])

    def test_casual_magic_imbue_works_without_any_talisman_then_stops(self):
        player = _player(imbued=True)
        player["inventory"]["Water talisman"] = 0

        self.assertTrue(_review(player))

        self.assertEqual(player["inventory"], {
            "Pure essence": 74, "Water rune": 74, "Water talisman": 0, "Mist rune": 26,
        })
        self.assertEqual(player["carried_inventory"]["combo_mist_at_air"], {
            "Pure essence": 1, "Water rune": 1,
        })
        bank = copy.deepcopy(player["inventory"])
        self.assertFalse(_review(player))
        self.assertEqual(player["inventory"], bank)
        self.assertEqual(player["item_charges"]["Binding necklace"], 14)

    def test_spent_casual_pack_banks_and_restocks_before_crafting_again(self):
        player = _player()
        self.assertTrue(_review(player))
        bank = copy.deepcopy(player["inventory"])

        self.assertTrue(_review(player))
        self.assertEqual(player["inventory"], bank)
        remaining = player["skilling_bank_run"]["reviews_remaining"]
        for _ in range(remaining):
            self.assertTrue(_review(player))
            self.assertEqual(player["inventory"], bank)

        self.assertEqual(player["skilling_bank_run"], {})
        self.assertEqual(player["carried_inventory"]["combo_mist_at_air"], {
            "Pure essence": 26, "Water rune": 26, "Water talisman": 1,
        })
        self.assertTrue(_review(player))
        self.assertEqual(player["inventory"], {
            "Pure essence": 48, "Water rune": 48, "Water talisman": 8, "Mist rune": 52,
        })
