"""Value-blind write-through probe for the Soul Wars helpers.

`immutability_gate.py` detects a leak by comparing the input save for
inequality after the call.  That misses a write which stores a value equal to
the one already present: real write-through, invisible on the fixture, and a
live-save corruption on different data.  Soul Wars is the worst place for that
to happen, because the same call graph carries the Zeal wallet and the state of
a match already in progress.

This probe removes the value dependence.  It lends the helper a save whose
nested containers refuse every mutating operation, so a write through one of
them raises no matter what value is written.  `dict`/`list` subclasses are used
rather than opaque proxies because the helpers do `dict(...)`,
`isinstance(x, Mapping)` and truthiness checks on these values, and a subclass
satisfies all of that unchanged; a failure here is a real defect rather than an
artifact of the probe.  `__deepcopy__` is honoured, since copying a lent
container is reading it, not writing to it.
"""

from __future__ import annotations

import copy
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.soul_wars_data import (
    SOUL_WARS_ACTIVITY_ID,
    SOUL_WARS_ACTIVITY_MAX,
    SOUL_WARS_CHARM_REWARDS_BY_ITEM,
    SOUL_WARS_EVENT_REVIEWS,
)
from ankiscape.logic.soul_wars_logic import (
    apply_soul_wars_command_pure,
    apply_soul_wars_review_pure,
    buy_soul_wars_charms_pure,
    enter_soul_wars_pure,
    leave_soul_wars_pure,
    set_soul_wars_policy_pure,
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

    def __copy__(self):
        return {key: value for key, value in self.items()}

    def __deepcopy__(self, memo):
        return {copy.deepcopy(k, memo): copy.deepcopy(v, memo) for k, v in self.items()}


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

    def __copy__(self):
        return list(self)

    def __deepcopy__(self, memo):
        return [copy.deepcopy(item, memo) for item in self]


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


def _player(**overrides):
    player = {
        "attack_level": 40,
        "strength_level": 40,
        "defense_level": 40,
        "constitution_level": 40,
        "ranged_level": 40,
        "magic_level": 40,
        "prayer_level": 40,
        "slayer_level": 100,
        "summoning_level": 40,
        "combat_lifepoints": 400,
        "combat_prayer_points": 100,
        "combat_special_attack_energy": 5,
        "agility_run_energy_credit_pct": 0,
        "summoning_state": {"summoning_points_current": 2, "pet_instances": {}},
        "activity_session": {"active_id": ""},
        "combat_encounter": {},
        "current_combat_target": "chicken",
        "current_utility": "gnome_restaurant",
        "combat_supply_loadout": {"food": {}},
        "inventory": {"Coins": 500},
        "equipment": {},
    }
    player.update(overrides)
    return player


def _entered(**overrides):
    payload = overrides.pop("payload", None)
    data, ok, info = enter_soul_wars_pure(_player(**overrides), payload)
    assert ok, info
    return data


def _combat_stub(*, damage=500, died=False, ok=True):
    """Deterministic stand-in for the combat engine.

    The real engine copies its own input, so the interesting question for this
    probe is what the Soul Wars code does with what the engine hands back.
    """

    def _apply(data, enemies, _equipment, **_kwargs):
        if not ok:
            return data, False, {"reason": "combat_locked", "locked_reasons": ("probe",)}
        updated = copy.deepcopy(data)
        encounter = dict(updated["combat_encounter"])
        before = int(encounter["enemy_lifepoints"])
        after = max(0, before - damage)
        encounter["enemy_lifepoints"] = after
        updated["combat_encounter"] = encounter
        updated["combat_lifepoints"] = 0 if died else int(updated["combat_lifepoints"])
        return updated, True, {
            "player_damage": min(before, damage),
            "enemy_lifepoints": after,
            "killed": after == 0,
            "died": died,
            "safe_death": died,
            "xp_rewards": {"attack_exp": damage * 0.4},
        }

    return _apply


class SoulWarsWriteThroughProbeTest(unittest.TestCase):
    def _assert_untouched(self, frozen, before, label):
        self.assertEqual(frozen, before, f"{label} changed the save it was lent")

    def test_the_probe_itself_catches_a_write_through(self):
        """Without this, a passing probe could mean the freeze does nothing."""
        frozen = _frozen_save({"nested": {"count": 1}, "rows": [1, 2]})
        with self.assertRaises(WriteThroughError):
            frozen["nested"]["count"] = 1  # same value: the gate cannot see this
        with self.assertRaises(WriteThroughError):
            frozen["rows"].append(3)

    def test_frozen_save_is_equal_to_the_plain_one(self):
        """The freeze must not change what the helpers observe."""
        plain = _entered()
        self.assertEqual(_frozen_save(plain), plain)
        self.assertEqual(copy.deepcopy(_frozen_save(plain)), plain)

    def test_enter_never_writes_through(self):
        plain = _player()
        frozen = _frozen_save(plain)
        data, ok, info = enter_soul_wars_pure(frozen)
        self.assertTrue(ok, info)
        self.assertEqual(data["activity_session"]["active_id"], SOUL_WARS_ACTIVITY_ID)
        self._assert_untouched(frozen, plain, "enter_soul_wars_pure")

    def test_rejected_entry_never_writes_through(self):
        plain = _player(equipment={"cape": "Ardougne cloak 1"})
        frozen = _frozen_save(plain)
        _data, ok, info = enter_soul_wars_pure(frozen)
        self.assertFalse(ok)
        self.assertIn("cape", info["reason"])
        self._assert_untouched(frozen, plain, "enter_soul_wars_pure (rejected)")

    def test_idle_review_never_writes_through(self):
        plain = _entered()
        frozen = _frozen_save(plain)
        data, ok, result = apply_soul_wars_review_pure(
            frozen, lambda: 0.9, productive=False
        )
        self.assertTrue(ok, result)
        self.assertEqual(data["soul_wars"]["activity"], SOUL_WARS_ACTIVITY_MAX - 1)
        self._assert_untouched(frozen, plain, "apply_soul_wars_review_pure (idle)")

    def test_inactivity_kick_never_writes_through(self):
        plain = _entered()
        plain["soul_wars"] = dict(plain["soul_wars"], activity=1)
        frozen = _frozen_save(plain)
        data, ok, result = apply_soul_wars_review_pure(
            frozen, lambda: 0.9, productive=False
        )
        self.assertTrue(ok, result)
        self.assertTrue(result["kicked"])
        self.assertEqual(data["soul_wars"], {})
        self._assert_untouched(frozen, plain, "apply_soul_wars_review_pure (kick)")

    def test_fragment_and_control_duties_never_write_through(self):
        for label in ("control", "fragments"):
            with self.subTest(duty=label):
                plain = _entered(
                    payload={"automation_mode": "advanced", "duty": label}
                )
                plain["soul_wars"] = dict(plain["soul_wars"], control_balance=5)
                frozen = _frozen_save(plain)
                _data, ok, result = apply_soul_wars_review_pure(
                    frozen, lambda: 0.9, productive=True
                )
                self.assertTrue(ok, result)
                self.assertEqual(result["duty"], label)
                self._assert_untouched(
                    frozen, plain, f"apply_soul_wars_review_pure ({label})"
                )

    def test_defend_duty_never_writes_through(self):
        plain = _entered(payload={"automation_mode": "advanced", "duty": "defend"})
        frozen = _frozen_save(plain)
        _data, ok, result = apply_soul_wars_review_pure(
            frozen, lambda: 0.1, productive=True
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["duty"], "defend")
        self._assert_untouched(frozen, plain, "apply_soul_wars_review_pure (defend)")

    def test_avatar_duty_never_writes_through(self):
        for label, stub in (
            ("hit", _combat_stub(damage=500)),
            ("killed", _combat_stub(damage=99_999)),
            ("died", _combat_stub(damage=500, died=True)),
        ):
            with self.subTest(outcome=label):
                plain = _entered(
                    payload={"automation_mode": "advanced", "duty": "avatar"}
                )
                plain["soul_wars"] = dict(plain["soul_wars"], control_balance=5)
                frozen = _frozen_save(plain)
                with patch("ankiscape.logic.soul_wars_logic.apply_combat_burst_pure", stub):
                    _data, ok, result = apply_soul_wars_review_pure(
                        frozen, lambda: 0.9, productive=True
                    )
                self.assertTrue(ok, result)
                self.assertEqual(result["duty"], "avatar")
                self._assert_untouched(
                    frozen, plain, f"apply_soul_wars_review_pure (avatar/{label})"
                )

    def test_avatar_duty_with_the_real_combat_engine_never_writes_through(self):
        plain = _entered(payload={"automation_mode": "advanced", "duty": "avatar"})
        plain["soul_wars"] = dict(plain["soul_wars"], control_balance=5)
        frozen = _frozen_save(plain)
        _data, ok, result = apply_soul_wars_review_pure(
            frozen, lambda: 0.9, productive=True
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["duty"], "avatar")
        self._assert_untouched(frozen, plain, "apply_soul_wars_review_pure (real burst)")

    def test_combat_failure_rollback_never_writes_through(self):
        """The rollback path returns the caller's save; it must stay unharmed."""
        plain = _entered(payload={"automation_mode": "advanced", "duty": "avatar"})
        plain["soul_wars"] = dict(plain["soul_wars"], control_balance=5)
        frozen = _frozen_save(plain)
        with patch("ankiscape.logic.soul_wars_logic.apply_combat_burst_pure", _combat_stub(ok=False)):
            data, ok, result = apply_soul_wars_review_pure(
                frozen, lambda: 0.9, productive=True
            )
        self.assertFalse(ok)
        self.assertTrue(result["combat_failed"])
        self.assertEqual(data["soul_wars"], plain["soul_wars"])
        self._assert_untouched(frozen, plain, "apply_soul_wars_review_pure (rollback)")

    def test_terminal_review_never_writes_through(self):
        plain = _entered()
        plain["soul_wars"] = dict(
            plain["soul_wars"], review=SOUL_WARS_EVENT_REVIEWS - 1, player_score=3
        )
        frozen = _frozen_save(plain)
        data, ok, result = apply_soul_wars_review_pure(
            frozen, lambda: 0.9, productive=False
        )
        self.assertTrue(ok, result)
        self.assertTrue(result["terminal"])
        self.assertEqual(data["soul_wars"], {})
        self._assert_untouched(frozen, plain, "apply_soul_wars_review_pure (terminal)")

    def test_leave_never_writes_through(self):
        plain = _entered()
        frozen = _frozen_save(plain)
        data, ok, result = leave_soul_wars_pure(frozen)
        self.assertTrue(ok, result)
        self.assertEqual(data["soul_wars"], {})
        self.assertEqual(data["current_combat_target"], "chicken")
        self._assert_untouched(frozen, plain, "leave_soul_wars_pure")

    def test_set_policy_never_writes_through(self):
        plain = _player()
        frozen = _frozen_save(plain)
        data, ok, result = set_soul_wars_policy_pure(frozen, {"duty": "avatar"})
        self.assertTrue(ok, result)
        self.assertEqual(data["soul_wars_policy"]["duty"], "avatar")
        self._assert_untouched(frozen, plain, "set_soul_wars_policy_pure")

    def test_charm_purchase_never_writes_through(self):
        reward = SOUL_WARS_CHARM_REWARDS_BY_ITEM["Gold charm"]
        plain = _player(soul_wars_zeal=reward.zeal_cost)
        frozen = _frozen_save(plain)
        data, ok, result = buy_soul_wars_charms_pure(frozen, "Gold charm")
        self.assertTrue(ok, result)
        self.assertGreater(data["inventory"]["Gold charm"], 0)
        self.assertEqual(data["inventory"]["Coins"], 500)
        self.assertEqual(data["soul_wars_zeal"], 0)
        self._assert_untouched(frozen, plain, "buy_soul_wars_charms_pure")

    def test_unknown_command_never_writes_through(self):
        plain = _entered()
        frozen = _frozen_save(plain)
        data, ok, result = apply_soul_wars_command_pure(frozen, "no_such_action")
        self.assertFalse(ok)
        self.assertIn("Unknown", result["reason"])
        self.assertEqual(data["soul_wars"], plain["soul_wars"])
        self._assert_untouched(frozen, plain, "apply_soul_wars_command_pure")


if __name__ == "__main__":
    unittest.main()
