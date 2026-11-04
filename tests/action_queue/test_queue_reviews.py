"""The queue driven through the real review handler, at the owner's 10x speed.

The owner's case (Pass 17): at 10x an action uses up its materials in a few
cards, so he queues mine, smelt, smith and keeps studying while it runs.
"""

from __future__ import annotations

import types
from unittest.mock import patch

from tests.integration_smoke import fixtures

_MINE_IRON = {"kind": "skill", "skill": "Mining", "target": "iron"}
_SMELT_IRON = {"kind": "skill", "skill": "Smithing", "target": "smelt_iron_bar"}
_SMITH_PLATEBODY = {"kind": "skill", "skill": "Smithing", "target": "forge_iron_platebody"}
_BKF = "black_knights_fortress"


class QueueProfile(fixtures.ReviewedProfile):
    def _queue_addon(self, name, *entries, **save):
        from ankiscape.core.action_queue import add_to_action_queue

        addon = self._addon(name)
        addon.mw.col.set_config("ankiscape_review_action_multiplier", 10)
        self.popups = []
        addon.mw.exp_popup = types.SimpleNamespace(
            show_text=self.popups.append, show_exp=lambda exp: self.popups.append(exp.display_text)
        )
        self._new_save(addon, mining_level=40, smithing_level=40, **save)
        addon._state.current_skill = "Utilities"
        addon._state.player_data["current_utility"] = "bankstanding"
        for action, count in entries:
            self.assertEqual(add_to_action_queue(addon, action, count), "")
        return addon

    def _rows(self, addon):
        from ankiscape.core.action_queue import action_queue_view_pure

        return [(row["name"], row["state"], row["done"]) for row in action_queue_view_pure(addon._state.player_data)["entries"]]

    def _log(self, addon):
        return [row["text"] for row in addon._state.player_data["review_event_log"] if row["kind"] != "achievement"]


class ActionQueueReviewTest(QueueProfile):
    def test_mine_smelt_smith_runs_its_counts_passes_a_short_entry_and_ends_at_bankstanding(self):
        from ankiscape.core.last_action import resume_button_view_pure

        addon = self._queue_addon(
            "ankiscape_queue_chain", (_MINE_IRON, 10), (_SMELT_IRON, 20), (_SMITH_PLATEBODY, 1)
        )
        self.assertEqual(addon._state.current_skill, "Mining")
        self.assertEqual(addon._state.player_data["current_ore"], "iron")

        # A constant mid roll lands every swing and keeps every smelt pure.
        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)
            self.assertEqual(self.popups, ["+350 XP · Mining · +10 Iron ore"])
            self.assertEqual(addon._state.current_skill, "Smithing")
            self.assertEqual(addon._state.player_data["current_smith"], "smelt_iron_bar")

            addon.load_player_data()
            self.assertEqual(
                self._rows(addon), [("Smithing: Iron bar", "current", 0), ("Smithing: Iron platebody", "waiting", 0)]
            )

            self._answer(addon)
            self.assertEqual(self._rows(addon)[0], ("Smithing: Iron bar", "current", 10))

            # Ten ore made ten bars; the eleventh smelt finds no ore.
            self._answer(addon)
            self.assertEqual(addon._state.player_data["current_smith"], "forge_iron_platebody")
            self.assertEqual(self.bankstanding_dialogs, [])

            self._answer(addon)

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")
        self.assertEqual(self.bankstanding_dialogs, ["Queue finished after Smithing: Iron platebody."])
        self.assertEqual(addon._state.player_data["inventory"]["Iron platebody"], 1)
        self.assertEqual(
            self._log(addon),
            [
                "+350 XP · Mining · +10 Iron ore",
                "Queue: Mining: Iron done",
                "+125 XP · Smithing · +10 Iron bar · −10 Iron ore",
                "Queue: Smithing: Iron bar stopped · You need 1 Iron ore to make Iron bar.",
                "+125 XP · Smithing · +1 Iron platebody · −5 Iron bar",
                "Queue: Smithing: Iron platebody done",
                "Switched to Bankstanding · Queue finished after Smithing: Iron platebody.",
            ],
        )
        self.assertEqual(self._rows(addon), [])
        # With the queue finished, Resume offers its last entry.
        view = resume_button_view_pure(addon._state.player_data, addon._state.current_skill)
        self.assertEqual(view["text"], "Resume Smithing")

    def test_a_quest_entry_ends_when_its_quest_stops_and_the_next_entry_starts(self):
        addon = self._queue_addon(
            "ankiscape_queue_quest",
            ({"kind": "quest", "quest_id": _BKF}, None),
            (_MINE_IRON, 30),
            quest_points=13,
        )
        addon._state.player_data["inventory"]["Bronze med helm"] = 1
        self.assertEqual(addon._state.current_skill, "Quests")

        self._answer(addon)

        self.assertEqual(self.errors, [])
        self.assertEqual(addon._state.current_skill, "Mining")
        self.assertEqual(self._log(addon)[-1], "Queue: Black Knights' Fortress stopped · Needs Iron chainbody. Next: Mining.")
        self.assertEqual(self.bankstanding_dialogs, [])
        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)
        self.assertEqual(self._rows(addon), [("Mining: Iron", "current", 10)])

    def test_an_entry_above_the_players_level_gives_its_notice_and_the_next_entry_starts(self):
        addon = self._queue_addon(
            "ankiscape_queue_level",
            ({"kind": "skill", "skill": "Smithing", "target": "smelt_rune_bar"}, 5),
            (_MINE_IRON, 30),
        )
        self.assertEqual(addon._state.current_skill, "Smithing")

        self._answer(addon)

        self.assertEqual(addon._state.current_skill, "Mining")
        self.assertEqual(addon._state.player_data["current_ore"], "iron")
        self.assertEqual((self.errors, self.bankstanding_dialogs), ([], []))
        self.assertEqual(
            self._log(addon)[-1], "Queue: Smithing: Rune bar stopped · You need level 85 Smithing to make Rune bar."
        )
        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)
        self.assertEqual(self._rows(addon), [("Mining: Iron", "current", 10)])

    def test_an_entry_that_takes_over_a_stop_is_not_credited_with_the_review_that_stopped(self):
        addon = self._queue_addon(
            "ankiscape_queue_takeover_credit",
            ({"kind": "skill", "skill": "Smithing", "target": "smelt_rune_bar"}, 5),
            ({"kind": "skill", "skill": "Agility", "target": "gnome_normal"}, 1),
            agility_level=40,
        )

        self._answer(addon)

        self.assertEqual(addon._state.current_skill, "Agility")
        self.assertEqual(self._rows(addon), [("Agility: Gnome Stronghold Course", "current", 0)])
        # A constant mid roll keeps a random distraction from moving Agility to another course.
        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)
        self.assertGreater(addon._state.player_data["agility_exp"], 0)
        self.assertEqual(self._rows(addon), [])
        self.assertEqual(self.bankstanding_dialogs, ["Queue finished after Agility: Gnome Stronghold Course."])
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")

    def test_a_stopped_entry_keeps_the_reason_its_review_gave_after_the_stop(self):
        addon = self._queue_addon(
            "ankiscape_queue_late_reason",
            (_MINE_IRON, 30),
            ({"kind": "skill", "skill": "Agility", "target": "gnome_normal"}, 1),
            toolbelt={"mining": []},
            agility_level=40,
        )

        self._answer(addon)

        reason = "You need a usable pickaxe to train Mining. Mining has been switched off."
        self.assertEqual(self.errors, [])
        self.assertEqual(addon._state.current_skill, "Agility")
        self.assertEqual(self._log(addon)[-1], f"Queue: Mining: Iron stopped · {reason} Next: Agility.")
        self.assertEqual(self._rows(addon), [("Agility: Gnome Stronghold Course", "current", 0)])

    def test_resume_of_a_paused_entry_that_cannot_start_shows_why_and_keeps_the_queue_paused(self):
        from ankiscape.core.action_queue import action_queue_view_pure

        addon = self._queue_addon(
            "ankiscape_queue_resume_refusal", ({"kind": "quest", "quest_id": _BKF}, None), (_MINE_IRON, 30), quest_points=13
        )
        addon._state.player_data["inventory"]["Bronze med helm"] = 1
        captured = {}
        addon.ui.show_main_menu = lambda *_args, **kwargs: captured.update(kwargs)
        addon._on_main_menu()
        self.assertTrue(captured["on_stop_training"]())

        self.assertFalse(addon.on_resume_last_action())
        self.assertFalse(captured["on_action_queue_command"]("resume", {})["ok"])

        self.assertEqual([title for title, _message in self.errors], ["Quest blocked", "Quest blocked"])
        self.assertEqual((addon._state.current_skill, addon._state.player_data["current_utility"]), ("Utilities", "bankstanding"))
        self.assertTrue(action_queue_view_pure(addon._state.player_data)["paused"])
        self.assertEqual(self._rows(addon), [("Black Knights' Fortress", "current", 0), ("Mining: Iron", "waiting", 0)])

    def test_a_manual_stop_pauses_the_queue_and_resume_continues_its_entry(self):
        from ankiscape.core.action_queue import action_queue_view_pure, clear_action_queue

        addon = self._queue_addon("ankiscape_queue_pause", (_MINE_IRON, 30), (_SMELT_IRON, 5))
        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)
        captured = {}
        addon.ui.show_main_menu = lambda *_args, **kwargs: captured.update(kwargs)
        addon._on_main_menu()

        self.assertTrue(captured["on_stop_training"]())
        captured["on_set_ore"]("copper")

        self.assertTrue(action_queue_view_pure(addon._state.player_data)["paused"])
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")
        self.assertEqual(self.bankstanding_dialogs, [])
        self.assertTrue(addon.on_resume_last_action())
        self.assertEqual(addon._state.current_skill, "Mining")
        self.assertEqual(addon._state.player_data["current_ore"], "iron")
        self.assertFalse(action_queue_view_pure(addon._state.player_data)["paused"])
        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)
        self.assertEqual(self._rows(addon)[0], ("Mining: Iron", "current", 20))

        # Clear cancels the plan, stopping the entry it runs; Resume offers that entry back.
        self.assertTrue(clear_action_queue(addon))
        self.assertEqual(action_queue_view_pure(addon._state.player_data)["entries"], [])
        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertEqual(self.bankstanding_dialogs, [])
        self.assertTrue(addon.on_resume_last_action())
        self.assertEqual((addon._state.current_skill, addon._state.player_data["current_ore"]), ("Mining", "iron"))

    def test_an_action_the_player_starts_himself_sets_aside_the_queue(self):
        from ankiscape.core.action_queue import action_queue_view_pure

        addon = self._queue_addon("ankiscape_queue_takeover", (_MINE_IRON, 30), woodcutting_level=40)
        addon.save_skill("Woodcutting", None)

        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)

        self.assertEqual(addon._state.current_skill, "Woodcutting")
        view = action_queue_view_pure(addon._state.player_data)
        self.assertFalse(view["paused"])
        self.assertTrue(view["suspended"])
        self.assertEqual(view["entries"][0]["done"], 0)

    def _paused_at_first_entry(self, name):
        addon = self._queue_addon(name, (_MINE_IRON, 30), (_SMELT_IRON, 5))
        captured = {}
        addon.ui.show_main_menu = lambda *_args, **kwargs: captured.update(kwargs)
        addon._on_main_menu()
        self.assertTrue(captured["on_stop_training"]())
        return addon

    def test_a_resume_that_fails_partway_leaves_the_entry_and_its_queue_in_step(self):
        from ankiscape.core.action_queue import action_queue_view_pure

        with self.subTest("a HUD that cannot draw does not split a start that committed"):
            addon = self._paused_at_first_entry("ankiscape_queue_resume_hud")
            with patch.object(addon, "update_review_hud", side_effect=RuntimeError("no reviewer")):
                self.assertTrue(addon.on_resume_last_action())
            self.assertEqual(addon._state.current_skill, "Mining")
            self.assertFalse(action_queue_view_pure(addon._state.player_data)["paused"])

        with self.subTest("a save that fails after the start never splits the saved entry from its queue"):
            addon = self._paused_at_first_entry("ankiscape_queue_resume_save")
            saves = []
            real_save = addon.save_player_data

            def save_once():
                saves.append(1)
                if len(saves) > 1:
                    raise OSError("disk full")
                real_save()

            with patch.object(addon, "save_player_data", side_effect=save_once):
                try:
                    addon.on_resume_last_action()
                except OSError:
                    pass
            addon.load_player_data()
            running = addon._state.current_skill == "Mining"
            self.assertEqual(running, not action_queue_view_pure(addon._state.player_data)["paused"])

    def test_a_late_reason_refines_only_the_entry_its_own_stop_passed(self):
        from ankiscape.core.action_queue import ACTION_QUEUE_KEY, action_queue_pure, pass_queue_entry_pure
        from ankiscape.core.review_event_log import record_review_event_pure

        addon = self._queue_addon(
            "ankiscape_queue_late_reason_scope",
            (_MINE_IRON, 30),
            ({"kind": "skill", "skill": "Agility", "target": "gnome_normal"}, 1),
            toolbelt={"mining": []},
            agility_level=40,
        )
        # An older Mining stop that gave no reason ended the first entry, and the player then paused Agility.
        generic = "Mining could not continue."
        older_line = f"Queue: Mining: Iron stopped · {generic}"
        player_data = record_review_event_pure(addon._state.player_data, "activity", older_line)
        queue = pass_queue_entry_pure(action_queue_pure(player_data))
        addon._state.player_data = {**player_data, ACTION_QUEUE_KEY: {**queue, "paused": True}, "current_ore": "copper"}
        addon.save_skill("Mining", None)

        self._answer(addon)

        reason = "You need a usable pickaxe to train Mining. Mining has been switched off."
        self.assertEqual(self.errors, [("Missing pickaxe", reason)])
        self.assertEqual(addon._state.player_data["last_action"]["reason"], reason)
        self.assertIn(older_line, self._log(addon))

    def test_a_stop_the_queue_takes_over_leaves_an_older_last_action_alone(self):
        addon = self._queue_addon(
            "ankiscape_queue_late_reason_last_action",
            (_MINE_IRON, 30),
            ({"kind": "skill", "skill": "Agility", "target": "gnome_normal"}, 1),
            toolbelt={"mining": []},
            agility_level=40,
        )
        # An older Mining stop that gave no reason is still the action Resume would offer.
        older = {**_MINE_IRON, "reason": "Mining could not continue."}
        addon._state.player_data["last_action"] = dict(older)

        self._answer(addon)

        self.assertEqual(addon._state.current_skill, "Agility")
        self.assertEqual(addon._state.player_data["last_action"], older)
