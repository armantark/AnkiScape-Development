"""Slayer assignments must be undoable through the shared direct-action seam,
and a locked master must refuse one there.

These tests drive the real main-menu handler through the real
``commit_direct_action`` seam. Only display side effects are stubbed.
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


_SEED = 8675309


class _Collection:
    def __init__(self, *, raises: bool = False) -> None:
        self.raises = raises
        self.entries: list[str] = []

    def add_custom_undo_entry(self, name: str) -> None:
        if self.raises:
            raise RuntimeError("collection refused the undo entry")
        self.entries.append(name)

    def set_config(self, *_args) -> None:
        pass


class _DummyMW:
    def __init__(self, col) -> None:
        self.col = col

    def update_undo_actions(self) -> None:
        pass


class SlayerUndoSeamTest(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_modules = dict(sys.modules)
        self._random_state = random.getstate()
        from tests.test_integration_smoke import (
            _install_runtime_fakes,
            _load_addon_as_package,
        )

        _install_runtime_fakes()
        self.addon = _load_addon_as_package("ankiscape_slayer_undo_seam")
        self.addon._state.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        self.addon._state.current_skill = "Slayer"
        self.saves: list[bool] = []
        self.addon.save_player_data = lambda: self.saves.append(True)
        self.collection = _Collection()
        self.addon.mw = _DummyMW(self.collection)
        self.addon.check_achievements = lambda *_args: None
        self.addon._refresh_skill_availability = lambda: None
        self.addon.update_review_hud = lambda *_args: None
        self.addon.ui.update_menu_visibility = lambda *_args: None

        captured = {}
        self.addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(
            kwargs
        )
        self.addon._on_main_menu()
        self.command = captured["on_slayer_command"]

    def tearDown(self) -> None:
        random.setstate(self._random_state)
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_assignment_commits_and_undo_restores_state_and_random_sequence(self):
        addon = self.addon
        before = copy.deepcopy(addon._state.player_data)
        expected_next_draw = random.Random(_SEED).random()
        random.seed(_SEED)
        before_random = random.getstate()

        result = self.command("get_assignment", {"master_id": "turael_spria"})

        self.assertTrue(result["ok"], result)
        self.assertGreater(addon._state.player_data["slayer_assignment"]["remaining"], 0)
        self.assertNotEqual(addon._state.player_data, before)
        self.assertNotEqual(random.getstate(), before_random)
        self.assertEqual(self.collection.entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)
        self.assertEqual(len(self.saves), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )

        self.assertEqual(addon._state.player_data, before)
        self.assertEqual(random.getstate(), before_random)
        self.assertEqual(random.random(), expected_next_draw)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_refused_assignment_reports_refusal_and_writes_nothing(self):
        addon = self.addon
        addon._state.player_data["slayer_assignment"] = {
            "master_id": "turael_spria",
            "family_id": "bats",
            "initial_count": 10,
            "remaining": 10,
            "completed": False,
        }
        before = copy.deepcopy(addon._state.player_data)
        random.seed(_SEED)
        before_random = random.getstate()

        result = self.command("get_assignment", {"master_id": "turael_spria"})

        self.assertEqual(result, {"ok": False, "message": "Assignment active"})
        self.assertEqual(addon._state.player_data, before, "a refusal must write nothing")
        self.assertEqual(self.saves, [], "a refusal must save nothing")
        self.assertEqual(
            self.collection.entries, [], "a refusal must not create an undo entry"
        )
        self.assertEqual(addon._state.direct_action_undo_stack, [])
        self.assertEqual(random.getstate(), before_random)

    def test_undo_entry_failure_reports_unavailable_and_writes_nothing(self):
        addon = self.addon
        self.collection = _Collection(raises=True)
        addon.mw = _DummyMW(self.collection)
        before = copy.deepcopy(addon._state.player_data)
        random.seed(_SEED)
        before_random = random.getstate()

        result = self.command("get_assignment", {"master_id": "turael_spria"})

        self.assertEqual(
            result,
            {"ok": False, "message": "Anki could not create an undo entry."},
        )
        self.assertEqual(addon._state.player_data, before, "the failed action must not write")
        self.assertEqual(self.saves, [], "the failed action must not save")
        self.assertEqual(self.collection.entries, [])
        self.assertEqual(addon._state.direct_action_undo_stack, [])
        self.assertEqual(random.getstate(), before_random)

    def test_mazchna_assigns_from_combat_level_20_and_refuses_below_it(self):
        addon = self.addon
        # Attack and Strength 26 on a new save make combat level 19; 27 make 20.
        addon._state.player_data.update(attack_level=26, strength_level=26)
        before = copy.deepcopy(addon._state.player_data)

        refused = self.command("get_assignment", {"master_id": "mazchna_achtryn"})

        self.assertEqual(
            refused, {"ok": False, "message": "Mazchna requires Combat level 20."}
        )
        self.assertEqual(addon._state.player_data, before, "a refusal must write nothing")
        self.assertEqual(self.collection.entries, [])

        addon._state.player_data.update(attack_level=27, strength_level=27)
        assigned = self.command("get_assignment", {"master_id": "mazchna_achtryn"})

        self.assertTrue(assigned["ok"], assigned)
        self.assertEqual(assigned["master_display_name"], "Mazchna")
        assignment = addon._state.player_data["slayer_assignment"]
        self.assertEqual(assignment["master_id"], "mazchna_achtryn")
        self.assertGreater(assignment["remaining"], 0)
        self.assertEqual(self.collection.entries, ["AnkiScape direct action"])


if __name__ == "__main__":
    unittest.main()
