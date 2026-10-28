"""The main menu's queue commands and count box, driven through the real add-on.

The owner's case (Pass 17): the count box starts at the most the Bank allows,
so a smelt entry with that count ends as done when the ore runs out, not as
stopped short; the queue holds five entries and Clear drops the plan and
stops whatever runs.
"""

from __future__ import annotations

import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.menu_action_queue import action_bank_limit_pure, queue_add_view_pure
from tests.action_queue.test_queue_reviews import _MINE_IRON, _SMELT_IRON, QueueProfile


class BankLimitTest(unittest.TestCase):
    def test_the_limit_counts_products_from_every_input_the_bank_holds(self):
        bank = {"Iron ore": 37, "Logs": 3, "Rune essence": 10, "Arrow shafts": 30, "Feather": 20, "Red feather": 12}
        save = {"inventory": bank, "runecrafting_level": 44}
        for action, limit in (
            (_SMELT_IRON, 37),
            # One log whittles 15 shafts.
            ({"kind": "skill", "skill": "Fletching", "target": "arrow_shafts"}, 45),
            # Any feather colour flights an arrow: 32 feathers and 30 shafts make two batches of 15.
            ({"kind": "skill", "skill": "Fletching", "target": "headless_arrows"}, 30),
            # Air runes at Runecrafting 44 make five per essence.
            ({"kind": "skill", "skill": "Runecrafting", "target": "craft_air_runes"}, 50),
            (_MINE_IRON, None),
            ({"kind": "combat", "target": "chicken", "combat_action": "attack"}, None),
        ):
            with self.subTest(action=action):
                self.assertEqual(action_bank_limit_pure(save, action), limit)

    def test_an_unlimited_action_starts_at_one_inventory(self):
        view = queue_add_view_pure({"inventory": {}}, _MINE_IRON)
        self.assertEqual((view["count"], view["unit"]), (28, "Iron ore"))


class QueueMenuCommandTest(QueueProfile):
    def _menu(self, addon):
        captured = {}
        addon.ui.show_main_menu = lambda *_args, **kwargs: captured.update(kwargs)
        addon._on_main_menu()
        return captured["on_action_queue_command"]

    def test_the_bank_default_runs_a_smelt_entry_to_done(self):
        addon = self._queue_addon("ankiscape_queue_menu_default", **{"inventory": {"Iron ore": 10}})
        command = self._menu(addon)
        count = queue_add_view_pure(addon._state.player_data, _SMELT_IRON)["count"]
        self.assertEqual(count, 10)

        result = command("add", {"action": _SMELT_IRON, "count": count})
        self.assertEqual(result, {"ok": True, "active": "Smithing", "message": ""})
        self.assertEqual(addon._state.current_skill, "Smithing")
        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)

        self.assertEqual(self._rows(addon), [])
        self.assertNotIn("Queue: Smithing: Iron bar stopped", " ".join(self._log(addon)))
        self.assertEqual(self.bankstanding_dialogs, ["The queue is finished: Smithing: Iron bar done."])

    def test_a_bury_entry_counts_the_bones_it_buries(self):
        bury = {"kind": "skill", "skill": "Prayer", "target": "bury_bones"}
        addon = self._queue_addon("ankiscape_queue_menu_bury", **{"inventory": {"Bones": 40}})
        view = queue_add_view_pure(addon._state.player_data, bury)
        self.assertEqual((view["count"], view["unit"], view["materials"]), (40, "Bones used", "Bones: 40 in Bank"))

        self.assertTrue(self._menu(addon)("add", {"action": bury, "count": 40})["ok"])
        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)

        # At 10x one review buries ten bones; the entry counts each of them, not the one review.
        self.assertEqual(addon._state.player_data["inventory"]["Bones"], 30)
        self.assertEqual(self._rows(addon), [("Prayer: Bones", "current", 10)])

    def test_a_sixth_entry_is_refused_and_clear_stops_the_entry_the_queue_runs(self):
        from ankiscape.core.last_action import resume_button_view_pure

        addon = self._queue_addon("ankiscape_queue_menu_cap")
        command = self._menu(addon)
        for _ in range(5):
            self.assertTrue(command("add", {"action": _MINE_IRON, "count": 100})["ok"])

        refused = command("add", {"action": _SMELT_IRON, "count": 100})
        self.assertEqual(
            refused,
            {"ok": False, "active": "Mining", "message": "The queue holds 5 entries. Clear it to plan again."},
        )
        self.assertFalse(queue_add_view_pure(addon._state.player_data, _SMELT_IRON)["enabled"])

        self.assertTrue(command("remove", {"position": 4})["ok"])
        self.assertFalse(command("remove", {"position": 0})["ok"])
        self.assertEqual(len(self._rows(addon)), 4)

        self.assertEqual(command("clear", {}), {"ok": True, "active": "Utilities", "message": ""})
        self.assertEqual(self._rows(addon), [])
        self.assertEqual(self.bankstanding_dialogs, [])
        view = resume_button_view_pure(addon._state.player_data, addon._state.current_skill)
        self.assertEqual((view["text"], view["bank_status"]), ("Resume Mining", "stopped: The queue was cleared."))

    def test_a_plan_waits_behind_a_hand_started_action_until_it_stops(self):
        addon = self._queue_addon("ankiscape_queue_menu_wait", woodcutting_level=40)
        addon.save_skill("Woodcutting", None)
        command = self._menu(addon)

        self.assertEqual(command("add", {"action": _MINE_IRON, "count": 30}), {"ok": True, "active": "Woodcutting", "message": ""})
        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)
        # Woodcutting's review neither pauses nor counts toward the waiting plan.
        self.assertEqual(addon._state.current_skill, "Woodcutting")
        self.assertEqual(self._rows(addon), [("Mining: Iron", "current", 0)])

        # Stopping the hand-started action starts the plan, and the menu learns what runs now.
        captured = {}
        addon.ui.show_main_menu = lambda *_args, **kwargs: captured.update(kwargs)
        addon._on_main_menu()
        self.assertEqual(captured["on_stop_training"](), "Mining")
        self.assertEqual(addon._state.player_data["current_ore"], "iron")
        self.assertEqual(self._log(addon)[-1], "Queue: Woodcutting stopped, so the plan starts")

    def test_start_now_starts_a_waiting_plan_at_once(self):
        addon = self._queue_addon("ankiscape_queue_menu_start_now", woodcutting_level=40)
        addon.save_skill("Woodcutting", None)
        command = self._menu(addon)
        command("add", {"action": _MINE_IRON, "count": 30})

        self.assertEqual(command("resume", {}), {"ok": True, "active": "Mining", "message": ""})
        self.assertEqual(self._rows(addon), [("Mining: Iron", "current", 0)])

    def test_a_hud_that_cannot_draw_leaves_each_committed_command_in_place(self):
        addon = self._queue_addon("ankiscape_queue_menu_hud")
        command = self._menu(addon)

        with patch.object(addon, "update_review_hud", side_effect=RuntimeError("no reviewer")):
            self.assertEqual(command("add", {"action": _MINE_IRON, "count": 30}), {"ok": True, "active": "Mining", "message": ""})
            self.assertTrue(command("clear", {})["ok"])

        self.assertEqual(self._rows(addon), [])
        self.assertEqual(addon._state.player_data["last_action"]["skill"], "Mining")


if __name__ == "__main__":
    unittest.main()
