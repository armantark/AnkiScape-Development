"""The carried pack reconciles consumption without exposing the capped bank."""

import copy
import unittest

import pkg_alias  # noqa: F401
from ankiscape.runtime import runtime_actions_carried_overlay as overlay
from ankiscape.runtime.runtime_actions_carried_overlay import (
    _reconcile_processing_inventory,
    run_answer_with_carried_overlay,
)
from ankiscape.runtime.runtime_actions_production import handle_firemaking_answer
from tests.test_runtime_actions import _context
from tools.carried import compare_processing_reconciliation as scenarios


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

    def test_a_raising_handler_leaves_the_real_bank_not_the_capped_pack(self):
        player_data = {
            "inventory": {"Logs": 100},
            "firemaking_level": 1,
            "firemaking_exp": 0,
            "current_firemaking": "logs",
            "completed_achievements": [],
        }
        ctx = _context(player_data, random_values=[0.0] * 8)

        def failing_award(_exp_key, _base_exp):
            raise RuntimeError("xp callback failed")

        ctx.award_skill_exp = failing_award
        with self.assertRaisesRegex(RuntimeError, "xp callback failed"):
            run_answer_with_carried_overlay(ctx, "firemaking", handle_firemaking_answer)
        self.assertEqual(player_data["inventory"], {"Logs": 99, "Ashes": 1})


class TestProcessingHandlerReconciliation(unittest.TestCase):
    def test_only_false_rejects_the_action_and_restores_admission(self):
        cases = dict(scenarios.fixture_cases())
        for label, cadence, carried in (
            ("partial", 1, {"Tool": 1}),
            ("rejected", 0, {"Input": 5, "Tool": 1, "Potion": 2, "Zero": 0}),
            ("none_return", 1, {"Tool": 1}),
            ("zero_return", 1, {"Tool": 1}),
        ):
            with self.subTest(result=label):
                config = cases[f"{label}-replace-True"]
                report = scenarios.run_fixture(overlay, config)
                self.assertIs(report["result"], config["result"])
                self.assertEqual(report["player"]["cadence_profiles"], {"probe": cadence})
                self.assertEqual(report["player"]["carried_inventory"]["probe"], carried)
                bank = {"Input": 98, "Tool": 1, "Potion": 8, "Hidden potion": 9,
                        "Alt": 8, "Output": 2, "Absent potion": 3}
                self.assertEqual(report["player"]["inventory"], bank)
                callbacks = [event[2]["inventory"] for event in report["events"]
                             if event[0] in ("check_achievements", "refresh_skill_availability",
                                             "save_player_data")]
                self.assertEqual(callbacks, [bank, bank, bank])

    def test_rejected_winter_storage_restores_stock_and_follower_charge(self):
        config = dict(scenarios.fixture_cases())["rejection-winter-True-child-cadence-False"]
        report = scenarios.run_fixture(overlay, config)
        player = report["player"]
        self.assertIs(report["result"], False)
        self.assertEqual(player["inventory"], scenarios.fixture_player()["inventory"]
                         | {"Winter storage scroll": 1})
        self.assertEqual(player["carried_inventory"]["probe"],
                         {"Input": 5, "Tool": 1, "Potion": 2, "Zero": 0,
                          "Winter storage scroll": 1})
        self.assertEqual(player["carried_churn"], {"probe": 28})
        self.assertEqual(player["cadence_profiles"], {"probe": 0})
        self.assertEqual(player["summoning_state"]["special_move_points_current"], 20)
        self.assertNotIn("summoning_exp", player)
        saves = [event[2] for event in report["events"] if event[0] == "save_player_data"]
        self.assertEqual(saves, [player])

    def test_rejected_child_attempt_keeps_its_own_cadence_and_reconciles_stock(self):
        config = dict(scenarios.fixture_cases())["rejection-winter-False-child-cadence-True"]
        report = scenarios.run_fixture(overlay, config)
        self.assertIs(report["result"], False)
        self.assertEqual(report["player"]["cadence_profiles"], {"probe": 2})
        self.assertEqual(report["player"]["inventory"]["Input"], 98)
        self.assertEqual(report["player"]["carried_inventory"]["probe"],
                         {"Input": 5, "Tool": 1, "Potion": 2, "Zero": 0})

    def test_advanced_refills_keep_bank_and_saves_reconciled(self):
        for case in scenarios.advanced_cases():
            with self.subTest(recipe=case[0]):
                report = scenarios.advanced_trip(overlay, case)
                self.assertEqual([step["result"] for step in report["steps"]], [True, True])
                self.assertEqual(report["player"]["agility_last_travel"]["charged_reviews"], 0)
