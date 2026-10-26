"""The Varrock Museum handler must go through the shared undo seam.

`_apply_varrock_museum_command` in `__init__.py` used to hand-roll its own
snapshot, custom-undo entry and save transaction. It now delegates to
`commit_direct_action`, so a museum command is undoable through Anki's Ctrl+Z,
a refusal writes and saves nothing, and a failed undo entry reports failure
rather than a fake success.
"""

from __future__ import annotations

import copy
import random
import sys
import types
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)

from tests.quest_catalog.defender_museum_fixture import (
    CLAIM_REASON, DEFENDER, SHIELD, ready_defender_player, typed_snapshot,
)
from tests.quest_catalog.test_defender_museum import claim, reasons
from ankiscape.logic.varrock_museum_logic import varrock_museum_kudos_pure


class _RefusingCollection:
    def add_custom_undo_entry(self, name):
        raise RuntimeError("collection refused the undo entry")


class _DummyMW:
    def __init__(self, col):
        self.col = col
        self.undo_updates = 0

    def update_undo_actions(self):
        self.undo_updates += 1


def _load_addon():
    from tests.test_integration_smoke import (
        _install_runtime_fakes,
        _load_addon_as_package,
    )

    _install_runtime_fakes()
    return _load_addon_as_package("ankiscape_undo_seam_museum")


def _wire_museum(addon, col):
    """Install the runtime state and stubbed side-effect collaborators."""
    museum_logic = sys.modules[
        f"{addon.__name__}.logic.varrock_museum_logic"
    ]
    captured = {}
    addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
    addon.mw = _DummyMW(col)
    addon._state.current_skill = "Activities"
    initial = {
        "inventory": {},
        "varrock_museum": museum_logic.default_varrock_museum_state_pure(),
        "completed_achievements": [],
    }
    addon._state.player_data = copy.deepcopy(initial)
    addon.save_player_data = lambda: None
    addon.update_review_hud = lambda *_args: None
    addon._refresh_skill_availability = lambda: None
    addon._show_activity_gain = lambda _message: None
    addon._show_quest_exp_delta = lambda _delta: None
    addon.check_achievements = lambda *_args: None
    addon.get_skill = lambda _skill_id: None
    addon.level_up_check = lambda *_args: None
    addon._on_main_menu()
    return initial, captured["on_varrock_museum_command"]


class MuseumUndoSeamTest(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_modules = dict(sys.modules)
        self.addon = _load_addon()

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_take_cleaning_kit_is_undoable_through_the_seam(self):
        addon = self.addon
        col = addon._FakeCollectionForMuseum = type(
            "_Col", (), {
                "custom_undo_entries": [],
                "add_custom_undo_entry": (
                    lambda self, name: self.custom_undo_entries.append(name)
                ),
            },
        )()
        initial, command = _wire_museum(addon, col)

        result = command("take_cleaning_kit", {})

        self.assertTrue(result["ok"])
        for item_name in ("Trowel", "Rock pick", "Specimen brush"):
            self.assertEqual(addon._state.player_data["inventory"][item_name], 1)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_a_refused_command_writes_and_saves_nothing(self):
        addon = self.addon
        col = type(
            "_Col", (), {
                "custom_undo_entries": [],
                "add_custom_undo_entry": (
                    lambda self, name: self.custom_undo_entries.append(name)
                ),
            },
        )()
        initial, command = _wire_museum(addon, col)
        # The rack is already complete, so the pure function refuses.
        addon._state.player_data["inventory"] = {
            "Trowel": 1,
            "Rock pick": 1,
            "Specimen brush": 1,
            "Leather gloves": 1,
            "Leather boots": 1,
        }
        initial["inventory"] = copy.deepcopy(addon._state.player_data["inventory"])
        saved = []
        addon.save_player_data = lambda: saved.append(True)

        result = command("take_cleaning_kit", {})

        self.assertFalse(result["ok"])
        self.assertIn("already have", result["message"])
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(col.custom_undo_entries, [])
        self.assertEqual(saved, [])
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_undo_unavailable_reports_failure_not_success(self):
        addon = self.addon
        initial, command = _wire_museum(addon, _RefusingCollection())
        saved = []
        addon.save_player_data = lambda: saved.append(True)

        result = command("take_cleaning_kit", {})

        self.assertEqual(
            result,
            {"ok": False, "message": "Anki could not create an undo entry."},
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(saved, [])

    def _earned_runtime(self, player=None, refusing=False):
        from tests.test_integration_smoke import _DummyCol

        addon = self.addon
        col = _DummyCol()
        if refusing:
            col.add_custom_undo_entry = _RefusingCollection().add_custom_undo_entry
        _initial, command = _wire_museum(addon, col)
        addon._state.player_data = copy.deepcopy(player if player is not None else ready_defender_player())
        col.set_config("ankiscape_player_data", copy.deepcopy(addon._state.player_data))
        col.set_config("ankiscape_current_skill", addon._state.current_skill)
        self.counters = dict.fromkeys(("save", "refresh", "reward", "hud", "xp", "achievement", "level"), 0)

        def save():
            self.counters["save"] += 1
            col.set_config("ankiscape_player_data", copy.deepcopy(addon._state.player_data))
            col.set_config("ankiscape_current_skill", addon._state.current_skill)

        def count(key):
            def counted(*_args):
                self.counters[key] += 1
            return counted

        addon.save_player_data = save
        addon._refresh_skill_availability = count("refresh")
        addon._show_activity_gain = count("reward")
        addon.update_review_hud = count("hud")
        addon._show_quest_exp_delta = count("xp")
        addon.check_achievements = count("achievement")
        addon.level_up_check = count("level")
        addon.show_error_message = lambda *_args: None
        self.collection = col
        self.addCleanup(random.setstate, random.getstate())
        return command

    def _runtime_packet(self):
        addon = self.addon
        return typed_snapshot(copy.deepcopy({
            "player": addon._state.player_data,
            "config": self.collection._store,
            "skill": addon._state.current_skill,
            "review_undo": addon._state.review_undo_stack,
            "direct_undo": addon._state.direct_action_undo_stack,
            "rng": random.getstate(),
            "undo_entries": self.collection.custom_undo_entries,
            "undo_updates": addon.mw.undo_updates,
            "counters": self.counters,
        }))

    def test_shield_story_claim_undo_and_replay_restore_the_same_lock(self):
        command = self._earned_runtime()
        addon = self.addon
        # Another prerequisite must remain effective on both sides of the claim.
        addon._state.player_data["quests"].pop("garden_of_tranquillity")
        before = copy.deepcopy(addon._state.player_data)
        kudos = varrock_museum_kudos_pure(before)
        self.assertEqual(reasons(before), ("Garden of Tranquillity", CLAIM_REASON))
        first = command("claim_quest_stories", {})
        self.assertTrue(first["ok"])
        self.assertEqual(first["quest_ids"], (SHIELD,))
        self.assertEqual(first["kudos"], 5)
        self.assertEqual(self.counters["save"], 1)
        self.assertEqual(self.collection.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)
        accepted = copy.deepcopy(addon._state.player_data)
        self.assertEqual(reasons(accepted), ("Garden of Tranquillity",))
        self.assertFalse(addon.on_set_quest(DEFENDER))
        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(typed_snapshot(addon._state.player_data), typed_snapshot(before))
        self.assertEqual(typed_snapshot(self.collection._store["ankiscape_player_data"]), typed_snapshot(before))
        self.assertNotIn(SHIELD, addon._state.player_data["varrock_museum"]["quest_stories_claimed"])
        self.assertEqual(varrock_museum_kudos_pure(addon._state.player_data), kudos)
        self.assertEqual(reasons(addon._state.player_data), ("Garden of Tranquillity", CLAIM_REASON))
        replay = command("claim_quest_stories", {})
        self.assertEqual(replay, first)
        self.assertEqual(typed_snapshot(addon._state.player_data), typed_snapshot(accepted))
        self.assertEqual(varrock_museum_kudos_pure(addon._state.player_data), kudos + 5)
        self.assertEqual(addon._state.player_data["varrock_museum"]["quest_stories_claimed"].count(SHIELD), 1)
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)
        self.assertFalse(addon.on_set_quest(DEFENDER))

    def test_refused_story_commands_preserve_complete_runtime_state(self):
        incomplete = ready_defender_player()
        incomplete["quests"][SHIELD]["completed"] = False
        repeated, _info = claim(ready_defender_player())
        malformed = copy.deepcopy(incomplete)
        malformed["varrock_museum"] = {"quest_stories_claimed": "legacy", "version": -1}
        # Without other completed stories, the normalized candidate is still refused.
        malformed["quests"] = {}
        legacy = copy.deepcopy(malformed)
        legacy["varrock_museum"] = None
        for player in (incomplete, repeated, malformed, legacy):
            with self.subTest(museum=player["varrock_museum"]):
                command = self._earned_runtime(player)
                before = self._runtime_packet()
                result = command("claim_quest_stories", {})
                self.assertFalse(result["ok"])
                self.assertEqual(result["message"], "No completed quest stories are ready for Minas.")
                self.assertEqual(self._runtime_packet(), before)

    def test_refused_defender_start_preserves_complete_runtime_state(self):
        self._earned_runtime()
        self.assertEqual(reasons(self.addon._state.player_data), (CLAIM_REASON,))
        before = self._runtime_packet()
        self.assertFalse(self.addon.on_set_quest(DEFENDER))
        self.assertEqual(self._runtime_packet(), before)

    def test_story_claim_without_undo_entry_does_not_commit(self):
        command = self._earned_runtime(refusing=True)
        before = self._runtime_packet()
        result = command("claim_quest_stories", {})
        self.assertEqual(result, {"ok": False, "message": "Anki could not create an undo entry."})
        self.assertEqual(self._runtime_packet(), before)


if __name__ == "__main__":
    unittest.main()
