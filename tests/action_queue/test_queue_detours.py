"""Hand starts set the queue aside; only an explicit pause keeps it stopped."""

from __future__ import annotations

import random
from unittest.mock import patch

from tests.action_queue.test_queue_reviews import _MINE_IRON, _SMELT_IRON, QueueProfile

_QUEST = {"kind": "quest", "quest_id": "jungle_potion"}
_PICKUP = {"kind": "utility", "utility_id": "pick_onions"}
_HERBS = ("Clean snake weed", "Clean ardrigal", "Clean sito foil", "Clean volencia moss", "Clean rogue's purse")


class QueueDetourTest(QueueProfile):
    def test_a_hand_started_skill_uses_its_supplies_then_returns_without_crediting_pending_work(self):
        addon = self._queue_addon(
            "ankiscape_detour_supplies", (_MINE_IRON, 30), (_SMELT_IRON, 5), inventory={"Iron ore": 1}
        )
        addon._set_value("current_smith", "smelt_iron_bar")
        addon.save_skill("Smithing", None)
        addon.load_player_data()
        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)
            self.assertEqual(addon._state.player_data["inventory"]["Iron bar"], 1)
            self._answer(addon)
            self.assertEqual(addon._state.current_skill, "Mining")
            self.assertEqual([row[2] for row in self._rows(addon)], [0, 0])
            self._answer(addon)
        self.assertEqual(self._rows(addon)[0][2], 10)
        self.assertEqual(self.bankstanding_dialogs, [])

    def test_hand_started_mining_returns_when_its_pickaxe_is_unavailable(self):
        addon = self._queue_addon("ankiscape_detour_mining", (_PICKUP, 600), (_SMELT_IRON, 5))
        addon._set_value("current_ore", "iron")
        addon.save_skill("Mining", None)
        addon._state.player_data["toolbelt"]["mining"] = []
        self._answer(addon)
        self.assertEqual((addon._state.current_skill, addon._state.player_data["current_utility"]), ("Utilities", "pick_onions"))
        self.assertEqual([row[2] for row in self._rows(addon)], [0, 0])
        self._answer(addon)
        self.assertEqual(self._rows(addon)[0][2], 280)
        self.assertEqual(self.bankstanding_dialogs, [])

    def _quest_addon(self, name, *entries):
        return self._queue_addon(
            name, *entries, herblore_level=40, herblore_exp=40000, quests={"druidic_ritual": {"completed": True}}
        )

    def _finish_jungle_potion(self, addon):
        addon._state.player_data["inventory"].update({name: 1 for name in _HERBS})
        self.assertTrue(addon.on_set_quest("jungle_potion"))
        addon.save_skill("Quests", None)
        for _card in range(8):
            self._answer(addon)
            if addon._state.player_data["quests"]["jungle_potion"].get("completed"):
                return
        self.fail("Jungle Potion did not complete in eight reviews")

    def test_a_hand_run_quest_prunes_every_copy_and_preserves_the_prior_pause(self):
        for paused, quest_first in ((False, False), (False, True), (True, False), (True, True)):
            with self.subTest(paused=paused, quest_first=quest_first):
                self._assert_quest_removal_sequence(paused, quest_first)

    def _assert_quest_removal_sequence(self, paused, quest_first):
        from ankiscape.core.action_queue import action_queue_pure, stop_action

        entries = [(_QUEST, None), (_MINE_IRON, 30), (_QUEST, None)] if quest_first else [(_MINE_IRON, 30), (_QUEST, None), (_QUEST, None)]
        addon = self._quest_addon(f"ankiscape_detour_quest_{paused}_{quest_first}", *entries)
        if paused:
            stop_action(addon)
        elif not quest_first:
            with patch.object(addon.random, "random", lambda: 0.5):
                self._answer(addon)
        self._finish_jungle_potion(addon)
        queue = action_queue_pure(addon._state.player_data)
        self.assertEqual(queue["entries"], [{"action": _MINE_IRON, "count": 30}])
        self.assertEqual(queue["done"], 10 if not paused and not quest_first else 0)
        self.assertEqual(queue["paused"], paused)
        self.assertEqual(addon._state.current_skill, "Utilities" if paused else "Mining")
        self.assertEqual(self._log(addon).count("Queue: Jungle Potion done"), 1)

    def test_a_free_pickup_keeps_running_until_stop_or_add(self):
        from ankiscape.core.action_queue import action_queue_pure, add_to_action_queue, stop_action

        for end in ("stop", "add"):
            with self.subTest(end=end):
                addon = self._queue_addon(f"ankiscape_detour_pickup_{end}", (_MINE_IRON, 30))
                addon._set_value("current_utility", "pick_onions")
                addon.save_skill("Utilities", None)
                for _card in range(4):
                    self._answer(addon)
                    self.assertEqual(addon._state.player_data["current_utility"], "pick_onions")
                self.assertGreater(addon._state.player_data["inventory"]["Onion"], 28)
                self.assertEqual(self._rows(addon)[0][2], 0)
                self.assertTrue(action_queue_pure(addon._state.player_data)["suspended"])
                if end == "stop":
                    self.assertTrue(stop_action(addon))
                else:
                    self.assertEqual(add_to_action_queue(addon, _SMELT_IRON, 5), "")
                self.assertEqual(addon._state.current_skill, "Mining")
                self.assertFalse(action_queue_pure(addon._state.player_data)["suspended"])
                self.assertEqual(self.bankstanding_dialogs, [])

    def test_stop_and_old_saved_pause_survive_a_hand_start_and_clear_ends_the_detour(self):
        from ankiscape.core.action_queue import action_queue_pure, clear_action_queue, stop_action

        addon = self._queue_addon("ankiscape_detour_pause", (_MINE_IRON, 30), (_SMELT_IRON, 5))
        self.assertTrue(stop_action(addon))
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")
        addon._state.player_data["action_queue"].pop("suspended", None)
        addon.save_player_data()
        addon.load_player_data()
        addon._set_value("current_utility", "pick_onions")
        addon.save_skill("Utilities", None)
        self._answer(addon)
        self.assertTrue(stop_action(addon))
        self.assertTrue(action_queue_pure(addon._state.player_data)["paused"])
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")
        addon.save_skill("Mining", None)
        self.assertTrue(clear_action_queue(addon))
        self.assertEqual(self._rows(addon), [])
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")
        self.assertEqual(self.bankstanding_dialogs, [])

    def test_a_same_skill_hand_start_is_saved_and_does_not_spend_the_queued_count(self):
        from ankiscape.core.action_queue import action_queue_pure, stop_action

        addon = self._queue_addon("ankiscape_detour_same_skill", (_MINE_IRON, 30))
        addon._set_value("current_ore", "copper")
        addon.save_skill("Mining", None)
        addon.load_player_data()
        self.assertTrue(action_queue_pure(addon._state.player_data)["suspended"])
        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)
        self.assertGreater(addon._state.player_data["inventory"].get("Copper ore", 0), 0)
        self.assertEqual(self._rows(addon)[0][2], 0)
        self.assertTrue(stop_action(addon))
        self.assertEqual(addon._state.player_data["current_ore"], "iron")

    def test_random_played_commands_keep_queue_ownership_and_finished_quests_consistent(self):
        for seed in range(8):
            addon = self._quest_addon(f"ankiscape_detour_random_{seed}", (_MINE_IRON, 30))
            rng = random.Random(seed)
            with patch.object(addon.random, "random", rng.random):
                for _step in range(80):
                    self._random_command(addon, rng)
                    self._assert_queue_invariants(addon)

    def _random_command(self, addon, rng):
        from ankiscape.core.action_queue import add_to_action_queue, clear_action_queue, stop_action

        command = rng.choice(("add", "hand", "stop", "clear", "review", "quest"))
        if command == "add":
            add_to_action_queue(addon, rng.choice((_MINE_IRON, _PICKUP, _QUEST)), rng.randint(1, 30))
        elif command == "hand":
            addon._set_value("current_utility", "pick_onions")
            addon.save_skill("Utilities", None)
        elif command == "stop":
            stop_action(addon)
        elif command == "clear":
            clear_action_queue(addon)
        elif command == "quest":
            if not addon._state.player_data["quests"].get("jungle_potion", {}).get("completed"):
                self._finish_jungle_potion(addon)
        else:
            self._answer(addon)

    def _assert_queue_invariants(self, addon):
        from ankiscape.core.action_queue import action_queue_pure, queue_runs_pure
        from ankiscape.core.last_action import last_action_record_pure

        queue = action_queue_pure(addon._state.player_data)
        self.assertLessEqual(len(queue["entries"]), 5)
        if queue["entries"] and not queue["paused"] and not queue["suspended"]:
            self.assertTrue(queue_runs_pure(addon._state.player_data, addon._state.current_skill))
            self.assertEqual(last_action_record_pure(addon._state.player_data, addon._state.current_skill), queue["entries"][0]["action"])
        if addon._state.player_data["quests"].get("jungle_potion", {}).get("completed"):
            self.assertNotIn(_QUEST, [entry["action"] for entry in queue["entries"]])
