"""Stealing Creation commands must go through the shared undo seam.

The handler used to hand-roll its snapshot, custom-undo entry and save
transaction. These tests drive the real handler through `commit_direct_action`
and assert an undo restores the pre-action state, plus that the two refusal
paths stay distinct when the seam reports a single False.
"""

from __future__ import annotations

import copy
import sys
import types
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data
from tests.test_integration_smoke import (
    _DummyCol,
    _DummyMW,
    _install_runtime_fakes,
    _load_addon_as_package,
)


class StealingCreationUndoSeamTest(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()
        self.addon = _load_addon_as_package("ankiscape_stealing_undo_seam")
        self.col = _DummyCol()
        self.addon.mw = _DummyMW(self.col)
        self.addon.save_player_data = lambda: None
        self.addon.update_review_hud = lambda *_args: None
        self.addon._refresh_skill_availability = lambda: None
        self.addon.check_achievements = lambda *_args: None
        self.addon._show_activity_gain = lambda *_args: None
        self.addon._show_quest_exp_delta = lambda *_args: None
        self.addon._state.current_skill = "Activities"
        self.initial = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        self.addon._state.player_data = copy.deepcopy(self.initial)
        captured = {}
        self.addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        self.addon._on_main_menu()
        self.command = captured["on_stealing_creation_command"]

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def _undo(self) -> None:
        self.addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )

    def test_enter_is_committed_and_undo_restores_pre_action_state(self):
        result = self.command("enter", {})
        self.assertTrue(result["ok"], result)
        self.assertEqual(self.col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertTrue(self.addon._state.player_data["stealing_creation"]["active_session"])
        self._undo()
        self.assertEqual(self.addon._state.player_data, self.initial)

    def test_pure_refusal_reports_the_refusal(self):
        result = self.command("leave", {})
        self.assertFalse(result["ok"], result)
        self.assertEqual(
            result["message"], "No Stealing Creation session is active."
        )
        self.assertEqual(self.col.custom_undo_entries, [])
        self.assertEqual(self.addon._state.player_data, self.initial)

    def test_undo_entry_failure_reports_undo_unavailable(self):
        def _raise(name):
            raise RuntimeError("collection refused the undo entry")

        self.col.add_custom_undo_entry = _raise
        result = self.command("enter", {})
        self.assertEqual(
            result,
            {
                "ok": False,
                "reason": "undo_unavailable",
                "message": "Anki could not create an undo entry.",
            },
        )
        self.assertEqual(self.addon._state.player_data, self.initial)


if __name__ == "__main__":
    unittest.main()
