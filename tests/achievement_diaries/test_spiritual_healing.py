"""Spiritual Healing completes only when a Visit obelisk restores a point.

Each test drives the real Summoning handler captured from the real main-menu
wiring, the shared direct-action undo seam, the real achievement check and a
collection that round-trips the save through JSON as Anki's config store does.
Only presentation is silenced: the popup surface, HUD and skill refresh.
"""

from __future__ import annotations

import copy
import json
import sys
import types
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data
from tests.test_integration_smoke import (
    _DummyCol,
    _DummyMW,
    _install_runtime_fakes,
    _load_addon_as_package,
)


TASK_ID = "burthorpe_period_spiritual_healing"
DIRECT_ACTION_UNDO = types.SimpleNamespace(operation="AnkiScape direct action")


class _SavedCollection(_DummyCol):
    accepts_undo = True

    def get_config(self, key, default=None):
        return copy.deepcopy(super().get_config(key, default))

    def set_config(self, key, value):
        self._store[key] = json.loads(json.dumps(value))

    def add_custom_undo_entry(self, name):
        if not self.accepts_undo:
            raise RuntimeError("collection refused the undo entry")
        return super().add_custom_undo_entry(name)


class SpiritualHealingDeedTest(unittest.TestCase):
    def setUp(self) -> None:
        modules = dict(sys.modules)
        self.addCleanup(lambda: (sys.modules.clear(), sys.modules.update(modules)))
        _install_runtime_fakes()
        addon = self.addon = _load_addon_as_package("ankiscape_spiritual_healing")
        self.col = _SavedCollection({"ankiscape_floating_xp_enabled": False})
        addon.mw = _DummyMW(self.col)
        sys.modules[f"{addon.__name__}.core.storage"].mw = addon.mw
        sys.modules[f"{addon.__name__}.core.logic"]._popups_enabled = lambda: False
        addon.update_review_hud = lambda *_args, **_kwargs: None
        addon._refresh_skill_availability = lambda: None
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["summoning_level"] = 10
        addon._state.player_data = player
        addon._state.current_skill = "Summoning"
        self._set_points(3)
        addon.save_player_data()
        addon.load_player_data()
        captured = {}
        addon.ui.show_main_menu = lambda *_args, **kwargs: captured.update(kwargs)
        addon._on_main_menu(initial_skill="Summoning")
        self.on_summoning_command = captured["on_summoning_command"]

    def _player(self):
        return self.addon._state.player_data

    def _set_points(self, points: int) -> None:
        self._player()["summoning_state"]["summoning_points_current"] = points

    def _points(self) -> int:
        return self._player()["summoning_state"]["summoning_points_current"]

    def _completions(self, player=None) -> int:
        player = self._player() if player is None else player
        return player["achievement_diaries"]["completed_tasks"].count(TASK_ID)

    def _visit_obelisk(self):
        return self.on_summoning_command("restore_points", {})

    def test_a_visit_below_maximum_earns_the_deed_once_across_save_and_reopen(self):
        result = self._visit_obelisk()

        self.assertTrue(result["ok"], result)
        self.assertEqual(self._points(), 10)
        self.assertEqual(self._completions(), 1)
        self.assertEqual(self.col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(
            self._completions(self.col.get_config("ankiscape_player_data")), 1
        )
        self.addon.load_player_data()
        self.assertEqual(self._completions(), 1)
        self._set_points(4)

        self.assertTrue(self._visit_obelisk()["ok"])

        self.assertEqual(self._points(), 10)
        self.assertEqual(self._completions(), 1)
        notices = [
            row["text"]
            for row in self._player()["review_event_log"]
            if row["kind"] == "achievement" and row["text"].startswith("Spiritual Healing")
        ]
        self.assertEqual(len(notices), 1, notices)

    def test_undo_takes_the_deed_back_and_a_new_visit_earns_it_again(self):
        before = copy.deepcopy(self._player())
        self.assertTrue(self._visit_obelisk()["ok"])
        self.assertEqual(self._completions(), 1)

        self.addon._on_state_did_undo(DIRECT_ACTION_UNDO)

        self.assertEqual(self._player(), before)
        self.addon.load_player_data()
        self.assertEqual(self._points(), 3)
        self.assertEqual(self._completions(), 0)
        self.assertEqual(self._player()["achievement_diaries"]["event_counts"], {})
        self.assertTrue(self._visit_obelisk()["ok"])
        self.assertEqual(self._completions(), 1)

    def test_visits_that_restore_no_point_never_earn_the_deed(self):
        self._set_points(10)
        full = copy.deepcopy(self._player())
        saved = self.col.get_config("ankiscape_player_data")

        refused = self._visit_obelisk()

        self.assertEqual(
            refused, {"ok": False, "message": "That action is unavailable."}
        )
        self.assertEqual(self._player(), full, "a refusal must write nothing")
        self.assertEqual(self.col.custom_undo_entries, [])
        self.assertEqual(self.col.get_config("ankiscape_player_data"), saved)
        # Clamping points above the level changes state but restores nothing.
        self._set_points(12)
        self._visit_obelisk()
        self.assertEqual(self._points(), 10)
        self.assertEqual(self._completions(), 0)

    def test_a_visit_whose_undo_entry_fails_writes_nothing(self):
        before = copy.deepcopy(self._player())
        saved = self.col.get_config("ankiscape_player_data")
        self.col.accepts_undo = False

        result = self._visit_obelisk()

        self.assertEqual(
            result, {"ok": False, "message": "Anki could not create an undo entry."}
        )
        self.assertEqual(self._player(), before)
        self.assertEqual(self.col.get_config("ankiscape_player_data"), saved)
        self.assertEqual(self.addon._state.direct_action_undo_stack, [])

    def test_bank_runs_and_potions_restore_points_without_the_deed(self):
        self.addon._state.current_skill = "Farming"
        self.assertTrue(self.addon.on_do_bank_run_now())
        self.assertEqual(self._points(), 10)
        self.addon.check_achievements(self._player())
        self.assertEqual(self._completions(), 0)
        self._set_points(3)
        self._player()["inventory"]["Summoning potion (4)"] = 1

        self.assertTrue(self.addon.on_consume_item("Summoning potion (4)")["allowed"])

        self.assertEqual(self._points(), 10)
        self.addon.check_achievements(self._player())
        self.assertEqual(self._completions(), 0)


if __name__ == "__main__":
    unittest.main()
