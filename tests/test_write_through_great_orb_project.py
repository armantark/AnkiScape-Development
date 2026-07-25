"""Value-blind write-through probe for great_orb_project_logic.

`immutability_gate.py` compares the input save for inequality after a call, so
it cannot see a write that stores a value equal to the one already present.
This probe removes that value dependence: it lends the helpers a save whose
nested containers refuse every mutating operation, so a write-through raises no
matter what value is written.

Great Orb Project is worth probing this way because it keeps per-round charge
state.  `_sanitize_active` rebuilds the `active` round dict and
`apply_great_orb_project_review_pure` then mutates that rebuilt dict in place
(round, rounds_won, pending_tokens, saved_essence), which is correct only as
long as `active` really is a fresh object rather than the caller's live
sub-dict.  `_craft_essence` writes runes into the inventory, so the inventory
must be rebuilt with `dict()` before every write.

`dict`/`list` subclasses are used rather than opaque proxies deliberately: the
helpers do `dict(...)`, `isinstance(x, Mapping)` and truthiness checks on these
values, so a failure here is a real defect rather than a probe artifact.
`__deepcopy__` returns a plain container because a deep copy is legitimately
owned by the helper that made it.
"""

from __future__ import annotations

import copy
import unittest

from great_orb_project_data import (
    GREAT_ORB_PROJECT_ACTIVITY_ID,
    GREAT_ORB_PROJECT_ROUNDS,
    OMNI_TALISMAN_ACCESS_PAIRS,
)
from great_orb_project_logic import (
    GREAT_ORB_PROJECT_STATE_VERSION,
    apply_great_orb_project_command_pure,
    apply_great_orb_project_review_pure,
    buy_great_orb_project_reward_pure,
    enter_great_orb_project_pure,
    great_orb_project_view_pure,
    leave_great_orb_project_pure,
    set_great_orb_project_policy_pure,
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
        "inventory": {"Pure essence": 20},
        "runecrafting_level": 60,
        "runecrafting_exp": 100.0,
        "activity_session": {"active_id": ""},
        "wicked_hood": {"omni_fed": False},
        "great_orb_project_last_result": "",
    }
    player.update(overrides)
    return player


def _match_save(
    round_index: int = 2, crafting_policy: str = "save_for_nature"
) -> dict:
    return _player(
        activity_session={"active_id": GREAT_ORB_PROJECT_ACTIVITY_ID},
        current_utility=GREAT_ORB_PROJECT_ACTIVITY_ID,
        great_orb_project={
            "version": GREAT_ORB_PROJECT_STATE_VERSION,
            "tokens": 900,
            "games_completed": 3,
            "games_won": 1,
            "automation_mode": "advanced",
            "doctrine": "attract",
            "crafting_policy": crafting_policy,
            "omni_talisman_xp_claimed": False,
            "active": {
                "round": round_index,
                "rounds_won": 1,
                "rounds_lost": 1,
                "rounds_tied": 0,
                "pending_tokens": 110,
                "saved_essence": 5,
                "crafted_essence": 12,
                "xp_earned": 42.5,
                "participating_rounds": 2,
            },
        },
    )


def _idle_save(**overrides) -> dict:
    return _player(
        great_orb_project={
            "version": GREAT_ORB_PROJECT_STATE_VERSION,
            "tokens": 900,
            "games_completed": 3,
            "games_won": 1,
            "automation_mode": "advanced",
            "doctrine": "attract",
            "crafting_policy": "craft_each_round",
            "omni_talisman_xp_claimed": False,
            "active": {},
        },
        **overrides,
    )


def _all_access_inventory() -> dict:
    return {talisman: 1 for talisman, _tiara in OMNI_TALISMAN_ACCESS_PAIRS}


class GreatOrbProjectWriteThroughTest(unittest.TestCase):
    def test_the_probe_itself_catches_a_write_through(self):
        """Without this, a passing probe could mean the freeze does nothing."""
        frozen = _frozen_save({"nested": {"count": 1}, "rows": [1, 2]})
        with self.assertRaises(WriteThroughError):
            frozen["nested"]["count"] = 1  # same value: the gate cannot see this
        with self.assertRaises(WriteThroughError):
            frozen["rows"].append(3)

    def test_frozen_save_is_equal_to_the_plain_one(self):
        """The freeze must not change what the helpers observe."""
        self.assertEqual(_frozen_save(_match_save()), _match_save())
        self.assertEqual(_frozen_save(_idle_save()), _idle_save())

    def test_command_helpers_never_write_through(self):
        cases = (
            (
                "set_great_orb_project_policy_pure",
                lambda d: set_great_orb_project_policy_pure(
                    d, {"automation_mode": "advanced", "doctrine": "repel"}
                ),
                _idle_save(),
            ),
            (
                "set_great_orb_project_policy_pure/rejected",
                lambda d: set_great_orb_project_policy_pure(d, {"doctrine": "nope"}),
                _idle_save(),
            ),
            (
                "enter_great_orb_project_pure",
                lambda d: enter_great_orb_project_pure(d),
                _idle_save(),
            ),
            (
                "enter_great_orb_project_pure/rejected",
                lambda d: enter_great_orb_project_pure(d),
                _match_save(),
            ),
            (
                "leave_great_orb_project_pure",
                lambda d: leave_great_orb_project_pure(d),
                _match_save(),
            ),
            (
                "buy_great_orb_project_reward_pure/pure_essence",
                lambda d: buy_great_orb_project_reward_pure(d, "pure_essence", 5),
                _idle_save(),
            ),
            (
                "buy_great_orb_project_reward_pure/omni_talisman",
                lambda d: buy_great_orb_project_reward_pure(d, "omni_talisman"),
                _idle_save(inventory=_all_access_inventory()),
            ),
            (
                "buy_great_orb_project_reward_pure/omni_tiara",
                lambda d: buy_great_orb_project_reward_pure(d, "omni_tiara"),
                _idle_save(inventory={"Omni-talisman": 1, "Tiara": 1}),
            ),
            (
                "buy_great_orb_project_reward_pure/unknown",
                lambda d: buy_great_orb_project_reward_pure(d, "no_such_reward"),
                _idle_save(),
            ),
            (
                "apply_great_orb_project_command_pure/unknown",
                lambda d: apply_great_orb_project_command_pure(d, "not_an_action"),
                _match_save(),
            ),
            (
                "great_orb_project_view_pure",
                lambda d: (great_orb_project_view_pure(d), True, {}),
                _match_save(),
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
            ("mid_round/win", _match_save(2), 0.9, 0.1),
            ("mid_round/loss", _match_save(2), 0.1, 0.9),
            ("mid_round/craft_each_round", _match_save(2, "craft_each_round"), 0.5, 0.5),
            ("final_round", _match_save(GREAT_ORB_PROJECT_ROUNDS - 1), 0.9, 0.1),
            ("not_entered", _idle_save(), 0.5, 0.5),
        )
        for label, fixture, player_roll, opponent_roll in cases:
            with self.subTest(case=label):
                frozen = _frozen_save(fixture)
                updated, result = apply_great_orb_project_review_pure(
                    frozen, player_roll, opponent_roll
                )
                self.assertEqual(
                    frozen,
                    fixture,
                    f"apply_great_orb_project_review_pure ({label}) changed the save "
                    "it was lent",
                )
                self.assertIsInstance(updated, dict)
                self.assertIn("allowed", result)

    def test_round_progress_and_runes_land_only_in_the_returned_save(self):
        """A frozen fixture would raise on write-through, so this pins the values."""
        fixture = _match_save(2, "craft_each_round")
        frozen = _frozen_save(fixture)
        updated, result = apply_great_orb_project_review_pure(frozen, 0.9, 0.1)
        self.assertTrue(result["allowed"])
        self.assertEqual(updated["great_orb_project"]["active"]["round"], 3)
        self.assertEqual(frozen["great_orb_project"]["active"]["round"], 2)
        self.assertGreater(updated["inventory"][result["output_item"]], 0)
        self.assertNotIn(result["output_item"], frozen["inventory"])


if __name__ == "__main__":
    unittest.main()
