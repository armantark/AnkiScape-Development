"""Value-blind write-through probe for the Phoenix Lair helpers.

`immutability_gate.py` only compares the input save for inequality after a
call, so it cannot see a write that stores a value equal to the one already
present.  This probe removes that value dependence: it lends the helpers a save
whose nested containers refuse every mutating operation, so a write through a
lent container raises no matter what value is written.

Phoenix Lair drives a live Combat encounter across a three-phase run, so a leak
here would rewrite the real save mid-run.  The command, review, and egg-choice
surfaces are probed on both their success and their rejection paths, because the
rejections return a whole-save copy the caller is expected to treat as
untouched.
"""

import copy
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import EQUIPMENT_DATA, ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data

from ankiscape.logic import phoenix_lair_logic


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
    data["quests"]["in_pyre_need"] = {
        "started": True,
        "progress": 1,
        "completed": True,
    }
    data.update(
        {
            "slayer_level": 99,
            "summoning_level": 99,
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "magic_level": 99,
            "ranged_level": 99,
            "combat_lifepoints": 990,
        }
    )
    data["inventory"].update({"Knife": 1, "Secateurs": 1, "Tinderbox": 1})
    data.update(overrides)
    return data


def _entered(**overrides) -> dict:
    entered, ok, info = phoenix_lair_logic.apply_phoenix_lair_command_pure(
        _player(**overrides),
        "enter",
        rng=lambda: 0.5,
        equipment_data=EQUIPMENT_DATA,
    )
    assert ok, info
    return entered


def _pending_egg(**overrides) -> dict:
    data = _player(**overrides)
    data["phoenix_lair"]["pending_egg"] = True
    return data


class PhoenixLairWriteThroughTest(unittest.TestCase):
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
        view = phoenix_lair_logic.phoenix_lair_view_pure(
            frozen, equipment_data=EQUIPMENT_DATA
        )
        self.assertEqual(frozen, _entered(), "the view changed the save it was lent")
        self.assertEqual(view["phase"], "guardians")

    def test_command_success_paths_never_write_through(self):
        for label, save, action in (
            ("enter", _player(), "enter"),
            ("reselect an active run", _entered(), "enter"),
            ("leave", _entered(), "leave"),
        ):
            with self.subTest(command=label):
                plain = dict(save)
                frozen = _frozen_save(save)
                updated, ok, info = phoenix_lair_logic.apply_phoenix_lair_command_pure(
                    frozen,
                    action,
                    {},
                    rng=lambda: 0.5,
                    equipment_data=EQUIPMENT_DATA,
                )
                self.assertTrue(ok, info)
                self.assertEqual(frozen, plain, f"{label} changed the save it was lent")
                self.assertIn("message", info)

    def test_command_failure_paths_never_write_through(self):
        """The rejection paths return a whole-save copy the caller may keep."""
        no_quest = _player()
        no_quest["quests"]["in_pyre_need"] = {"started": True, "completed": False}
        no_tools = _player()
        no_tools["inventory"]["Tinderbox"] = 0
        same_day = _player()
        same_day["phoenix_lair"]["last_completed_world_day"] = 0
        locked_loadout = _player(
            combat_selected_magic_spell="nonsense",
            equipment={"weapon": "Staff of air"},
        )
        for label, save, action in (
            ("another activity active", _player(activity_session={"active_id": "x"}), "enter"),
            ("quest not complete", no_quest, "enter"),
            ("slayer level too low", _player(slayer_level=50), "enter"),
            ("missing tools", no_tools, "enter"),
            ("already rewarded today", same_day, "enter"),
            ("locked combat loadout", locked_loadout, "enter"),
            ("leave without a run", _player(), "leave"),
            ("unknown command", _player(), "not_a_command"),
        ):
            with self.subTest(command=label):
                plain = dict(save)
                frozen = _frozen_save(save)
                updated, ok, info = phoenix_lair_logic.apply_phoenix_lair_command_pure(
                    frozen,
                    action,
                    {},
                    rng=lambda: 0.5,
                    equipment_data=EQUIPMENT_DATA,
                )
                self.assertFalse(ok, info)
                self.assertEqual(frozen, plain, f"{label} changed the save it was lent")
                self.assertIn("reason", info)
                self.assertEqual(updated.get("slayer_level"), save["slayer_level"])

    def test_review_never_writes_through(self):
        guardians = _entered()
        prepare = copy.deepcopy(guardians)
        prepare["phoenix_lair"]["phase"] = "prepare"
        for label, save in (("guardians", guardians), ("prepare", prepare)):
            with self.subTest(phase=label):
                plain = copy.deepcopy(save)
                frozen = _frozen_save(save)
                updated, ok, result = phoenix_lair_logic.apply_phoenix_lair_review_pure(
                    frozen, lambda: 0.5, equipment_data=EQUIPMENT_DATA
                )
                self.assertTrue(ok, result)
                self.assertEqual(
                    frozen, plain, f"the {label} review changed the save it was lent"
                )
                self.assertIn("status", result)

    def test_review_locked_loadout_never_writes_through(self):
        """The combat burst refuses this loadout, so the review rolls back."""
        overrides = {
            "combat_selected_magic_spell": "nonsense",
            "equipment": {"weapon": "Staff of air"},
        }
        plain = {**_entered(), **overrides}
        frozen = _frozen_save({**_entered(), **overrides})
        updated, ok, result = phoenix_lair_logic.apply_phoenix_lair_review_pure(
            frozen, lambda: 0.5, equipment_data=EQUIPMENT_DATA
        )
        self.assertFalse(ok, result)
        self.assertEqual(result["reason"], "combat_locked")
        self.assertEqual(frozen, plain, "the review changed the save it was lent")
        self.assertTrue(updated["phoenix_lair"]["active"])

    def test_review_without_a_run_never_writes_through(self):
        plain = _player()
        frozen = _frozen_save(_player())
        updated, ok, result = phoenix_lair_logic.apply_phoenix_lair_review_pure(
            frozen, lambda: 0.5, equipment_data=EQUIPMENT_DATA
        )
        self.assertFalse(ok, result)
        self.assertEqual(frozen, plain, "the review changed the save it was lent")
        self.assertEqual(updated.get("slayer_level"), 99)

    def test_egg_choice_never_writes_through(self):
        for label, save, option in (
            ("pet at level 72", _pending_egg(summoning_level=72), "clap"),
            ("item below level 72", _pending_egg(summoning_level=71), "kick"),
        ):
            with self.subTest(choice=label):
                plain = copy.deepcopy(save)
                frozen = _frozen_save(save)
                updated, ok, result = phoenix_lair_logic.resolve_phoenix_egg_choice_pure(
                    frozen, option, remember_choice=True
                )
                self.assertTrue(ok, result)
                self.assertEqual(
                    frozen, plain, f"{label} changed the save it was lent"
                )
                self.assertFalse(updated["phoenix_lair"]["pending_egg"])

    def test_egg_choice_failure_paths_never_write_through(self):
        for label, save, option in (
            ("unknown option", _pending_egg(), "shrug"),
            ("no egg pending", _player(), "clap"),
        ):
            with self.subTest(choice=label):
                plain = copy.deepcopy(save)
                frozen = _frozen_save(save)
                updated, ok, result = phoenix_lair_logic.resolve_phoenix_egg_choice_pure(
                    frozen, option
                )
                self.assertFalse(ok, result)
                self.assertEqual(
                    frozen, plain, f"{label} changed the save it was lent"
                )
                self.assertIn("reason", result)
                self.assertEqual(updated.get("slayer_level"), 99)

    def test_egg_choice_rolls_back_a_failed_pet_acquisition(self):
        """Both egglings need Summoning 72, so the failure is forced here."""
        save = _pending_egg(summoning_level=72)
        plain = copy.deepcopy(save)
        frozen = _frozen_save(save)
        with patch.object(
            phoenix_lair_logic,
            "acquire_pet_pure",
            lambda data, pet_id: (dict(data), False, "summoning_level"),
        ):
            updated, ok, result = phoenix_lair_logic.resolve_phoenix_egg_choice_pure(
                frozen, "clap"
            )
        self.assertFalse(ok, result)
        self.assertEqual(result["reason"], "summoning_level")
        self.assertEqual(frozen, plain, "the rollback changed the save it was lent")
        self.assertTrue(updated["phoenix_lair"]["pending_egg"])


if __name__ == "__main__":
    unittest.main()
