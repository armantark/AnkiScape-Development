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
from ankiscape.core.menu_action_queue import action_supply_limit_pure, queue_add_view_pure
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
                self.assertEqual(action_supply_limit_pure(save, action), limit)

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
        self.assertEqual(self.bankstanding_dialogs, ["Queue finished after Smithing: Iron bar."])

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
            {"ok": False, "active": "Mining", "message": "The queue is full."},
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

    def test_each_refused_add_names_its_own_cause(self):
        addon = self._queue_addon("ankiscape_queue_menu_refusals")
        addon._state.player_data["quests"] = {"rune_mysteries": {"completed": True}}
        command = self._menu(addon)

        for action, count, message in (
            ({}, 1, "Nothing selected."),
            ({"kind": "skill", "skill": "Sailing", "target": "raft"}, 1, "This action cannot be queued."),
            ({"kind": "quest", "quest_id": "rune_mysteries"}, None, "This quest is complete."),
            ({"kind": "quest", "quest_id": "dragon_slayer"}, None, "Requires: 32 quest points"),
            (_MINE_IRON, 0, "Type a count of 1 or more."),
        ):
            with self.subTest(message=message):
                self.assertEqual(command("add", {"action": action, "count": count}), {"ok": False, "active": "Utilities", "message": message})
        self.assertEqual(self._rows(addon), [])

    def test_an_add_starts_the_queue_in_place_of_the_selected_pickup(self):
        # The owner's cases (Pass 19): with the pickup already selected, a queued
        # Doogle leaf waited behind it while 140 leaves came in, and so did nettles.
        for utility_id, item in (("gather_doogle_leaves", "Doogle leaves"), ("pick_nettles", "Nettles")):
            with self.subTest(utility_id=utility_id):
                addon = self._queue_addon(f"ankiscape_queue_menu_{utility_id}")
                addon._state.player_data["current_utility"] = utility_id
                pickup = {"kind": "utility", "utility_id": utility_id}

                self.assertEqual(self._menu(addon)("add", {"action": pickup, "count": 1})["ok"], True)
                self._answer(addon)

                self.assertEqual(addon._state.player_data["inventory"].get(item), 1)
                self.assertEqual(self._rows(addon), [])
                self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")

    def test_an_add_starts_the_queue_in_place_of_a_hand_started_skill(self):
        addon = self._queue_addon("ankiscape_queue_menu_hand_started", woodcutting_level=40)
        addon.save_skill("Woodcutting", None)

        self.assertEqual(self._menu(addon)("add", {"action": _MINE_IRON, "count": 30}), {"ok": True, "active": "Mining", "message": ""})
        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)
        self.assertEqual(self._rows(addon), [("Mining: Iron", "current", 10)])

    def test_an_add_that_cannot_start_says_so_and_leaves_the_running_action(self):
        addon = self._queue_addon("ankiscape_queue_menu_no_star", woodcutting_level=40)
        addon.save_skill("Woodcutting", None)
        stars = {"kind": "utility", "utility_id": "shooting_stars"}

        result = self._menu(addon)("add", {"action": stars, "count": 1})
        self.assertEqual(result, {"ok": False, "active": "Woodcutting", "message": "Shooting Stars could not start."})
        self.assertEqual(self._rows(addon), [])

    def test_an_add_restarts_a_queue_that_does_not_run_its_entry(self):
        for name, step_off in (
            ("stopped", lambda addon, menu: menu["on_stop_training"]()),
            ("hand_started", lambda addon, _menu: addon.save_skill("Woodcutting", None)),
        ):
            with self.subTest(name=name):
                addon = self._queue_addon(f"ankiscape_queue_menu_restart_{name}", (_MINE_IRON, 30), woodcutting_level=40)
                captured = {}
                addon.ui.show_main_menu = lambda *_args, **kwargs: captured.update(kwargs)
                addon._on_main_menu()
                step_off(addon, captured)

                result = captured["on_action_queue_command"]("add", {"action": _SMELT_IRON, "count": 10})
                self.assertEqual(result, {"ok": True, "active": "Mining", "message": ""})
                self.assertEqual(self._rows(addon), [("Mining: Iron", "current", 0), ("Smithing: Iron bar", "waiting", 0)])
                self.assertFalse(addon._state.player_data["action_queue"]["paused"])

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
