"""Value-blind write-through probe for barbarian_assault_logic.

`immutability_gate.py` compares the input save for inequality after a call, so
it cannot see a write that stores a value equal to the one already present.
This probe removes that value dependence: it lends the helpers a save whose
nested containers refuse every mutating operation, so a write-through raises no
matter what value is written.

Barbarian Assault is worth probing this way because it keeps per-wave role
state.  `sanitize_barbarian_assault_session_pure` rebuilds the session dict and
deep-copies the nested encounter, and the wave/queen helpers then mutate that
rebuilt session in place — which is correct only as long as the session really
is a fresh object rather than the caller's live sub-dict.

`dict`/`list` subclasses are used rather than opaque proxies deliberately: the
helpers do `dict(...)`, `isinstance(x, Mapping)` and truthiness checks on these
values, so a failure here is a real defect rather than a probe artifact.
`__deepcopy__` returns a plain container because a deep copy is legitimately
owned by the helper that made it.
"""

from __future__ import annotations

import copy
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic import barbarian_assault_logic
from ankiscape.data.barbarian_assault_data import (
    BARBARIAN_ASSAULT_QUEEN_LIFEPOINTS,
    RUNNER_BOOTS_COST_PER_ROLE,
    BARBARIAN_ASSAULT_ROLE_IDS,
)
from ankiscape.logic.barbarian_assault_logic import (
    BARBARIAN_ASSAULT_ACTIVITY_ID,
    apply_barbarian_assault_command_pure,
    apply_barbarian_assault_review_pure,
    barbarian_assault_view_pure,
    buy_runner_boots_pure,
    complete_barbarian_assault_tutorial_pure,
    enter_barbarian_assault_pure,
    leave_barbarian_assault_pure,
    set_barbarian_assault_policy_pure,
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

    def __deepcopy__(self, memo):
        return {copy.deepcopy(k, memo): copy.deepcopy(v, memo) for k, v in self.items()}

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

    def __deepcopy__(self, memo):
        return [copy.deepcopy(item, memo) for item in self]

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

    Only the *nested* values matter: every helper is expected to build its own
    top-level copy, and writing into that copy is correct.
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
        "activity_session": {"active_id": ""},
        "current_utility": "make_soft_clay",
        "current_combat_target": "chicken",
        "combat_encounter": {},
        "combat_status_effects": {},
        "combat_lifepoints": 400,
        "constitution_level": 40,
        "attack_level": 40,
        "strength_level": 40,
        "defense_level": 40,
        "inventory": {"Bones": 4},
        "equipment": {},
        "barbarian_assault_tutorial_complete": True,
        "barbarian_assault_points": {role: 250 for role in BARBARIAN_ASSAULT_ROLE_IDS},
    }
    player.update(overrides)
    return player


def _wave_save(wave: int = 3) -> dict:
    return _player(
        activity_session={"active_id": BARBARIAN_ASSAULT_ACTIVITY_ID},
        current_utility=BARBARIAN_ASSAULT_ACTIVITY_ID,
        barbarian_assault={
            "version": barbarian_assault_logic.BARBARIAN_ASSAULT_STATE_VERSION,
            "wave": wave,
            "phase": "wave",
            "role": "attacker",
            "automation_mode": "advanced",
            "queen_lifepoints": BARBARIAN_ASSAULT_QUEEN_LIFEPOINTS,
            "omega_eggs": 0,
            "previous_combat_target": "chicken",
            "encounter": {
                "target_id": barbarian_assault_logic.BARBARIAN_ASSAULT_COMBAT_TARGET_ID,
                "enemy_lifepoints": 500,
            },
        },
    )


def _queen_save() -> dict:
    save = _wave_save(10)
    session = dict(save["barbarian_assault"])
    session["phase"] = "queen"
    session["omega_eggs"] = 6
    session["encounter"] = {}
    save["barbarian_assault"] = session
    return save


def _combat_stub(*, ok=True, died=False):
    def _apply(data, enemies, _equipment, **_kwargs):
        if not ok:
            return data, False, {"reason": "combat refused"}
        updated = dict(data)
        encounter = dict(updated.get("combat_encounter") or {})
        encounter["enemy_lifepoints"] = 0
        updated["combat_encounter"] = encounter
        return updated, True, {
            "died": died,
            "safe_death": died,
            "xp_rewards": {},
            "enemy": next(iter(enemies.values())),
        }

    return _apply


class BarbarianAssaultWriteThroughTest(unittest.TestCase):
    def test_the_probe_itself_catches_a_write_through(self):
        """Without this, a passing probe could mean the freeze does nothing."""
        frozen = _frozen_save({"nested": {"count": 1}, "rows": [1, 2]})
        with self.assertRaises(WriteThroughError):
            frozen["nested"]["count"] = 1  # same value: the gate cannot see this
        with self.assertRaises(WriteThroughError):
            frozen["rows"].append(3)

    def test_frozen_save_is_equal_to_the_plain_one(self):
        """The freeze must not change what the helpers observe."""
        self.assertEqual(_frozen_save(_wave_save()), _wave_save())
        self.assertEqual(_frozen_save(_queen_save()), _queen_save())

    def test_command_helpers_never_write_through(self):
        cases = (
            (
                "complete_barbarian_assault_tutorial_pure",
                lambda d: complete_barbarian_assault_tutorial_pure(d),
                _player(barbarian_assault_tutorial_complete=False),
            ),
            (
                "set_barbarian_assault_policy_pure",
                lambda d: set_barbarian_assault_policy_pure(
                    d, {"automation_mode": "advanced", "role": "healer"}
                ),
                _wave_save(),
            ),
            (
                "enter_barbarian_assault_pure",
                lambda d: enter_barbarian_assault_pure(d),
                _player(),
            ),
            (
                "leave_barbarian_assault_pure",
                lambda d: leave_barbarian_assault_pure(d),
                _wave_save(),
            ),
            (
                "buy_runner_boots_pure",
                lambda d: buy_runner_boots_pure(d),
                _player(
                    barbarian_assault_points={
                        role: RUNNER_BOOTS_COST_PER_ROLE
                        for role in BARBARIAN_ASSAULT_ROLE_IDS
                    }
                ),
            ),
            (
                "apply_barbarian_assault_command_pure/unknown",
                lambda d: apply_barbarian_assault_command_pure(d, "not_an_action"),
                _wave_save(),
            ),
            (
                "barbarian_assault_view_pure",
                lambda d: (barbarian_assault_view_pure(d), True, {}),
                _wave_save(),
            ),
        )
        for label, call, fixture in cases:
            with self.subTest(function=label):
                frozen = _frozen_save(fixture)
                updated, ok, info = call(frozen)
                self.assertEqual(
                    frozen, fixture, f"{label} changed the save it was lent"
                )
                self.assertIsInstance(updated, dict)
                self.assertTrue(ok or info.get("reason"), f"{label} failed silently")

    def test_review_helper_never_writes_through(self):
        cases = (
            ("wave/idle", _wave_save(), False, _combat_stub()),
            ("wave/cleared", _wave_save(), True, _combat_stub()),
            ("wave/safe_death", _wave_save(), True, _combat_stub(died=True)),
            ("wave/combat_refused", _wave_save(), True, _combat_stub(ok=False)),
            ("wave10/front_cleared", _wave_save(10), True, _combat_stub()),
            ("queen/idle", _queen_save(), False, None),
            ("queen/omega_egg", _queen_save(), True, None),
        )
        for label, fixture, productive, stub in cases:
            with self.subTest(case=label):
                frozen = _frozen_save(fixture)
                patcher = (
                    patch.object(
                        barbarian_assault_logic, "apply_combat_burst_pure", stub
                    )
                    if stub is not None
                    else None
                )
                if patcher is not None:
                    patcher.start()
                try:
                    updated, ok, result = apply_barbarian_assault_review_pure(
                        frozen, lambda: 0.5, productive=productive, equipment_data={}
                    )
                finally:
                    if patcher is not None:
                        patcher.stop()
                self.assertEqual(
                    frozen,
                    fixture,
                    f"apply_barbarian_assault_review_pure ({label}) changed the save "
                    "it was lent",
                )
                self.assertIsInstance(updated, dict)
                self.assertTrue(ok or result.get("reason"), f"{label} failed silently")

    def test_queen_omega_egg_progress_lands_only_in_the_returned_save(self):
        """A frozen fixture would raise on write-through, so this pins the value."""
        fixture = _queen_save()
        frozen = _frozen_save(fixture)
        updated, ok, _result = apply_barbarian_assault_review_pure(
            frozen, lambda: 0.5, productive=True, equipment_data={}
        )
        self.assertTrue(ok)
        self.assertEqual(updated["barbarian_assault"]["omega_eggs"], 7)
        self.assertEqual(frozen["barbarian_assault"]["omega_eggs"], 6)


if __name__ == "__main__":
    unittest.main()
