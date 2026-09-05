"""The Stronghold player-safety handler must go through the shared undo seam.

`_apply_stronghold_player_safety_command` in `__init__.py` used to hand-roll
its own snapshot, custom-undo entry and save transaction. It now delegates to
`commit_direct_action`, so a stronghold action is undoable through Anki's
Ctrl+Z like every other menu mutation, and its refusal path reports the
stronghold refusal while writing and saving nothing.
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
    return _load_addon_as_package("ankiscape_undo_seam_stronghold")


def _wire_stronghold(addon, col):
    """Install runtime state and stubbed side-effect collaborators."""
    captured = {}
    addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
    addon.mw = _DummyMW(col)
    addon._state.current_skill = "Activities"
    initial = {
        "inventory": {},
        "equipment": {},
        "combat_grave": {},
        "death_office": {},
        "smithing_level": 1,
        "stronghold_player_safety": {
            "version": 2,
            "stage": 3,
            "crevice_unlocked": True,
            "chest_claimed": False,
            "safety_first_emote_unlocked": False,
            "last_result": "Reached the reward passage.",
        },
    }
    addon._state.player_data = copy.deepcopy(initial)
    addon.save_calls = []
    addon.save_player_data = lambda: addon.save_calls.append(1)
    addon.update_review_hud = lambda *_args: None
    addon._refresh_skill_availability = lambda: None
    addon._show_activity_gain = lambda _message: None
    addon._show_quest_exp_delta = lambda _delta: None
    addon.level_up_check = lambda *_args: None
    # An unstubbed achievement dialog opens a modal nothing can click under
    # the offscreen Qt lane; stub it like every sibling suite does.
    addon.check_achievements = lambda *_args: None
    addon._on_main_menu()
    return initial, captured["on_stronghold_player_safety_command"]


class StrongholdUndoSeamTest(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_modules = dict(sys.modules)
        self.addon = _load_addon()

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_claim_chest_is_undoable_through_the_seam(self):
        addon = self.addon
        col = type(
            "_Col", (), {
                "custom_undo_entries": [],
                "add_custom_undo_entry": (
                    lambda self, name: self.custom_undo_entries.append(name)
                ),
            },
        )()
        initial, command = _wire_stronghold(addon, col)

        result = command("claim_chest", {})

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 10_000)
        self.assertEqual(addon._state.player_data["inventory"]["Safety gloves"], 1)
        state = addon._state.player_data["stronghold_player_safety"]
        self.assertTrue(state["chest_claimed"])
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_the_retired_lamp_command_reports_refusal_and_writes_nothing(self):
        addon = self.addon
        col = type(
            "_Col", (), {
                "custom_undo_entries": [],
                "add_custom_undo_entry": (
                    lambda self, name: self.custom_undo_entries.append(name)
                ),
            },
        )()
        initial, command = _wire_stronghold(addon, col)

        result = command("claim_lamp", {"skill_id": "smithing"})

        self.assertFalse(result["ok"])
        self.assertIn("Unknown Stronghold command", result["message"])
        # Nothing was written or saved: the refused state must not leak.
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon.save_calls, [])
        self.assertEqual(col.custom_undo_entries, [])
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_undo_unavailable_reports_failure_not_success(self):
        addon = self.addon
        initial, command = _wire_stronghold(
            addon, _RefusingCollection()
        )

        result = command("claim_chest", {})

        self.assertEqual(
            result,
            {"ok": False, "message": "Anki could not create an undo entry."},
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon.save_calls, [])


if __name__ == "__main__":
    unittest.main()
