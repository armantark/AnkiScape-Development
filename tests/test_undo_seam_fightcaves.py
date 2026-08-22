"""The Fight Caves handler must go through the shared undo seam.

Before the migration `_apply_fight_caves_command` hand-rolled its own snapshot,
custom-undo entry and save transaction, exactly the pattern the first wave found
in thirty-two handlers. These tests drive the real handler through
`commit_direct_action` and assert undo restores the pre-action state, plus that
a failed `add_custom_undo_entry` reports `undo_unavailable` rather than a
success payload.
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
        self.undo_updates = 0

    def update_undo_actions(self):
        self.undo_updates += 1


def _load_addon():
    from tests.test_integration_smoke import (
        _install_runtime_fakes,
        _load_addon_as_package,
    )

    _install_runtime_fakes()
    return _load_addon_as_package("ankiscape_undo_seam_fightcaves")


class FightCavesUndoSeamTest(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_modules = dict(sys.modules)
        self.addon = _load_addon()
        self.addon.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        self.saves = []
        self.addon.save_player_data = lambda: self.saves.append(True)
        self.collection = _FakeCollection()
        self.addon.mw = _DummyMW(self.collection)
        # Stub side-effect collaborators only; the seam and handler stay real.
        self.gains = []
        self.addon._show_activity_gain = lambda message: self.gains.append(
            message
        )
        self.addon._refresh_skill_availability = lambda: None
        self.huds = []
        self.addon.update_review_hud = lambda *args: self.huds.append(args)

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def _handler(self):
        captured = {}
        def _capture(*args, **kwargs):
            captured.update(kwargs)

        self.addon.ui.show_main_menu = _capture
        self.addon._on_main_menu()
        handler = captured.get("on_fight_caves_command")
        self.assertIsNotNone(handler, "menu wiring lost on_fight_caves_command")
        return handler

    def test_enter_commits_through_the_seam_and_undo_restores_state(self):
        addon = self.addon
        handler = self._handler()
        before = copy.deepcopy(dict(addon.player_data))
        stack_depth = len(addon._DIRECT_ACTION_UNDO_STACK)

        result = handler("enter", {})

        self.assertTrue(result["ok"], f"enter refused: {result}")
        state = addon.player_data["fight_caves"]
        self.assertTrue(state["active"])
        self.assertEqual(state["wave"], 1)
        self.assertEqual(self.collection.entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._DIRECT_ACTION_UNDO_STACK), stack_depth + 1)
        self.assertEqual(len(self.saves), 1)
        self.assertEqual(len(self.gains), 1)

        addon._restore_direct_action_snapshot(
            addon._DIRECT_ACTION_UNDO_STACK.pop()
        )
        self.assertEqual(dict(addon.player_data), before)
        self.assertFalse(addon.player_data["fight_caves"]["active"])

    def test_refused_action_returns_the_pure_reason_and_writes_nothing(self):
        addon = self.addon
        handler = self._handler()
        addon.player_data["combat_encounter"] = {"enemy_id": "rock"}
        before = copy.deepcopy(dict(addon.player_data))

        result = handler("enter", {})

        self.assertEqual(
            result,
            {
                "ok": False,
                "message": "Finish or leave the current Combat encounter first.",
            },
        )
        self.assertEqual(dict(addon.player_data), before, "refusal wrote state")
        self.assertEqual(self.collection.entries, [])
        self.assertEqual(self.saves, [])

    def test_failed_undo_entry_reports_undo_unavailable_not_success(self):
        addon = self.addon
        handler = self._handler()
        self.collection.accepts = False
        before = copy.deepcopy(dict(addon.player_data))

        result = handler("enter", {})

        self.assertEqual(
            result,
            {
                "ok": False,
                "reason": "undo_unavailable",
                "message": "Anki could not create an undo entry.",
            },
        )
        self.assertEqual(dict(addon.player_data), before, "nothing was written")
        self.assertEqual(self.saves, [])


if __name__ == "__main__":
    unittest.main()
