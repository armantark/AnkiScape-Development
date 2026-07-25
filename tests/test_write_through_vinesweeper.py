"""Value-blind write-through probe for the Vinesweeper helpers.

`immutability_gate.py` only compares the input save for inequality after the
call, so it cannot see a write that stores a value equal to the one already
there.  This probe removes that value dependence: the save it lends the helpers
has nested containers that refuse every mutating operation, so a write-through
raises regardless of the value written.

Vinesweeper is the interesting case because the board round buys replacement
flags and Ogleroots out of `inventory` mid-loop, and entry hands the save to the
pet and familiar dismissal helpers, which own `summoning_state`.  Those are the
two nested containers a shallow copy would alias.

`dict`/`list` subclasses are used rather than opaque proxies deliberately: the
helpers do `dict(...)`, `isinstance(x, Mapping)` and truthiness checks on these
values, and a subclass satisfies all of that unchanged, so a failure here is a
real defect rather than an artifact of the probe.
"""

import copy
import unittest

from summoning_logic import default_summoning_state_pure
from vinesweeper_logic import (
    apply_vinesweeper_command_pure,
    apply_vinesweeper_review_pure,
    default_vinesweeper_state_pure,
    vinesweeper_view_pure,
)


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
        # `copy.deepcopy` rebuilds a dict subclass by calling __setitem__ on the
        # *copy*, which is not a write into the lent container.  Returning a
        # plain dict keeps the still-unconverted deep-copy sites from tripping
        # the probe falsely, which is what lets step 2 of the method run.
        plain: dict = {}
        memo[id(self)] = plain
        for key, value in self.items():
            plain[copy.deepcopy(key, memo)] = copy.deepcopy(value, memo)
        return plain


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
        plain: list = []
        memo[id(self)] = plain
        for value in list.__iter__(self):
            plain.append(copy.deepcopy(value, memo))
        return plain


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


def _player(**overrides) -> dict:
    data = {
        "inventory": {"Spade": 1, "Coins": 10_000, "Compost": 2},
        "toolbelt": {"tools": ["Spade"]},
        "farming_level": 40,
        "farming_exp": 0.0,
        "hunter_level": 1,
        "hunter_exp": 0.0,
        "summoning_level": 1,
        "summoning_state": default_summoning_state_pure(),
        "vinesweeper": default_vinesweeper_state_pure(),
        "current_utility": "vinesweeper",
    }
    data.update(overrides)
    return data


def _pet_follower_save() -> dict:
    state = default_summoning_state_pure()
    state["active_follower"] = {"kind": "pet", "entity_id": "probe-1"}
    state["pet_instances"] = {
        "probe-1": {
            "pet_id": "bulldog",
            "stage": 0,
            "growth": 10.0,
            "hunger": 80.0,
            "location": "active",
            "variant": 0,
            "name": "Probe",
            "policy_lapse_reason": "",
        }
    }
    return _player(summoning_state=state)


def _familiar_follower_save() -> dict:
    state = default_summoning_state_pure()
    state["active_follower"] = {
        "kind": "familiar",
        "entity_id": "spiritwolf",
        "remaining_reviews": 10,
        "max_reviews": 10,
        "lifepoints": 400,
        "max_lifepoints": 400,
        "storage": {},
    }
    return _player(summoning_state=state, summoning_level=10)


def _unknown_follower_save(kind: str) -> dict:
    state = default_summoning_state_pure()
    state["active_follower"] = {"kind": kind, "entity_id": "probe-1"}
    return _player(summoning_state=state)


def _active_board(**state_overrides) -> dict:
    board = default_vinesweeper_state_pure()
    board.update({"active": True, "free_flags_claimed": True, "flags": 5, "points": 400})
    board.update(state_overrides)
    return _player(vinesweeper=board)


class VinesweeperWriteThroughTest(unittest.TestCase):
    def test_the_probe_itself_catches_a_write_through(self):
        """Without this, a passing probe could mean the freeze does nothing."""
        frozen = _frozen_save({"inventory": {"Coins": 5}, "tools": ["Spade"]})
        with self.assertRaises(WriteThroughError):
            frozen["inventory"]["Coins"] = 5  # same value: the gate cannot see this
        with self.assertRaises(WriteThroughError):
            frozen["tools"].append("Spade")

    def test_frozen_save_is_equal_to_the_plain_one(self):
        """The freeze must not change what the helpers observe."""
        self.assertEqual(_frozen_save(_player()), _player())
        self.assertEqual(_frozen_save(_pet_follower_save()), _pet_follower_save())

    def test_a_full_board_round_never_writes_through_the_inventory(self):
        """Flag replacement and Ogleroot purchases both spend from `inventory`."""
        rolls = (0.02, 0.30, 0.50, 0.70, 0.85, 0.92, 0.97, 0.99, 0.44, 0.46)
        start = _active_board(flags=1, points=60, ogleroots=1)
        frozen = _frozen_save(start)
        updated, result = apply_vinesweeper_review_pure(
            frozen, rolls, operations=len(rolls)
        )
        self.assertEqual(frozen, start, "the review helper changed the save it was lent")
        self.assertGreater(result["completed_operations"], 0)
        self.assertNotEqual(updated["inventory"]["Coins"], start["inventory"]["Coins"])

    def test_a_flagless_broke_board_pauses_without_writing_through(self):
        start = _active_board(flags=0, points=0)
        start["inventory"] = {"Spade": 1, "Coins": 0}
        frozen = _frozen_save(start)
        _updated, result = apply_vinesweeper_review_pure(frozen, (0.50,))
        self.assertEqual(frozen, start, "the paused round changed the save it was lent")
        self.assertTrue(result["paused"])

    def test_entry_never_writes_through_for_any_follower_shape(self):
        for label, builder in (
            ("no_follower", _player),
            ("pet_follower", _pet_follower_save),
            ("familiar_follower", _familiar_follower_save),
            ("blank_kind_follower", lambda: _unknown_follower_save("")),
            ("undismissable_follower", lambda: _unknown_follower_save("beast")),
        ):
            with self.subTest(follower=label):
                start = builder()
                frozen = _frozen_save(start)
                updated, ok, info = apply_vinesweeper_command_pure(
                    frozen, "enter", {"confirm_dismiss_follower": True}
                )
                self.assertEqual(
                    frozen, start, f"entry with {label} changed the save it was lent"
                )
                if label == "undismissable_follower":
                    self.assertFalse(ok, info)
                else:
                    self.assertTrue(ok, info)
                    self.assertTrue(updated["vinesweeper"]["active"])

    def test_shop_and_redemption_commands_never_write_through(self):
        for label, action, payload in (
            ("leave_with_refund", "leave", {}),
            ("buy_flag", "buy_reward", {"reward_id": "flag", "quantity": 2}),
            ("buy_item", "buy_reward", {"reward_id": "compost_potion_4", "quantity": 1}),
            ("redeem_xp", "redeem_farming_xp", {"points": 100}),
            ("unknown_action", "no_such_action", {}),
            ("unconfirmed_entry", "enter", {}),
        ):
            with self.subTest(command=label):
                start = _active_board(ogleroots=4)
                frozen = _frozen_save(start)
                updated, _ok, _info = apply_vinesweeper_command_pure(
                    frozen, action, payload
                )
                self.assertEqual(
                    frozen, start, f"{label} changed the save it was lent"
                )
                self.assertIsInstance(updated, dict)

    def test_the_view_never_writes_through(self):
        start = _active_board()
        frozen = _frozen_save(start)
        view = vinesweeper_view_pure(frozen)
        self.assertEqual(frozen, start, "the view changed the save it was lent")
        self.assertTrue(view["has_spade"])


if __name__ == "__main__":
    unittest.main()
