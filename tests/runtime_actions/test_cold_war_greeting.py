"""Real menu, storage and review handlers preserve Cold War's assignment."""

import copy
import random
import sys
import unittest
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.data.cold_war_greeting_data import COLD_WAR_GREETING_EMOTES
from ankiscape.logic_pure.logic_pure_quest import quest_journal_rows_pure
from tests.test_cold_war_greeting import GREETING, GREETING_LINE, SAMPLER, eligible_player
from tests.test_combat_quest_gate import _answer_review
from tests.test_integration_smoke import _DummyCol, _DummyMW, _install_runtime_fakes, _load_addon_as_package
from tests.test_storage_runtime import _LegacyTextCollection, _load_storage_module


PLAYER_KEY = "ankiscape_player_data"
RECOVERY_KEY = "ankiscape_player_data_recovery"
SKILL_KEY = "ankiscape_current_skill"


@contextmanager
def review_session():
    original_modules, original_random = dict(sys.modules), random.getstate()
    try:
        _install_runtime_fakes()
        addon = _load_addon_as_package("ankiscape_cold_war_greeting_e2e")
        collection = _DummyCol()
        collection.set_config = lambda key, value: collection._store.__setitem__(key, copy.deepcopy(value))
        addon.mw = _DummyMW(collection)
        storage = sys.modules[f"{addon.__name__}.core.storage"]
        storage.mw = addon.mw
        addon.storage_save_player_data = storage.save_player_data
        addon.storage_load_player_data = storage.load_player_data
        errors = []
        addon.show_error_message = lambda title, message: errors.append((title, message))
        addon.ui.update_menu_visibility = lambda *_args: None
        addon._show_activity_gain = lambda _text: None
        addon._show_exp = lambda _amount: None
        addon.update_review_hud = lambda *_args: None
        addon._state.player_data = eligible_player()
        addon._state.current_skill = "None"
        addon._state.review_undo_stack.clear()
        addon.check_achievements(addon._state.player_data)
        yield addon, collection, errors
    finally:
        random.setstate(original_random)
        sys.modules.clear()
        sys.modules.update(original_modules)


class ColdWarGreetingRuntimeTest(unittest.TestCase):
    def setUp(self):
        self.addCleanup(random.setstate, random.getstate())

    def test_menu_start_saves_greeting_and_reopen_preserves_it(self):
        with review_session() as (addon, collection, errors):
            before = copy.deepcopy(addon._state.player_data)
            with patch(SAMPLER, return_value=list(GREETING)) as sample:
                self.assertTrue(addon.on_set_quest("cold_war"))
                sample.assert_called_once_with(COLD_WAR_GREETING_EMOTES, 3)
                saved = collection._store[PLAYER_KEY]
                self.assertEqual(saved["cold_war_greeting"], GREETING)
                self.assertEqual(saved["current_quest"], "cold_war")
                self.assertEqual(saved["quests"]["cold_war"], dict(started=True, progress=0, completed=False))
                for key in ("inventory", "quest_points", "quest_action_proofs", "pending_skill_exp_rewards"):
                    self.assertEqual(saved[key], before[key])
                addon.load_player_data()
                self.assertEqual(addon._state.player_data["cold_war_greeting"], GREETING)
                for _ in range(2):
                    rows = quest_journal_rows_pure(addon._state.player_data, "cold_war", addon.QUEST_DATA)
                    self.assertEqual([line for row in rows for line in row["lines"]].count(GREETING_LINE), 1)
                self.assertTrue(addon.on_set_quest("rune_mysteries"))
                self.assertEqual(collection._store[PLAYER_KEY]["current_quest"], "rune_mysteries")
                self.assertTrue(addon.on_set_quest("cold_war"))
                addon.load_player_data()
                self.assertEqual(addon._state.player_data["cold_war_greeting"], GREETING)
                self.assertEqual(collection._store[PLAYER_KEY]["cold_war_greeting"], GREETING)
                self.assertEqual(collection._store[PLAYER_KEY]["current_quest"], "cold_war")
                sample.assert_called_once()
            self.assertEqual(errors, [])

    def test_load_backfill_is_saved_before_another_action(self):
        original_modules = dict(sys.modules)
        self.addCleanup(sys.modules.update, original_modules)
        self.addCleanup(sys.modules.clear)
        for completed in (False, True):
            for record_key in (PLAYER_KEY, RECOVERY_KEY):
                with self.subTest(completed=completed, record=record_key):
                    raw = {
                        "config_version": 1,
                        "quests": {"cold_war": dict(started=not completed, completed=completed, progress=3)},
                        "coins": 37,
                        "unrelated_raw_field": {"nested": [1, "kept"]},
                        "inventory": {"Unknown legacy item": 2},
                        "quest_action_proofs": ["untouched raw proof"],
                    }
                    collection = _LegacyTextCollection()
                    collection.legacy_row = False
                    collection.values = {record_key: copy.deepcopy(raw), SKILL_KEY: "Hunter", "other_config": 42}
                    storage = _load_storage_module(collection)
                    with patch(SAMPLER, return_value=list(GREETING)) as sample, patch.object(
                        collection, "set_config", wraps=collection.set_config,
                    ) as save:
                        loaded, skill = storage.load_player_data()
                        self.assertEqual(loaded["cold_war_greeting"], GREETING)
                        self.assertEqual(skill, "Hunter")
                        sample.assert_called_once()
                        save.assert_called_once_with(PLAYER_KEY, {**raw, "cold_war_greeting": GREETING, "cold_war_suit_backfill_checked": True, "inventory": {**raw["inventory"], "Clockwork suit": 1}})
                        saved = collection.values[PLAYER_KEY]
                        self.assertEqual(saved, {**raw, "cold_war_greeting": GREETING, "cold_war_suit_backfill_checked": True, "inventory": {**raw["inventory"], "Clockwork suit": 1}})
                        self.assertIsNot(saved["cold_war_greeting"], loaded["cold_war_greeting"])
                        self.assertEqual(collection.values[SKILL_KEY], "Hunter")
                        self.assertEqual(collection.values["other_config"], 42)
                        self.assertNotIn(RECOVERY_KEY, collection.values)
                        loaded_again, skill_again = storage.load_player_data()
                        self.assertEqual(loaded_again, loaded)
                        self.assertEqual(skill_again, skill)
                        sample.assert_called_once()
                        save.assert_called_once()
                    self.assertNotIn("cold_war_greeting", raw)

        # The existing TEXT-row recovery route also works during this backfill.
        collection = _LegacyTextCollection()
        collection.values[PLAYER_KEY] = copy.deepcopy(raw)
        storage = _load_storage_module(collection)
        with patch(SAMPLER, return_value=list(GREETING)):
            storage.load_player_data()
        self.assertFalse(collection.legacy_row)
        self.assertEqual(collection.values[PLAYER_KEY], {**raw, "cold_war_greeting": GREETING, "cold_war_suit_backfill_checked": True, "inventory": {**raw["inventory"], "Clockwork suit": 1}})
        self.assertNotIn(RECOVERY_KEY, collection.values)

        collection = _LegacyTextCollection()
        collection.legacy_row = False
        collection.values = {PLAYER_KEY: raw, SKILL_KEY: "Hunter"}
        storage = _load_storage_module(collection)
        with patch(SAMPLER, return_value=list(GREETING)), patch.object(
            collection, "set_config", side_effect=RuntimeError("persist failed"),
        ):
            with self.assertRaisesRegex(RuntimeError, "persist failed"):
                storage.load_player_data()
        self.assertEqual(collection.values, {PLAYER_KEY: raw, SKILL_KEY: "Hunter"})

    def test_review_undo_preserves_existing_assignment(self):
        with review_session() as (addon, collection, errors):
            with patch(SAMPLER, return_value=list(GREETING)) as sample:
                self.assertTrue(addon.on_set_quest("cold_war"))
                addon._state.current_skill = "Woodcutting"
                addon._state.player_data["current_tree"] = "tree"
                addon.save_player_data()
                before = copy.deepcopy(addon._state.player_data)
                before_config = copy.deepcopy(collection._store)
                with patch.object(addon.random, "random", return_value=0.0):
                    _answer_review(addon)
                reviewed = copy.deepcopy(addon._state.player_data)
                self.assertGreater(reviewed["woodcutting_exp"], before["woodcutting_exp"])
                self.assertEqual(len(addon._state.review_undo_stack), 1)
                self.assertEqual(reviewed["cold_war_greeting"], GREETING)
                self.assertEqual(collection._store[PLAYER_KEY]["cold_war_greeting"], GREETING)
                addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))
                self.assertEqual(addon._state.player_data, before)
                self.assertEqual(collection._store, before_config)
                self.assertEqual(addon._state.review_undo_stack, [])
                with patch.object(addon.random, "random", return_value=0.0):
                    _answer_review(addon)
                self.assertEqual(addon._state.player_data, reviewed)
                self.assertEqual(collection._store[PLAYER_KEY]["cold_war_greeting"], GREETING)
                addon.load_player_data()
                self.assertEqual(addon._state.player_data["cold_war_greeting"], GREETING)
                sample.assert_called_once()
            self.assertEqual(errors, [])

    def test_refused_cold_war_review_preserves_assignment(self):
        with review_session() as (addon, collection, errors):
            # Keep the opening blocked by one missing Oak plank.
            row = addon.QUEST_DATA["cold_war"]["stage_requirements"][0]
            addon._state.player_data["inventory"].update(row["required_inventory"])
            addon._state.player_data["toolbelt"].update(row["required_tools"])
            addon._state.player_data["inventory"]["Oak plank"] = 9
            with patch(SAMPLER, return_value=list(GREETING)) as sample:
                self.assertTrue(addon.on_set_quest("cold_war"))
                addon._state.current_skill = "Quests"
                addon.save_player_data()
                before = copy.deepcopy(addon._state.player_data)
                _answer_review(addon)
                player = addon._state.player_data
                for key in ("cold_war_greeting", "quests", "quest_action_proofs", "inventory", "quest_points", "pending_skill_exp_rewards"):
                    self.assertEqual(player[key], before[key])
                self.assertEqual(collection._store[PLAYER_KEY]["cold_war_greeting"], GREETING)
                self.assertEqual(player["quests"]["cold_war"]["progress"], 0)
                self.assertEqual(player["quest_action_proofs"], [])
                self.assertEqual(errors, [("Quest blocked", "Cold War is blocked:\n• Needs Oak plank x10\n\nQuesting has been switched off until this is resolved.")])
                self.assertEqual(addon._state.current_skill, "Utilities")
                self.assertEqual(player["current_utility"], "bankstanding")
                sample.assert_called_once()


class ColdWarBackfillIsolationTest(unittest.TestCase):
    def test_current_version_backfill_preserves_raw_nested_save(self):
        original_modules = dict(sys.modules)
        self.addCleanup(sys.modules.update, original_modules)
        self.addCleanup(sys.modules.clear)
        for completed in (False, True):
            for record_key in ("ankiscape_player_data", "ankiscape_player_data_recovery"):
                with self.subTest(completed=completed, record=record_key):
                    raw = {
                        "config_version": 124,
                        "quests": {"cold_war": {
                            "started": not completed, "completed": completed, "progress": 3,
                        }},
                        "inventory": {"Coins": 37},
                        "unrelated_raw_field": {"nested": [1, "kept"]},
                        "quest_action_proofs": ["untouched raw proof"],
                    }
                    before = copy.deepcopy(raw)
                    collection = _LegacyTextCollection()
                    collection.legacy_row = False
                    collection.values = {record_key: raw, "ankiscape_current_skill": "Hunter"}
                    storage = _load_storage_module(collection)
                    with patch(SAMPLER, return_value=list(GREETING)) as sample, patch.object(
                        collection, "set_config", wraps=collection.set_config,
                    ) as save:
                        loaded, skill = storage.load_player_data()
                        expected = {**before, "cold_war_greeting": GREETING, "cold_war_suit_backfill_checked": True, "inventory": {**before["inventory"], "Clockwork suit": 1}}
                        self.assertEqual(raw, before)
                        save.assert_called_once_with("ankiscape_player_data", expected)
                        self.assertEqual(collection.values, {
                            "ankiscape_player_data": expected, "ankiscape_current_skill": "Hunter",
                        })
                        self.assertEqual(skill, "Hunter")
                        self.assertEqual(loaded["cold_war_greeting"], GREETING)
                        self.assertGreater(len(loaded["inventory"]), 1)
                        self.assertIsNot(loaded["inventory"], raw["inventory"])
                        persisted = collection.values["ankiscape_player_data"]
                        self.assertIsNot(persisted["cold_war_greeting"], loaded["cold_war_greeting"])
                        reopened, reopened_skill = storage.load_player_data()
                        self.assertEqual(reopened, loaded)
                        self.assertEqual(reopened_skill, skill)
                        self.assertEqual(persisted, expected)
                        sample.assert_called_once()
                        save.assert_called_once()


if __name__ == "__main__":
    unittest.main()
