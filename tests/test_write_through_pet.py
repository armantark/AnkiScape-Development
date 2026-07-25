"""Value-blind write-through probe for every pet_logic entry point.

`tests/test_logic_no_input_mutation.py` gates these helpers by comparing the
input save for inequality after the call, which cannot see a write that stores
a value equal to the one already present.  This probe removes the value
dependence: it lends each helper a save whose nested containers refuse every
mutating operation, so writing through raises regardless of the value written.

The coverage here goes wider than `tests/test_write_through_probe.py`, which
only drives the world clock and the follower-slot helpers.  Acquisition,
hatching, the menagerie locations, and the auto-feed branch are all exercised,
because those are the paths that rebuild the inventories rather than only the
summoning state.

`dict`/`list` subclasses are used rather than opaque proxies deliberately: the
helpers do `dict(...)`, `isinstance(x, Mapping)` and truthiness checks on these
values, and a subclass satisfies all of that unchanged, so a failure here is a
real defect rather than an artifact of the probe.
"""

import copy
import unittest

import pet_logic
from pet_logic import (
    acquire_pet_pure,
    advance_active_pet_pure,
    hatch_phoenix_egg_pure,
    let_out_pet_pure,
    release_pet_pure,
    store_active_pet_pure,
)
from summoning_logic import default_summoning_state_pure


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


def _owner(pet_id: str = "bulldog", *, location: str = "bank", **overrides) -> dict:
    """A save that already owns one pet, built without the helpers under test."""

    state = default_summoning_state_pure()
    state["pet_instances"] = {
        "pet-1": {
            "pet_id": pet_id,
            "stage": 0,
            "growth": 10.0,
            "hunger": 80.0,
            "location": location,
            "variant": 0,
            "name": "Probe",
            "policy_lapse_reason": "",
        }
    }
    state["pet_next_instance_id"] = 2
    save = {
        "summoning_level": 99,
        "inventory": {"Raw chicken": 3, "Coins": 500},
        "carried_inventory": {"probe-pack": {"Raw chicken": 2}},
        "pet_auto_care": True,
        "summoning_state": state,
    }
    save.update(overrides)
    return save


def _active_owner(**overrides) -> dict:
    save = _owner(location="active", **overrides)
    save["summoning_state"]["active_follower"] = {
        "kind": "pet",
        "entity_id": "pet-1",
        "remaining_reviews": 0,
        "max_reviews": 0,
        "storage": {},
        "hidden_in_spirit_plane": False,
        "policy_lapse_reason": "",
    }
    return save


class PetWriteThroughTest(unittest.TestCase):
    def test_the_probe_itself_catches_a_write_through(self):
        """Without this, a passing probe could mean the freeze does nothing."""
        frozen = _frozen({"nested": {"count": 1}, "rows": [1, 2]})
        with self.assertRaises(WriteThroughError):
            frozen["nested"]["count"] = 1  # same value: the gate cannot see this
        with self.assertRaises(WriteThroughError):
            frozen["rows"].append(3)

    def test_frozen_save_is_equal_to_the_plain_one(self):
        """The freeze must not change what the helpers observe."""
        self.assertEqual(_frozen(_owner()), _owner())
        self.assertEqual(_frozen(copy.deepcopy(_active_owner())), _active_owner())

    def test_acquire_never_writes_through(self):
        for location in ("bank", "carried", "menagerie", "nonsense"):
            with self.subTest(location=location):
                frozen = _frozen(_owner())
                updated, ok, instance_id = acquire_pet_pure(
                    frozen, "bulldog", location=location
                )
                self.assertTrue(ok)
                self.assertEqual(frozen, _owner())
                self.assertEqual(
                    len(updated["summoning_state"]["pet_instances"]), 2
                )
                self.assertIn(instance_id, updated["summoning_state"]["pet_instances"])

    def test_acquire_refusals_never_write_through(self):
        for label, save, pet_id in (
            ("unavailable_pet", _owner(), "sparkles"),
            ("summoning_level", _owner(summoning_level=1), "bulldog"),
        ):
            with self.subTest(reason=label):
                frozen = _frozen(save)
                _, ok, reason = acquire_pet_pure(frozen, pet_id)
                self.assertFalse(ok)
                self.assertEqual(reason, label)
                self.assertEqual(frozen, save)

    def test_let_out_and_store_never_write_through(self):
        frozen = _frozen(_owner())
        active, ok, _ = let_out_pet_pure(frozen, "pet-1")
        self.assertTrue(ok)
        self.assertEqual(frozen, _owner())
        self.assertEqual(
            active["summoning_state"]["pet_instances"]["pet-1"]["location"], "active"
        )

        for location in ("bank", "carried", "menagerie"):
            with self.subTest(location=location):
                frozen_active = _frozen(_active_owner())
                stored, ok = store_active_pet_pure(frozen_active, location=location)
                self.assertTrue(ok)
                self.assertEqual(frozen_active, _active_owner())
                self.assertEqual(
                    stored["summoning_state"]["pet_instances"]["pet-1"]["location"],
                    location,
                )

    def test_let_out_and_store_refusals_never_write_through(self):
        occupied = _active_owner()
        frozen = _frozen(occupied)
        _, ok, reason = let_out_pet_pure(frozen, "pet-1")
        self.assertFalse(ok)
        self.assertEqual(reason, "follower_slot_occupied")
        self.assertEqual(frozen, occupied)

        frozen = _frozen(_owner())
        _, ok, reason = let_out_pet_pure(frozen, "missing")
        self.assertFalse(ok)
        self.assertEqual(reason, "unknown_pet")
        self.assertEqual(frozen, _owner())

        frozen = _frozen(_owner())
        _, ok = store_active_pet_pure(frozen, location="bank")
        self.assertFalse(ok)  # no active follower to store
        self.assertEqual(frozen, _owner())

    def test_release_never_writes_through(self):
        frozen = _frozen(_active_owner())
        released, ok, reason = release_pet_pure(frozen, "pet-1")
        self.assertTrue(ok)
        self.assertEqual(reason, "released")
        self.assertEqual(frozen, _active_owner())
        self.assertEqual(released["summoning_state"]["pet_instances"], {})
        self.assertEqual(released["summoning_state"]["active_follower"], {})

        blocked = _owner(pet_id="broav")
        frozen = _frozen(blocked)
        _, ok, reason = release_pet_pure(frozen, "pet-1")
        self.assertFalse(ok)
        self.assertEqual(reason, "reacquisition_source_blocked")
        self.assertEqual(frozen, blocked)

        frozen = _frozen(_owner())
        _, ok, reason = release_pet_pure(frozen, "missing")
        self.assertFalse(ok)
        self.assertEqual(reason, "unknown_pet")
        self.assertEqual(frozen, _owner())

    def test_hatch_phoenix_egg_never_writes_through(self):
        holder = _owner()
        holder["inventory"]["Phoenix egg"] = 1
        frozen = _frozen(holder)
        hatched, ok, instance_id = hatch_phoenix_egg_pure(frozen, "Phoenix egg")
        self.assertTrue(ok)
        self.assertEqual(frozen, holder)
        self.assertEqual(hatched["inventory"]["Phoenix egg"], 0)
        self.assertEqual(
            hatched["summoning_state"]["pet_instances"][instance_id]["pet_id"],
            "cute_phoenix_eggling",
        )

    def test_hatch_phoenix_egg_refusals_never_write_through(self):
        low = _owner(summoning_level=1)
        low["inventory"]["Phoenix egg"] = 1
        cases = (
            ("unknown_phoenix_egg", _owner(), "Bucket"),
            ("summoning_level", low, "Phoenix egg"),
            ("missing_phoenix_egg", _owner(), "Cracked phoenix egg"),
        )
        for label, save, item_name in cases:
            with self.subTest(reason=label):
                frozen = _frozen(save)
                _, ok, reason = hatch_phoenix_egg_pure(frozen, item_name)
                self.assertFalse(ok)
                self.assertEqual(reason, label)
                self.assertEqual(frozen, save)

    def test_world_clock_never_writes_through(self):
        """The auto-feed branch is the one that rebuilds both inventories."""
        hungry = _active_owner()
        frozen = _frozen(hungry)
        fed, result = advance_active_pet_pure(
            frozen, active_carried_target="probe-pack"
        )
        self.assertEqual(frozen, hungry)
        self.assertEqual(result["fed_item"], "Raw chicken")
        self.assertEqual(fed["carried_inventory"]["probe-pack"]["Raw chicken"], 1)
        self.assertEqual(fed["inventory"]["Raw chicken"], 2)

        starving = _active_owner()
        starving["summoning_state"]["pet_instances"]["pet-1"]["hunger"] = 99.0
        frozen = _frozen(starving)
        sent_home, result = advance_active_pet_pure(frozen)
        self.assertEqual(frozen, starving)
        self.assertTrue(result["returned_home"])
        self.assertEqual(
            sent_home["summoning_state"]["pet_instances"]["pet-1"]["location"], "bank"
        )

        orphan = _active_owner()
        orphan["summoning_state"]["pet_instances"] = {}
        frozen = _frozen(orphan)
        cleared, result = advance_active_pet_pure(frozen)
        self.assertEqual(frozen, orphan)
        self.assertIsNone(result["instance_id"])
        self.assertEqual(cleared["summoning_state"]["active_follower"], {})

    def test_sanitize_never_writes_through(self):
        frozen = _frozen(_owner())
        instances = pet_logic.sanitize_pet_instances_pure(
            frozen["summoning_state"]["pet_instances"]
        )
        instances["pet-1"]["hunger"] = 0.0  # the rebuild must be ours to write
        self.assertEqual(frozen, _owner())
        self.assertEqual(
            frozen["summoning_state"]["pet_instances"]["pet-1"]["hunger"], 80.0
        )


if __name__ == "__main__":
    unittest.main()
