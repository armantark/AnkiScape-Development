"""The queue's state machine: counts in each action's unit, passes, the cap, no repeat.

The owner asked for a short planned chain, never a loop (2026-10-26): at most
five entries, each worked through once, top to bottom.
"""

from __future__ import annotations

import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.action_products import action_product_items_pure
from ankiscape.core.action_queue import (
    ACTION_QUEUE_KEY,
    action_queue_pure,
    action_queue_view_pure,
    add_queue_entry_pure,
    advance_queue_pure,
    current_queue_entry_pure,
    pass_queue_entry_pure,
    queue_entry_progress_pure,
)

_MINE_IRON = {"kind": "skill", "skill": "Mining", "target": "iron"}
_SMELT_IRON = {"kind": "skill", "skill": "Smithing", "target": "smelt_iron_bar"}
_CHICKENS = {"kind": "combat", "target": "chicken", "combat_action": "attack"}


def _queue(*entries):
    queue = action_queue_pure({})
    for action, count in entries:
        queue, ok = add_queue_entry_pure(queue, action, count)
        assert ok
    return queue


class ActionQueueStateTest(unittest.TestCase):
    def test_an_entry_that_reaches_its_count_hands_over_to_the_next(self):
        queue = _queue((_MINE_IRON, 10), (_SMELT_IRON, 5))

        queue, full = advance_queue_pure(queue, 6)
        self.assertFalse(full)
        self.assertEqual((queue["index"], queue["done"]), (0, 6))

        queue, full = advance_queue_pure(queue, 7)
        self.assertTrue(full)
        self.assertEqual(current_queue_entry_pure(queue)["action"], _SMELT_IRON)
        self.assertEqual(queue["done"], 0)

    def test_an_entry_that_runs_short_is_passed_with_its_reason(self):
        queue = pass_queue_entry_pure(_queue((_SMELT_IRON, 20), (_MINE_IRON, 5)), "You need 1 Iron ore")

        rows = action_queue_view_pure({ACTION_QUEUE_KEY: queue})["entries"]
        self.assertEqual(
            [(row["name"], row["state"], row["stopped"]) for row in rows],
            [("Smithing: Iron bar", "stopped", "You need 1 Iron ore"), ("Mining: Iron", "current", "")],
        )

    def test_a_sixth_entry_is_refused(self):
        queue = _queue(*[(_MINE_IRON, 1)] * 5)

        refused, ok = add_queue_entry_pure(queue, _SMELT_IRON, 1)

        self.assertFalse(ok)
        self.assertEqual(refused, queue)
        self.assertFalse(action_queue_view_pure({ACTION_QUEUE_KEY: queue})["can_add"])

    def test_a_finished_queue_never_repeats_and_gives_way_to_a_new_plan(self):
        queue, _full = advance_queue_pure(_queue((_MINE_IRON, 3)), 3)

        self.assertIsNone(current_queue_entry_pure(queue))
        self.assertEqual(advance_queue_pure(queue, 50), (queue, False))
        view = action_queue_view_pure({ACTION_QUEUE_KEY: queue})
        self.assertTrue(view["finished"])
        self.assertEqual([row["state"] for row in view["entries"]], ["done"])

        queue, ok = add_queue_entry_pure(queue, _SMELT_IRON, 4)
        self.assertTrue(ok)
        self.assertEqual([entry["action"] for entry in queue["entries"]], [_SMELT_IRON])

    def test_a_quest_takes_no_count_and_a_count_below_one_is_refused(self):
        queue, ok = add_queue_entry_pure(
            action_queue_pure({}), {"kind": "quest", "quest_id": "cooks_assistant"}, 99
        )
        self.assertTrue(ok)
        self.assertIsNone(queue["entries"][0]["count"])
        self.assertEqual(advance_queue_pure(queue, 1), (queue, False))

        for count in (0, -2, "5", True):
            with self.subTest(count=count):
                self.assertFalse(add_queue_entry_pure(queue, _MINE_IRON, count)[1])

    def test_each_entry_counts_in_its_own_unit(self):
        before = {"inventory": {"Iron ore": 4, "Vial": 0}, "combat_kill_counts": {"chicken": 2, "cow": 9}}
        after = {"inventory": {"Iron ore": 9, "Vial": 1}, "combat_kill_counts": {"chicken": 5, "cow": 12}}
        agility_lap = {"kind": "skill", "skill": "Agility", "target": "gnome_normal"}

        self.assertEqual(queue_entry_progress_pure(_MINE_IRON, before, after), 5)
        self.assertEqual(queue_entry_progress_pure(_CHICKENS, before, after), 3)
        self.assertEqual(queue_entry_progress_pure(agility_lap, before, after), 1)
        self.assertEqual(queue_entry_progress_pure(_SMELT_IRON, before, after), 0)

    def test_the_product_is_what_the_player_picked_the_action_for(self):
        cases = {
            "a fishing spot's every catch": (
                {"kind": "skill", "skill": "Fishing", "target": "catch_shrimp_anchovies"},
                ("Raw anchovies", "Raw shrimps"),
            ),
            "both essences of the essence mine": (
                {"kind": "skill", "skill": "Mining", "target": "rune_essence"},
                ("Rune essence", "Pure essence"),
            ),
            "cooked food, never the burnt": (
                {"kind": "skill", "skill": "Cooking", "target": "cook_shrimps"},
                ("Shrimps",),
            ),
            "a minigame's reward shop is no product": ({"kind": "utility", "utility_id": "castle_wars"}, ()),
            "a fight's loot is no product": (_CHICKENS, ()),
        }
        for label, (action, products) in cases.items():
            with self.subTest(label):
                self.assertEqual(action_product_items_pure(action), products)


if __name__ == "__main__":
    unittest.main()
