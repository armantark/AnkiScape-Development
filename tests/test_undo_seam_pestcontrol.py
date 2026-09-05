"""Pest Control commands must go through the shared undo seam, like every other
mutation. Drives the REAL handler (captured from _on_main_menu) through the REAL
commit_direct_action and asserts an undo restores the pre-action state."""

from __future__ import annotations

import copy
import sys
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data
from tests.test_integration_smoke import _DummyCol, _DummyMW


def _load_addon():
    from tests.test_integration_smoke import (
        _install_runtime_fakes,
        _load_addon_as_package,
    )

    _install_runtime_fakes()
    return _load_addon_as_package("ankiscape_undo_seam_pestcontrol")


def _ready_player() -> dict:
    from ankiscape.data.conquest_data import CONQUEST_DEFLECTOR_RATING

    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player["pest_control_commendations"] = 500
    player["conquest_rating"] = CONQUEST_DEFLECTOR_RATING
    return player


class PestControlUndoSeamTest(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_modules = dict(sys.modules)
        self.addon = _load_addon()
        captured = {}
        self.addon.ui.show_main_menu = lambda *a, **kw: captured.update(kw)
        self.addon.save_player_data = lambda: None
        # Side-effect collaborators: stubbed so no UI or dialog is opened.
        self.addon.update_review_hud = lambda *_args: None
        self.addon._refresh_skill_availability = lambda: None
        self.gains = []
        self.addon._show_activity_gain = self.gains.append
        self.addon.check_achievements = lambda _data: None
        self.col = _DummyCol()
        self.addon.mw = _DummyMW(self.col)
        self.addon._state.player_data = _ready_player()
        self.before = copy.deepcopy(self.addon._state.player_data)
        self.addon._on_main_menu()
        self.handler = captured["on_pest_control_command"]

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_buy_deflector_commits_and_undo_restores_state(self):
        from ankiscape.data.conquest_data import CONQUEST_DEFLECTOR_ITEM

        result = self.handler("buy_void_knight_deflector", {})

        self.assertTrue(result["ok"], result)
        addon = self.addon
        self.assertEqual(addon._state.player_data["pest_control_commendations"], 350)
        self.assertEqual(addon._state.player_data["inventory"][CONQUEST_DEFLECTOR_ITEM], 1)
        self.assertEqual(self.col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertTrue(self.gains, "the purchase feedback message must still show")

        addon._restore_direct_action_snapshot(addon._state.direct_action_undo_stack.pop())
        self.assertEqual(addon._state.player_data["pest_control_commendations"], 500)
        self.assertEqual(addon._state.player_data["inventory"][CONQUEST_DEFLECTOR_ITEM], 0)

    def test_refused_command_returns_the_pure_refusal_and_writes_nothing(self):
        result = self.handler("no_such_action", {})

        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "Unknown Pest Control command.")
        self.assertEqual(dict(self.addon._state.player_data), self.before)
        self.assertEqual(self.col.custom_undo_entries, [])

    def test_accepted_but_no_undo_entry_reports_undo_unavailable(self):
        col = _DummyCol()
        col.add_custom_undo_entry = lambda name: (_ for _ in ()).throw(
            RuntimeError("collection refused the undo entry")
        )
        self.addon.mw = _DummyMW(col)

        result = self.handler("buy_void_knight_deflector", {})

        self.assertEqual(
            result,
            {
                "ok": False,
                "reason": "undo_unavailable",
                "message": "Anki could not create an undo entry.",
            },
        )
        # Nothing was written: the player keeps the commendations.
        self.assertEqual(
            self.addon._state.player_data["pest_control_commendations"], 500
        )
        self.assertEqual(
            self.gains,
            [],
            "no success feedback may be shown when nothing was saved",
        )


if __name__ == "__main__":
    unittest.main()
