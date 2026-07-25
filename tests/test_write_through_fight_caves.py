"""Value-blind write-through probe for the TzHaar Fight Cave helpers.

`immutability_gate.py` only compares the input save for inequality after a
call, so it cannot see a write that stores a value equal to the one already
present.  This probe removes that value dependence: it lends the helpers a save
whose nested containers refuse every mutating operation, so a write through a
lent container raises no matter what value is written.

Fight Cave runs a live Combat encounter on every answered card, so a leak here
would rewrite the real save mid-fight.  Both the command surface and the review
surface are probed, including their failure paths, because those return a
whole-save copy the caller is expected to be able to treat as untouched.
"""

import copy
import unittest

from constants import EQUIPMENT_DATA, ITEM_DEFINITIONS, ORE_DATA
from storage_pure import default_player_data

import fight_caves_logic


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
        # Copying a lent container is a read, not a write, so it must succeed.
        # `copy` rebuilds a subclass by assigning into a fresh instance, which
        # the refusals above would otherwise report as a leak.
        return {
            copy.deepcopy(key, memo): copy.deepcopy(value, memo)
            for key, value in self.items()
        }


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
        # See _FrozenDict.__deepcopy__: copying a lent container is a read.
        return [copy.deepcopy(item, memo) for item in self]


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


def _frozen_save(save: dict) -> dict:
    return {key: _freeze(value, f"save[{key!r}]") for key, value in save.items()}


def _player(**overrides) -> dict:
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data.update(
        {
            "attack_level": 80,
            "strength_level": 80,
            "defense_level": 80,
            "ranged_level": 80,
            "magic_level": 80,
            "prayer_level": 80,
            "constitution_level": 80,
            "combat_lifepoints": 800,
            "combat_prayer_points": 800,
            "combat_auto_eat_food": [],
            "combat_auto_flee_percent": 0,
            "inventory": {"Shark": 4},
            "equipment": {"cape": "Fire cape"},
            "current_combat_target": "chicken",
        }
    )
    data.update(overrides)
    return data


def _entered(**overrides) -> dict:
    data, ok, info = fight_caves_logic.apply_fight_caves_command_pure(
        _player(**overrides), "enter"
    )
    assert ok, info
    return data


class FightCavesWriteThroughTest(unittest.TestCase):
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
        self.assertEqual(_frozen_save(_entered()), _entered())

    def test_view_never_writes_through(self):
        frozen = _frozen_save(_entered())
        view = fight_caves_logic.fight_caves_view_pure(frozen)
        self.assertEqual(frozen, _entered(), "the view changed the save it was lent")
        self.assertTrue(view["active"])

    def test_command_success_paths_never_write_through(self):
        for label, save, action, payload in (
            ("enter", _player(), "enter", {}),
            ("resume", _entered(), "enter", {}),
            ("leave", _entered(), "leave", {}),
            ("set_mode", _entered(), "set_mode", {"automation_mode": "advanced"}),
            (
                # A follower with no kind takes the early-return branch of
                # _dismiss_follower, which hands back a whole-save copy.
                "follower without a kind",
                _player(
                    summoning_state={
                        "active_follower": {"entity_id": "x"},
                        "pet_instances": {},
                    }
                ),
                "enter",
                {"confirm_dismiss_follower": True},
            ),
        ):
            with self.subTest(command=label):
                plain = dict(save)
                frozen = _frozen_save(save)
                updated, ok, info = fight_caves_logic.apply_fight_caves_command_pure(
                    frozen, action, payload
                )
                self.assertTrue(ok, info)
                self.assertEqual(
                    frozen, plain, f"{label} changed the save it was lent"
                )
                self.assertTrue(updated)

    def test_command_failure_paths_never_write_through(self):
        """The rejection paths return a whole-save copy the caller may keep."""
        follower_save = _player(
            summoning_state={
                "active_follower": {"kind": "unknown-kind", "entity_id": "x"},
                "pet_instances": {},
            }
        )
        for label, save, action, payload in (
            (
                "another activity active",
                _player(activity_session={"active_id": "other"}),
                "enter",
                {},
            ),
            (
                "encounter in progress",
                _player(combat_encounter={"target_id": "chicken"}),
                "enter",
                {},
            ),
            ("follower needs dismissing", follower_save, "enter", {}),
            (
                "follower cannot be dismissed",
                follower_save,
                "enter",
                {"confirm_dismiss_follower": True},
            ),
            ("unknown command", _player(), "not_a_command", {}),
            ("leave without a run", _player(), "leave", {}),
            (
                "select a missing target",
                _entered(),
                "select_target",
                {"instance_id": "gone"},
            ),
        ):
            with self.subTest(command=label):
                plain = dict(save)
                frozen = _frozen_save(save)
                updated, ok, info = fight_caves_logic.apply_fight_caves_command_pure(
                    frozen, action, payload
                )
                self.assertFalse(ok, info)
                self.assertEqual(
                    frozen, plain, f"{label} changed the save it was lent"
                )
                self.assertIn("reason", info)
                self.assertEqual(updated.get("attack_level"), 80)

    def test_review_never_writes_through(self):
        plain = _entered()
        frozen = _frozen_save(_entered())
        updated, ok, result = fight_caves_logic.apply_fight_caves_review_pure(
            frozen, lambda: 0.5, equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok, result)
        self.assertEqual(frozen, plain, "the review changed the save it was lent")
        self.assertEqual(updated["fight_caves"]["wave"], 1)

    def test_review_locked_loadout_never_writes_through(self):
        """The combat burst refuses this loadout, so the review rolls back."""
        overrides = {
            "combat_selected_magic_spell": "nonsense",
            "equipment": {"weapon": "Staff of air"},
        }
        plain = {**_entered(), **overrides}
        frozen = _frozen_save({**_entered(), **overrides})
        updated, ok, result = fight_caves_logic.apply_fight_caves_review_pure(
            frozen, lambda: 0.5, equipment_data=EQUIPMENT_DATA
        )
        self.assertFalse(ok, result)
        self.assertEqual(result["reason"], "combat_locked")
        self.assertEqual(frozen, plain, "the review changed the save it was lent")
        self.assertEqual(updated["fight_caves"]["wave"], 1)

    def test_review_rejection_never_writes_through(self):
        plain = _player()
        frozen = _frozen_save(_player())
        updated, ok, result = fight_caves_logic.apply_fight_caves_review_pure(
            frozen, lambda: 0.5, equipment_data=EQUIPMENT_DATA
        )
        self.assertFalse(ok, result)
        self.assertEqual(frozen, plain, "the review changed the save it was lent")
        self.assertEqual(updated.get("attack_level"), 80)


if __name__ == "__main__":
    unittest.main()
