"""The TzHaar Fight Pit menu commands must be undoable through the shared seam.

`_apply_tzhaar_fight_pit_command` used to hand-roll its own snapshot,
custom-undo entry and save transaction. It now goes through
`commit_direct_action` like every other migrated handler, so a Ctrl+Z after a
Fight Pit command restores the whole save and the random state. These tests
drive the REAL handler through the REAL seam; only side-effect collaborators
(HUD, achievements, dialogs) are stubbed.
"""

from __future__ import annotations

import copy
import random
import sys
import types
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


def _load_addon():
    from tests.test_integration_smoke import (
        _install_runtime_fakes,
        _load_addon_as_package,
    )

    _install_runtime_fakes()
    return _load_addon_as_package("ankiscape_undo_seam_fightpit")


def _ready_player_data(addon):
    """A save that passes every gate on the pit's `enter` command."""
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data.update(
        {
            "attack_level": 60,
            "strength_level": 60,
            "defense_level": 60,
            "constitution_level": 60,
            "combat_lifepoints": 600,
        }
    )
    return data


class UndoSeamFightPitTest(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_modules = dict(sys.modules)
        self.addon = _load_addon()
        self.addon._state.player_data = _ready_player_data(self.addon)
        self.addon._state.current_skill = "Activities"
        self.saves = []
        self.addon.save_player_data = lambda: self.saves.append(True)
        self.addon.mw = _DummyMW(types.SimpleNamespace())
        # Stub every side-effect collaborator; none may open a dialog.
        self.addon.check_achievements = lambda *_args: None
        self.addon._refresh_skill_availability = lambda: None
        self.addon._show_activity_gain = lambda *_args: None
        self.addon.update_review_hud = lambda *_args: None

        captured = {}
        addon = self.addon
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon._on_main_menu()
        self.command = captured["on_tzhaar_fight_pit_command"]

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def _install_collection(self, col):
        self.addon.mw = _DummyMW(col)

    def test_enter_is_undoable_and_restores_the_whole_save(self):
        addon = self.addon

        class _Col:
            def __init__(self):
                self.entries = []

            def add_custom_undo_entry(self, name):
                self.entries.append(name)

        col = _Col()
        self._install_collection(col)

        before = copy.deepcopy(addon._state.player_data)
        before_random = random.getstate()
        before_stack_depth = len(addon._state.direct_action_undo_stack)

        result = self.command("enter", {})

        self.assertTrue(result["ok"], result)
        self.assertTrue(addon._state.player_data["tzhaar_fight_pit"])
        self.assertEqual(
            addon._state.player_data["activity_session"]["active_id"],
            "tzhaar_fight_pit",
        )
        self.assertEqual(col.entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), before_stack_depth + 1)
        self.assertEqual(len(self.saves), 1, "a committed change must persist")
        self.assertNotEqual(addon._state.player_data, before)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="ankiscape direct action")
        )

        self.assertEqual(addon._state.player_data, before)
        self.assertEqual(random.getstate(), before_random)

    def test_refused_command_writes_and_saves_nothing(self):
        addon = self.addon

        entries = []

        class _Col:
            def add_custom_undo_entry(self, name):
                # Record rather than raise: an exception here unwinds
                # commit_direct_action before anything is written, which makes
                # the write-nothing assertions below pass vacuously.
                entries.append(name)

        self._install_collection(_Col())
        addon._state.player_data["activity_session"] = {"active_id": "something_else"}
        before = copy.deepcopy(addon._state.player_data)

        result = self.command("enter", {})

        self.assertFalse(result["ok"])
        self.assertIn(
            "Finish the active persistent activity first.", result["message"]
        )
        self.assertEqual(entries, [], "a refusal must never reach the undo entry")
        # The half that kills the "commit anyway" mutant: assert NOTHING was
        # written and nothing was saved, not just that a message came back.
        self.assertEqual(addon._state.player_data, before, "a refusal must write nothing")
        self.assertEqual(len(self.saves), 0, "a refusal must save nothing")

    def test_undo_entry_failure_reports_undo_unavailable_not_success(self):
        addon = self.addon
        self._install_collection(_RaisingCol())
        before = copy.deepcopy(addon._state.player_data)

        result = self.command("enter", {})

        self.assertFalse(result["ok"])
        self.assertEqual(result["message"], "Anki could not create an undo entry.")
        self.assertEqual(len(self.saves), 0, "nothing may be written or saved")
        self.assertEqual(
            addon._state.player_data,
            before,
            "the failed action must not start a match",
        )


if __name__ == "__main__":
    unittest.main()
