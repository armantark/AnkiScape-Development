"""Value-blind write-through probe for shades_of_mortton_logic.

Modelled on tests/test_write_through_probe.py.  The equality gate in
`immutability_gate.py` cannot see a write that stores a value equal to the one
already present, so this probe lends the helpers a save whose nested containers
refuse every mutating operation.  Any write through a container the helper did
not rebuild raises immediately, whatever value is written.

Mort'ton is a communal-repair plus personal-sanctity loop: the repair, cremate,
and Loar-shade duties all read the shared inventory and the nested loop state,
and the combat duty hands the working save straight to the real combat engine.
Those are the paths where a shallow working copy would leak.
"""

from __future__ import annotations

import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data

from ankiscape.logic import shades_of_mortton_logic as shades


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
        # Copying is not writing.  `copy.deepcopy` rebuilds a subclass by
        # __setitem__, which would otherwise read as a write-through, so hand it
        # a plain container: what the helper gets back is legitimately writable.
        return {key: _plain_copy(value) for key, value in self.items()}

    def __copy__(self):
        return dict(self)


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
        return [_plain_copy(item) for item in self]

    def __copy__(self):
        return list(self)


def _plain_copy(value):
    if isinstance(value, dict):
        return {key: _plain_copy(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_plain_copy(item) for item in value]
    return value


def _freeze(value, path="save"):
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
    """Freeze nested containers only; the top level stays a plain dict."""
    return {key: _freeze(value, f"save[{key!r}]") for key, value in save.items()}


def _save(**overrides) -> dict:
    save = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    save["quests"] = {"shades_of_mortton": {"completed": True}}
    save["activity_session"] = {"active_id": ""}
    save["combat_encounter"] = {}
    save["inventory"] = {
        "Flamtaer hammer": 1,
        "Timber beam": 4,
        "Limestone brick": 4,
        "Swamp paste": 40,
        "Tinderbox": 1,
        "Loar remains": 3,
        "Pyre logs": 3,
        "Logs": 5,
        "Olive oil (4)": 2,
        "Sacred oil (4)": 4,
        "Bronze key red": 2,
    }
    save["firemaking_level"] = 80
    for key in ("attack_level", "strength_level", "defence_level", "constitution_level"):
        if key in save:
            save[key] = 50
    save.update(overrides)
    return save


def _entered(**overrides) -> dict:
    entered, ok, info = shades.enter_shades_of_mortton_pure(_save(**overrides))
    assert ok, info
    return entered


def _repaired_temple(**overrides) -> dict:
    """A save whose temple is already at the altar threshold."""
    entered = _entered(**overrides)
    loop = dict(entered["shades_of_mortton"])
    loop["temple_repair"] = shades.SHADES_REPAIR_MAX
    loop["sanctity_tenths"] = shades.SHADES_SANCTITY_MAX_TENTHS
    loop["altar_lit"] = False
    entered["shades_of_mortton"] = loop
    return entered


class ShadesOfMorttonWriteThroughTest(unittest.TestCase):
    def test_the_probe_itself_catches_a_write_through(self):
        """Without this, a passing probe could mean the freeze does nothing."""
        frozen = _frozen_save({"nested": {"count": 1}, "rows": [1, 2]})
        with self.assertRaises(WriteThroughError):
            frozen["nested"]["count"] = 1  # same value: the gate cannot see this
        with self.assertRaises(WriteThroughError):
            frozen["rows"].append(3)

    def test_frozen_save_is_equal_to_the_plain_one(self):
        """The freeze must not change what the helpers observe."""
        plain = _save()
        self.assertEqual(_frozen_save(plain), plain)

    def test_entry_and_exit_never_write_through(self):
        frozen = _frozen_save(_save())
        entered, ok, info = shades.enter_shades_of_mortton_pure(frozen, {"duty": "repair"})
        self.assertTrue(ok, info)
        self.assertEqual(frozen, _save(), "enter changed the save it was lent")

        frozen_active = _frozen_save(_entered())
        left, ok, info = shades.leave_shades_of_mortton_pure(frozen_active)
        self.assertTrue(ok, info)
        self.assertEqual(frozen_active, _entered(), "leave changed the save it was lent")

    def test_policy_write_never_writes_through(self):
        frozen = _frozen_save(_save())
        updated, ok, info = shades.set_shades_of_mortton_policy_pure(
            frozen, {"automation_mode": "advanced", "duty": "cremate"}
        )
        self.assertTrue(ok, info)
        self.assertEqual(updated["shades_of_mortton_policy"]["duty"], "cremate")
        self.assertEqual(frozen, _save(), "set_policy changed the save it was lent")

    def test_each_review_duty_never_writes_through(self):
        """Repair, cremate, and the real combat engine all get the working save."""
        for duty in ("repair", "cremate", "combat"):
            with self.subTest(duty=duty):
                baseline = _entered(
                    shades_of_mortton_policy={
                        "automation_mode": "advanced",
                        "duty": duty,
                    }
                )
                frozen = _frozen_save(baseline)
                updated, ok, result = shades.apply_shades_of_mortton_review_pure(frozen)
                self.assertTrue(ok, result)
                self.assertEqual(result["duty"], duty)
                self.assertEqual(
                    frozen, baseline, f"the {duty} duty changed the save it was lent"
                )

    def test_altar_bless_and_production_never_write_through(self):
        baseline = _repaired_temple()
        frozen = _frozen_save(baseline)
        lit, ok, info = shades.light_shades_altar_pure(frozen, lambda: 0.0)
        self.assertTrue(ok, info)
        self.assertTrue(lit["shades_of_mortton"]["altar_lit"])
        self.assertEqual(frozen, baseline, "light_altar changed the save it was lent")

        blessed_baseline = dict(lit)
        frozen_lit = _frozen_save(blessed_baseline)
        blessed, ok, info = shades.bless_shades_item_pure(frozen_lit, "Olive oil (4)")
        self.assertTrue(ok, info)
        self.assertEqual(blessed["inventory"]["Sacred oil (4)"], 5)
        self.assertEqual(
            frozen_lit, blessed_baseline, "bless changed the save it was lent"
        )

        frozen_plain = _frozen_save(_save())
        made, ok, info = shades.make_shades_pyre_logs_pure(frozen_plain, "Pyre logs")
        self.assertTrue(ok, info)
        self.assertEqual(made["inventory"]["Pyre logs"], 4)
        self.assertEqual(
            frozen_plain, _save(), "make_pyre_logs changed the save it was lent"
        )

    def test_bronze_chest_never_writes_through(self):
        frozen = _frozen_save(_save())
        opened, ok, info = shades.open_shades_bronze_chest_pure(frozen, "Bronze key red")
        self.assertTrue(ok, info)
        self.assertEqual(opened["shades_of_mortton_chests_opened"], 1)
        self.assertEqual(frozen, _save(), "open_bronze_chest changed the save it was lent")

    def test_unknown_command_returns_the_save_without_writing_through(self):
        """The router's fallback: it must hand back an unchanged, unaliased save."""
        frozen = _frozen_save(_save())
        returned, ok, info = shades.apply_shades_of_mortton_command_pure(frozen, "wat")
        self.assertFalse(ok)
        self.assertIn("Unknown", info["reason"])
        self.assertEqual(returned, _save())
        self.assertEqual(frozen, _save(), "the router changed the save it was lent")
        # The caller may keep the returned dict; writing its own top-level keys
        # must not reach the save that was lent.
        returned["shades_of_mortton_last_result"] = "caller wrote here"
        self.assertEqual(frozen, _save())

    def test_router_command_paths_never_write_through(self):
        for action_id, payload in (
            ("enter", {"duty": "repair"}),
            ("set_policy", {"duty": "combat"}),
            ("make_pyre_logs", {"output_name": "Pyre logs"}),
            ("open_bronze_chest", {"key_name": "Bronze key red"}),
        ):
            with self.subTest(action_id=action_id):
                frozen = _frozen_save(_save())
                _updated, ok, info = shades.apply_shades_of_mortton_command_pure(
                    frozen, action_id, payload
                )
                self.assertTrue(ok, info)
                self.assertEqual(
                    frozen, _save(), f"{action_id} changed the save it was lent"
                )


if __name__ == "__main__":
    unittest.main()
