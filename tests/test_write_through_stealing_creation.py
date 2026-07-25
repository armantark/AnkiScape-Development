"""Value-blind write-through probe for stealing_creation_logic.

Modelled on tests/test_write_through_probe.py.  The equality gate in
`immutability_gate.py` cannot see a write that stores a value equal to the one
already present, so this probe lends the helpers a save whose nested containers
refuse every mutating operation.  Any write through a container the helper did
not rebuild raises immediately, whatever value is written.

Stealing Creation is a gather-and-spend loop with three paths worth pinning:
entry, which dismisses an outside follower through two other modules; the raid
review, which builds a temporary loadout out of the working save and hands it to
the real combat engine; and the reward tools, whose charge and form live in a
nested sub-dict that the XP-bonus reducer edits on every eligible action.
"""

from __future__ import annotations

import random
import unittest

from constants import ITEM_DEFINITIONS, ORE_DATA
from pet_data import PETS_BY_ID
from storage_pure import default_player_data

import stealing_creation_logic as sc


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
        # Copying is not writing.  `copy.deepcopy` rebuilds a subclass through
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
    save.update(
        {
            "attack_level": 80,
            "strength_level": 80,
            "defense_level": 80,
            "constitution_level": 80,
            "mining_level": 80,
            "fishing_level": 80,
            "hunter_level": 80,
            "woodcutting_level": 80,
            "construction_level": 80,
            "smithing_level": 80,
            "combat_lifepoints": 800,
            "inventory": {},
        }
    )
    save.update(overrides)
    return save


def _entered(**overrides) -> dict:
    entered, ok, info = sc.apply_stealing_creation_command_pure(
        _save(**overrides), "enter", {"confirm_dismiss_follower": True}, lambda: 0.5
    )
    assert ok, info
    return entered


def _entered_with_raid_next() -> dict:
    """An active session whose next review is the raid review."""
    entered = _entered()
    session = dict(entered["stealing_creation"]["active_session"])
    session["next_raid_review"] = 1
    entered["stealing_creation"]["active_session"] = session
    return entered


def _weak_entered() -> dict:
    """A low-level entrant, so the raider sometimes wins."""
    save = _save()
    for key in ("attack_level", "strength_level", "defense_level", "constitution_level"):
        save[key] = 3
    save["combat_lifepoints"] = 30
    entered, ok, info = sc.start_stealing_creation_session_pure(save, lambda: 0.5)
    assert ok, info
    return entered


def _with_tool(kind: str = "morphic") -> dict:
    """An owned, fully charged reward tool of the given kind."""
    save = _save(stealing_creation={"points": sc.STEALING_CREATION_REWARD_COST})
    bought, ok, info = sc.purchase_stealing_creation_tool_pure(save, kind)
    assert ok, info
    return bought


def _familiar_follower_save() -> dict:
    save = _save()
    summoning = dict(save["summoning_state"])
    summoning["active_follower"] = {
        "kind": "familiar",
        "entity_id": "spiritwolf",
        "remaining_reviews": 4,
        "max_reviews": 4,
        "storage": {},
    }
    save["summoning_state"] = summoning
    return save


def _pet_follower_save() -> dict:
    save = _save()
    save["summoning_state"] = {
        "active_follower": {"kind": "pet", "entity_id": "probe-1"},
        "pet_instances": {
            "probe-1": {
                "pet_id": next(iter(PETS_BY_ID)),
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
    return save


def _kindless_follower_save() -> dict:
    """A follower record with no kind: the entry path's own fallback branch."""
    save = _save()
    summoning = dict(save["summoning_state"])
    summoning["active_follower"] = {"entity_id": "orphaned"}
    save["summoning_state"] = summoning
    return save


class StealingCreationWriteThroughTest(unittest.TestCase):
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

    def test_ensure_state_never_writes_through(self):
        frozen = _frozen_save(_save())
        data = sc.ensure_stealing_creation_state_pure(frozen)
        self.assertEqual(data["stealing_creation"]["reward_tools"]["morphic"], {})
        self.assertEqual(frozen, _save(), "ensure_state changed the save it was lent")

    def test_entry_never_writes_through(self):
        for label, builder in (
            ("no follower", _save),
            ("familiar follower", _familiar_follower_save),
            ("pet follower", _pet_follower_save),
            ("follower without a kind", _kindless_follower_save),
        ):
            with self.subTest(case=label):
                baseline = builder()
                frozen = _frozen_save(baseline)
                entered, ok, info = sc.start_stealing_creation_session_pure(
                    frozen, lambda: 0.5, confirm_dismiss_follower=True
                )
                self.assertTrue(ok, info)
                self.assertTrue(entered["stealing_creation"]["active_session"])
                self.assertEqual(
                    frozen, baseline, f"entry with {label} changed the save it was lent"
                )

    def test_each_review_duty_never_writes_through(self):
        for duty in ("gather", "process", "deposit"):
            with self.subTest(duty=duty):
                baseline = _entered()
                state = dict(baseline["stealing_creation"])
                state["automation_mode"] = "advanced"
                state["selected_duty"] = duty
                session = dict(state["active_session"])
                session["next_raid_review"] = 20
                session["clay"] = dict(session["clay"])
                session["clay"]["3"] = 6
                state["active_session"] = session
                baseline["stealing_creation"] = state
                frozen = _frozen_save(baseline)
                updated, ok, result = sc.apply_stealing_creation_review_pure(
                    frozen, lambda: 0.0
                )
                self.assertTrue(ok, result)
                self.assertEqual(result["action"], duty)
                self.assertEqual(
                    frozen, baseline, f"the {duty} duty changed the save it was lent"
                )

    def test_raid_review_never_writes_through(self):
        """The raid hands a temporary loadout built from the save to the engine."""
        baseline = _entered_with_raid_next()
        frozen = _frozen_save(baseline)
        updated, ok, result = sc.apply_stealing_creation_review_pure(frozen, lambda: 0.5)
        self.assertTrue(ok, result)
        self.assertEqual(result["action"], "raid")
        self.assertEqual(frozen, baseline, "the raid review changed the save it was lent")

    def test_a_full_session_never_writes_through(self):
        """Whole sessions on several rng streams, to reach the rarer raid ends.

        Each review is lent a freshly frozen save, which is what the runtime
        does: it copies the returned save back over the live one between calls.
        """
        outcomes: set[str] = set()
        for seed in range(8):
            rng = random.Random(seed).random
            for builder in (_entered, _weak_entered):
                save = builder()
                for _ in range(sc.STEALING_CREATION_SESSION_REVIEWS):
                    baseline = _plain_copy(save)
                    frozen = _frozen_save(save)
                    save, ok, result = sc.apply_stealing_creation_review_pure(frozen, rng)
                    self.assertTrue(ok, result)
                    self.assertEqual(
                        frozen, baseline, "a review changed the save it was lent"
                    )
                    outcomes.add(str(result.get("action", "")))
                    outcomes.update(
                        key
                        for key in ("killed", "died", "fled", "complete")
                        if result.get(key)
                    )
        self.assertIn("raid", outcomes)
        self.assertIn("complete", outcomes)
        self.assertTrue(
            {"killed", "died"} & outcomes,
            f"no raid ever resolved in a kill or a death: {sorted(outcomes)}",
        )

    def test_reward_tool_paths_never_write_through(self):
        baseline = _save(stealing_creation={"points": sc.STEALING_CREATION_REWARD_COST})
        frozen = _frozen_save(baseline)
        bought, ok, info = sc.purchase_stealing_creation_tool_pure(frozen, "morphic")
        self.assertTrue(ok, info)
        self.assertEqual(bought["inventory"]["Proto-tool"], 1)
        self.assertEqual(frozen, baseline, "buy_tool changed the save it was lent")

        owned = _with_tool("morphic")
        frozen_owned = _frozen_save(owned)
        spent, bonus, detail = sc.apply_stealing_creation_xp_bonus_pure(
            frozen_owned, "smithing_exp", 50.0
        )
        self.assertTrue(detail["applied"], detail)
        self.assertGreater(bonus, 0.0)
        self.assertLess(
            spent["stealing_creation"]["reward_tools"]["morphic"]["charge"], 1.0
        )
        self.assertEqual(
            frozen_owned, owned, "the XP-bonus reducer changed the save it was lent"
        )

    def test_router_command_paths_never_write_through(self):
        for label, baseline, action_id, payload in (
            ("leave", _entered(), "leave", {}),
            (
                "set_policy",
                _save(),
                "set_policy",
                {"automation_mode": "advanced", "selected_duty": "deposit"},
            ),
            ("activate_tool", _with_tool("morphic"), "activate_tool", {"kind": "morphic"}),
            (
                "morph_tool",
                _with_tool("morphic"),
                "morph_tool",
                {"form_id": "needle"},
            ),
        ):
            with self.subTest(case=label):
                frozen = _frozen_save(baseline)
                _updated, ok, info = sc.apply_stealing_creation_command_pure(
                    frozen, action_id, payload, lambda: 0.5
                )
                self.assertTrue(ok, info)
                self.assertEqual(
                    frozen, baseline, f"{label} changed the save it was lent"
                )

    def test_unknown_command_returns_the_save_without_writing_through(self):
        frozen = _frozen_save(_save())
        returned, ok, info = sc.apply_stealing_creation_command_pure(frozen, "wat")
        self.assertFalse(ok)
        self.assertIn("Unknown", info["reason"])
        self.assertEqual(frozen, _save(), "the router changed the save it was lent")
        returned["current_utility"] = "caller wrote here"
        self.assertEqual(frozen, _save())


if __name__ == "__main__":
    unittest.main()
