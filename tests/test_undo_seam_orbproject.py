"""Great Orb Project commands through the live undo seam.

The handler used to hand-roll its own snapshot, custom-undo entry and save
transaction. These tests drive the shipped `_apply_great_orb_project_command`
through the real `commit_direct_action` and assert an undo restores the
pre-action save. The achievement surface is stubbed because it can open a modal
dialog no offscreen test can click.
"""

from __future__ import annotations

import copy
import sys
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data


class _FakeCollection:
    def __init__(self, raise_on_entry: bool = False) -> None:
        self.entries: list[str] = []
        self._raise = raise_on_entry

    def add_custom_undo_entry(self, name: str) -> None:
        if self._raise:
            raise RuntimeError("collection refused the undo entry")
        self.entries.append(name)


class _DummyMW:
    def __init__(self, col) -> None:
        self.col = col

    def update_undo_actions(self) -> None:
        return None


def _load_addon():
    from tests.test_integration_smoke import (
        _install_runtime_fakes,
        _load_addon_as_package,
    )

    _install_runtime_fakes()
    return _load_addon_as_package("ankiscape_orbproject_undo_seam")


class GreatOrbProjectUndoSeamTest(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_modules = dict(sys.modules)
        self.addon = _load_addon()
        self.saves = []
        self.addon.save_player_data = lambda: self.saves.append(True)
        self.collection = _FakeCollection()
        self.addon.mw = _DummyMW(self.collection)
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["runecrafting_level"] = 50
        player["inventory"] = {
            "Pure essence": 25,
            "Air talisman": 1,
            "Earth talisman": 1,
        }
        self.addon.player_data = player
        # Stub the surfaces that open dialogs or touch Qt.
        self.addon.check_achievements = lambda *_a, **_k: None
        self.patches = [
            patch.object(self.addon, "_show_activity_gain", lambda *_a: None),
            patch.object(
                self.addon, "_show_quest_exp_delta", lambda *_a: None
            ),
        ]
        for p in self.patches:
            p.start()

    def tearDown(self) -> None:
        for p in self.patches:
            p.stop()
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def _handler(self):
        # _on_main_menu builds and shows the real menu dialog; capture the
        # callback wiring instead of opening a dialog nothing can click.
        captured = {}
        with patch.object(
            self.addon.ui,
            "show_main_menu",
            side_effect=lambda *args, **kwargs: captured.update(kwargs),
        ):
            self.addon._on_main_menu()
        handler = captured["on_great_orb_project_command"]
        self.assertIsNotNone(handler)
        return handler

    def test_entering_commits_through_the_seam_and_undo_restores_the_save(self):
        addon = self.addon
        before = copy.deepcopy(dict(addon.player_data))
        depth = len(addon._DIRECT_ACTION_UNDO_STACK)

        result = self._handler()("enter_great_orb_project", {})

        self.assertTrue(result["ok"], result)
        self.assertEqual(self.collection.entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._DIRECT_ACTION_UNDO_STACK), depth + 1)
        self.assertEqual(len(self.saves), 1)
        self.assertEqual(
            addon.player_data["activity_session"]["active_id"],
            "great_orb_project",
        )

        addon._restore_direct_action_snapshot(
            addon._DIRECT_ACTION_UNDO_STACK.pop()
        )
        self.assertEqual(dict(addon.player_data), before)
        self.assertEqual(
            addon.player_data["great_orb_project"]["active"], {}
        )

    def test_a_refused_command_returns_the_pure_refusal_and_writes_nothing(self):
        addon = self.addon
        depth = len(addon._DIRECT_ACTION_UNDO_STACK)

        result = self._handler()("not_an_action", {})

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["message"], "Unknown Great Orb Project action."
        )
        self.assertEqual(
            addon.player_data["great_orb_project"]["active"], {}
        )
        self.assertEqual(len(addon._DIRECT_ACTION_UNDO_STACK), depth)
        self.assertEqual(self.collection.entries, [])
        self.assertEqual(self.saves, [])

    def test_when_anki_cannot_create_an_undo_entry_nothing_is_written(self):
        addon = self.addon
        before = copy.deepcopy(dict(addon.player_data))
        self.collection._raise = True

        with patch.object(
            addon.mw.col, "add_custom_undo_entry", side_effect=RuntimeError
        ):
            result = self._handler()("enter_great_orb_project", {})

        self.assertEqual(
            result,
            {"ok": False, "message": "Anki could not create an undo entry."},
        )
        self.assertEqual(dict(addon.player_data), before)
        self.assertEqual(self.saves, [])


if __name__ == "__main__":
    unittest.main()
