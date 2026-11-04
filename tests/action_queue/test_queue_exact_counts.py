"""The queue makes exactly the count the player picks, through the real review handler at 10x.

The owner's case (Pass 18): he queued 3 Goblin mail, 3 Redberries and 28 Onion
and got more of each, because the queue counted only after the whole card.
"""

from __future__ import annotations

from unittest.mock import patch

from tests.action_queue.test_queue_reviews import _MINE_IRON, _SMITH_PLATEBODY, QueueProfile

_COWS = {"kind": "combat", "target": "cow", "combat_action": "attack"}
_WHITTLE_SHAFTS = {"kind": "skill", "skill": "Fletching", "target": "arrow_shafts"}
_FIGHTER = {"attack_level": 99, "strength_level": 99, "defense_level": 99, "constitution_level": 99, "combat_lifepoints": 990}


class QueueExactCountTest(QueueProfile):
    def test_the_owners_three_entries_make_exactly_their_counts_in_one_card(self):
        addon = self._queue_addon(
            "ankiscape_queue_exact_utilities",
            ({"kind": "utility", "utility_id": "gather_goblin_mail"}, 3),
            ({"kind": "utility", "utility_id": "pick_redberries"}, 3),
            ({"kind": "utility", "utility_id": "pick_onions"}, 28),
        )

        self._answer(addon)

        inventory = addon._state.player_data["inventory"]
        self.assertEqual([inventory.get(item, 0) for item in ("Goblin mail", "Redberries", "Onion")], [3, 3, 28])
        # One card runs all three entries; a queue that counted once per card needed a card for each.
        self.assertEqual(self._rows(addon), [])
        self.assertEqual(
            self._log(addon),
            [
                "+3 Goblin mail",
                "Queue: Search Goblin Village crates done",
                "+3 Redberries",
                "Queue: Pick redberries done",
                "+28 Onion",
                "Switched to Bankstanding · Queue finished after Pick onions.",
            ],
        )
        self.assertEqual(self.bankstanding_dialogs, ["Queue finished after Pick onions."])

    def test_one_platebody_makes_one_and_the_rest_of_the_card_runs_the_next_entry(self):
        addon = self._queue_addon("ankiscape_queue_exact_platebody", (_SMITH_PLATEBODY, 1), (_MINE_IRON, 5))
        addon._state.player_data["inventory"]["Iron bar"] = 10

        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)

        inventory = addon._state.player_data["inventory"]
        self.assertEqual((inventory["Iron platebody"], inventory["Iron bar"], inventory["Iron ore"]), (1, 5, 5))
        self.assertEqual(
            self._log(addon),
            [
                "+125 XP · Smithing · +1 Iron platebody · −5 Iron bar",
                "Queue: Smithing: Iron platebody done",
                "+175 XP · Mining · +5 Iron ore",
                "Switched to Bankstanding · Queue finished after Mining: Iron.",
            ],
        )

    def test_a_count_inside_one_whole_lot_keeps_the_lot_and_the_rest_of_the_card_runs_the_next_entry(self):
        # One log always whittles 15 shafts; taking 5 back after the log is spent would lose what the player paid for.
        addon = self._queue_addon("ankiscape_queue_exact_lot", (_WHITTLE_SHAFTS, 10), (_MINE_IRON, 5))
        addon._state.player_data["inventory"]["Logs"] = 3

        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)

        inventory = addon._state.player_data["inventory"]
        self.assertEqual((inventory["Arrow shafts"], inventory["Logs"], inventory["Iron ore"]), (15, 2, 5))
        self.assertEqual(self._log(addon)[1], "Queue: Fletching: Arrow shafts (Logs) done")
        self.assertEqual(self._rows(addon), [])

    def test_a_kill_entry_stops_inside_its_burst_and_the_smaller_of_its_and_a_slayer_tasks_counts_wins(self):
        with self.subTest("the entry's count ends the burst, and the rest of the card runs the next entry"):
            addon = self._queue_addon("ankiscape_queue_exact_kills", (_COWS, 3), (_MINE_IRON, 5), **_FIGHTER)
            with patch.object(addon.random, "random", lambda: 0.5):
                self._answer(addon)
            self.assertEqual(addon._state.player_data["combat_kill_counts"], {"cow": 3})
            self.assertEqual(addon._state.player_data["inventory"]["Iron ore"], 5)
            self.assertEqual(self._rows(addon), [])

        with self.subTest("a Slayer task with fewer kills left ends the card first"):
            task = {"master_id": "turael_spria", "family_id": "cows", "initial_count": 15, "remaining": 2}
            addon = self._queue_addon(
                "ankiscape_queue_exact_slayer", (_COWS, 3), (_MINE_IRON, 5), slayer_assignment=task, **_FIGHTER
            )
            with patch.object(addon.random, "random", lambda: 0.5):
                self._answer(addon)
            self.assertEqual(addon._state.player_data["combat_kill_counts"], {"cow": 2})
            self.assertEqual(self._rows(addon), [("Combat: Cow", "current", 2), ("Mining: Iron", "waiting", 0)])

            with patch.object(addon.random, "random", lambda: 0.5):
                self._answer(addon)
            self.assertEqual(addon._state.player_data["combat_kill_counts"], {"cow": 3})
            self.assertEqual(addon._state.player_data["inventory"]["Iron ore"], 5)
            self.assertEqual(self._rows(addon), [])
