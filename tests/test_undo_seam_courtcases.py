"""The Court Cases command handler must go through the shared undo seam.

Before this migration `_apply_court_cases_command` hand-rolled its own snapshot,
undo entry and save, duplicating `commit_direct_action`. These tests drive the
real handler through the real seam: a committed action must register an undo
entry, and undoing it must restore the pre-action save exactly.
"""

from __future__ import annotations

import copy
import sys
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data


class _FakeCollection:
    def __init__(self, accepts: bool = True) -> None:
        self.accepts = accepts
        self.entries: list[str] = []

    def add_custom_undo_entry(self, name: str) -> None:
        if not self.accepts:
            raise RuntimeError("collection refused the undo entry")
        self.entries.append(name)


class _DummyMW:
    def __init__(self, col) -> None:
        self.col = col

    def update_undo_actions(self) -> None:
        pass


class CourtCasesUndoSeamTest(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_modules = dict(sys.modules)
        from tests.test_integration_smoke import (
            _install_runtime_fakes,
            _load_addon_as_package,
        )

        _install_runtime_fakes()
        self.addon = _load_addon_as_package("ankiscape_undo_seam_courtcases")
        self.addon._state.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        self.saves = []
        self.addon.save_player_data = lambda: self.saves.append(True)
        # Stub the modal achievement dialog: an unstubbed one hung the Qt lane.
        self.achievement_calls = []
        self.addon.check_achievements = lambda data: self.achievement_calls.append(True)
        self.collection = _FakeCollection()
        self.addon.mw = _DummyMW(self.collection)

    def _handler(self):
        """Open the real main menu and capture the real Court Cases handler."""
        captured = {}
        self.addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        self.addon._on_main_menu(initial_skill="Court Cases")
        return captured["on_court_cases_command"]

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_set_policy_is_undoable_through_the_seam(self):
        addon = self.addon
        before = copy.deepcopy(addon._state.player_data)
        before_depth = len(addon._state.direct_action_undo_stack)

        result = self._handler()("set_policy", {"role": "defence", "automation_mode": "advanced"})

        self.assertTrue(result["ok"], result)
        self.assertEqual(len(self.collection.entries), 1)
        self.assertEqual(len(addon._state.direct_action_undo_stack), before_depth + 1)
        self.assertEqual(len(self.saves), 1)
        self.assertEqual(
            addon._state.player_data["court_cases_policy"],
            {"role": "defence", "automation_mode": "advanced"},
        )

        # Undo restores exactly the pre-action save.
        addon._state.player_data.clear()
        addon._state.player_data.update(addon._state.direct_action_undo_stack[-1]["player_data"])
        self.assertEqual(addon._state.player_data, before)

    def test_refused_action_returns_the_pure_refusal(self):
        result = self._handler()("set_policy", {"role": "bogus", "automation_mode": "casual"})

        self.assertFalse(result["ok"])
        self.assertEqual(result["message"], "Choose Prosecute or Defend.")
        self.assertEqual(self.collection.entries, [])
        self.assertEqual(self.saves, [])

    def test_undo_entry_failure_reports_undo_unavailable(self):
        self.collection.accepts = False
        before = copy.deepcopy(self.addon._state.player_data)

        result = self._handler()("set_policy", {"role": "defence", "automation_mode": "advanced"})

        self.assertEqual(
            result,
            {"ok": False, "message": "Anki could not create an undo entry."},
        )
        self.assertEqual(self.addon._state.player_data, before, "nothing may be written")
        self.assertEqual(self.saves, [])


if __name__ == "__main__":
    unittest.main()
