"""Value-blind write-through probe for the Castle Wars helpers.

Castle Wars holds a ticket wallet and spends it in the reward shop, so a leaked
nested container would corrupt currency rather than merely a scoreboard.  The
equality gate in ``tests/test_logic_no_input_mutation.py`` cannot see a write
that stores the value already present; this probe removes that blind spot by
lending the helpers a save whose nested containers refuse every mutating
operation.

``dict``/``list`` subclasses are used rather than opaque proxies deliberately:
the helpers do ``dict(...)``, ``isinstance(x, Mapping)`` and truthiness checks
on these values, and a subclass satisfies all of that unchanged, so a failure
here is a real defect rather than an artifact of the probe.
"""

import copy
import unittest
from unittest.mock import patch

from castle_wars_data import CASTLE_WARS_BALLISTA_PARTS, CASTLE_WARS_MATCH_REVIEWS

import castle_wars_logic


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


def _player(**overrides) -> dict:
    player = {
        "attack_level": 50,
        "strength_level": 50,
        "defense_level": 50,
        "constitution_level": 50,
        "ranged_level": 50,
        "magic_level": 50,
        "prayer_level": 50,
        "summoning_level": 1,
        "activity_session": {"active_id": ""},
        "combat_encounter": {},
        "current_combat_target": "chicken",
        "combat_lifepoints": 500,
        "combat_status_effects": {},
        "combat_supply_loadout": {},
        "inventory": {"Coins": 250},
        "equipment": {},
    }
    player.update(overrides)
    return player


def _entered(**overrides) -> dict:
    data, ok, info = castle_wars_logic.enter_castle_wars_pure(_player(**overrides))
    assert ok, info
    return data


def _burst(data, *_args, **_kwargs):
    """Stand-in for the combat engine: reports a survived, non-lethal round.

    The real engine is probed by its own suite; mocking it keeps this probe
    scoped to Castle Wars' own copying, which is what is under review.
    """
    encounter = dict(data.get("combat_encounter") or {})
    encounter["enemy_lifepoints"] = 390
    return {**data, "combat_encounter": encounter}, True, {
        "killed": False,
        "died": False,
        "player_damage": 110,
    }


class CastleWarsWriteThroughTest(unittest.TestCase):
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
            ("enter", lambda data: castle_wars_logic.enter_castle_wars_pure(data, {})),
            (
                "set_policy",
                lambda data: castle_wars_logic.set_castle_wars_policy_pure(
                    data, {"automation_mode": "advanced", "duty": "repair"}
                ),
            ),
        ):
            with self.subTest(function=label):
                frozen = _frozen_save(_player())
                updated, ok, info = call(frozen)
                self.assertTrue(ok, info)
                self.assertEqual(frozen, _player(), f"{label} changed the lent save")
                self.assertEqual(updated["inventory"], {"Coins": 250})

    def test_leave_never_writes_through(self):
        entered = _entered()
        frozen = _frozen_save(copy.deepcopy(entered))
        updated, ok, info = castle_wars_logic.leave_castle_wars_pure(frozen)
        self.assertTrue(ok, info)
        self.assertEqual(frozen, entered, "leave changed the save it was lent")
        self.assertEqual(updated["castle_wars"], {})

    def test_unknown_command_never_writes_through(self):
        frozen = _frozen_save(_player())
        updated, ok, info = castle_wars_logic.apply_castle_wars_command_pure(
            frozen, "no-such-action"
        )
        self.assertFalse(ok)
        self.assertIn("reason", info)
        self.assertEqual(frozen, _player(), "the rejected command changed the save")
        self.assertEqual(updated, _player())

    def test_deployments_never_write_through_the_inventory(self):
        inventory = {item: 1 for item in CASTLE_WARS_BALLISTA_PARTS}
        inventory["Castlewars chinchompa"] = 1
        entered = _entered(inventory=inventory)
        for label, call in (
            ("ballista", castle_wars_logic.deploy_castle_wars_ballista_pure),
            ("chinchompa", castle_wars_logic.deploy_castle_wars_chinchompa_pure),
        ):
            with self.subTest(function=label):
                frozen = _frozen_save(copy.deepcopy(entered))
                updated, ok, info = call(frozen)
                self.assertTrue(ok, info)
                self.assertEqual(
                    frozen, entered, f"{label} changed the save it was lent"
                )
                self.assertEqual(frozen["inventory"]["Castlewars chinchompa"], 1)
                self.assertEqual(updated["castle_wars"]["contribution"], 2 if label == "chinchompa" else 0)

    def test_shop_never_writes_through_the_wallet_or_inventory(self):
        shopper = _player(
            castle_wars_tickets=4,
            castle_wars_games_played=500,
            inventory={"Coins": 250, "Castle wars hobbyist cape": 1},
        )
        for label, call in (
            ("buy", castle_wars_logic.buy_castle_wars_reward_pure),
            ("sell", castle_wars_logic.sell_castle_wars_reward_pure),
        ):
            with self.subTest(function=label):
                frozen = _frozen_save(copy.deepcopy(shopper))
                updated, ok, info = call(frozen, "hobbyist_cape")
                self.assertTrue(ok, info)
                self.assertEqual(frozen, shopper, f"{label} changed the lent save")
                self.assertEqual(frozen["inventory"]["Castle wars hobbyist cape"], 1)
                expected = 2 if label == "buy" else 0
                self.assertEqual(
                    updated["inventory"]["Castle wars hobbyist cape"], expected
                )
                self.assertNotEqual(updated["castle_wars_tickets"], 4)

    def test_defend_round_never_writes_through(self):
        """Covers the encounter handoff between the session and the engine."""
        entered = _entered()
        frozen = _frozen_save(copy.deepcopy(entered))
        with patch.object(
            castle_wars_logic, "apply_combat_burst_pure", side_effect=_burst
        ):
            updated, ok, result = castle_wars_logic.apply_castle_wars_review_pure(
                frozen, lambda: 0.5, productive=True, duty="defend"
            )
        self.assertTrue(ok, result)
        self.assertEqual(frozen, entered, "the round changed the save it was lent")
        self.assertEqual(updated["castle_wars"]["contribution"], 110)

    def test_noncombat_duties_never_write_through(self):
        entered = _entered()
        for duty in ("capture", "barricade", "repair", "catapult", "support"):
            with self.subTest(duty=duty):
                frozen = _frozen_save(copy.deepcopy(entered))
                updated, ok, result = castle_wars_logic.apply_castle_wars_review_pure(
                    frozen, lambda: 0.5, productive=True, duty=duty
                )
                self.assertTrue(ok, result)
                self.assertEqual(
                    frozen, entered, f"the {duty} duty changed the save it was lent"
                )
                self.assertEqual(updated["castle_wars"]["review"], 1)

    def test_terminal_settlement_never_writes_through_the_wallet(self):
        data = _entered()
        for _ in range(CASTLE_WARS_MATCH_REVIEWS):
            before = copy.deepcopy(data)
            frozen = _frozen_save(before)
            data, ok, result = castle_wars_logic.apply_castle_wars_review_pure(
                frozen, lambda: 0.5, productive=True, duty="capture"
            )
            self.assertTrue(ok, result)
            self.assertEqual(frozen, before, "a match beat changed the lent save")
        self.assertTrue(result["terminal"])
        self.assertEqual(data["castle_wars_tickets"], result["tickets"])

    def test_unrunnable_combat_returns_the_save_without_writing_through(self):
        entered = _entered()
        frozen = _frozen_save(copy.deepcopy(entered))

        def broken_burst(data, *_args, **_kwargs):
            return data, False, {"reason": "no such enemy"}

        with patch.object(
            castle_wars_logic, "apply_combat_burst_pure", side_effect=broken_burst
        ):
            updated, ok, result = castle_wars_logic.apply_castle_wars_review_pure(
                frozen, lambda: 0.5, productive=True, duty="defend"
            )
        self.assertFalse(ok)
        self.assertIn("reason", result)
        self.assertEqual(frozen, entered, "the failed round changed the lent save")
        self.assertEqual(updated, entered, "the failure path must return the save as-is")


if __name__ == "__main__":
    unittest.main()
