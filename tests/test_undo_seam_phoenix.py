"""The Phoenix Lair menu commands must be undoable through the shared seam.

`_apply_phoenix_lair_command` used to hand-roll its own snapshot, custom-undo
entry and save transaction. It now goes through `commit_direct_action` like
every other migrated handler, so a Ctrl+Z after a Lair command restores the
whole save and the random state. These tests drive the REAL handler through the
REAL seam; only side-effect collaborators (HUD, achievements, dialogs) are
stubbed.
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
    return _load_addon_as_package("ankiscape_undo_seam_phoenix")


def _ready_player_data(addon):
    """A save that passes every gate on the Lair's `enter` command."""
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data["quests"]["in_pyre_need"] = {
        "started": True,
        "progress": 1,
        "completed": True,
    }
    data.update(
        {
            "slayer_level": 99,
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "magic_level": 99,
            "ranged_level": 99,
            "combat_lifepoints": 990,
        }
    )
    data["inventory"].update({"Knife": 1, "Secateurs": 1, "Tinderbox": 1})
    data["carried_advanced_targets"]["phoenix_lair"] = True
    data["carried_layout"]["phoenix_lair"] = {
        "Knife": 1,
        "Secateurs": 1,
        "Tinderbox": 1,
    }
    return data


class UndoSeamPhoenixTest(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_modules = dict(sys.modules)
        self.addon = _load_addon()
        self.addon.player_data = _ready_player_data(self.addon)
        self.addon.current_skill = "Activities"
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
        self.command = captured["on_phoenix_lair_command"]

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

        before = copy.deepcopy(addon.player_data)
        before_random = random.getstate()
        before_stack_depth = len(addon._DIRECT_ACTION_UNDO_STACK)

        result = self.command("enter", {})

        self.assertTrue(result["ok"], result)
        self.assertEqual(addon.player_data["phoenix_lair"]["phase"], "guardians")
        self.assertEqual(col.entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._DIRECT_ACTION_UNDO_STACK), before_stack_depth + 1)
        self.assertEqual(len(self.saves), 1, "a committed change must persist")
        self.assertNotEqual(addon.player_data, before)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="ankiscape direct action")
        )

        self.assertEqual(addon.player_data, before)
        self.assertEqual(random.getstate(), before_random)

    def test_refused_command_reports_the_pure_refusal(self):
        addon = self.addon
        addon.player_data["activity_session"] = {"active_id": "something_else"}

        class _Col:
            def add_custom_undo_entry(self, name):
                self.fail("a refusal must never reach the undo entry")

        self._install_collection(_Col())

        result = self.command("enter", {})

        self.assertFalse(result["ok"])
        self.assertIn("Another persistent activity is active.", result["message"])

    def test_undo_entry_failure_reports_undo_unavailable_not_success(self):
        addon = self.addon
        self._install_collection(_RaisingCol())

        result = self.command("enter", {})

        self.assertEqual(
            result,
            {"ok": False, "message": "Anki could not create an undo entry."},
        )
        self.assertEqual(len(self.saves), 0, "nothing may be written or saved")
        self.assertEqual(
            addon.player_data["phoenix_lair"].get("phase"),
            "idle",
            "the failed action must not start a run",
        )
