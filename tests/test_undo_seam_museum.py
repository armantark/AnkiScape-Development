"""The Varrock Museum handler must go through the shared undo seam.

`_apply_varrock_museum_command` in `__init__.py` used to hand-roll its own
snapshot, custom-undo entry and save transaction. It now delegates to
`commit_direct_action`, so a museum command is undoable through Anki's Ctrl+Z,
a refusal writes and saves nothing, and a failed undo entry reports failure
rather than a fake success.
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
    return _load_addon_as_package("ankiscape_undo_seam_museum")


def _wire_museum(addon, col):
    """Install the runtime state and stubbed side-effect collaborators."""
    museum_logic = sys.modules[
        f"{addon.__name__}.logic.varrock_museum_logic"
    ]
    captured = {}
    addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
    addon.mw = _DummyMW(col)
    addon._state.current_skill = "Activities"
    initial = {
        "inventory": {},
        "varrock_museum": museum_logic.default_varrock_museum_state_pure(),
        "completed_achievements": [],
    }
    addon._state.player_data = copy.deepcopy(initial)
    addon.save_player_data = lambda: None
    addon.update_review_hud = lambda *_args: None
    addon._refresh_skill_availability = lambda: None
    addon._show_activity_gain = lambda _message: None
    addon._show_quest_exp_delta = lambda _delta: None
    addon.check_achievements = lambda *_args: None
    addon.get_skill = lambda _skill_id: None
    addon.level_up_check = lambda *_args: None
    addon._on_main_menu()
    return initial, captured["on_varrock_museum_command"]


class MuseumUndoSeamTest(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_modules = dict(sys.modules)
        self.addon = _load_addon()

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_take_cleaning_kit_is_undoable_through_the_seam(self):
        addon = self.addon
        col = addon._FakeCollectionForMuseum = type(
            "_Col", (), {
                "custom_undo_entries": [],
                "add_custom_undo_entry": (
                    lambda self, name: self.custom_undo_entries.append(name)
                ),
            },
        )()
        initial, command = _wire_museum(addon, col)

        result = command("take_cleaning_kit", {})

        self.assertTrue(result["ok"])
        for item_name in ("Trowel", "Rock pick", "Specimen brush"):
            self.assertEqual(addon._state.player_data["inventory"][item_name], 1)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_a_refused_command_writes_and_saves_nothing(self):
        addon = self.addon
        col = type(
            "_Col", (), {
                "custom_undo_entries": [],
                "add_custom_undo_entry": (
                    lambda self, name: self.custom_undo_entries.append(name)
                ),
            },
        )()
        initial, command = _wire_museum(addon, col)
        # The rack is already complete, so the pure function refuses.
        addon._state.player_data["inventory"] = {
            "Trowel": 1,
            "Rock pick": 1,
            "Specimen brush": 1,
            "Leather gloves": 1,
            "Leather boots": 1,
        }
        initial["inventory"] = copy.deepcopy(addon._state.player_data["inventory"])
        saved = []
        addon.save_player_data = lambda: saved.append(True)

        result = command("take_cleaning_kit", {})

        self.assertFalse(result["ok"])
        self.assertIn("already have", result["message"])
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(col.custom_undo_entries, [])
        self.assertEqual(saved, [])
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_undo_unavailable_reports_failure_not_success(self):
        addon = self.addon
        initial, command = _wire_museum(addon, _RefusingCollection())
        saved = []
        addon.save_player_data = lambda: saved.append(True)

        result = command("take_cleaning_kit", {})

        self.assertEqual(
            result,
            {"ok": False, "message": "Anki could not create an undo entry."},
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(saved, [])


if __name__ == "__main__":
    unittest.main()
