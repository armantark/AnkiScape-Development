"""The Wicked hood menu commands must be undoable through the shared seam.

`_apply_wicked_hood_command` used to hand-roll its own snapshot, custom-undo
entry and save transaction. It now goes through `commit_direct_action` like
every other migrated handler, so a Ctrl+Z after a hood command restores the
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
    return _load_addon_as_package("ankiscape_undo_seam_wickedhood")


def _ready_player_data():
    """A save that passes every gate on the Wicked hood `essence` command."""
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data["quests"]["rune_mysteries"] = {
        "started": True,
        "progress": 6,
        "completed": True,
    }
    data["claims"]["wicked_hood"] = {"claimed": True}
    data["equipment"] = {"head": "Wicked hood"}
    data["current_runecrafting"] = "craft_air_runes"
    return data


class UndoSeamWickedHoodTest(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_modules = dict(sys.modules)
        self.addon = _load_addon()
        self.addon.player_data = _ready_player_data()
        self.addon.current_skill = "Runecrafting"
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
        self.command = captured["on_wicked_hood_command"]

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def _install_collection(self, col):
        self.addon.mw = _DummyMW(col)

    def test_essence_is_undoable_and_restores_the_whole_save(self):
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

        result = self.command("essence", {})

        self.assertTrue(result["ok"], result)
        self.assertEqual(addon.player_data["inventory"]["Rune essence"], 28)
        self.assertEqual(col.entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._DIRECT_ACTION_UNDO_STACK), before_stack_depth + 1)
        self.assertEqual(len(self.saves), 1, "a committed change must persist")
        self.assertNotEqual(addon.player_data, before)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="ankiscape direct action")
        )

        self.assertEqual(addon.player_data, before)
        self.assertEqual(random.getstate(), before_random)

    def test_refused_command_reports_the_refusal_and_writes_nothing(self):
        addon = self.addon
        # Fill every free carried-pack slot so `essence` is refused by the pure
        # function for lack of space.
        addon.player_data["inventory"]["Shark"] = 28
        addon.player_data["carried_inventory"]["craft_air_runes"] = {"Shark": 28}

        # A WORKING recording col, not a raising one: if a broken migration
        # commits a refused change, the corruption must be visible as an undo
        # entry plus a save, not masked by an unrelated failure.
        class _Col:
            def __init__(self):
                self.entries = []

            def add_custom_undo_entry(self, name):
                self.entries.append(name)

        col = _Col()
        self._install_collection(col)

        before = copy.deepcopy(addon.player_data)
        result = self.command("essence", {})

        self.assertFalse(result["ok"])
        self.assertIn("No carried-pack space", result["message"])
        self.assertEqual(
            addon.player_data,
            before,
            "a refused action must write nothing",
        )
        self.assertEqual(len(self.saves), 0, "a refused action must save nothing")
        self.assertEqual(col.entries, [], "a refused action must not create an undo entry")

    def test_undo_entry_failure_reports_undo_unavailable_not_success(self):
        addon = self.addon
        self._install_collection(_RaisingCol())

        result = self.command("essence", {})

        self.assertEqual(
            result,
            {"ok": False, "message": "Anki could not create an undo entry."},
        )
        self.assertEqual(len(self.saves), 0, "nothing may be written or saved")
        self.assertEqual(
            addon.player_data["inventory"]["Rune essence"],
            0,
            "the failed action must not withdraw essence",
        )
        self.assertNotIn(
            "Rune essence",
            addon.player_data["carried_inventory"].get("craft_air_runes", {}),
            "the failed action must not carry essence",
        )
