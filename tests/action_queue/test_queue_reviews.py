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


class ActionQueueReviewTest(fixtures.ReviewedProfile):
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
            self.assertTrue(add_to_action_queue(addon, action, count))
        return addon

    def _rows(self, addon):
        from ankiscape.core.action_queue import action_queue_view_pure

        return [(row["name"], row["state"], row["done"]) for row in action_queue_view_pure(addon._state.player_data)["entries"]]

    def _log(self, addon):
        return [row["text"] for row in addon._state.player_data["review_event_log"] if row["kind"] != "achievement"]

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
                self._rows(addon),
                [("Mining: Iron", "done", 10), ("Smithing: Iron bar", "current", 0), ("Smithing: Iron platebody", "waiting", 0)],
            )

            self._answer(addon)
            self.assertEqual(self._rows(addon)[1], ("Smithing: Iron bar", "current", 10))

            # Ten ore made ten bars; the eleventh smelt finds no ore.
            self._answer(addon)
            self.assertEqual(addon._state.player_data["current_smith"], "forge_iron_platebody")
            self.assertEqual(self.bankstanding_dialogs, [])

            self._answer(addon)

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")
        self.assertEqual(self.bankstanding_dialogs, ["The queue is finished: Smithing: Iron platebody done."])
        self.assertEqual(addon._state.player_data["inventory"]["Iron platebody"], 2)
        self.assertEqual(
            self._log(addon),
            [
                "+350 XP · Mining · +10 Iron ore",
                "Queue: Mining: Iron done",
                "+125 XP · Smithing · +10 Iron bar · −10 Iron ore",
                "Queue: Smithing: Iron bar stopped · You need 1 Iron ore to make Iron bar.",
                "+250 XP · Smithing · +2 Iron platebody · −10 Iron bar",
                "Switched to Bankstanding · The queue is finished: Smithing: Iron platebody done.",
            ],
        )
        self.assertEqual(
            self._rows(addon),
            [("Mining: Iron", "done", 10), ("Smithing: Iron bar", "stopped", 10), ("Smithing: Iron platebody", "done", 2)],
        )
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

        self.assertEqual([title for title, _message in self.errors], ["Quest blocked"])
        self.assertEqual(addon._state.current_skill, "Mining")
        self.assertEqual(self._log(addon)[-1], "Queue: Black Knights' Fortress stopped · Needs Iron chainbody")
        self.assertEqual(self.bankstanding_dialogs, [])
        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)
        self.assertEqual(self._rows(addon)[1], ("Mining: Iron", "current", 10))

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

        self.assertTrue(clear_action_queue(addon))
        self.assertEqual(action_queue_view_pure(addon._state.player_data)["entries"], [])
        self.assertEqual(addon._state.current_skill, "Mining")

    def test_an_action_the_player_starts_himself_pauses_the_queue(self):
        from ankiscape.core.action_queue import action_queue_view_pure

        addon = self._queue_addon("ankiscape_queue_takeover", (_MINE_IRON, 30), woodcutting_level=40)
        addon.save_skill("Woodcutting", None)

        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)

        self.assertEqual(addon._state.current_skill, "Woodcutting")
        view = action_queue_view_pure(addon._state.player_data)
        self.assertTrue(view["paused"])
        self.assertEqual(view["entries"][0]["done"], 0)
