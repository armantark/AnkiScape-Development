"""The Soul Wars command handler must be undoable through the shared seam.

`_apply_soul_wars_command` hand-rolled its own snapshot, custom-undo entry and
save transaction instead of calling `commit_direct_action`. These tests drive
the REAL handler through the REAL seam: enter a match, undo, and assert the
whole save is exactly what it was before; assert a refused command writes and
saves nothing; assert an undo-entry failure reports failure rather than
success. The achievement surface is stubbed because an unstubbed achievement
dialog hung the Qt lane in the first wave.
"""

from __future__ import annotations

import copy
import sys
import types
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA


class _FakeCollection:
    def __init__(self, accepts: bool = True) -> None:
        self.accepts = accepts
        self.entries: list[str] = []
        self.saved_calls = 0

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
    return _load_addon_as_package("ankiscape_soulwars_undo_seam")


class SoulWarsUndoSeamTest(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_modules = dict(sys.modules)
        self.addon = _load_addon()
        addon = self.addon
        logic = sys.modules[f"{addon.__name__}.logic.soul_wars_logic"]
        addon.player_data = {
            "inventory": {},
            "equipment": {},
            "combat_encounter": {},
            "combat_supply_loadout": {"food": {}},
            "shop_market_clock": {"answered_cards": 0},
            "current_combat_target": "chicken",
            "current_utility": "make_soft_clay",
            "activity_session": {"active_id": ""},
        }
        addon.player_data.update(logic.default_soul_wars_state_pure())
        addon.player_data = copy.deepcopy(addon.player_data)
        addon.current_skill = "Activities"
        self.save_calls = []
        addon.save_player_data = lambda: self.save_calls.append(1)
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
        self.handler = captured["on_soul_wars_command"]
        addon.mw = _DummyMW(self.collection)

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_enter_soul_wars_then_undo_restores_exact_pre_action_state(self):
        addon = self.addon
        before = copy.deepcopy(addon.player_data)

        result = self.handler(
            "enter",
            {"automation_mode": "advanced", "duty": "defend", "team": "creation"},
        )
        self.assertTrue(result["ok"], result)
        self.assertEqual(addon.player_data["current_utility"], "soul_wars")
        self.assertEqual(addon.player_data["soul_wars"]["duty"], "defend")
        self.assertEqual(
            self.collection.entries, ["AnkiScape direct action"]
        )
        self.assertEqual(len(self.save_calls), 1)
        self.assertEqual(len(addon._DIRECT_ACTION_UNDO_STACK), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )

        self.assertEqual(
            addon.player_data, before, "undo must restore the exact pre-action save"
        )
        self.assertEqual(addon._DIRECT_ACTION_UNDO_STACK, [])

    def test_refused_command_reports_refusal_and_writes_and_saves_nothing(self):
        addon = self.addon
        # A cape is equipped, so entering refuses.
        addon.player_data["equipment"]["cape"] = {"item_name": "Accumulator max cape"}
        before = copy.deepcopy(addon.player_data)

        result = self.handler(
            "enter",
            {"automation_mode": "advanced", "duty": "defend", "team": "creation"},
        )

        self.assertFalse(result["ok"])
        self.assertIn("cape", result["message"].lower())
        self.assertEqual(
            addon.player_data,
            before,
            "a refusal must write nothing to player state",
        )
        self.assertEqual(self.collection.entries, [])
        self.assertEqual(self.save_calls, [], "a refusal must not save")
        self.assertEqual(addon._DIRECT_ACTION_UNDO_STACK, [])

    def test_undo_entry_failure_returns_failure_not_success(self):
        addon = self.addon
        addon.mw.col = _FakeCollection(accepts=False)

        result = self.handler("enter", {})

        self.assertFalse(result["ok"])
        self.assertEqual(result["message"], "Anki could not create an undo entry.")
        self.assertEqual(addon.player_data["soul_wars"], {})
        self.assertEqual(addon.player_data["activity_session"], {"active_id": ""})
        self.assertEqual(self.save_calls, [])
        self.assertEqual(addon._DIRECT_ACTION_UNDO_STACK, [])


if __name__ == "__main__":
    unittest.main()
