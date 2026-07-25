"""Value-blind write-through probe for the highest-consequence helpers.

`immutability_gate.py` detects a leak by comparing the input save for
inequality after the call.  That misses a write which stores a value equal to
the one already present: real write-through, invisible on this fixture, and a
live-save corruption on different data.

This probe removes the value dependence.  It hands the helper a save whose
nested containers refuse every mutating operation, so writing through raises
immediately no matter what value is written.  The helpers covered are the ones
where a leak would be worst and hardest to notice: the combat engine, which
runs on every answered card mid-fight, and the pet world clock, which the
independent reviewer flagged as the likeliest leak in the sweep.

`dict`/`list` subclasses are used rather than opaque proxies deliberately: the
helpers under test do `dict(...)`, `isinstance(x, Mapping)` and truthiness
checks on these values, and a subclass satisfies all of that unchanged, so a
failure here is a real defect rather than an artifact of the probe.
"""

import copy
import unittest

from constants import ITEM_DEFINITIONS, ORE_DATA
from storage_pure import default_player_data

import logic_pure
import pet_logic
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


def _combat_save() -> dict:
    save = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    save["inventory"] = {"Bones": 12, "Coins": 5000}
    for key in ("attack_level", "strength_level", "defense_level", "constitution_level"):
        if key in save:
            save[key] = 40
    return save


def _pet_save() -> dict:
    pet_id = next(iter(PETS_BY_ID))
    save = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    save["summoning_state"] = {
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
    }
    save["carried_inventory"] = {"probe-pack": {}}
    save["pet_auto_care"] = True
    return save


class WriteThroughProbeTest(unittest.TestCase):
    def test_the_probe_itself_catches_a_write_through(self):
        """Without this, a passing probe could mean the freeze does nothing."""
        frozen = _frozen_save({"nested": {"count": 1}, "rows": [1, 2]})
        with self.assertRaises(WriteThroughError):
            frozen["nested"]["count"] = 1  # same value: the gate cannot see this
        with self.assertRaises(WriteThroughError):
            frozen["rows"].append(3)

    def test_pet_world_clock_never_writes_through(self):
        frozen = _frozen_save(_pet_save())
        updated, result = pet_logic.advance_active_pet_pure(
            frozen, active_carried_target="probe-pack"
        )
        self.assertEqual(
            frozen,
            _pet_save(),
            "advance_active_pet_pure changed the save it was lent",
        )
        self.assertIsInstance(updated, dict)
        self.assertEqual(result["instance_id"], "probe-1")

    def test_pet_helpers_never_write_through(self):
        for label, call in (
            ("store_active_pet_pure", lambda d: pet_logic.store_active_pet_pure(d)),
            ("let_out_pet_pure", lambda d: pet_logic.let_out_pet_pure(d, "probe-1")),
            ("release_pet_pure", lambda d: pet_logic.release_pet_pure(d, "probe-1")),
        ):
            helper = getattr(pet_logic, label, None)
            if helper is None:
                continue
            with self.subTest(function=label):
                frozen = _frozen_save(_pet_save())
                returned = call(frozen)
                self.assertEqual(
                    frozen, _pet_save(), f"{label} changed the save it was lent"
                )
                self.assertIsNotNone(returned)

    def test_combat_encounter_helpers_never_write_through(self):
        """The engine that runs on every answered card during a fight."""
        covered = 0
        for label in (
            "advance_temporary_effects_pure",
            "combat_status_summary_pure",
            "combat_hud_state_pure",
        ):
            helper = getattr(logic_pure, label, None)
            if helper is None:
                continue
            with self.subTest(function=label):
                frozen = _frozen_save(_combat_save())
                try:
                    helper(frozen)
                except TypeError:
                    helper(frozen, 1.0)
                self.assertEqual(
                    frozen, _combat_save(), f"{label} changed the save it was lent"
                )
                covered += 1
        self.assertGreater(covered, 0, "no combat helper was actually probed")

    def test_frozen_save_is_equal_to_the_plain_one(self):
        """The freeze must not change what the helpers observe."""
        plain = _combat_save()
        self.assertEqual(_frozen_save(plain), plain)
        self.assertEqual(_frozen_save(copy.deepcopy(_pet_save())), _pet_save())


if __name__ == "__main__":
    unittest.main()
