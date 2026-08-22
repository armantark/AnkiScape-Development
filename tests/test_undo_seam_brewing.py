"""The Trouble Brewing command handler must go through the shared undo seam.

`_apply_trouble_brewing_command` used to hand-roll its own snapshot, custom
undo entry and save transaction. These tests drive the REAL handler (captured
from the real main-menu wiring) through the REAL `commit_direct_action` seam
and assert that undo restores the pre-action state, that a refusal from the
pure function is reported as itself, and that a failed undo entry is never
disguised as success.
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
        self.entries = []

    def add_custom_undo_entry(self, name: str) -> None:
        if not self.accepts:
            raise RuntimeError("collection refused the undo entry")
        self.entries.append(name)


class _DummyMW:
    def __init__(self, col):
        self.col = col

    def update_undo_actions(self):
        pass


class TroubleBrewingUndoSeamTest(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_modules = dict(sys.modules)
        from tests.test_integration_smoke import (
            _install_runtime_fakes,
            _load_addon_as_package,
        )

        _install_runtime_fakes()
        self.addon = _load_addon_as_package("ankiscape_brewing_seam")
        self.addon.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        self.addon.save_player_data = lambda: None
        # check_achievements opens a modal dialog on completion; under a live
        # QApplication that blocks forever.
        self.addon.check_achievements = lambda _data: None
        self.addon._refresh_skill_availability = lambda: None
        self.addon.update_review_hud = lambda *_args: None
        self.addon.mw = _DummyMW(_FakeCollection())
        captured = {}
        self.addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        self.addon._on_main_menu(initial_skill="Activities")
        self.handler = captured["on_trouble_brewing_command"]

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_setting_the_plan_commits_and_restores_through_the_real_handler(self):
        addon = self.addon
        before = copy.deepcopy(addon.player_data)

        result = self.handler("set_policy", {"duty": "sabotage"})
        self.assertTrue(result["ok"])
        self.assertEqual(
            addon.player_data["trouble_brewing_policy"],
            {"automation_mode": "casual", "duty": "sabotage"},
        )
        self.assertIn("Trouble Brewing plan saved.", result["message"])
        addon._restore_direct_action_snapshot(
            addon._DIRECT_ACTION_UNDO_STACK.pop()
        )
        self.assertEqual(addon.player_data, before)

    def test_a_refused_action_reports_its_own_refusal(self):
        addon = self.addon
        before = copy.deepcopy(addon.player_data)

        result = self.handler("bogus_action", {})

        self.assertFalse(result["ok"])
        self.assertEqual(result["message"], "Unknown Trouble Brewing action.")
        self.assertNotEqual(result["message"], "Anki could not create an undo entry.")
        self.assertEqual(dict(addon.player_data), before)

    def test_when_the_undo_entry_cannot_be_created_nothing_is_written_or_claimed(self):
        addon = self.addon
        before = copy.deepcopy(addon.player_data)
        addon.mw.col.accepts = False
        stack_depth = len(addon._DIRECT_ACTION_UNDO_STACK)

        result = self.handler("set_policy", {"target_games": 3})

        self.assertEqual(
            result,
            {"ok": False, "message": "Anki could not create an undo entry."},
            "a failed undo entry must be reported as such, never as success",
        )
        self.assertEqual(dict(addon.player_data), before, "nothing may be written")
        self.assertEqual(len(addon._DIRECT_ACTION_UNDO_STACK), stack_depth)


if __name__ == "__main__":
    unittest.main()
