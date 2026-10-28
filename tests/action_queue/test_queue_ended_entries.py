"""Ended entries leave the queue, through the real review handler and menu commands.

The owner's case (Pass 18): finished entries stayed in the queue box and kept
one of its five places. A done or stopped entry now leaves at once; the Event
log keeps its line, and the review HUD the reason the last one stopped.
"""

from __future__ import annotations

from unittest.mock import patch

from tests.action_queue.test_queue_reviews import _MINE_IRON, _SMELT_IRON, _SMITH_PLATEBODY, QueueProfile

_GATHER = [{"kind": "utility", "utility_id": utility} for utility in (
    "gather_goblin_mail", "pick_redberries", "pick_onions", "pick_cabbages", "pick_potatoes",
)]


class QueueEndedEntriesTest(QueueProfile):
    def _panel(self, addon):
        from ankiscape.core.menu_action_queue import queue_panel_view_pure

        return queue_panel_view_pure(addon._state.player_data, addon._state.current_skill)

    def _hud(self, addon):
        from ankiscape.core.last_action import resume_button_view_pure

        view = resume_button_view_pure(addon._state.player_data, addon._state.current_skill)
        return view["text"], view["bank_status"]

    def test_each_ended_entry_frees_its_place_and_a_finished_plan_frees_all_five(self):
        from ankiscape.core.action_queue import QUEUE_FULL_TEXT, add_to_action_queue

        addon = self._queue_addon(
            "ankiscape_queue_ended_places", *[(action, 1) for action in _GATHER[:4]], (_MINE_IRON, 30)
        )
        self.assertEqual(add_to_action_queue(addon, _GATHER[4], 1), QUEUE_FULL_TEXT)

        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)

        # Four gathers ended in the card, and the rest of it went to Mining.
        self.assertEqual(self._rows(addon)[0][:2], ("Mining: Iron", "current"))
        self.assertEqual(self._panel(addon)["title"], "Queue: 1 of 5 entries")
        self.assertIn("Queue: Pick cabbages done", self._log(addon))
        for action in _GATHER[:4]:
            self.assertEqual(add_to_action_queue(addon, action, 1), "")
        self.assertEqual(add_to_action_queue(addon, _GATHER[4], 1), QUEUE_FULL_TEXT)

        for _card in range(4):
            with patch.object(addon.random, "random", lambda: 0.5):
                self._answer(addon)

        self.assertEqual((self._rows(addon), self._panel(addon)["title"]), ([], "Queue: empty"))
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")
        for action in _GATHER:
            self.assertEqual(add_to_action_queue(addon, action, 1), "")

    def test_a_stopped_last_entry_leaves_with_its_reason_in_the_log_and_on_the_hud(self):
        addon = self._queue_addon("ankiscape_queue_ended_stop", (_SMELT_IRON, 20), inventory={"Iron ore": 10})

        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)
            self._answer(addon)

        reason = "You need 1 Iron ore to make Iron bar."
        self.assertEqual(self._rows(addon), [])
        self.assertEqual(self._log(addon)[-2:], [f"Queue: Smithing: Iron bar stopped · {reason}", f"Switched to Bankstanding · {reason}"])
        self.assertEqual(self._hud(addon), ("Resume Smithing", f"stopped: {reason}"))

    def test_a_card_that_fills_an_entry_and_stops_its_action_ends_the_entry_as_done(self):
        hero = {"kind": "skill", "skill": "Thieving", "target": "pickpocket_hero"}
        addon = self._queue_addon(
            "ankiscape_queue_ended_fill_and_stop", (hero, 1), (_MINE_IRON, 5), thieving_level=99, combat_lifepoints=1
        )

        # A high roll fails the pickpocket, and the hero's hit kills a player on 1 life point.
        with patch.object(addon.random, "random", lambda: 0.99):
            self._answer(addon)

        self.assertEqual(addon._state.current_skill, "Mining")
        self.assertIn("Queue: Thieving: Hero done", self._log(addon))
        self.assertFalse([line for line in self._log(addon) if line.startswith("Queue: Thieving: Hero stopped")])

    def test_clear_stops_a_hand_started_action_and_resume_offers_it(self):
        addon = self._queue_addon("ankiscape_queue_ended_clear", woodcutting_level=40)
        addon.save_skill("Woodcutting", None)
        captured = {}
        addon.ui.show_main_menu = lambda *_args, **kwargs: captured.update(kwargs)
        addon._on_main_menu()
        command = captured["on_action_queue_command"]

        # A new plan still waits behind the hand-started action.
        self.assertEqual(command("add", {"action": _MINE_IRON, "count": 30})["active"], "Woodcutting")

        self.assertEqual(command("clear", {}), {"ok": True, "active": "Utilities", "message": ""})
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")
        self.assertEqual(self.bankstanding_dialogs, [])
        self.assertEqual(self._hud(addon), ("Resume Woodcutting", "stopped: The queue was cleared."))
        self.assertTrue(addon.on_resume_last_action())
        self.assertEqual(addon._state.current_skill, "Woodcutting")

    def test_a_pass_17_save_loads_with_only_the_entries_left_to_run(self):
        addon = self._queue_addon("ankiscape_queue_ended_pass17", inventory={"Iron bar": 10})
        entry = lambda action, count, **ended: {"action": action, "count": count, **ended}  # noqa: E731
        addon._state.player_data["action_queue"] = {
            "entries": [
                entry(_MINE_IRON, 10, done=10),
                entry(_SMELT_IRON, 20, done=10, stopped="You need 1 Iron ore to make Iron bar."),
                entry(_SMITH_PLATEBODY, 1),
                entry(_MINE_IRON, 5),
            ],
            "index": 2,
            "done": 0,
            "paused": False,
            "waiting": True,
        }
        addon.save_player_data()
        addon.load_player_data()

        self.assertEqual(
            self._rows(addon), [("Smithing: Iron platebody", "current", 0), ("Mining: Iron", "waiting", 0)]
        )
        self.assertEqual(self._panel(addon)["title"], "Queue: 2 of 5 entries")
        captured = {}
        addon.ui.show_main_menu = lambda *_args, **kwargs: captured.update(kwargs)
        addon._on_main_menu()
        self.assertEqual(captured["on_action_queue_command"]("resume", {})["active"], "Smithing")
        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)

        # Only the two entries left ran: the ended Mining and smelting entries never ran again.
        inventory = addon._state.player_data["inventory"]
        self.assertEqual((inventory["Iron platebody"], inventory["Iron ore"]), (1, 5))
        self.assertEqual(self._rows(addon), [])
