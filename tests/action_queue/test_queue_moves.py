"""Up and Down on queue entries, played through the add-on's queue command and the real review handler."""

from __future__ import annotations

from unittest.mock import patch

from tests.action_queue.test_queue_reviews import _MINE_IRON, _SMELT_IRON, _SMITH_PLATEBODY, QueueProfile

_COOKS_ASSISTANT = {"kind": "quest", "quest_id": "cooks_assistant"}


class QueueMoveTest(QueueProfile):
    def _move(self, addon, position, new_index):
        from ankiscape.core.action_queue import apply_action_queue_command

        return apply_action_queue_command(addon, "move", {"position": position, "new_index": new_index})

    def _entries(self, addon):
        from ankiscape.core.action_queue import action_queue_pure

        return [(entry["action"], entry["count"]) for entry in action_queue_pure(addon._state.player_data)["entries"]]

    def test_a_new_top_entry_runs_the_next_card_and_the_old_entry_owes_only_what_it_has_left(self):
        for position, new_index in ((1, 0), (0, 1)):
            with self.subTest(position=position, new_index=new_index):
                addon = self._queue_addon(
                    f"ankiscape_move_top_{position}", (_MINE_IRON, 30), (_SMELT_IRON, 5), inventory={"Iron ore": 5}
                )
                with patch.object(addon.random, "random", lambda: 0.5):
                    self._answer(addon)
                    self.assertEqual(self._rows(addon)[0], ("Mining: Iron", "current", 10))
                    ore = addon._state.player_data["inventory"]["Iron ore"]

                    result = self._move(addon, position, new_index)

                    self.assertEqual((result["ok"], result["active"]), (True, "Smithing"))
                    self.assertEqual(addon._state.player_data["current_smith"], "smelt_iron_bar")
                    self.assertEqual(self._entries(addon), [(_SMELT_IRON, 5), (_MINE_IRON, 20)])
                    self.assertEqual(self._rows(addon)[0], ("Smithing: Iron bar", "current", 0))

                    self._answer(addon)
                    self.assertEqual(addon._state.player_data["inventory"]["Iron bar"], 5)
                    self.assertEqual(addon._state.current_skill, "Mining")
                    while self._rows(addon):
                        self._answer(addon)
                # Ten ore before the move, 20 after, none lost or credited twice.
                self.assertEqual(addon._state.player_data["inventory"]["Iron ore"], ore - 5 + 20)
                self.assertEqual(self.bankstanding_dialogs, ["Queue finished after Mining: Iron."])

    def test_a_move_between_two_targets_of_one_skill_changes_the_target(self):
        addon = self._queue_addon("ankiscape_move_same_skill", (_SMELT_IRON, 5), (_SMITH_PLATEBODY, 1), inventory={"Iron ore": 5, "Iron bar": 5})
        self.assertEqual(self._move(addon, 1, 0)["active"], "Smithing")
        self.assertEqual(addon._state.player_data["current_smith"], "forge_iron_platebody")
        self.assertEqual(self._rows(addon)[0], ("Smithing: Iron platebody", "current", 0))

    def test_a_move_below_the_top_leaves_the_running_entry_and_its_progress_alone(self):
        addon = self._queue_addon("ankiscape_move_below", (_MINE_IRON, 30), (_SMELT_IRON, 5), (_SMITH_PLATEBODY, 1), inventory={"Iron bar": 5})
        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)
        self.assertTrue(self._move(addon, 2, 1)["ok"])
        self.assertEqual(self._entries(addon), [(_MINE_IRON, 30), (_SMITH_PLATEBODY, 1), (_SMELT_IRON, 5)])
        self.assertEqual(self._rows(addon)[0], ("Mining: Iron", "current", 10))
        self.assertEqual(addon._state.current_skill, "Mining")

    def test_a_paused_queue_only_changes_its_order_and_resume_runs_the_new_top(self):
        from ankiscape.core.action_queue import action_queue_pure, apply_action_queue_command, stop_action

        addon = self._queue_addon("ankiscape_move_paused", (_MINE_IRON, 30), (_SMELT_IRON, 5))
        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)
        self.assertTrue(stop_action(addon))

        self.assertTrue(self._move(addon, 1, 0)["ok"])

        self.assertTrue(action_queue_pure(addon._state.player_data)["paused"])
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")
        self.assertEqual(self._entries(addon), [(_SMELT_IRON, 5), (_MINE_IRON, 20)])
        self.assertEqual(apply_action_queue_command(addon, "resume", {})["active"], "Smithing")

    def test_a_set_aside_queue_only_changes_its_order_and_stop_returns_to_the_new_top(self):
        from ankiscape.core.action_queue import action_queue_pure, stop_action

        addon = self._queue_addon("ankiscape_move_set_aside", (_MINE_IRON, 30), (_SMELT_IRON, 5), inventory={"Iron ore": 5})
        addon._set_value("current_utility", "pick_onions")
        addon.save_skill("Utilities", None)
        self.assertTrue(action_queue_pure(addon._state.player_data)["suspended"])

        self.assertTrue(self._move(addon, 1, 0)["ok"])

        self.assertEqual(addon._state.player_data["current_utility"], "pick_onions")
        self._answer(addon)
        self.assertEqual(addon._state.player_data["current_utility"], "pick_onions")
        self.assertTrue(stop_action(addon))
        self.assertEqual(addon._state.current_skill, "Smithing")

    def test_a_new_top_entry_that_cannot_start_leaves_and_the_old_entry_runs_on(self):
        addon = self._queue_addon("ankiscape_move_cannot_start", (_MINE_IRON, 30), (_COOKS_ASSISTANT, None))
        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)
        addon._state.player_data["quests"]["cooks_assistant"] = {"completed": True}

        self.assertTrue(self._move(addon, 1, 0)["ok"])

        self.assertEqual(self._entries(addon), [(_MINE_IRON, 20)])
        self.assertEqual(addon._state.current_skill, "Mining")
        self.assertEqual(self.bankstanding_dialogs, [])

    def test_a_move_off_either_end_changes_nothing(self):
        addon = self._queue_addon("ankiscape_move_ends", (_MINE_IRON, 30), (_SMELT_IRON, 5))
        for position, new_index in ((0, -1), (1, 2), (2, 1), (0, 0)):
            with self.subTest(position=position, new_index=new_index):
                self.assertFalse(self._move(addon, position, new_index)["ok"])
                self.assertEqual(self._entries(addon), [(_MINE_IRON, 30), (_SMELT_IRON, 5)])
