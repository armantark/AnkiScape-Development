"""Value-blind write-through probe for big_chinchompa_logic.

Every helper in that module builds its working copy through
`ensure_big_chinchompa_state_pure`, which is a shallow copy of the save.  An
equality gate cannot see a write that stores a value equal to the one already
present, so this probe lends each helper a save whose nested containers refuse
every mutating operation: a write through the shallow copy raises immediately
no matter what value is written.

The paths that matter most are the ones that touch containers `ensure_` does
not rebuild — the inventory, the per-target carried packs, and the world clock —
because those are the keys the shallow copy still shares with the caller.

`dict`/`list` subclasses are used rather than opaque proxies deliberately: the
helpers do `dict(...)`, `isinstance(x, Mapping)` and truthiness checks on these
values, and a subclass satisfies all of that unchanged, so a failure here is a
real defect rather than an artifact of the probe.
"""

import copy
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.big_chinchompa_data import BIG_CHINCHOMPA_REWARDS_BY_ID
from ankiscape.logic.big_chinchompa_logic import (
    advance_big_chinchompa_world_clock_pure,
    apply_big_chinchompa_review_pure,
    apply_big_chinchompa_reward_purchase_pure,
    big_chinchompa_view_pure,
    consume_hunter_quota_ticket_pure,
    default_big_chinchompa_state_pure,
    ensure_big_chinchompa_state_pure,
    hunter_private_ground_status_pure,
    set_hunter_private_ground_pure,
    set_world_population_profile_pure,
)
from ankiscape.core.constants import EXP_TABLE


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
        return _thaw(self, memo)


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
        return _thaw(self, memo)


def _thaw(value, memo):
    """Deep-copy a frozen container into a plain, writable one.

    A helper that genuinely deep-copies the save owns the result, so the copy
    must accept writes; without this hook `copy.deepcopy` rebuilds the subclass
    through `__setitem__` and the probe would flag its own copy as a leak.
    """
    if isinstance(value, dict):
        copied = {}
        memo[id(value)] = copied
        for key, item in value.items():
            copied[copy.deepcopy(key, memo)] = copy.deepcopy(item, memo)
        return copied
    copied = []
    memo[id(value)] = copied
    copied.extend(copy.deepcopy(item, memo) for item in value)
    return copied


def _freeze(value, path="save"):
    """Freeze nested containers. The top level stays a plain dict."""
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


def _frozen(save: dict) -> dict:
    return {key: _freeze(value, f"save[{key!r}]") for key, value in save.items()}


_TICKET = "Swamp lizard quota ticket"
_TARGET = "catch_swamp_lizard"


def _player(answered_cards: int = 0, hunter_level: int = 1, **overrides) -> dict:
    save = {
        "shop_market_clock": {"answered_cards": answered_cards},
        "hunter_level": hunter_level,
        "hunter_exp": 0.0,
        "inventory": {},
        "carried_inventory": {},
        "big_chinchompa": default_big_chinchompa_state_pure(),
        "world_population_profile": "normal",
        "hunter_private_ground_targets": [],
    }
    save.update(overrides)
    return save


def _in_event(answered_cards: int = 61, hunter_level: int = 60) -> dict:
    """A save with a live event, spawned without the helpers under test."""

    player = _player(60, hunter_level)
    player, events = advance_big_chinchompa_world_clock_pure(player)
    assert events and events[0]["kind"] == "spawned"
    player["shop_market_clock"] = {"answered_cards": answered_cards}
    return player


def _ticket_holder() -> dict:
    return _player(
        inventory={_TICKET: 2},
        carried_inventory={_TARGET: {_TICKET: 2}},
        hunter_level=60,
    )


class BigChinchompaWriteThroughTest(unittest.TestCase):
    def test_the_probe_itself_catches_a_write_through(self):
        """Without this, a passing probe could mean the freeze does nothing."""
        frozen = _frozen({"nested": {"count": 1}, "rows": [1, 2]})
        with self.assertRaises(WriteThroughError):
            frozen["nested"]["count"] = 1  # same value: the gate cannot see this
        with self.assertRaises(WriteThroughError):
            frozen["rows"].append(3)

    def test_frozen_save_is_equal_to_the_plain_one(self):
        """The freeze must not change what the helpers observe."""
        self.assertEqual(_frozen(_player()), _player())
        self.assertEqual(_frozen(copy.deepcopy(_in_event())), _in_event())

    def test_ensure_never_writes_through(self):
        original = _player(60, hunter_level=30)
        frozen = _frozen(original)
        data = ensure_big_chinchompa_state_pure(frozen)
        data["big_chinchompa"]["competence_points"] = 99
        data["hunter_private_ground_targets"].append(_TARGET)
        self.assertEqual(frozen, original)
        self.assertEqual(frozen["big_chinchompa"]["competence_points"], 0)

    def test_world_clock_never_writes_through(self):
        for label, save in (
            ("spawn", _player(60)),
            ("tick", _in_event(61)),
            ("resolve", _in_event(63)),
        ):
            with self.subTest(phase=label):
                original = copy.deepcopy(save)
                frozen = _frozen(save)
                data, events = advance_big_chinchompa_world_clock_pure(frozen)
                self.assertEqual(frozen, original)
                self.assertIsInstance(events, tuple)
                self.assertIsInstance(data["big_chinchompa"], dict)

    def test_review_never_writes_through(self):
        original = _in_event()
        frozen = _frozen(original)
        data, ok, info = apply_big_chinchompa_review_pure(frozen, circuits=3)
        self.assertTrue(ok)
        self.assertEqual(frozen, original)
        self.assertEqual(info["circuits"], 3)
        self.assertGreater(
            data["big_chinchompa"]["active_event"]["event_points"], 0
        )

        idle = _player()
        frozen = _frozen(idle)
        _, ok, info = apply_big_chinchompa_review_pure(frozen)
        self.assertFalse(ok)
        self.assertEqual(frozen, idle)
        self.assertIn("No Big Chinchompa event", info["reason"])

    def test_population_profile_never_writes_through(self):
        original = _player()
        frozen = _frozen(original)
        data, ok, info = set_world_population_profile_pure(frozen, "quiet")
        self.assertTrue(ok)
        self.assertEqual(frozen, original)
        self.assertEqual(data["world_population_profile"], "quiet")
        self.assertEqual(info["profile"], "quiet")

        frozen = _frozen(original)
        _, ok, info = set_world_population_profile_pure(frozen, "nonsense")
        self.assertFalse(ok)
        self.assertEqual(frozen, original)
        self.assertIn("Unknown world-population profile", info["reason"])

    def test_reward_purchase_never_writes_through(self):
        """The item branch rebuilds the inventory the shallow copy still shares."""
        reward = BIG_CHINCHOMPA_REWARDS_BY_ID["swamp_lizard_ticket"]
        state = default_big_chinchompa_state_pure()
        state["competence_points"] = reward.competence_cost
        rich = _player(
            hunter_level=reward.hunter_level,
            big_chinchompa=state,
            inventory={_TICKET: 1},
        )
        frozen = _frozen(rich)
        data, ok, info = apply_big_chinchompa_reward_purchase_pure(
            frozen, reward.id, exp_table=EXP_TABLE
        )
        self.assertTrue(ok)
        self.assertEqual(frozen, rich)
        self.assertEqual(data["inventory"][_TICKET], 2)
        self.assertEqual(info["competence_points"], 0)

        for label, save, reward_id in (
            ("unknown", _player(), "no_such_reward"),
            ("level", _player(hunter_level=1), reward.id),
            ("wallet", _player(hunter_level=reward.hunter_level), reward.id),
        ):
            with self.subTest(refusal=label):
                frozen = _frozen(save)
                _, ok, info = apply_big_chinchompa_reward_purchase_pure(
                    frozen, reward_id
                )
                self.assertFalse(ok)
                self.assertEqual(frozen, save)
                self.assertTrue(info["reason"])

    def test_private_ground_toggle_never_writes_through(self):
        original = _ticket_holder()
        frozen = _frozen(original)
        data, ok, info = set_hunter_private_ground_pure(frozen, _TARGET, True)
        self.assertTrue(ok)
        self.assertEqual(frozen, original)
        self.assertEqual(data["hunter_private_ground_targets"], [_TARGET])
        self.assertEqual(info["ticket"], _TICKET)

        configured = _ticket_holder()
        configured["hunter_private_ground_targets"] = [_TARGET]
        frozen = _frozen(configured)
        data, ok, _ = set_hunter_private_ground_pure(frozen, _TARGET, False)
        self.assertTrue(ok)
        self.assertEqual(frozen, configured)
        self.assertEqual(data["hunter_private_ground_targets"], [])

        broke = _player(hunter_level=60)
        frozen = _frozen(broke)
        _, ok, info = set_hunter_private_ground_pure(frozen, _TARGET, True)
        self.assertFalse(ok)
        self.assertEqual(frozen, broke)
        self.assertIn(_TICKET, info["reason"])

    def test_quota_ticket_consumption_never_writes_through(self):
        """This is the path that rewrites the per-target carried pack."""
        configured = _ticket_holder()
        configured["hunter_private_ground_targets"] = [_TARGET]
        frozen = _frozen(configured)
        data, ticket = consume_hunter_quota_ticket_pure(frozen, _TARGET)
        self.assertEqual(ticket, _TICKET)
        self.assertEqual(frozen, configured)
        self.assertEqual(data["carried_inventory"][_TARGET][_TICKET], 1)
        self.assertEqual(data["inventory"][_TICKET], 1)

        last = _ticket_holder()
        last["inventory"] = {_TICKET: 1}
        last["carried_inventory"] = {_TARGET: {_TICKET: 1}}
        last["hunter_private_ground_targets"] = [_TARGET]
        frozen = _frozen(last)
        data, ticket = consume_hunter_quota_ticket_pure(frozen, _TARGET)
        self.assertEqual(ticket, _TICKET)
        self.assertEqual(frozen, last)
        self.assertEqual(data["carried_inventory"][_TARGET], {})
        self.assertEqual(data["hunter_private_ground_targets"], [])

        unconfigured = _ticket_holder()
        frozen = _frozen(unconfigured)
        data, ticket = consume_hunter_quota_ticket_pure(frozen, _TARGET)
        self.assertEqual(ticket, "")
        self.assertEqual(frozen, unconfigured)

    def test_read_only_helpers_never_write_through(self):
        original = _in_event()
        frozen = _frozen(original)
        view = big_chinchompa_view_pure(frozen)
        status = hunter_private_ground_status_pure(frozen, _TARGET)
        self.assertEqual(frozen, original)
        self.assertTrue(view["active"])
        self.assertFalse(status["configured"])


if __name__ == "__main__":
    unittest.main()
