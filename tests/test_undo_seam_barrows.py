"""The Barrows command handler must be undoable through the shared seam.

`_apply_barrows_command` used to hand-roll its own snapshot, custom-undo entry
and save transaction instead of calling `commit_direct_action`, so a Barrows
run could not be taken back with Ctrl+Z while every other migrated family
could. These tests drive the REAL handler through the REAL seam: enter a run,
undo, and assert the whole save is byte-for-byte what it was before. The
achievement surface and HUD are stubbed because an unstubbed achievement dialog
hung the Qt lane in the first wave.
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


class _FakeCollection:
    def __init__(self, accepts: bool = True) -> None:
        self.accepts = accepts
        self.entries: list[str] = []

    def add_custom_undo_entry(self, name: str) -> None:
        if not self.accepts:
            raise RuntimeError("collection refused the undo entry")
        self.entries.append(name)


class _DummyMW:
    def __init__(self, col) -> None:
        self.col = col

    def update_undo_actions(self) -> None:
        pass


def _load_addon():
    from tests.test_integration_smoke import (
        _install_runtime_fakes,
        _load_addon_as_package,
    )

    _install_runtime_fakes()
    return _load_addon_as_package("ankiscape_barrows_undo_seam")


class BarrowsUndoSeamTest(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_modules = dict(sys.modules)
        self.addon = _load_addon()
        addon = self.addon
        addon._state.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        addon._state.current_skill = "Activities"
        addon.save_player_data = lambda: None
        addon.ui.update_menu_visibility = lambda _skill: None
        addon.check_achievements = lambda *_args, **_kwargs: None
        addon._show_activity_gain = lambda _text: None
        addon.update_review_hud = lambda *_args, **_kwargs: None
        addon._refresh_skill_availability = lambda: None
        addon._update_review_context_surface = lambda: None
        addon._show_exp = lambda _gained: None
        addon._award_skill_exp = lambda *args, **kwargs: 0.0
        addon.level_up_check = lambda *_args: None
        self.collection = _FakeCollection()
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon._on_main_menu(initial_skill="Activities")
        self.handler = captured["on_barrows_command"]
        addon.mw = _DummyMW(self.collection)

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_enter_barrows_then_undo_restores_exact_pre_action_state(self):
        addon = self.addon
        before = copy.deepcopy(addon._state.player_data)

        result = self.handler("enter", {})
        self.assertTrue(result["ok"], result)
        self.assertIn("message", result)
        self.assertTrue(addon._state.player_data["barrows"]["active"])
        self.assertEqual(
            addon._state.player_data["activity_session"]["active_id"], "barrows"
        )
        self.assertEqual(
            self.collection.entries, ["AnkiScape direct action"]
        )
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )

        self.assertEqual(
            addon._state.player_data, before, "undo must restore the exact pre-action save"
        )
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_refused_command_reports_the_pure_refusal_and_writes_nothing(self):
        addon = self.addon
        # Another persistent activity is active, so "enter" refuses.
        addon._state.player_data["activity_session"] = {"active_id": "fishing_trawler"}
        before = copy.deepcopy(addon._state.player_data)

        result = self.handler("enter", {})

        self.assertFalse(result["ok"])
        self.assertEqual(result["message"], "Another persistent activity is active.")
        self.assertEqual(addon._state.player_data, before, "a refusal must write nothing")
        self.assertEqual(self.collection.entries, [])
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_undo_entry_failure_returns_failure_not_success(self):
        addon = self.addon
        addon.mw.col = _FakeCollection(accepts=False)

        result = self.handler("enter", {})

        self.assertFalse(result["ok"])
        self.assertEqual(result["message"], "Anki could not create an undo entry.")
        self.assertEqual(addon._state.player_data["activity_session"], {"active_id": ""})
        self.assertEqual(addon._state.direct_action_undo_stack, [])
