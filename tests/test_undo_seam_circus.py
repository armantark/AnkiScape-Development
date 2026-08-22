"""The Big Top Bonanza command handler must go through the shared undo seam.

Before the migration _apply_circus_command hand-rolled its own snapshot, undo
entry and save transaction. These tests drive the real handler through
commit_direct_action and assert an undo restores the pre-action save. Stubbed
here are only side-effect collaborators (achievements surface, HUD, activity
gain popup) — never the seam itself.
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

    def add_custom_undo_entry(self, name: str) -> None:
        if not self.accepts:
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
    return _load_addon_as_package("ankiscape_undo_seam_circus")


class CircusUndoSeamTest(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_modules = dict(sys.modules)
        self.addon = _load_addon()
        self.addon.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        self.saves = []
        self.addon.save_player_data = lambda: self.saves.append(True)
        self.collection = _FakeCollection()
        self.addon.mw = _DummyMW(self.collection)
        self.addon.check_achievements = lambda _data: None
        self.addon._refresh_skill_availability = lambda: None
        self.addon.update_review_hud = lambda *_args: None
        self.gains = []
        addon = self.addon

        def _gain(text):
            self.gains.append(str(text))

        # The handler resolves _show_activity_gain at call time from the module,
        # so patch it there; the popup path would need a live Qt widget.
        self._orig_gain = addon._show_activity_gain
        addon._show_activity_gain = _gain

    def tearDown(self) -> None:
        self.addon._show_activity_gain = self._orig_gain
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def _handler(self):
        captured = {}
        self.addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        self.addon._on_main_menu(initial_activity_id="circus")
        return captured["on_circus_command"]

    def test_circus_command_restores_through_the_real_handler(self):
        addon = self.addon
        handler = self._handler()
        payload = {
            "executing": ["magic"],
            "non_executing": ["ranged", "agility"],
            "automation_mode": "casual",
        }
        before = copy.deepcopy(addon.player_data)

        result = handler("start_activity", payload)

        self.assertTrue(result["ok"])
        state = addon.player_data["circus"]
        self.assertEqual(state["performance_queue"]["executing"], ["magic"])
        self.assertEqual(
            state["performance_queue"]["non_executing"],
            ["ranged", "agility", "fire_breathing", "flaming_poi", "thieving"],
        )
        snapshot = addon._DIRECT_ACTION_UNDO_STACK.pop()
        self.assertEqual(len(self.saves), 1)
        addon._restore_direct_action_snapshot(snapshot)
        self.assertEqual(addon.player_data, before)

    def test_circus_refusal_returns_the_reason_and_writes_nothing(self):
        addon = self.addon
        handler = self._handler()
        baseline = copy.deepcopy(addon.player_data)

        result = handler(
            "start_activity",
            {"executing": [], "non_executing": [], "automation_mode": "casual"},
        )

        self.assertEqual(addon.player_data, baseline, "a refusal must write nothing")
        self.assertEqual(self.saves, [], "a refusal must not persist anything")
        self.assertFalse(result["ok"])
        self.assertEqual(
            result["message"], "Choose at least one executing performance."
        )

    def test_circus_undo_unavailable_reports_failure_not_success(self):
        addon = self.addon
        handler = self._handler()
        addon.mw.col = _ClosedCollection()
        baseline = copy.deepcopy(addon.player_data)
        payload = {
            "executing": ["magic"],
            "non_executing": [],
            "automation_mode": "casual",
        }

        result = handler("start_activity", payload)

        self.assertFalse(result["ok"])
        self.assertEqual(result["message"], "Anki could not create an undo entry.")
        self.assertEqual(addon.player_data, baseline)
        self.assertEqual(len(self.saves), 0)


class _ClosedCollection:
    def add_custom_undo_entry(self, _operation):
        raise RuntimeError("collection closed")
