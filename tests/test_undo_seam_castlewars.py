"""The Castle Wars command handler must be undoable through the shared seam.

`_apply_castle_wars_command` used to hand-roll its own snapshot, custom-undo
entry and save instead of calling `commit_direct_action`, so Castle Wars actions
were the only menu commands in their family that Ctrl+Z could not take back.

These tests drive the REAL handler (captured from a real `_on_main_menu`) through
the REAL seam. Stubbed here are only side-effect collaborators (HUD refresh,
achievements surface), never the seam itself.
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
        self.undo_updates = 0

    def update_undo_actions(self):
        self.undo_updates += 1


class CastleWarsUndoSeamTest(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_modules = dict(sys.modules)
        from tests.test_integration_smoke import (
            _install_runtime_fakes,
            _load_addon_as_package,
        )

        _install_runtime_fakes()
        self.addon = _load_addon_as_package("ankiscape_castlewars_undo_seam")
        self.addon.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        self.addon.current_skill = "Utility / Activities"
        self.saves = []
        self.addon.save_player_data = lambda: self.saves.append(True)
        self.collection = _FakeCollection()
        self.addon.mw = _DummyMW(self.collection)
        self.addon.update_review_hud = lambda *_args: None
        self.addon._refresh_skill_availability = lambda: None
        self.addon.check_achievements = lambda _data: None
        captured = {}
        self.addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(
            kwargs
        )
        self.addon._on_main_menu()
        self.handler = captured["on_castle_wars_command"]

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_saving_a_plan_commits_and_restores_through_the_real_handler(self):
        addon = self.addon
        before = copy.deepcopy(dict(addon.player_data))

        result = self.handler("set_policy", {"duty": "defend", "team": "zamorak"})

        self.assertTrue(result["ok"])
        self.assertEqual(result["message"], "Castle Wars plan saved.")
        policy = addon.player_data["castle_wars_policy"]
        self.assertEqual(policy["duty"], "defend")
        self.assertEqual(policy["team"], "zamorak")
        self.assertEqual(self.collection.entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._DIRECT_ACTION_UNDO_STACK), 1)
        self.assertEqual(len(self.saves), 1)

        addon._restore_direct_action_snapshot(
            addon._DIRECT_ACTION_UNDO_STACK.pop()
        )
        self.assertEqual(dict(addon.player_data), before)

    def test_entering_a_match_restores_through_the_real_handler(self):
        addon = self.addon
        before = copy.deepcopy(dict(addon.player_data))

        result = self.handler("enter", {})

        self.assertTrue(result["ok"])
        state = addon.player_data.get("activity_session") or {}
        self.assertEqual(state.get("active_id"), "castle_wars")
        addon._restore_direct_action_snapshot(
            addon._DIRECT_ACTION_UNDO_STACK.pop()
        )
        self.assertEqual(dict(addon.player_data), before)

    def test_refused_command_reports_the_refusal_and_writes_nothing(self):
        addon = self.addon
        # A helmet blocks entering Castle Wars.
        addon.player_data["equipment"]["head"] = "Iron full helm"
        before = copy.deepcopy(dict(addon.player_data))

        result = self.handler("enter", {})

        self.assertFalse(result["ok"])
        self.assertIn("helmets", result["message"])
        self.assertEqual(dict(addon.player_data), before)
        self.assertEqual(len(self.saves), 0)
        self.assertEqual(
            addon._DIRECT_ACTION_UNDO_STACK,
            [],
            "a refused command must not register an undo entry",
        )

    def test_undo_unavailable_reports_failure_not_success(self):
        """commit_direct_action returns False for a refusal AND for a failed
        undo entry. The second must not leak the successful info dict: nothing
        was written, so the player must not be told the plan saved."""
        addon = self.addon

        class _ClosedCollection:
            def add_custom_undo_entry(self, _operation):
                raise RuntimeError("collection closed")

            def set_config(self, *_args):
                pass

        addon.mw.col = _ClosedCollection()
        baseline = copy.deepcopy(dict(addon.player_data))

        result = self.handler("set_policy", {"duty": "defend"})

        self.assertFalse(result["ok"])
        self.assertEqual(
            result.get("reason"),
            "undo_unavailable",
            "a failed undo entry must surface as undo_unavailable, not success",
        )
        self.assertEqual(
            result["message"], "Anki could not create an undo entry."
        )
        self.assertEqual(dict(addon.player_data), baseline)
        self.assertEqual(len(self.saves), 0)


if __name__ == "__main__":
    unittest.main()
