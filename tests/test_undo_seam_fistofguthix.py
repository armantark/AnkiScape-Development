"""Fist of Guthix commands through the real handler and the real undo seam.

The handler used to hand-roll its snapshot, undo entry and save. Now it calls
`commit_direct_action`, so one undo must restore exactly the pre-command save —
including a policy change, which the old code deliberately left unundoable.

The modal surfaces (`check_achievements`) are stubbed: an offscreen achievement
dialog has nobody to click it and hung the Qt lane in the first wave.
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
    def __init__(self, col):
        self.col = col

    def update_undo_actions(self):
        return None


def _load_addon(name: str):
    from tests.test_integration_smoke import (
        _install_runtime_fakes,
        _load_addon_as_package,
    )

    _install_runtime_fakes()
    return _load_addon_as_package(name)


class FistOfGuthixUndoSeamTest(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_modules = dict(sys.modules)
        self.addon = _load_addon("ankiscape_fog_undo")
        self.addon._state.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        self.saves: list[bool] = []
        self.addon.save_player_data = lambda: self.saves.append(True)
        self.collection = _FakeCollection()
        self.addon.mw = _DummyMW(self.collection)

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def _fog_handler(self):
        """Open the real main menu and capture the real Fist of Guthix handler."""
        addon = self.addon
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon.check_achievements = lambda _data: None  # opens a modal otherwise
        addon._refresh_skill_availability = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._show_exp = lambda _gained: None
        addon.level_up_check = lambda *_args: None
        addon._on_main_menu(initial_skill="Activities")
        return captured["on_fist_of_guthix_command"]

    def test_talk_fiara_restores_through_the_real_handler(self):
        addon = self.addon
        before = copy.deepcopy(addon._state.player_data)
        depth = len(addon._state.direct_action_undo_stack)
        handler = self._fog_handler()

        result = handler("talk_fiara", {})

        self.assertTrue(result["ok"])
        self.assertTrue(
            addon._state.player_data["fist_of_guthix"]["tutorial_complete"]
        )
        self.assertEqual(self.collection.entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), depth + 1)
        self.assertEqual(len(self.saves), 1)
        snapshot = addon._state.direct_action_undo_stack[-1]["player_data"]
        self.assertEqual(snapshot, before)

        addon._restore_direct_action_snapshot(addon._state.direct_action_undo_stack.pop())
        self.assertEqual(addon._state.player_data, before)

    def test_set_policy_is_undoable_too(self):
        addon = self.addon
        before = copy.deepcopy(addon._state.player_data)
        handler = self._fog_handler()

        result = handler(
            "set_policy",
            {"automation_mode": "advanced", "stance": "centre"},
        )

        self.assertTrue(result["ok"])
        state = addon._state.player_data["fist_of_guthix"]
        self.assertEqual(state["automation_mode"], "advanced")
        self.assertEqual(state["selected_stance"], "centre")
        addon._restore_direct_action_snapshot(addon._state.direct_action_undo_stack.pop())
        self.assertEqual(addon._state.player_data, before)

    def test_a_refused_command_returns_its_own_refusal(self):
        addon = self.addon
        handler = self._fog_handler()

        result = handler("forfeit", {})

        self.assertFalse(result["ok"])
        self.assertEqual(result["message"], "No Fist of Guthix match is active.")
        self.assertEqual(self.collection.entries, [])
        self.assertEqual(len(self.saves), 0)

    def test_when_the_undo_entry_cannot_be_created_nothing_is_written(self):
        """A failed undo entry must be reported as such, never as success."""
        addon = self.addon
        before = copy.deepcopy(addon._state.player_data)
        self.collection.accepts = False
        handler = self._fog_handler()

        result = handler("talk_fiara", {})

        self.assertEqual(
            result,
            {"ok": False, "message": "Anki could not create an undo entry."},
            "a failed undo entry must not echo the successful info dict",
        )
        self.assertEqual(dict(addon._state.player_data), before, "nothing may be written")


if __name__ == "__main__":
    unittest.main()
