"""Review dispatch, transaction boundaries, Undo and persistence for Larrissa."""

import copy
import random
import sys
from contextlib import contextmanager
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import QUEST_DATA
from ankiscape.logic_pure import quest_action_proofs
from ankiscape.logic_pure.logic_pure_quest import quest_journal_rows_pure
from ankiscape.runtime.runtime_actions import handle_quest_answer
from tests.quest_catalog.test_horror_from_the_deep_opening import (
    OPENED, OPENING_ACTIONS, QUEST_ID, _expected_opening, _player,
)
from tests.runtime_actions.test_monks_friend_opening import _review_session as _monks_review_session
from tests.test_combat_quest_gate import _answer_review
from tests.test_integration_smoke import _FakeReviewer
from tests.test_runtime_actions import _context


def _success_telemetry(quest_id):
    return {
        "skill_id": "quest", "action_id": quest_id, "attempts": 1, "successes": 1,
        "failures": 0, "expected_successes": 1.0, "current_dry_streak": 0,
        "longest_dry_streak": 0, "outputs": {}, "failure_kinds": {},
        "last_success": True, "last_expected_success_chance": 1.0,
    }


def _account_quest(expected, quest_id):
    expected["action_telemetry"]["actions"][f"quest:{quest_id}"] = _success_telemetry(quest_id)
    expected["achievement_progress"]["skills"]["quest"] = {"actions": {quest_id: 1}, "outputs": {}}


@contextmanager
def _review_session(multiplier=1):
    with _monks_review_session() as (addon, collection, errors):
        addon._state.player_data = _player()
        addon._state.current_skill = "None"
        addon.check_achievements(addon._state.player_data)
        collection.set_config("ankiscape_review_action_multiplier", multiplier)
        addon.save_player_data()
        addon.load_player_data()
        addon.save_player_data()
        yield addon, collection, errors


def _undo(addon):
    addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))


def _again_review(addon):
    addon._state.card_turned = True
    addon._state.answer_shown = True
    addon._state.exp_awarded = False
    addon.on_answer_card(_FakeReviewer(), 1, lambda _self, _ease: "answered")


def _proof_spy(addon):
    proofs = sys.modules[f"{addon.__name__}.logic_pure.quest_action_proofs"]
    return patch.object(proofs, "quest_action_proofs_after_event_pure", wraps=proofs.quest_action_proofs_after_event_pure)


class HorrorFromTheDeepOpeningRuntimeTest(unittest.TestCase):
    def test_handler_emits_exact_ordered_opening_events(self):
        player = _player()
        calls = {"xp": [], "saves": 0, "errors": []}
        context = _context(player, calls)
        context.show_quest_exp_delta = unittest.mock.Mock()
        with patch.object(quest_action_proofs, "quest_action_proofs_after_event_pure", wraps=quest_action_proofs.quest_action_proofs_after_event_pure) as events:
            self.assertTrue(handle_quest_answer(context))
        self.assertEqual([(call.args[1], call.args[2]) for call in events.call_args_list if call.args[1] == "quest_stage"], [
            ("quest_stage", f"{QUEST_ID}:{action}") for action in OPENING_ACTIONS
        ])
        self.assertEqual(player["quest_action_proofs"], sorted(("Unrelated deed", *OPENING_ACTIONS)))
        self.assertEqual(player["quests"][QUEST_ID], OPENED)
        self.assertEqual([(call.args[1], call.args[2]) for call in events.call_args_list if call.args[1] != "quest_stage"], [("quest", QUEST_ID)])
        self.assertEqual(player["action_telemetry"]["actions"], {f"quest:{QUEST_ID}": _success_telemetry(QUEST_ID)})
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["activity"], ["Horror from the Deep 2/8"])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["errors"], [])
        context.show_quest_exp_delta.assert_not_called()
        self.assertNotIn("deactivated", calls)

    def test_handler_refusals_have_no_gameplay_mutation(self):
        incomplete = _player()
        incomplete["quests"]["bar_crawl"]["completed"] = False
        low = _player()
        low["agility_level"] = 34
        completed = _player()
        completed["quests"][QUEST_ID] = {"started": True, "progress": 8, "completed": True}
        legacy_completed = copy.deepcopy(completed)
        legacy_completed["quests"][QUEST_ID]["progress"] = 7
        for player in (incomplete, low, completed, legacy_completed):
            with self.subTest(state=player["quests"][QUEST_ID], agility=player["agility_level"]):
                before = copy.deepcopy(player)
                calls = {"xp": [], "saves": 0, "errors": []}
                with patch.object(quest_action_proofs, "quest_action_proofs_after_event_pure", wraps=quest_action_proofs.quest_action_proofs_after_event_pure) as events:
                    self.assertFalse(handle_quest_answer(_context(player, calls)))
                self.assertEqual(player, before)
                events.assert_not_called()
                self.assertEqual(calls["saves"], 0)
                self.assertEqual(calls["xp"], [])
                self.assertTrue(calls["deactivated"])

    def test_again_and_other_quest_do_not_credit_horror(self):
        with _review_session() as (addon, collection, errors):
            before = copy.deepcopy(addon._state.player_data)
            rng = random.getstate()
            _again_review(addon)
            control = copy.deepcopy(addon._state.player_data)
            control_config = copy.deepcopy(collection._store)
            _undo(addon)
            self.assertEqual(addon._state.player_data, before)
            addon._state.current_skill = "Quests"
            addon.save_player_data()
            random.setstate(rng)
            with _proof_spy(addon) as events:
                _again_review(addon)
            self.assertEqual(addon._state.player_data, control, errors)
            expected_config = copy.deepcopy(control_config)
            expected_config["ankiscape_current_skill"] = "Quests"
            self.assertEqual(collection._store, expected_config)
            events.assert_not_called()
            _undo(addon)
            self.assertEqual(addon._state.player_data, before)
            self.assert_other_quest_matches_control(addon, collection, errors)

    def assert_other_quest_matches_control(self, addon, collection, errors):
        # Monk's Friend stage 3 is an existing item-free, single-action review.
        other = "monks_friend"
        action = "Ask Brother Omad about Brother Cedric and the party"
        addon._state.player_data["current_quest"] = other
        addon._state.player_data["quests"][other] = {"started": True, "progress": 3, "completed": False}
        addon._state.current_skill = "None"
        addon.save_player_data()
        rng = random.getstate()
        _answer_review(addon)
        control = copy.deepcopy(addon._state.player_data)
        control_config = copy.deepcopy(collection._store)
        _undo(addon)
        addon._state.current_skill = "Quests"
        addon.save_player_data()
        random.setstate(rng)
        with _proof_spy(addon) as events:
            _answer_review(addon)
        expected = copy.deepcopy(control)
        expected["quests"][other]["progress"] = 4
        expected["quest_action_proofs"] = sorted((*control["quest_action_proofs"], action))
        _account_quest(expected, other)
        expected_config = copy.deepcopy(control_config)
        expected_config.update(ankiscape_player_data=expected, ankiscape_current_skill="Quests")
        self.assertEqual(addon._state.player_data, expected, errors)
        self.assertEqual(collection._store, expected_config)
        self.assertEqual([call.args[2] for call in events.call_args_list if call.args[1] == "quest_stage"], [f"{other}:{action}"])
        self.assertFalse(set(OPENING_ACTIONS) & set(expected["quest_action_proofs"]))

    def test_genuine_review_undo_replay_and_reopen_restore_complete_state(self):
        with _review_session() as (addon, collection, errors):
            before = copy.deepcopy(addon._state.player_data)
            before_config = copy.deepcopy(collection._store)
            journal_before = quest_journal_rows_pure(before, QUEST_ID, QUEST_DATA)
            rng = random.getstate()
            _answer_review(addon)
            control = copy.deepcopy(addon._state.player_data)
            control_config = copy.deepcopy(collection._store)
            _undo(addon)
            self.assertEqual(addon._state.player_data, before)
            self.assertEqual(collection._store, before_config)
            addon._state.current_skill = "Quests"
            addon.save_player_data()
            selected_config = copy.deepcopy(collection._store)
            random.setstate(rng)
            with _proof_spy(addon) as events:
                _answer_review(addon)
            self.assertEqual([call.args[2] for call in events.call_args_list if call.args[1] == "quest_stage"], [f"{QUEST_ID}:{action}" for action in OPENING_ACTIONS])
            expected = _expected_opening(control)
            _account_quest(expected, QUEST_ID)
            expected_config = copy.deepcopy(control_config)
            expected_config.update(ankiscape_player_data=expected, ankiscape_current_skill="Quests")
            self.assertEqual(addon._state.player_data, expected, errors)
            self.assertEqual(collection._store, expected_config)
            journal_after = quest_journal_rows_pure(expected, QUEST_ID, QUEST_DATA)
            self.assertEqual(journal_after, (
                {"stage": 1, "lines": OPENING_ACTIONS, "completed": True, "current": False},
                {"stage": 2, "lines": QUEST_DATA[QUEST_ID]["journal_stages"][2], "completed": False, "current": True},
            ))
            after_rng = random.getstate()
            _undo(addon)
            self.assertEqual(addon._state.player_data, before)
            self.assertEqual(collection._store, selected_config)
            self.assertEqual(quest_journal_rows_pure(addon._state.player_data, QUEST_ID, QUEST_DATA), journal_before)
            random.setstate(rng)
            _answer_review(addon)
            self.assertEqual(addon._state.player_data, expected, errors)
            self.assertEqual(collection._store, expected_config)
            self.assertEqual(random.getstate(), after_rng)
            addon._state.player_data = {}
            addon._state.current_skill = "None"
            addon.load_player_data()
            self.assertEqual(addon._state.player_data, expected)
            self.assertEqual(addon._state.current_skill, "Quests")
            self.assertEqual(collection._store, expected_config)
            self.assertEqual(quest_journal_rows_pure(addon._state.player_data, QUEST_ID, QUEST_DATA), journal_after)

    def test_genuine_review_cannot_cross_the_next_boundary(self):
        for multiplier in (1, 10):
            with self.subTest(multiplier=multiplier), _review_session(multiplier) as (addon, collection, errors):
                addon._state.current_skill = "Quests"
                addon.save_player_data()
                with _proof_spy(addon) as events:
                    _answer_review(addon)
                self.assertEqual(addon._state.player_data["quests"][QUEST_ID], OPENED, errors)
                self.assertEqual([call.args[1:] for call in events.call_args_list if call.args[1] == "quest_stage"], [
                    ("quest_stage", f"{QUEST_ID}:{action}") for action in OPENING_ACTIONS
                ])
                self.assertEqual(addon._state.player_data["quest_action_proofs"], sorted(("Unrelated deed", *OPENING_ACTIONS)))
                self.assertNotIn("Lighthouse key", addon._state.player_data["inventory"])
                self.assertFalse(addon._state.player_data["quest_combat_encounters"])
                before_blocked = copy.deepcopy(addon._state.player_data)
                config_before_blocked = copy.deepcopy(collection._store)
                with _proof_spy(addon) as events:
                    _answer_review(addon)
                events.assert_not_called()
                self.assertEqual(addon._state.player_data["quests"][QUEST_ID], OPENED)
                self.assertEqual(addon._state.player_data["quest_action_proofs"], before_blocked["quest_action_proofs"])
                self.assertEqual(addon._state.player_data["inventory"], before_blocked["inventory"])
                _undo(addon)
                self.assertEqual(addon._state.player_data, before_blocked)
                self.assertEqual(collection._store, config_before_blocked)
