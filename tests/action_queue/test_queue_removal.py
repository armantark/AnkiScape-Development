"""Removing queue entries, played through the add-on's queue command and the real review handler."""

from __future__ import annotations

import types
from unittest.mock import patch

from tests.action_queue.test_queue_reviews import _MINE_IRON, _SMELT_IRON, QueueProfile

_COOKS_ASSISTANT = {"kind": "quest", "quest_id": "cooks_assistant"}


class QueueRemovalTest(QueueProfile):
    def _remove(self, addon, position):
        from ankiscape.core.action_queue import action_queue_pure, apply_action_queue_command

        entry = action_queue_pure(addon._state.player_data)["entries"][position]
        return apply_action_queue_command(addon, "remove", {"position": position, "entry": entry})

    def _mined_one_card(self, name, *entries):
        addon = self._queue_addon(name, *entries)
        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)
        self.assertEqual(self._rows(addon)[0], ("Mining: Iron", "current", 10))
        return addon

    def test_removing_the_running_entry_runs_the_next_on_the_next_card_and_keeps_what_it_made(self):
        addon = self._mined_one_card("ankiscape_remove_running", (_MINE_IRON, 30), (_SMELT_IRON, 5))
        save = addon._state.player_data
        ore, mining_exp = save["inventory"]["Iron ore"], save["mining_exp"]

        result = self._remove(addon, 0)

        self.assertEqual((result["ok"], result["active"]), (True, "Smithing"))
        self.assertEqual(save["current_smith"], "smelt_iron_bar")
        self.assertEqual(self._rows(addon), [("Smithing: Iron bar", "current", 0)])
        self.assertEqual((save["inventory"]["Iron ore"], save["mining_exp"]), (ore, mining_exp))
        self.assertEqual(self.bankstanding_dialogs, [])
        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)
        self.assertEqual(save["inventory"]["Iron bar"], 5)
        self.assertEqual(save["inventory"]["Iron ore"], ore - 5)

    def test_removing_the_last_entry_ends_at_bankstanding_with_no_dialog_and_resume_offers_it(self):
        from ankiscape.core.last_action import resume_button_view_pure

        addon = self._mined_one_card("ankiscape_remove_last", (_MINE_IRON, 30))

        result = self._remove(addon, 0)

        self.assertEqual((result["ok"], result["active"]), (True, "Utilities"))
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")
        self.assertEqual(self._rows(addon), [])
        self.assertEqual(self.bankstanding_dialogs, [])
        self.assertIn("Switched to Bankstanding · The queue is empty.", self._log(addon))
        self.assertEqual(resume_button_view_pure(addon._state.player_data, "Utilities")["text"], "Resume Mining")

    def test_when_no_later_entry_can_start_the_queue_ends_at_bankstanding(self):
        addon = self._mined_one_card("ankiscape_remove_none_start", (_MINE_IRON, 30), (_COOKS_ASSISTANT, None))
        addon._state.player_data["quests"]["cooks_assistant"] = {"completed": True}

        self.assertEqual(self._remove(addon, 0)["active"], "Utilities")

        self.assertEqual(self._rows(addon), [])
        self.assertIn("Queue: Cook's Assistant stopped · it could not start", self._log(addon))

    def test_two_entries_of_one_action_restart_the_count_and_never_pause(self):
        from ankiscape.core.action_queue import action_queue_pure

        addon = self._mined_one_card("ankiscape_remove_twin", (_MINE_IRON, 30), (_MINE_IRON, 50))

        self.assertEqual(self._remove(addon, 0)["active"], "Mining")

        self.assertEqual(self._rows(addon), [("Mining: Iron", "current", 0)])
        self.assertFalse(action_queue_pure(addon._state.player_data)["paused"])

    def test_a_later_entry_leaves_alone_and_the_running_entry_keeps_its_progress(self):
        addon = self._mined_one_card("ankiscape_remove_later", (_MINE_IRON, 30), (_SMELT_IRON, 5))
        self.assertEqual(self._remove(addon, 1)["active"], "Mining")
        self.assertEqual(self._rows(addon), [("Mining: Iron", "current", 10)])

    def test_a_paused_queue_only_changes_its_list_and_resume_runs_the_new_top(self):
        from ankiscape.core.action_queue import action_queue_pure, apply_action_queue_command, stop_action

        addon = self._mined_one_card("ankiscape_remove_paused", (_MINE_IRON, 30), (_SMELT_IRON, 5))
        self.assertTrue(stop_action(addon))

        self.assertEqual(self._remove(addon, 0)["active"], "Utilities")

        self.assertTrue(action_queue_pure(addon._state.player_data)["paused"])
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")
        self.assertEqual(self._rows(addon), [("Smithing: Iron bar", "current", 0)])
        self.assertEqual(apply_action_queue_command(addon, "resume", {})["active"], "Smithing")

    def test_a_set_aside_queue_only_changes_its_list_and_the_hand_started_action_runs_on(self):
        from ankiscape.core.action_queue import action_queue_pure, stop_action

        addon = self._queue_addon("ankiscape_remove_set_aside", (_MINE_IRON, 30), (_SMELT_IRON, 5), inventory={"Iron ore": 5})
        addon._set_value("current_utility", "pick_onions")
        addon.save_skill("Utilities", None)
        self.assertTrue(action_queue_pure(addon._state.player_data)["suspended"])

        self.assertEqual(self._remove(addon, 0)["active"], "Utilities")

        self.assertEqual(addon._state.player_data["current_utility"], "pick_onions")
        self.assertTrue(stop_action(addon))
        self.assertEqual(addon._state.current_skill, "Smithing")

    def test_undo_restores_the_entry_its_progress_and_what_ran(self):
        for name, entries, active in (
            ("ankiscape_remove_undo_next", ((_MINE_IRON, 30), (_SMELT_IRON, 5)), "Smithing"),
            ("ankiscape_remove_undo_last", ((_MINE_IRON, 30),), "Utilities"),
        ):
            with self.subTest(name):
                addon = self._mined_one_card(name, *entries)
                rows = self._rows(addon)
                self.assertEqual(self._remove(addon, 0)["active"], active)

                addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))

                self.assertEqual(self._rows(addon), rows)
                self.assertEqual(addon._state.current_skill, "Mining")
                self.assertEqual(addon._state.player_data["current_ore"], "iron")
                with patch.object(addon.random, "random", lambda: 0.5):
                    self._answer(addon)
                self.assertEqual(self._rows(addon)[0], ("Mining: Iron", "current", 20))

    def test_a_position_that_holds_another_entry_now_refuses(self):
        from ankiscape.core.action_queue import action_queue_pure, apply_action_queue_command

        addon = self._queue_addon("ankiscape_remove_stale", (_MINE_IRON, 30), (_SMELT_IRON, 5))
        passed = action_queue_pure(addon._state.player_data)["entries"][1]

        self.assertFalse(apply_action_queue_command(addon, "remove", {"position": 0, "entry": passed})["ok"])
        self.assertFalse(apply_action_queue_command(addon, "remove", {"position": 2, "entry": passed})["ok"])

        self.assertEqual(len(self._rows(addon)), 2)
