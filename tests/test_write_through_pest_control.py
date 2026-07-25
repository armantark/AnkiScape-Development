"""Value-blind write-through probe for the Pest Control helpers.

`immutability_gate.py` detects a leak by comparing the input save for
inequality after the call.  That misses a write which stores a value equal to
the one already present: real write-through, invisible on the fixture, and a
live-save corruption on different data.  Pest Control is one of the worst
places for that, because the same call graph carries the commendation wallet,
Void seal charges, and the state of a game already in progress.

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

from pest_control_data import (
    PEST_CONTROL_ACTIVITY_ID,
    PEST_CONTROL_EVENT_REVIEWS,
    PEST_CONTROL_PORTAL_COUNT,
    VOID_SEAL_COST,
)
from pest_control_logic import (
    apply_pest_control_command_pure,
    apply_pest_control_review_pure,
    buy_void_seal_pure,
    enter_pest_control_pure,
    leave_pest_control_pure,
    set_pest_control_policy_pure,
)
from pet_data import PETS_BY_ID


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
        "summoning_level": 40,
        "activity_session": {"active_id": ""},
        "combat_encounter": {},
        "current_combat_target": "chicken",
        "inventory": {"Coins": 500},
        "equipment": {},
        "coins": 0,
    }
    player.update(overrides)
    return player


def _pet_follower_player(**overrides):
    pet_id = next(iter(PETS_BY_ID))
    return _player(
        summoning_state={
            "active_follower": {"kind": "pet", "entity_id": "probe-1"},
            "pet_instances": {
                "probe-1": {
                    "pet_id": pet_id,
                    "stage": 0,
                    "growth": 10.0,
                    "hunger": 80.0,
                    "location": "active",
                    "variant": 0,
                    "name": "Probe",
                    "policy_lapse_reason": "",
                }
            },
        },
        **overrides,
    )


def _entered(**overrides):
    payload = overrides.pop("payload", None)
    data, ok, info = enter_pest_control_pure(_player(**overrides), payload)
    assert ok, info
    return data


def _combat_stub(damage: int = 0, *, died: bool = False, ok: bool = True):
    """Deterministic stand-in for the combat engine.

    The real engine copies its own input, so the interesting question for this
    probe is what the Pest Control code does with what the engine hands back.
    """

    def _apply(data, _enemy_data, _equipment_data, **_kwargs):
        if not ok:
            return data, False, {"reason": "combat_locked", "locked_reasons": ("probe",)}
        updated = copy.deepcopy(data)
        before = int(updated["combat_encounter"]["enemy_lifepoints"])
        after = max(0, before - damage)
        updated["combat_encounter"]["enemy_lifepoints"] = after
        return updated, True, {
            "player_damage": min(before, damage),
            "enemy_lifepoints": after,
            "killed": after == 0,
            "died": died,
            "safe_death": died,
            "xp_rewards": {"attack_exp": damage * 0.2} if damage else {},
        }

    return _apply


class PestControlWriteThroughProbeTest(unittest.TestCase):
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
        data, ok, info = enter_pest_control_pure(frozen)
        self.assertTrue(ok, info)
        self.assertEqual(data["activity_session"]["active_id"], PEST_CONTROL_ACTIVITY_ID)
        self._assert_untouched(frozen, plain, "enter_pest_control_pure")

    def test_rejected_entry_never_writes_through(self):
        plain = _player(
            attack_level=1,
            strength_level=1,
            defense_level=1,
            constitution_level=10,
            ranged_level=1,
            magic_level=1,
            prayer_level=1,
        )
        frozen = _frozen_save(plain)
        _data, ok, info = enter_pest_control_pure(frozen)
        self.assertFalse(ok)
        self.assertIn("combat level 40", info["reason"])
        self._assert_untouched(frozen, plain, "enter_pest_control_pure (rejected)")

    def test_entry_that_stores_a_pet_never_writes_through(self):
        plain = _pet_follower_player()
        frozen = _frozen_save(plain)
        data, ok, info = enter_pest_control_pure(
            frozen, {"confirm_dismiss_follower": True}
        )
        self.assertTrue(ok, info)
        self.assertEqual(info["dismissed_follower"], "pet")
        self.assertEqual(data["summoning_state"]["active_follower"], {})
        self._assert_untouched(frozen, plain, "enter_pest_control_pure (pet)")

    def test_entry_that_dismisses_a_familiar_never_writes_through(self):
        plain = _player(
            summoning_state={
                "active_follower": {
                    "kind": "familiar",
                    "entity_id": "spiritwolf",
                    "remaining_reviews": 3,
                    "max_reviews": 3,
                    "storage": {},
                }
            }
        )
        frozen = _frozen_save(plain)
        data, ok, info = enter_pest_control_pure(
            frozen, {"confirm_dismiss_follower": True}
        )
        self.assertTrue(ok, info)
        self.assertEqual(info["dismissed_follower"], "familiar")
        self.assertEqual(data["summoning_state"]["active_follower"], {})
        self._assert_untouched(frozen, plain, "enter_pest_control_pure (familiar)")

    def test_entry_blocked_by_an_undismissable_follower_never_writes_through(self):
        """Exercises the rollback taken when the follower cannot be stored."""
        plain = _player(
            summoning_state={"active_follower": {"kind": "wagon", "entity_id": "x"}}
        )
        frozen = _frozen_save(plain)
        data, ok, info = enter_pest_control_pure(
            frozen, {"confirm_dismiss_follower": True}
        )
        self.assertFalse(ok)
        self.assertIn("dismissed safely", info["reason"])
        self.assertEqual(data["summoning_state"], plain["summoning_state"])
        self._assert_untouched(frozen, plain, "enter_pest_control_pure (rollback)")

    def test_idle_review_never_writes_through(self):
        plain = _entered()
        frozen = _frozen_save(plain)
        _data, ok, result = apply_pest_control_review_pure(
            frozen, lambda: 0.9, productive=False
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["duty"], "idle")
        self._assert_untouched(frozen, plain, "apply_pest_control_review_pure (idle)")

    def test_assault_review_never_writes_through(self):
        for label, stub in (
            ("hit", _combat_stub(200)),
            ("killed", _combat_stub(99_999)),
            ("died", _combat_stub(200, died=True)),
        ):
            with self.subTest(outcome=label):
                plain = _entered()
                frozen = _frozen_save(plain)
                with patch("pest_control_logic.apply_combat_burst_pure", stub):
                    _data, ok, result = apply_pest_control_review_pure(
                        frozen, lambda: 0.9, productive=True, duty="assault"
                    )
                self.assertTrue(ok, result)
                self.assertEqual(result["duty"], "assault")
                self._assert_untouched(
                    frozen, plain, f"apply_pest_control_review_pure (assault/{label})"
                )

    def test_assault_with_the_real_combat_engine_never_writes_through(self):
        plain = _entered()
        frozen = _frozen_save(plain)
        _data, ok, result = apply_pest_control_review_pure(
            frozen, lambda: 0.9, productive=True, duty="assault"
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["duty"], "assault")
        self._assert_untouched(
            frozen, plain, "apply_pest_control_review_pure (real burst)"
        )

    def test_combat_failure_rollback_never_writes_through(self):
        """The rollback path returns the caller's save; it must stay unharmed."""
        plain = _entered()
        frozen = _frozen_save(plain)
        with patch(
            "pest_control_logic.apply_combat_burst_pure", _combat_stub(ok=False)
        ):
            data, ok, result = apply_pest_control_review_pure(
                frozen, lambda: 0.9, productive=True, duty="assault"
            )
        self.assertFalse(ok)
        self.assertEqual(result["reason"], "combat_locked")
        self.assertEqual(data["pest_control"], plain["pest_control"])
        self._assert_untouched(
            frozen, plain, "apply_pest_control_review_pure (rollback)"
        )

    def test_defend_review_never_writes_through(self):
        plain = _entered()
        frozen = _frozen_save(plain)
        _data, ok, result = apply_pest_control_review_pure(
            frozen, lambda: 0.9, productive=True, duty="defend"
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["duty"], "defend")
        self._assert_untouched(frozen, plain, "apply_pest_control_review_pure (defend)")

    def test_seal_review_spends_a_charge_without_writing_through(self):
        plain = _entered(inventory={"Coins": 500, "Void seal (8)": 1})
        frozen = _frozen_save(plain)
        data, ok, result = apply_pest_control_review_pure(
            frozen, lambda: 0.9, productive=True, duty="seal"
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["duty"], "seal")
        self.assertEqual(data["inventory"]["Void seal (7)"], 1)
        self.assertNotIn("Void seal (8)", data["inventory"])
        self.assertEqual(data["inventory"]["Coins"], 500)
        self._assert_untouched(frozen, plain, "apply_pest_control_review_pure (seal)")

    def test_equipped_seal_review_never_writes_through(self):
        plain = _entered(equipment={"neck": "Void seal (8)"})
        frozen = _frozen_save(plain)
        data, ok, result = apply_pest_control_review_pure(
            frozen, lambda: 0.9, productive=True, duty="seal"
        )
        self.assertTrue(ok, result)
        self.assertEqual(data["equipment"]["neck"], "Void seal (7)")
        self._assert_untouched(
            frozen, plain, "apply_pest_control_review_pure (equipped seal)"
        )

    def test_won_game_never_writes_through(self):
        plain = _entered()
        plain["pest_control"] = dict(
            plain["pest_control"],
            portal_index=PEST_CONTROL_PORTAL_COUNT - 1,
            portal_lifepoints=1,
        )
        frozen = _frozen_save(plain)
        with patch("pest_control_logic.apply_combat_burst_pure", _combat_stub(99_999)):
            data, ok, result = apply_pest_control_review_pure(
                frozen, lambda: 0.9, productive=True, duty="assault"
            )
        self.assertTrue(ok, result)
        self.assertTrue(result["won"])
        self.assertGreater(data["pest_control_commendations"], 0)
        self._assert_untouched(frozen, plain, "apply_pest_control_review_pure (won)")

    def test_lost_game_never_writes_through(self):
        plain = _entered()
        plain["pest_control"] = dict(plain["pest_control"], knight_lifepoints=1)
        frozen = _frozen_save(plain)
        data, ok, result = apply_pest_control_review_pure(
            frozen, lambda: 0.9, productive=False
        )
        self.assertTrue(ok, result)
        self.assertFalse(result["won"])
        self.assertEqual(data["pest_control"], {})
        self._assert_untouched(frozen, plain, "apply_pest_control_review_pure (lost)")

    def test_timed_out_game_never_writes_through(self):
        plain = _entered()
        plain["pest_control"] = dict(
            plain["pest_control"], review=PEST_CONTROL_EVENT_REVIEWS - 1
        )
        frozen = _frozen_save(plain)
        data, ok, result = apply_pest_control_review_pure(
            frozen, lambda: 0.9, productive=False
        )
        self.assertTrue(ok, result)
        self.assertTrue(result["terminal"])
        self.assertEqual(data["pest_control"], {})
        self._assert_untouched(
            frozen, plain, "apply_pest_control_review_pure (timed out)"
        )

    def test_leave_never_writes_through(self):
        plain = _entered()
        frozen = _frozen_save(plain)
        data, ok, result = leave_pest_control_pure(frozen)
        self.assertTrue(ok, result)
        self.assertEqual(data["pest_control"], {})
        self.assertEqual(data["current_combat_target"], "chicken")
        self._assert_untouched(frozen, plain, "leave_pest_control_pure")

    def test_set_policy_never_writes_through(self):
        plain = _player()
        frozen = _frozen_save(plain)
        data, ok, result = set_pest_control_policy_pure(frozen, {"duty": "defend"})
        self.assertTrue(ok, result)
        self.assertEqual(data["pest_control_policy"]["duty"], "defend")
        self._assert_untouched(frozen, plain, "set_pest_control_policy_pure")

    def test_seal_purchase_never_writes_through(self):
        plain = _player(pest_control_commendations=VOID_SEAL_COST)
        frozen = _frozen_save(plain)
        data, ok, result = buy_void_seal_pure(frozen)
        self.assertTrue(ok, result)
        self.assertEqual(data["inventory"]["Void seal (8)"], 1)
        self.assertEqual(data["inventory"]["Coins"], 500)
        self.assertEqual(data["pest_control_commendations"], 0)
        self._assert_untouched(frozen, plain, "buy_void_seal_pure")

    def test_unknown_command_never_writes_through(self):
        plain = _entered()
        frozen = _frozen_save(plain)
        data, ok, result = apply_pest_control_command_pure(frozen, "no_such_action")
        self.assertFalse(ok)
        self.assertIn("Unknown", result["reason"])
        self.assertEqual(data["pest_control"], plain["pest_control"])
        self._assert_untouched(frozen, plain, "apply_pest_control_command_pure")


if __name__ == "__main__":
    unittest.main()
