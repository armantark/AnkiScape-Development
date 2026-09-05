"""The Dagannoth Kings room commands must be undoable through the shared seam.

`_apply_dagannoth_kings_command` used to hand-roll its own snapshot, undo entry
and save transaction. It now goes through `commit_direct_action`, so an undo
must restore exactly the pre-action save — and a refusal must be reported as
the pure function's refusal, while a lost undo entry must never be reported as
success.
"""

from __future__ import annotations

import copy
import sys
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data


class _RaisingCol:
    """A collection whose undo-entry registration always fails."""

    def add_custom_undo_entry(self, name):
        raise RuntimeError("collection refused the undo entry")


class _DummyMW:
    def __init__(self, col):
        self.col = col

    def update_undo_actions(self):
        pass


class UndoSeamDagannothTest(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_modules = dict(sys.modules)
        from tests.test_integration_smoke import (
            _install_runtime_fakes,
            _load_addon_as_package,
        )

        _install_runtime_fakes()
        self.addon = _load_addon_as_package("ankiscape_undo_seam_dagannoth")
        self.addon._state.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        self.saves = []
        self.addon.save_player_data = lambda: self.saves.append(True)
        self.addon.mw = _DummyMW(type("C", (), {"add_custom_undo_entry": lambda self, name: 1})())
        self.addon.check_achievements = lambda *_args: None
        self.addon._refresh_skill_availability = lambda: None
        self.addon._show_activity_gain = lambda *_args: None
        self.addon.update_review_hud = lambda *_args: None
        self.addon._state.current_skill = "Activities"
        # The handler is nested inside _on_main_menu; capture it the way the
        # smoke tests do, through the menu factory's keyword arguments.
        captured = {}
        self.addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        self.addon._on_main_menu()
        self.handler = captured["on_dagannoth_kings_command"]

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_enter_is_undoable_and_restores_pre_action_state(self):
        addon = self.addon
        before = copy.deepcopy(dict(addon._state.player_data))

        result = self.handler("enter", {})

        self.assertTrue(result["ok"], result)
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)
        self.assertEqual(len(self.saves), 1)
        self.assertTrue(addon._state.player_data["dagannoth_kings"]["active"])
        self.assertEqual(
            addon._state.player_data["activity_session"],
            {"active_id": "dagannoth_kings"},
        )

        addon._restore_direct_action_snapshot(addon._state.direct_action_undo_stack.pop())
        self.assertEqual(dict(addon._state.player_data), before)

    def test_refused_action_reports_the_pure_refusal(self):
        addon = self.addon
        # A persistent activity is already active, so "enter" refuses.
        addon._state.player_data["activity_session"] = {"active_id": "cooking"}

        result = self.handler("enter", {})

        self.assertFalse(result["ok"])
        self.assertEqual(result["message"], "Another persistent activity is active.")
        self.assertEqual(addon._state.direct_action_undo_stack, [])
        self.assertEqual(self.saves, [])

    def test_lost_undo_entry_reports_undo_unavailable_not_success(self):
        addon = self.addon
        addon.mw = _DummyMW(_RaisingCol())
        before = copy.deepcopy(dict(addon._state.player_data))

        result = self.handler("enter", {})

        self.assertEqual(
            result,
            {
                "ok": False,
                "reason": "undo_unavailable",
                "message": "Anki could not create an undo entry.",
            },
            "a successful pure result without an undo entry must not be reported as success",
        )
        self.assertEqual(dict(addon._state.player_data), before)
        self.assertEqual(addon._state.direct_action_undo_stack, [])
        self.assertEqual(self.saves, [])


if __name__ == "__main__":
    unittest.main()
