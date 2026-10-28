"""The performed sconce search and commission are one review transaction."""

import copy
import json
import random
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import QUEST_DATA
from ankiscape.data.quest.stage_overrides.members.later.animal_magnetism import (
    COMPLETED_OPENING, OPENING_ACTIONS,
)
from ankiscape.logic_pure import quest_action_proofs as proofs
from ankiscape.logic_pure.logic_pure_quest import (
    apply_quest_progress_pure, quest_journal_rows_pure, quest_locked_reasons_pure, start_quest_pure,
)
from ankiscape.runtime import runtime_actions_quest
from tests.runtime_actions.quests.animal_magnetism_helpers import (
    OLD_SENTINEL, QUEST_ID, SKILL_GATES, eligible_player, ernest_only_player,
    product_values, restless_only_player, review,
)
from tests.runtime_actions.test_cold_war_greeting import PLAYER_KEY, review_session
from tests.test_combat_quest_gate import _answer_review
from tests.test_runtime_actions import _context

EVENT_READER = "ankiscape.logic_pure.quest_action_proofs.quest_action_proofs_after_event_pure"


def encoded(value):
    # Collection config uses JSON; compare every field across tuple/list encoding.
    return json.loads(json.dumps(value))


def snapshot(addon):
    state = addon._state
    return copy.deepcopy(dict(
        player=state.player_data, skill=state.current_skill, random=random.getstate(),
        dialogs=list(state.pending_review_dialogs), notice=state.pending_bankstanding_notice,
    ))


class AnimalMagnetismOpeningRuntimeTest(unittest.TestCase):
    def assert_no_opening(self, player):
        for action in OPENING_ACTIONS:
            self.assertFalse(proofs.quest_action_proof_completed_pure(player, action))
        lines = [line for row in quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA) for line in row["lines"]]
        self.assertNotIn(COMPLETED_OPENING, lines)

    def assert_refused(self, player):
        before = copy.deepcopy(player)
        calls = dict(xp=[], saves=0, errors=[])
        with patch(EVENT_READER, wraps=proofs.quest_action_proofs_after_event_pure) as events:
            self.assertFalse(review(player, calls))
        self.assertEqual(events.call_args_list, [])
        self.assertEqual(calls["saves"], 0)
        self.assertEqual(calls["xp"], [])
        self.assertEqual(player, before)
        self.assertEqual(product_values(player), product_values(before))
        self.assert_no_opening(player)

    def test_missing_each_ordinary_prerequisite_refuses_atomically(self):
        for fixture, missing in ((ernest_only_player, "The Restless Ghost"), (restless_only_player, "Ernest the Chicken")):
            with self.subTest(missing=missing):
                player = fixture()
                self.assertEqual(quest_locked_reasons_pure(player, QUEST_ID, QUEST_DATA), (missing,))
                self.assert_refused(player)

    def test_each_existing_skill_boundary_still_refuses(self):
        base = eligible_player()
        for skill, required in SKILL_GATES:
            with self.subTest(skill=skill):
                player = copy.deepcopy(base)
                player[skill + "_level"] = required - 1
                self.assertEqual(quest_locked_reasons_pure(player, QUEST_ID, QUEST_DATA), (f"{skill.title()} {required}",))
                self.assert_refused(player)

    def test_selection_and_start_do_not_perform_opening(self):
        player = eligible_player()
        before = copy.deepcopy(player)
        with patch(EVENT_READER, wraps=proofs.quest_action_proofs_after_event_pure) as events:
            selected, ok = start_quest_pure(player, QUEST_ID, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(events.call_args_list, [])
        self.assertEqual(player, before)
        self.assertEqual(selected["quests"][QUEST_ID], dict(started=True, progress=0, completed=False))
        self.assertEqual(selected["quest_action_proofs"], before["quest_action_proofs"])
        self.assert_no_opening(selected)

    def assert_ordered_review(self, player):
        calls = dict(xp=[], saves=0, errors=[])
        before = copy.deepcopy(player)
        retained = {}

        def reducer(incoming, *args, **kwargs):
            nested = {key: incoming[key] for key in ("quests", "quest_action_proofs", "inventory")}
            result = apply_quest_progress_pure(incoming, *args, **kwargs)
            self.assertEqual(incoming, before)
            self.assertEqual(nested, {key: before[key] for key in nested})
            retained.update(nested)
            return result

        with patch(EVENT_READER, wraps=proofs.quest_action_proofs_after_event_pure) as events, patch.object(
            runtime_actions_quest, "apply_quest_progress_pure", side_effect=reducer,
        ):
            self.assertTrue(review(player, calls))
        stage_events = [(args[1], args[2]) for args, _kwargs in events.call_args_list if args[1] == "quest_stage"]
        self.assertEqual(stage_events, [("quest_stage", f"{QUEST_ID}:{action}") for action in OPENING_ACTIONS])
        self.assertEqual(retained, {key: before[key] for key in retained})
        self.assertEqual(player["quests"][QUEST_ID], dict(started=True, progress=2, completed=False))
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(player["quest_action_proofs"], sorted(set(before["quest_action_proofs"]) | set(OPENING_ACTIONS)))
        return player

    def test_first_review_performs_sconce_then_commission_atomically(self):
        base = eligible_player()
        for started, progress in ((False, 0), (True, 0), (True, 1)):
            with self.subTest(started=started, progress=progress):
                player = copy.deepcopy(base)
                player["quests"][QUEST_ID] = dict(started=started, progress=progress, completed=False)
                self.assert_ordered_review(player)

    def test_talk_flags_old_sentinel_and_possessions_cannot_substitute(self):
        controls = (
            {"quest_conversations": {QUEST_ID: {"ava": True}}, "telemetry": {"ava_talks": 9}},
            {"quest_action_proofs": [OLD_SENTINEL]},
            {"inventory": {"Undead chicken": 2, "Ecto-token": 20, "Ghostspeak amulet": 1, "Crone-made amulet": 1}},
        )
        base = eligible_player()
        for control in controls:
            with self.subTest(control=control):
                player = copy.deepcopy(base)
                player.update(control)
                player["quests"][QUEST_ID] = dict(started=True, progress=1, completed=False)
                self.assert_no_opening(player)
                advanced = copy.deepcopy(player)
                advanced["quests"][QUEST_ID]["progress"] = 2
                self.assert_no_opening(advanced)
                self.assert_ordered_review(player)

    def test_repeated_review_and_reselection_do_not_repeat_or_skip(self):
        player = eligible_player()
        self.assertTrue(review(player))
        expected = copy.deepcopy(player)
        for _ in range(3):
            selected, ok = start_quest_pure(player, QUEST_ID, QUEST_DATA)
            self.assertTrue(ok)
            self.assertEqual(selected, expected)
            player = selected
            blockers = runtime_actions_quest.quest_current_stage_blocker_reasons_pure(player, QUEST_ID, QUEST_DATA)
            self.assertTrue(any("Complete Animal Magnetism stage 2 objective" in reason for reason in blockers))
            calls = dict(xp=[], saves=0, errors=[])
            with patch(EVENT_READER, wraps=proofs.quest_action_proofs_after_event_pure) as events:
                self.assertFalse(review(player, calls))
            self.assertEqual(events.call_args_list, [])
            self.assertEqual(player, expected)
            self.assertEqual(calls["saves"], 0)
        for action in OPENING_ACTIONS:
            self.assertEqual(player["quest_action_proofs"].count(action), 1)

    def test_opening_grants_no_items_experience_points_or_rewards(self):
        player = eligible_player()
        before = product_values(player)
        self.assertTrue(review(player))
        expected = copy.deepcopy(before)
        expected["quests"][QUEST_ID] = dict(started=True, progress=2, completed=False)
        expected["quest_action_proofs"] = sorted(set(before["quest_action_proofs"]) | set(OPENING_ACTIONS))
        self.assertEqual(product_values(player), expected)
        self.assertGreaterEqual(player["inventory"]["Ancient bones"], 5)
        self.assertGreaterEqual(player["inventory"]["Egg"], 10)
        self.assertEqual(player["inventory"]["Ghostspeak amulet"], 1)

    def assert_roundtrip(self, addon, collection):
        before = snapshot(addon)
        addon.save_player_data()
        self.assertEqual(collection._store[PLAYER_KEY], encoded(addon._state.player_data))
        addon.load_player_data()
        self.assertEqual(encoded(snapshot(addon)), encoded(before))

    def assert_undo(self, addon, before):
        addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))
        self.assertEqual(snapshot(addon), before)
        self.assertEqual(addon._state.review_undo_stack, [])

    def exercise_refusal(self, addon, collection):
        addon._state.player_data["crafting_level"] = 18
        addon._state.player_data["crafting_exp"] = addon.EXP_TABLE[17]
        addon.save_player_data()
        addon.load_player_data()
        before = snapshot(addon)
        before_product = product_values(addon._state.player_data)
        _answer_review(addon)
        self.assertEqual(product_values(addon._state.player_data), before_product)
        self.assert_no_opening(addon._state.player_data)
        self.assert_roundtrip(addon, collection)
        self.assert_undo(addon, before)
        self.assert_roundtrip(addon, collection)
        addon._state.player_data["crafting_level"] = 19
        addon._state.player_data["crafting_exp"] = addon.EXP_TABLE[18]

    def test_review_undo_replay_and_storage_roundtrip(self):
        with review_session() as (addon, collection, errors):
            collection.set_config = lambda key, value: collection._store.__setitem__(key, encoded(value))
            addon._state.player_data = eligible_player()
            addon._state.current_skill = "Quests"
            addon.check_achievements(addon._state.player_data)
            addon.save_player_data()
            addon.load_player_data()
            self.exercise_refusal(addon, collection)
            addon._state.current_skill = "Quests"
            addon.save_player_data()
            addon.load_player_data()
            before = snapshot(addon)
            # Same random state and ordinary clocks: isolate the quest's deltas
            # by comparing with a non-quest, no-XP Bankstanding review.
            addon._state.current_skill = "Utilities"
            addon._state.player_data["current_utility"] = "bankstanding"
            control_before = snapshot(addon)
            _answer_review(addon)
            control = copy.deepcopy(addon._state.player_data)
            self.assert_undo(addon, control_before)
            addon._state.player_data = copy.deepcopy(before["player"])
            addon._state.current_skill = before["skill"]
            random.setstate(before["random"])
            _answer_review(addon)
            earned = snapshot(addon)
            expected_goods = product_values(control)
            expected_goods["quests"][QUEST_ID] = dict(started=True, progress=2, completed=False)
            expected_goods["quest_action_proofs"] = sorted(set(expected_goods["quest_action_proofs"]) | set(OPENING_ACTIONS))
            self.assertEqual(product_values(earned["player"]), expected_goods)
            self.assert_roundtrip(addon, collection)
            self.assert_undo(addon, before)
            self.assert_roundtrip(addon, collection)
            _answer_review(addon)
            self.assertEqual(snapshot(addon), earned)
            self.assert_roundtrip(addon, collection)
            self.assertEqual(len(errors), 1)  # Only the deliberately refused review.
