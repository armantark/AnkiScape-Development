"""Value-blind write-through probe for the TzHaar Fight Pit helpers.

The Fight Pit credits TokKul into ``inventory`` and keeps a mutable roster in
``tzhaar_fight_pit``, so a leaked nested container would corrupt the player's
purse rather than merely a scoreboard.  The equality gate in
``tests/test_logic_no_input_mutation.py`` cannot see a write that stores the
value already present; this probe removes that blind spot by lending the
helpers a save whose nested containers refuse every mutating operation.

``dict``/``list`` subclasses are used rather than opaque proxies deliberately:
the helpers do ``dict(...)``, ``isinstance(x, Mapping)`` and truthiness checks
on these values, and a subclass satisfies all of that unchanged, so a failure
here is a real defect rather than an artifact of the probe.
"""

import copy
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic import tzhaar_fight_pit_logic


class WriteThroughError(AssertionError):
    """Raised the moment a helper writes into a container it was only lent."""


class _FrozenDict(dict):
    __slots__ = ("_path",)

    def __init__(self, *args, _path: str = "save", **kwargs):
        super().__init__(*args, **kwargs)
        object.__setattr__(self, "_path", _path)

    def _refuse(self, operation: str):
        raise WriteThroughError(
            f"{operation} on {object.__getattribute__(self, '_path')}: the helper "
            "wrote through a nested value of the save it was given"
        )

    def __setitem__(self, key, value):
        self._refuse(f"__setitem__({key!r})")

    def __delitem__(self, key):
        self._refuse(f"__delitem__({key!r})")

    def update(self, *args, **kwargs):
        self._refuse("update()")

    def setdefault(self, key, default=None):
        self._refuse(f"setdefault({key!r})")

    def pop(self, *args, **kwargs):
        self._refuse("pop()")

    def popitem(self):
        self._refuse("popitem()")

    def clear(self):
        self._refuse("clear()")

    def __deepcopy__(self, memo):
        # Copying a lent container is legitimate; only writing into it is not.
        # ``copy.deepcopy`` would otherwise rebuild the subclass through
        # ``__setitem__`` and trip the refusal on the copy, not the original.
        copied: dict = {}
        memo[id(self)] = copied
        copied.update({key: copy.deepcopy(value, memo) for key, value in self.items()})
        return copied


class _FrozenList(list):
    __slots__ = ("_path",)

    def __init__(self, *args, _path: str = "save", **kwargs):
        super().__init__(*args, **kwargs)
        object.__setattr__(self, "_path", _path)

    def _refuse(self, operation: str):
        raise WriteThroughError(
            f"{operation} on {object.__getattribute__(self, '_path')}: the helper "
            "wrote through a nested value of the save it was given"
        )

    def append(self, value):
        self._refuse("append()")

    def extend(self, values):
        self._refuse("extend()")

    def insert(self, index, value):
        self._refuse("insert()")

    def remove(self, value):
        self._refuse("remove()")

    def pop(self, *args):
        self._refuse("pop()")

    def sort(self, **kwargs):
        self._refuse("sort()")

    def clear(self):
        self._refuse("clear()")

    def __setitem__(self, index, value):
        self._refuse(f"__setitem__({index!r})")

    def __delitem__(self, index):
        self._refuse(f"__delitem__({index!r})")

    def __deepcopy__(self, memo):
        copied: list = []
        memo[id(self)] = copied
        copied.extend(copy.deepcopy(value, memo) for value in self)
        return copied


def _freeze(value, path="save"):
    """Freeze nested containers. The top level stays a plain dict.

    Only the *nested* values matter: every helper under test is expected to
    build its own top-level copy, and writing into that copy is correct.
    """
    if isinstance(value, dict):
        return _FrozenDict(
            {key: _freeze(item, f"{path}[{key!r}]") for key, item in value.items()},
            _path=path,
        )
    if isinstance(value, list):
        return _FrozenList(
            [_freeze(item, f"{path}[{index}]") for index, item in enumerate(value)],
            _path=path,
        )
    return value


def _frozen_save(save: dict) -> dict:
    return {key: _freeze(value, f"save[{key!r}]") for key, value in save.items()}


def _player(**changes) -> dict:
    data = {
        "attack_level": 60,
        "strength_level": 60,
        "defense_level": 60,
        "constitution_level": 60,
        "ranged_level": 1,
        "magic_level": 1,
        "prayer_level": 43,
        "summoning_level": 1,
        "combat_lifepoints": 600,
        "inventory": {"Coins": 250, "Tokkul": 40},
        "equipment": {},
        "activity_session": {"active_id": ""},
        "combat_encounter": {},
        "combat_status_effects": {},
        "current_combat_target": "chicken",
    }
    data.update(changes)
    return data


def _entered(**changes) -> dict:
    """A save mid-match, ready to be frozen and lent to the review helper."""
    entered, ok, _info = tzhaar_fight_pit_logic.enter_tzhaar_fight_pit_pure(
        _player(**changes)
    )
    assert ok, "the fixture must be able to enter the pit"
    return entered


def _burst(data, *_args, **_kwargs):
    """Stand-in for the combat engine: reports a survived, non-lethal round.

    The real engine is probed by its own suite; mocking it keeps this probe
    scoped to the Fight Pit's own copying, which is what is under review.
    """
    return {**data, "combat_encounter": {"enemy_lifepoints": 90}}, True, {
        "killed": False,
        "died": False,
        "ticks_elapsed": 6,
    }


class FightPitWriteThroughTest(unittest.TestCase):
    def test_the_probe_itself_catches_a_write_through(self):
        """Without this, a passing probe could mean the freeze does nothing."""
        frozen = _frozen_save({"nested": {"count": 1}, "rows": [1, 2]})
        with self.assertRaises(WriteThroughError):
            frozen["nested"]["count"] = 1  # same value: the gate cannot see this
        with self.assertRaises(WriteThroughError):
            frozen["rows"].append(3)

    def test_frozen_save_is_equal_to_the_plain_one(self):
        """The freeze must not change what the helpers observe."""
        self.assertEqual(_frozen_save(_player()), _player())
        self.assertEqual(_frozen_save(copy.deepcopy(_entered())), _entered())

    def test_entry_and_policy_never_write_through(self):
        for label, call in (
            ("enter", tzhaar_fight_pit_logic.enter_tzhaar_fight_pit_pure),
            (
                "set_policy",
                lambda data: tzhaar_fight_pit_logic.set_tzhaar_fight_pit_policy_pure(
                    data, "aggressive"
                ),
            ),
        ):
            with self.subTest(function=label):
                frozen = _frozen_save(_player())
                updated, ok, _info = call(frozen)
                self.assertTrue(ok, f"{label} refused the fixture")
                self.assertEqual(frozen, _player(), f"{label} changed the lent save")
                self.assertEqual(updated["inventory"], _player()["inventory"])
                self.assertIsNot(updated, frozen)

    def test_leave_never_writes_through_and_forfeits_the_purse(self):
        entered = _entered()
        entered["tzhaar_fight_pit"]["pending_tokkul"] = 90
        frozen = _frozen_save(copy.deepcopy(entered))
        updated, ok, result = tzhaar_fight_pit_logic.leave_tzhaar_fight_pit_pure(frozen)
        self.assertTrue(ok)
        self.assertEqual(result["forfeited_tokkul"], 90)
        self.assertEqual(frozen, entered, "leave changed the save it was lent")
        self.assertEqual(updated["inventory"]["Tokkul"], 40)

    def test_unknown_command_never_writes_through(self):
        frozen = _frozen_save(_player())
        updated, ok, info = tzhaar_fight_pit_logic.apply_tzhaar_fight_pit_command_pure(
            frozen, "no-such-action"
        )
        self.assertFalse(ok)
        self.assertIn("reason", info)
        self.assertEqual(frozen, _player(), "the rejected command changed the save")
        self.assertEqual(updated, _player())

    def test_review_round_never_writes_through(self):
        """Covers the roster, engaged-encounter and next-encounter handoff."""
        entered = _entered()
        frozen = _frozen_save(copy.deepcopy(entered))
        with patch.object(
            tzhaar_fight_pit_logic, "apply_combat_burst_pure", side_effect=_burst
        ):
            updated, ok, result = (
                tzhaar_fight_pit_logic.apply_tzhaar_fight_pit_review_pure(frozen)
            )
        self.assertTrue(ok, result.get("reason"))
        self.assertEqual(frozen, entered, "the review changed the save it was lent")
        self.assertEqual(updated["tzhaar_fight_pit"]["review"], 1)

    def test_win_settlement_never_writes_through_the_purse(self):
        entered = _entered(equipment={"cape": "Fire cape"})
        session = entered["tzhaar_fight_pit"]
        victim = session["roster"][0]
        session["roster"] = [victim]
        session["engaged_opponent_id"] = victim["opponent_id"]
        session["pending_tokkul"] = 100
        frozen = _frozen_save(copy.deepcopy(entered))

        def killing_burst(data, *_args, **_kwargs):
            return {**data, "combat_encounter": {}}, True, {
                "killed": True,
                "died": False,
                "ticks_elapsed": 1,
            }

        with patch.object(
            tzhaar_fight_pit_logic, "apply_combat_burst_pure", side_effect=killing_burst
        ):
            updated, ok, result = (
                tzhaar_fight_pit_logic.apply_tzhaar_fight_pit_review_pure(frozen)
            )
        self.assertTrue(ok)
        expected = (100 + victim["combat_level"]) * 2
        self.assertEqual(result["tokkul"], expected)
        self.assertEqual(updated["inventory"]["Tokkul"], 40 + expected)
        self.assertEqual(frozen, entered, "the payout wrote into the lent purse")
        self.assertEqual(frozen["inventory"]["Tokkul"], 40)

    def test_unrunnable_combat_returns_the_save_without_writing_through(self):
        entered = _entered()
        frozen = _frozen_save(copy.deepcopy(entered))

        def broken_burst(data, *_args, **_kwargs):
            return data, False, {"reason": "no such enemy"}

        with patch.object(
            tzhaar_fight_pit_logic, "apply_combat_burst_pure", side_effect=broken_burst
        ):
            updated, ok, result = (
                tzhaar_fight_pit_logic.apply_tzhaar_fight_pit_review_pure(frozen)
            )
        self.assertFalse(ok)
        self.assertIn("combat", result)
        self.assertEqual(frozen, entered, "the failed round changed the lent save")
        self.assertEqual(updated, entered, "the failure path must return the save as-is")


if __name__ == "__main__":
    unittest.main()
