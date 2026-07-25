"""Value-blind write-through probe for the Court Cases pure helpers.

`immutability_gate.py` only compares the lent save for inequality afterwards,
so it cannot see a write that stores a value equal to the one already there.
Court Cases keeps its progress in a nested `court_cases` session dict that the
review helper advances step by step, which is exactly the shape where a shallow
whole-save copy would alias the caller's live save.

The probe lends the helpers a save whose nested containers are dict/list
subclasses that raise on every mutating operation, so a write-through raises
regardless of the value written.  Subclasses rather than opaque proxies are used
deliberately: the helpers do `dict(...)`, `isinstance(x, Mapping)` and
truthiness checks on these values, so a failure here is a real defect.
"""

import copy
import unittest

from court_cases_data import COURT_CASES_ACTIVITY_ID
from court_cases_logic import (
    apply_court_case_review_pure,
    apply_court_cases_command_pure,
    court_cases_view_pure,
    enter_court_case_pure,
    leave_court_case_pure,
    select_court_trial_choice_pure,
    set_court_cases_policy_pure,
)

from tests.test_write_through_probe import _FrozenDict, _FrozenList, WriteThroughError


class _CopyableFrozenDict(_FrozenDict):
    def __deepcopy__(self, memo):
        return {key: copy.deepcopy(value, memo) for key, value in self.items()}


class _CopyableFrozenList(_FrozenList):
    def __deepcopy__(self, memo):
        return [copy.deepcopy(value, memo) for value in self]


def _freeze(value, path="save"):
    """`_freeze` from the shared probe, but deepcopy-aware.

    `copy.deepcopy` rebuilds a dict subclass by constructing it and assigning
    the keys back, which the refusal would report as a write-through even though
    deepcopy only ever touches its own new object.  These variants hand deepcopy
    a plain container so the still-deep helpers can be probed honestly.
    """
    if isinstance(value, dict):
        return _CopyableFrozenDict(
            {key: _freeze(item, f"{path}[{key!r}]") for key, item in value.items()},
            _path=path,
        )
    if isinstance(value, list):
        return _CopyableFrozenList(
            [_freeze(item, f"{path}[{index}]") for index, item in enumerate(value)],
            _path=path,
        )
    return value


def _frozen_save(save: dict) -> dict:
    """Only the nested values are frozen; the helper's own top-level copy is
    hers to write."""
    return {key: _freeze(value, f"save[{key!r}]") for key, value in save.items()}


def _idle_player() -> dict:
    return {
        "inventory": {"Court summons": 1, "Coins": 500},
        "quests": {"kings_ransom": {"completed": True}},
        "attack_level": 65,
        "attack_exp": 0.0,
        "defense_level": 65,
        "defense_exp": 0.0,
        "completed_achievements": [],
        "current_utility": COURT_CASES_ACTIVITY_ID,
        "activity_session": {"active_id": ""},
        "shop_market_clock": {"answered_cards": 4000},
        "court_cases": {},
        "court_cases_policy": {"role": "prosecution", "automation_mode": "casual"},
        "court_cases_completed_ids": [],
        "court_cases_attempts": 0,
        "court_cases_batch2_ready_at_review": 0,
        "court_cases_last_result": "Your first case is free.",
    }


def _mid_trial_player(*, mode: str = "casual") -> dict:
    """A save parked on the first trial beat, past preparation."""
    player = _idle_player()
    player["court_cases"] = {
        "version": 1,
        "case_id": "mugger",
        "role": "prosecution",
        "automation_mode": mode,
        "phase": "trial",
        "prep_index": 99,
        "trial_index": 0,
        "correct_count": 0,
        "pending_choice": "",
        "verdict_attempts": 0,
    }
    player["activity_session"] = {"active_id": COURT_CASES_ACTIVITY_ID}
    return player


def _mid_prep_player() -> dict:
    player = _idle_player()
    player["court_cases"] = {
        "version": 1,
        "case_id": "mugger",
        "role": "prosecution",
        "automation_mode": "casual",
        "phase": "preparation",
        "prep_index": 0,
        "trial_index": 0,
        "correct_count": 0,
        "pending_choice": "",
        "verdict_attempts": 0,
    }
    player["activity_session"] = {"active_id": COURT_CASES_ACTIVITY_ID}
    return player


class CourtCasesWriteThroughTest(unittest.TestCase):
    def test_probe_fixtures_survive_the_freeze(self):
        """The freeze must not change what the helpers observe."""
        for build in (_idle_player, _mid_prep_player, _mid_trial_player):
            with self.subTest(fixture=build.__name__):
                self.assertEqual(_frozen_save(build()), build())

    def test_frozen_court_session_refuses_an_equal_valued_write(self):
        """Guards against a passing probe that froze nothing."""
        frozen = _frozen_save(_mid_trial_player())
        with self.assertRaises(WriteThroughError):
            frozen["court_cases"]["trial_index"] = 0
        with self.assertRaises(WriteThroughError):
            frozen["court_cases_completed_ids"].append("mugger")

    def test_enter_never_writes_through(self):
        frozen = _frozen_save(_idle_player())
        data, ok, info = enter_court_case_pure(frozen, {"role": "prosecution"})
        self.assertTrue(ok, info)
        self.assertEqual(frozen, _idle_player(), "enter changed the save it was lent")
        self.assertEqual(data["court_cases"]["case_id"], "mugger")

    def test_set_policy_never_writes_through(self):
        frozen = _frozen_save(_idle_player())
        data, ok, info = set_court_cases_policy_pure(
            frozen, {"role": "defence", "automation_mode": "advanced"}
        )
        self.assertTrue(ok, info)
        self.assertEqual(frozen, _idle_player(), "set_policy changed the save it was lent")
        self.assertEqual(data["court_cases_policy"]["role"], "defence")

    def test_select_choice_never_writes_through(self):
        frozen = _frozen_save(_mid_trial_player(mode="advanced"))
        options = court_cases_view_pure(frozen)["trial_choices"]
        self.assertTrue(options, "fixture is not parked on a choosable trial beat")
        data, ok, info = select_court_trial_choice_pure(frozen, options[0])
        self.assertTrue(ok, info)
        self.assertEqual(
            frozen,
            _mid_trial_player(mode="advanced"),
            "select_choice changed the save it was lent",
        )
        self.assertEqual(data["court_cases"]["pending_choice"], options[0])

    def test_leave_never_writes_through(self):
        frozen = _frozen_save(_mid_trial_player())
        data, ok, info = leave_court_case_pure(frozen)
        self.assertTrue(ok, info)
        self.assertEqual(
            frozen, _mid_trial_player(), "leave changed the save it was lent"
        )
        self.assertEqual(data["court_cases"], {})

    def test_review_never_writes_through_across_a_whole_case(self):
        """The session dict advances every review; each step is checked."""
        lent = _mid_prep_player()
        steps = 0
        for _ in range(40):
            frozen = _frozen_save(lent)
            data, outcome = apply_court_case_review_pure(frozen)
            self.assertTrue(outcome.get("allowed"), outcome)
            self.assertEqual(
                frozen, lent, "a review wrote through the save it was lent"
            )
            steps += 1
            if outcome.get("terminal"):
                break
            # Carry the progress forward the way the runtime does, then re-freeze
            # so every later step of the session is probed too.
            lent = copy.deepcopy(data)
        else:
            self.fail("the case never reached a verdict")
        self.assertGreater(steps, 1, "the case finished without advancing")
        self.assertEqual(data["court_cases"], {})
        self.assertIn("mugger", data["court_cases_completed_ids"])

    def test_review_refusal_never_writes_through(self):
        """Advanced mode with no queued choice: the early-return path."""
        frozen = _frozen_save(_mid_trial_player(mode="advanced"))
        _data, outcome = apply_court_case_review_pure(frozen)
        self.assertFalse(outcome["allowed"])
        self.assertEqual(
            frozen,
            _mid_trial_player(mode="advanced"),
            "the refusal path changed the save it was lent",
        )

    def test_view_never_writes_through(self):
        frozen = _frozen_save(_mid_trial_player())
        view = court_cases_view_pure(frozen)
        self.assertEqual(frozen, _mid_trial_player(), "view changed the save it was lent")
        self.assertTrue(view["active"])

    def test_unknown_action_never_writes_through(self):
        frozen = _frozen_save(_mid_trial_player())
        data, ok, info = apply_court_cases_command_pure(frozen, "no_such_action", {})
        self.assertFalse(ok)
        self.assertIn("reason", info)
        self.assertEqual(
            frozen,
            _mid_trial_player(),
            "the unknown-action path changed the save it was lent",
        )
        self.assertEqual(data, _mid_trial_player())


if __name__ == "__main__":
    unittest.main()
