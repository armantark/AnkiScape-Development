"""Value-blind write-through probe for the Trouble Brewing helpers.

`immutability_gate.py` only compares the input save for inequality after the
call, so it cannot see a write that stores a value equal to the one already
there.  This probe removes that value dependence: the save it lends the helpers
has nested containers that refuse every mutating operation, so a write-through
raises regardless of the value written.

Trouble Brewing is the interesting case because the match session carries
per-side state — an ingredient `stores` dict, a three-element `boilers` list and
an `xp` dict — and every duty updates them with in-place `+=` on nested keys.
Those writes are only safe because `sanitize_trouble_brewing_session_pure`
rebuilds all three containers from scratch before any duty runs.

`dict`/`list` subclasses are used rather than opaque proxies deliberately: the
helpers do `dict(...)`, `isinstance(x, Mapping)` and truthiness checks on these
values, and a subclass satisfies all of that unchanged, so a failure here is a
real defect rather than an artifact of the probe.
"""

import copy
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.trouble_brewing_data import TROUBLE_BREWING_EVENT_REVIEWS
from ankiscape.logic.trouble_brewing_logic import (
    apply_trouble_brewing_command_pure,
    apply_trouble_brewing_review_pure,
    buy_trouble_brewing_reward_pure,
    enter_trouble_brewing_pure,
    leave_trouble_brewing_pure,
    set_trouble_brewing_policy_pure,
    trouble_brewing_view_pure,
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
        plain = {}
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
    player = {
        "cooking_level": 40,
        "quests": {"cabin_fever": {"completed": True}},
        "activity_session": {"active_id": ""},
        "inventory": {"Coins": 500},
        "trouble_brewing": {},
        "trouble_brewing_policy": {"automation_mode": "casual", "duty": "water"},
        "trouble_brewing_pieces_of_eight": 400,
    }
    player.update(overrides)
    return player


def _mid_game_session() -> dict:
    """A session with every per-side container already populated."""
    return {
        "version": 1,
        "review": 4,
        "stores": {
            "water": 2,
            "coloured_water": 1,
            "sweetgrubs": 1,
            "scrapey_bark": 1,
            "bitternut": 1,
        },
        "boilers": [9, 8, 7],
        "pending_bottle": True,
        "packed_rum": 1,
        "spilled_rum": 0,
        "opponent_progress": 3,
        "opponent_rum": 1,
        "opponent_slowed": 0,
        "repair_required": True,
        "contribution": 30,
        "xp": {
            "agility": 12.0,
            "cooking": 24.0,
            "crafting": 6.0,
            "firemaking": 40.0,
            "woodcutting": 18.0,
        },
        "automation_mode": "casual",
        "duty": "water",
    }


def _in_game(**overrides) -> dict:
    return _player(
        trouble_brewing=_mid_game_session(),
        activity_session={"active_id": "trouble_brewing"},
        **overrides,
    )


class TroubleBrewingWriteThroughTest(unittest.TestCase):
    def test_the_probe_itself_catches_a_write_through(self):
        """Without this, a passing probe could mean the freeze does nothing."""
        frozen = _frozen_save({"stores": {"water": 1}, "boilers": [9, 9, 9]})
        with self.assertRaises(WriteThroughError):
            frozen["stores"]["water"] = 1  # same value: the gate cannot see this
        with self.assertRaises(WriteThroughError):
            frozen["boilers"][0] = 9

    def test_frozen_save_is_equal_to_the_plain_one(self):
        """The freeze must not change what the helpers observe."""
        self.assertEqual(_frozen_save(_in_game()), _in_game())
        self.assertEqual(_frozen_save(_player()), _player())

    def test_entry_and_policy_never_write_through(self):
        for label, call in (
            ("set_policy", lambda d: set_trouble_brewing_policy_pure(d, {"duty": "sabotage"})),
            ("enter_plain", lambda d: enter_trouble_brewing_pure(d)),
            ("enter_with_policy", lambda d: enter_trouble_brewing_pure(d, {"duty": "sabotage"})),
            ("view", lambda d: trouble_brewing_view_pure(d)),
        ):
            with self.subTest(function=label):
                frozen = _frozen_save(_player())
                returned = call(frozen)
                self.assertEqual(frozen, _player(), f"{label} changed the save it was lent")
                self.assertIsNotNone(returned)

    def test_a_whole_match_of_duty_beats_never_writes_through(self):
        """Every duty updates stores, boilers and xp with nested in-place writes."""
        for mode, duty in (("casual", "water"), ("advanced", "sabotage")):
            with self.subTest(mode=mode):
                start = _in_game()
                start["trouble_brewing"]["automation_mode"] = mode
                start["trouble_brewing"]["duty"] = duty
                frozen = _frozen_save(start)
                data = frozen
                terminal = False
                for beat in range(TROUBLE_BREWING_EVENT_REVIEWS):
                    data, result = apply_trouble_brewing_review_pure(
                        data,
                        productive=True,
                        duty=duty,
                        opponent_roll=0.1 + 0.05 * beat,
                        sabotage_roll=0.02,
                    )
                    if result.get("terminal"):
                        terminal = True
                        break
                self.assertTrue(terminal, "the probed match never reached its final beat")
                self.assertEqual(
                    frozen, start, "the review helper changed the save it was lent"
                )

    def test_unproductive_review_and_leave_never_write_through(self):
        for label, call in (
            (
                "review_unproductive",
                lambda d: apply_trouble_brewing_review_pure(d, productive=False),
            ),
            ("leave", lambda d: leave_trouble_brewing_pure(d)),
            ("view_in_game", lambda d: trouble_brewing_view_pure(d)),
        ):
            with self.subTest(function=label):
                frozen = _frozen_save(_in_game())
                returned = call(frozen)
                self.assertEqual(
                    frozen, _in_game(), f"{label} changed the save it was lent"
                )
                self.assertIsNotNone(returned)

    def test_reward_purchase_never_writes_through_the_inventory(self):
        frozen = _frozen_save(_player())
        updated, ok, info = buy_trouble_brewing_reward_pure(frozen, "blue_tricorn_hat")
        self.assertTrue(ok, info)
        self.assertEqual(frozen, _player(), "the purchase wrote into the lent inventory")
        self.assertEqual(updated["inventory"]["Blue tricorn hat"], 1)

    def test_command_dispatch_never_writes_through(self):
        for action, save in (
                ("enter", _player()),
                ("leave", _in_game()),
                ("set_policy", _player()),
                ("buy_reward", _player()),
                ("no_such_action", _player()),
        ):
            with self.subTest(action=action):
                frozen = _frozen_save(save)
                updated, _ok, _info = apply_trouble_brewing_command_pure(
                    frozen, action, {"duty": "sabotage", "reward_id": "blue_tricorn_hat"}
                )
                self.assertEqual(
                    frozen, save, f"{action} changed the save it was lent"
                )
                self.assertIsInstance(updated, dict)


if __name__ == "__main__":
    unittest.main()
