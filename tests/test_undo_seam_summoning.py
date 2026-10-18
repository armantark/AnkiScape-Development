"""The Summoning command handler must be undoable through the shared seam.

`_apply_summoning_command` was one of the last handlers hand-rolling its own
snapshot, custom-undo entry and save transaction instead of calling
`commit_direct_action`, so a summoned familiar could not be taken back with
Ctrl+Z. These tests drive the REAL handler through the REAL seam. The
achievement surface and HUD are stubbed because an unstubbed achievement dialog
hung the Qt lane in the first wave.
"""

from __future__ import annotations

import copy
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
    return _load_addon_as_package("ankiscape_summoning_undo_seam")


class SummoningUndoSeamTest(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_modules = dict(sys.modules)
        self.addon = _load_addon()
        addon = self.addon
        addon._state.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        addon._state.current_skill = "Summoning"
        addon.save_calls = []
        addon.save_player_data = lambda: addon.save_calls.append(1)
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
        addon._on_main_menu(initial_skill="Summoning")
        self.handler = captured["on_summoning_command"]
        addon.mw = _DummyMW(self.collection)

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def _give_pouch_and_points(self) -> None:
        data = self.addon._state.player_data
        inventory = dict(data.get("inventory", {}) or {})
        inventory["Spirit wolf pouch"] = inventory.get(
            "Spirit wolf pouch", 0
        ) + 1
        data["inventory"] = inventory
        state = dict(data["summoning_state"])
        state["summoning_points_current"] = max(
            int(state.get("summoning_points_current", 0)), 10
        )
        data["summoning_state"] = state

    def test_summon_commits_then_undo_restores_exact_pre_action_state(self):
        addon = self.addon
        self._give_pouch_and_points()
        before = copy.deepcopy(addon._state.player_data)

        result = self.handler("summon", {"familiar_id": "spiritwolf"})

        self.assertTrue(result["ok"], result)
        follower = addon._state.player_data["summoning_state"]["active_follower"]
        self.assertEqual(follower["entity_id"], "spiritwolf")
        self.assertEqual(self.collection.entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)
        self.assertEqual(len(addon.save_calls), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )

        self.assertEqual(
            addon._state.player_data,
            before,
            "undo must restore the exact pre-action save",
        )
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_familiarisation_start_and_claim_each_undo_without_duplicate_reward(self):
        from ankiscape.logic.summoning_logic import apply_familiarisation_segment_pure

        before_start = copy.deepcopy(self.addon._state.player_data)
        self.assertTrue(self.handler("start_familiarisation", {})["ok"])
        self.addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(self.addon._state.player_data, before_start)
        self.assertTrue(self.handler("start_familiarisation", {})["ok"])
        for _answer in range(4):
            updated, ok, result = apply_familiarisation_segment_pure(
                self.addon._state.player_data, successful_answer=True
            )
            self.assertTrue(ok, result)
            self.addon._state.player_data = updated
        before_claim = copy.deepcopy(self.addon._state.player_data)
        self.assertTrue(self.handler("claim_familiarisation", {"choice": "triple_charms"})["ok"])
        claimed = copy.deepcopy(self.addon._state.player_data)
        self.assertEqual(claimed["summoning_state"]["triple_charm_ticks_remaining"], 4_000)
        self.assertEqual(claimed["activity_session"], {"active_id": ""})
        self.assertFalse(self.handler("claim_familiarisation", {"choice": "triple_charms"})["ok"])
        self.addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(self.addon._state.player_data, before_claim)
        self.assertTrue(self.handler("claim_familiarisation", {"choice": "triple_charms"})["ok"])
        self.assertEqual(self.addon._state.player_data, claimed)

    def test_refused_command_reports_refusal_and_writes_nothing(self):
        addon = self.addon
        # No pouch in inventory, so "summon" refuses.
        before = copy.deepcopy(addon._state.player_data)

        result = self.handler("summon", {"familiar_id": "spiritwolf"})

        self.assertFalse(result["ok"])
        self.assertTrue(result["message"])
        self.assertEqual(
            addon._state.player_data, before, "a refusal must write nothing"
        )
        self.assertEqual(self.collection.entries, [])
        self.assertEqual(addon._state.direct_action_undo_stack, [])
        self.assertEqual(addon.save_calls, [])

    def test_undo_entry_failure_reports_failure_not_success(self):
        addon = self.addon
        self._give_pouch_and_points()

        addon.mw.col = _FakeCollection(accepts=False)
        before = copy.deepcopy(addon._state.player_data)

        result = self.handler("summon", {"familiar_id": "spiritwolf"})

        self.assertFalse(result["ok"])
        self.assertEqual(result["message"], "Anki could not create an undo entry.")
        self.assertEqual(addon._state.player_data, before, "nothing may be written")
        self.assertEqual(addon._state.direct_action_undo_stack, [])
        self.assertEqual(addon.save_calls, [])


if __name__ == "__main__":
    unittest.main()
