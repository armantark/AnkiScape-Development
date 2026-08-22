"""The penguin hide-and-seek handler must go through the shared undo seam.

`_apply_penguin_command` in `__init__.py` used to hand-roll its own snapshot,
custom-undo entry and save transaction. It now delegates to
`commit_direct_action`, so a penguin command is undoable through Anki's Ctrl+Z
like every other menu mutation, and its refusal path reports the penguin
refusal rather than a fake success when no undo entry could be created.
"""

from __future__ import annotations

import copy
import sys
import types
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)


class _RefusingCollection:
    def add_custom_undo_entry(self, name):
        raise RuntimeError("collection refused the undo entry")


class _DummyMW:
    def __init__(self, col):
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
    return _load_addon_as_package("ankiscape_undo_seam_penguin")


def _wire_penguin(addon, col):
    """Install the runtime state and stubbed side-effect collaborators."""
    penguin_logic = sys.modules[
        f"{addon.__name__}.logic.penguin_hide_and_seek_logic"
    ]
    captured = {}
    addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
    addon.mw = _DummyMW(col)
    addon.current_skill = "Activities"
    initial = {
        "inventory": {},
        "penguin_hide_and_seek": penguin_logic.default_penguin_state_pure(),
        "completed_achievements": [],
        "smithing_level": 1,
    }
    initial["penguin_hide_and_seek"]["points"] = 2
    addon.player_data = copy.deepcopy(initial)
    addon.save_player_data = lambda: None
    addon.update_review_hud = lambda *_args: None
    addon._refresh_skill_availability = lambda: None
    addon._show_activity_gain = lambda _message: None
    addon._show_quest_exp_delta = lambda _delta: None
    addon.check_achievements = lambda *_args: None
    addon._on_main_menu()
    return initial, captured["on_penguin_command"]


class PenguinUndoSeamTest(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_modules = dict(sys.modules)
        self.addon = _load_addon()

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_redeem_coins_is_undoable_through_the_seam(self):
        addon = self.addon
        col = addon._FakeCollectionForPenguin = type(
            "_Col", (), {
                "custom_undo_entries": [],
                "add_custom_undo_entry": (
                    lambda self, name: self.custom_undo_entries.append(name)
                ),
            },
        )()
        initial, command = _wire_penguin(addon, col)

        result = command("redeem_coins", {})

        self.assertTrue(result["ok"])
        self.assertEqual(addon.player_data["inventory"]["Coins"], 13_000)
        self.assertEqual(addon.player_data["penguin_hide_and_seek"]["points"], 0)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._DIRECT_ACTION_UNDO_STACK), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon.player_data, initial)
        self.assertEqual(addon._DIRECT_ACTION_UNDO_STACK, [])

    def test_a_refused_command_reports_the_penguin_refusal(self):
        addon = self.addon
        col = type(
            "_Col", (), {
                "custom_undo_entries": [],
                "add_custom_undo_entry": (
                    lambda self, name: self.custom_undo_entries.append(name)
                ),
            },
        )()
        initial, command = _wire_penguin(addon, col)
        addon.player_data["penguin_hide_and_seek"]["points"] = 0
        initial["penguin_hide_and_seek"]["points"] = 0

        result = command("redeem_coins", {})

        self.assertFalse(result["ok"])
        self.assertEqual(addon.player_data, initial)
        self.assertEqual(col.custom_undo_entries, [])

    def test_undo_unavailable_reports_failure_not_success(self):
        addon = self.addon
        initial, command = _wire_penguin(addon, _RefusingCollection())

        result = command("redeem_coins", {})

        self.assertEqual(
            result,
            {"ok": False, "message": "Anki could not create an undo entry."},
        )
        self.assertEqual(addon.player_data, initial)


if __name__ == "__main__":
    unittest.main()
