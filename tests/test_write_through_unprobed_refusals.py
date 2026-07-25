"""Cover the three converted sites that no other probe actually executes.

The deepcopy sweep converted 37 sites and added 16 probe files, but a line trace
over all of them showed three converted lines with zero hits: the probes reasoned
about those paths without ever running them. All three are refusal or no-op exits
that return `dict(player_data)` with no write, which is why they were judged safe
by inspection — this file turns that judgement into coverage.

Each case is driven under containers that refuse mutation, so a write-through
raises regardless of the value written, rather than being invisible whenever the
value written happens to equal what was already there.
"""

from __future__ import annotations

import copy
import os
import sys
import unittest

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_ADDON_DIR = os.path.dirname(_THIS_DIR)
if _ADDON_DIR not in sys.path:
    sys.path.insert(0, _ADDON_DIR)

import pest_control_logic
import pet_logic
import stealing_creation_logic
from constants import ITEM_DEFINITIONS, ORE_DATA
from storage_pure import default_player_data
from tests.test_write_through_probe import WriteThroughError, _frozen_save


def _save_with_follower(kind: str) -> dict:
    save = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    summoning = dict(save.get("summoning_state") or {})
    summoning["active_follower"] = (
        {"kind": kind, "entity_id": "probe-1"} if kind else {}
    )
    save["summoning_state"] = summoning
    return save


class UnprobedRefusalPathsTest(unittest.TestCase):
    def test_pest_control_dismiss_with_no_follower_writes_nothing(self):
        frozen = _frozen_save(_save_with_follower(""))
        baseline = copy.deepcopy(_save_with_follower(""))

        updated, ok, kind = pest_control_logic._dismiss_follower(frozen)

        self.assertTrue(ok)
        self.assertEqual(kind, "")
        self.assertEqual(frozen, baseline, "the save it was lent changed")
        self.assertIsNot(updated, frozen, "must return a new top-level mapping")

    def test_stealing_creation_dismiss_with_unknown_kind_refuses_cleanly(self):
        frozen = _frozen_save(_save_with_follower("beast-of-burden"))
        baseline = copy.deepcopy(_save_with_follower("beast-of-burden"))

        updated, ok = stealing_creation_logic._dismiss_follower(frozen)

        self.assertFalse(ok, "an unknown follower kind must refuse")
        self.assertEqual(frozen, baseline, "the save it was lent changed")
        self.assertIsNot(updated, frozen)

    def test_hatch_phoenix_egg_refusals_return_the_save_untouched(self):
        """The reachable refusals in hatch_phoenix_egg_pure.

        Its third refusal — the `if not ok` after acquire_pet_pure — is NOT
        covered here because it cannot execute: this function gates on Summoning
        72 and both egglings require exactly 72, so clearing the gate above also
        clears acquire's, and acquire has no other refusal. That is recorded at
        the site rather than papered over with a contrived fixture.
        """
        for item_name, note in (
            ("Phoenix egg", "summoning gate at level 1"),
            ("Nonexistent egg", "unknown egg name"),
        ):
            with self.subTest(egg=item_name, path=note):
                save = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
                save["inventory"] = {item_name: 1}
                frozen = _frozen_save(save)
                baseline = copy.deepcopy(save)

                updated, ok, _info = pet_logic.hatch_phoenix_egg_pure(
                    frozen, item_name
                )

                self.assertFalse(ok, "a refused hatch must report failure")
                self.assertEqual(frozen, baseline, "the save it was lent changed")
                self.assertEqual(
                    updated.get("inventory", {}).get(item_name),
                    1,
                    "a refused hatch must not consume the egg",
                )

    def test_the_freeze_still_has_teeth_here(self):
        """Guard the guard: these assertions must be able to fail."""
        frozen = _frozen_save(_save_with_follower("pet"))
        with self.assertRaises(WriteThroughError):
            frozen["summoning_state"]["active_follower"] = {}


if __name__ == "__main__":
    unittest.main()
