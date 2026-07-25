"""Value-blind write-through probe for the Fishing Trawler pure helpers.

`immutability_gate.py` only compares the lent save for inequality afterwards, so
it cannot see a write that stores a value equal to the one already there.  The
Fishing Trawler accumulates a haul across a ten-review trip inside a nested
`fishing_trawler` session dict, and `_apply_duty` decrements the nested
`supplies` sub-dict in place, so a shallow whole-save copy that failed to rebuild
the session would spend the caller's real supplies.

The probe lends the helpers a save whose nested containers are dict/list
subclasses that raise on every mutating operation, so a write-through raises
regardless of the value written.  Subclasses rather than opaque proxies are used
deliberately: the helpers do `dict(...)`, `isinstance(x, Mapping)` and
truthiness checks on these values, so a failure here is a real defect.
"""

import copy
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.fishing_trawler_data import FISHING_TRAWLER_ACTIVITY_ID
from ankiscape.logic.fishing_trawler_logic import (
    apply_fishing_trawler_command_pure,
    apply_fishing_trawler_review_pure,
    enter_fishing_trawler_pure,
    fishing_trawler_view_pure,
    leave_fishing_trawler_pure,
    set_fishing_trawler_policy_pure,
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

    `copy.deepcopy` rebuilds a dict subclass by constructing it and assigning the
    keys back, which the refusal would report as a write-through even though
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
        "inventory": {"Swamp paste": 60, "Rope": 4, "Bailing bucket": 1},
        "fishing_level": 81,
        "fishing_exp": 0.0,
        "activity_session": {"active_id": ""},
        "fishing_trawler": {},
        "fishing_trawler_policy": {
            "automation_mode": "casual",
            "priority": "balanced",
            "layout": {"Swamp paste": 30, "Rope": 2, "Bailing bucket": 1},
        },
        "fishing_trawler_trips_completed": 0,
        "fishing_trawler_trips_sunk": 0,
        "fishing_trawler_last_result": "",
    }


def _boarded_player(*, review: int = 0) -> dict:
    """A save mid-trip, with supplies parked in the nested session dict."""
    player = _idle_player()
    player["inventory"] = {"Swamp paste": 30, "Rope": 2}
    player["activity_session"] = {"active_id": FISHING_TRAWLER_ACTIVITY_ID}
    player["fishing_trawler"] = {
        "version": 1,
        "review": review,
        "water": 20,
        "leaks": 2,
        "net_intact": False,
        "contribution": 4,
        "haul_quality": 6,
        "automation_mode": "casual",
        "priority": "balanced",
        "supplies": {"Swamp paste": 30, "Rope": 2, "Bailing bucket": 1},
    }
    return player


class FishingTrawlerWriteThroughTest(unittest.TestCase):
    def test_probe_fixtures_survive_the_freeze(self):
        """The freeze must not change what the helpers observe."""
        for build in (_idle_player, _boarded_player):
            with self.subTest(fixture=build.__name__):
                self.assertEqual(_frozen_save(build()), build())

    def test_frozen_supplies_refuse_an_equal_valued_write(self):
        """Guards against a passing probe that froze nothing."""
        frozen = _frozen_save(_boarded_player())
        with self.assertRaises(WriteThroughError):
            frozen["fishing_trawler"]["supplies"]["Rope"] = 2
        with self.assertRaises(WriteThroughError):
            frozen["inventory"]["Swamp paste"] = 30

    def test_enter_never_writes_through(self):
        frozen = _frozen_save(_idle_player())
        data, ok, info = enter_fishing_trawler_pure(frozen)
        self.assertTrue(ok, info)
        self.assertEqual(frozen, _idle_player(), "enter changed the save it was lent")
        self.assertEqual(data["fishing_trawler"]["supplies"]["Rope"], 2)

    def test_enter_with_a_policy_payload_never_writes_through(self):
        frozen = _frozen_save(_idle_player())
        data, ok, info = enter_fishing_trawler_pure(
            frozen, {"priority": "water_first", "automation_mode": "advanced"}
        )
        self.assertTrue(ok, info)
        self.assertEqual(frozen, _idle_player(), "enter changed the save it was lent")
        self.assertEqual(data["fishing_trawler"]["priority"], "water_first")

    def test_set_policy_never_writes_through(self):
        frozen = _frozen_save(_idle_player())
        data, ok, info = set_fishing_trawler_policy_pure(
            frozen, {"priority": "maintenance_first", "layout": {"Rope": 3}}
        )
        self.assertTrue(ok, info)
        self.assertEqual(
            frozen, _idle_player(), "set_policy changed the save it was lent"
        )
        self.assertEqual(data["fishing_trawler_policy"]["layout"]["Rope"], 3)

    def test_leave_never_writes_through(self):
        frozen = _frozen_save(_boarded_player())
        data, ok, info = leave_fishing_trawler_pure(frozen)
        self.assertTrue(ok, info)
        self.assertEqual(
            frozen, _boarded_player(), "leave changed the save it was lent"
        )
        # The supplies are handed back, which is where an aliased inventory
        # would have shown up.
        self.assertEqual(data["inventory"]["Rope"], 4)
        self.assertEqual(data["fishing_trawler"], {})

    def test_review_never_writes_through_across_a_whole_trip(self):
        """`_apply_duty` mutates the nested supplies dict on every review."""
        lent = _boarded_player()
        steps = 0
        for _ in range(20):
            frozen = _frozen_save(lent)
            data, outcome = apply_fishing_trawler_review_pure(frozen, 0.5)
            self.assertTrue(outcome.get("allowed"), outcome)
            self.assertEqual(
                frozen, lent, "a review wrote through the save it was lent"
            )
            steps += 1
            if outcome.get("terminal"):
                break
            # Carry the trip forward the way the runtime does, then re-freeze so
            # every later review is probed too.
            lent = copy.deepcopy(data)
        else:
            self.fail("the trip never docked")
        self.assertGreater(steps, 1, "the trip ended without advancing")
        self.assertEqual(data["fishing_trawler"], {})

    def test_review_refusal_never_writes_through(self):
        frozen = _frozen_save(_idle_player())
        _data, outcome = apply_fishing_trawler_review_pure(frozen, 0.5)
        self.assertFalse(outcome["allowed"])
        self.assertEqual(
            frozen, _idle_player(), "the refusal path changed the save it was lent"
        )

    def test_view_never_writes_through(self):
        frozen = _frozen_save(_boarded_player())
        view = fishing_trawler_view_pure(frozen)
        self.assertEqual(frozen, _boarded_player(), "view changed the save it was lent")
        self.assertTrue(view["active"])

    def test_unknown_action_never_writes_through(self):
        frozen = _frozen_save(_boarded_player())
        data, ok, info = apply_fishing_trawler_command_pure(frozen, "no_such_action", {})
        self.assertFalse(ok)
        self.assertIn("reason", info)
        self.assertEqual(
            frozen,
            _boarded_player(),
            "the unknown-action path changed the save it was lent",
        )
        self.assertEqual(data, _boarded_player())


if __name__ == "__main__":
    unittest.main()
