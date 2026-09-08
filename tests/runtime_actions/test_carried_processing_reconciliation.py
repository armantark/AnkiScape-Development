"""The carried pack reconciles consumption without exposing the capped bank."""

import copy
import unittest

import pkg_alias  # noqa: F401
from ankiscape.runtime.runtime_actions_carried_overlay import (
    _reconcile_processing_inventory,
)


class TestProcessingInventoryReconciliation(unittest.TestCase):
    def test_consumption_preserves_repeated_categories_and_input_ownership(self):
        arguments = (
            {"Ore": 100, "Tool": 1},
            {"Ore": 5, "Tool": 1},
            {"Ore": 3, "Tool": 1, "Bar": 2},
            {"Ore": 5, "Tool": 1, "Empty": 0, "Negative": -1},
            ("Ore", "Tool", "Ore", "Ore"),
            set(),
            set(),
        )
        before = copy.deepcopy(arguments)
        bank, carried = _reconcile_processing_inventory(*arguments)
        self.assertEqual(bank, {"Ore": 98, "Tool": 1, "Bar": 2})
        self.assertEqual(carried, {"Tool": 1})
        self.assertEqual(arguments, before)

    def test_hidden_potions_and_alternatives_have_distinct_absence_rules(self):
        bank, carried = _reconcile_processing_inventory(
            {"Potion": 9, "Feather": 7},
            {},
            {"New potion": 2, "New feather": 3, "Output": 4},
            {},
            (),
            {"Potion", "New potion"},
            {"Feather", "New feather"},
        )
        self.assertEqual(
            bank, {"Potion": 9, "New potion": 2, "Feather": 7, "Output": 4}
        )
        self.assertEqual(carried, {})

    def test_replaced_inventory_consumes_but_shared_inventory_keeps_old_semantics(self):
        cases = (({"Ore": 5}, {"Ore": 3}, 98, 3),)
        shared = {"Ore": 3}
        cases += ((shared, shared, 100, 5),)
        for scoped, after, expected_bank, expected_pack in cases:
            with self.subTest(shared=scoped is after):
                bank, carried = _reconcile_processing_inventory(
                    {"Ore": 100}, scoped, after, {"Ore": 5}, ("Ore",), set(), set()
                )
                self.assertEqual(bank, {"Ore": expected_bank})
                self.assertEqual(carried, {"Ore": expected_pack})

    def test_overproduction_is_not_consumption_and_bank_zero_is_retained(self):
        bank, carried = _reconcile_processing_inventory(
            {"Ore": 0, "Input": 20},
            {"Ore": 2, "Input": 3},
            {"Ore": 0, "Input": 7},
            {"Ore": 2, "Input": 3},
            ("Ore", "Input"),
            set(),
            set(),
        )
        self.assertEqual(bank, {"Ore": 0, "Input": 20})
        self.assertEqual(carried, {"Input": 3})
