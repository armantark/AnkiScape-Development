"""Effigy and lamp custody across dangerous deaths, recovery and expiry."""

from __future__ import annotations

import copy
import random
import sys
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.logic.ancient_effigies import actions
from ankiscape.logic.ancient_effigies.custody import INSTANCES_KEY, NEXT_ID_KEY, synchronize_effigy_custody_pure
from ankiscape.logic_pure.logic_pure_combat_engine import (
    advance_combat_grave_review_pure,
    reclaim_death_office_items_pure,
    start_combat_grave_walk_pure,
)
from ankiscape.logic_pure.logic_pure_combat_model import (
    _carried_inventory_grave_counts,
    _combat_apply_pvm_death,
)
from ankiscape.logic_pure.logic_pure_combat_outcome import _combat_settle_burst_outcome

SEED_A = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
SEED_B = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
_BASE = default_player_data(ORE_DATA, ITEM_DEFINITIONS)


def record(item_id, location, seed=SEED_A, step=0, pair=None):
    return {"item_id": item_id, "location": location, "request_seed": seed, "request_step": step, "pair_index": pair}


def fighter(*, starved=0, carried=None, lamps=0, coins=0, equipment=None):
    """A complete save at Goblins, carrying the given pack view and held lamps."""
    data = copy.deepcopy(_BASE)
    data["inventory"]["Starved ancient effigy"] = starved
    data["inventory"]["Coins"] = coins
    data["inventory"]["Shark"] = 5
    data["equipment"] = dict(equipment or {})
    data["current_combat_target"] = "goblin"
    data["carried_inventory"] = {"goblin": dict(carried or {}), "cow": {"Shark": 2}}
    instances = {}
    seeds = (SEED_A, SEED_B)
    for number in range(1, starved + 1):
        instances[f"ancient-effigy-{number}"] = record(18778, "bank", seeds[(number - 1) % 2], 0, number - 1)
    for number in range(starved + 1, starved + lamps + 1):
        instances[f"ancient-effigy-{number}"] = record(18782, "held", SEED_A, 3, None)
    data[INSTANCES_KEY] = instances
    data[NEXT_ID_KEY] = starved + lamps + 1
    return synchronize_effigy_custody_pure(data)


def die(data, **kwargs):
    data = copy.deepcopy(data)
    _combat_apply_pvm_death(data, 100, **kwargs)
    return data


def locations(data):
    return {key: value["location"] for key, value in data[INSTANCES_KEY].items()}


def walk_back(data):
    data, ok = start_combat_grave_walk_pure(data)
    assert ok
    for _ in range(50):
        data = advance_combat_grave_review_pure(data)
        if not data["combat_grave"]:
            return synchronize_effigy_custody_pure(data)
    raise AssertionError("the walk never arrived")


class DeathTest(unittest.TestCase):
    def test_held_lamps_are_carried_once_without_a_bank_count(self):
        data = fighter(lamps=2)
        self.assertEqual(_carried_inventory_grave_counts(data), {"Dragonkin lamp": 2})
        del data["carried_inventory"]
        self.assertEqual(_carried_inventory_grave_counts(data), {"Dragonkin lamp": 2})
        stale = fighter(lamps=1, carried={"Dragonkin lamp": 4})
        self.assertEqual(_carried_inventory_grave_counts(stale), {"Dragonkin lamp": 1})

    def test_ordinary_dangerous_death_graves_the_lowest_copy_and_each_lamp_once(self):
        data = fighter(starved=2, carried={"Starved ancient effigy": 1, "Shark": 2}, lamps=1)
        dead = die(data)
        self.assertEqual(sorted(dead["combat_grave"]["items"]), ["Dragonkin lamp", "Shark", "Shark", "Starved ancient effigy"])
        self.assertEqual(locations(dead), {"ancient-effigy-1": "grave", "ancient-effigy-2": "bank", "ancient-effigy-3": "grave"})
        self.assertEqual(dead["inventory"]["Starved ancient effigy"], 1)
        self.assertEqual(dead["inventory"]["Shark"], 3)
        self.assertNotIn("Dragonkin lamp", dead["inventory"], "no Bank lamp unit is debited or minted")
        self.assertNotIn("goblin", dead["carried_inventory"])
        self.assertEqual(dead["carried_inventory"]["cow"], {"Shark": 2}, "dormant packs stay banked")
        self.assertEqual(synchronize_effigy_custody_pure(dead)[INSTANCES_KEY], dead[INSTANCES_KEY])

    def test_safe_death_changes_no_custody(self):
        data = fighter(starved=1, carried={"Starved ancient effigy": 1}, lamps=1)
        before = copy.deepcopy(data)
        _combat_settle_burst_outcome(
            data, "goblin", 0, True, False, 0, 100, 10, 10,
            live_cadence=True, safe_death=True, no_grave=False, enemy={},
        )
        self.assertEqual(data[INSTANCES_KEY], before[INSTANCES_KEY])
        self.assertEqual(data["inventory"], before["inventory"])

    def test_no_grave_death_keeps_protected_lamps_and_deletes_the_rest(self):
        data = fighter(lamps=3)
        kept = die(data, no_grave=True, kept_items=2)
        # The lost copy is chosen in numeric order, like every other loss.
        self.assertEqual(locations(kept), {"ancient-effigy-2": "held", "ancient-effigy-3": "held"})
        self.assertEqual(kept["combat_grave"], {})
        self.assertEqual(kept["death_office"], data["death_office"])
        self.assertEqual(synchronize_effigy_custody_pure(kept)[INSTANCES_KEY], kept[INSTANCES_KEY])
        lost = die(fighter(starved=1, carried={"Starved ancient effigy": 1}, lamps=1), no_grave=True, kept_items=1)
        self.assertEqual(locations(lost), {"ancient-effigy-1": "bank"}, "the more valuable effigy is the protected item")
        self.assertNotIn("Dragonkin lamp", lost["inventory"])
        self.assertEqual(lost["combat_grave"], {})

    def test_redemption_refuses_while_the_lamp_is_graved_or_officed(self):
        dead = die(fighter(lamps=1))
        token = actions.lamp_token_pure("ancient-effigy-1")
        updated, ok, info = actions.redeem_lamp_pure(dead, token, "attack")
        self.assertFalse(ok)
        self.assertIs(updated, dead)
        self.assertIn("Reclaim", info["message"])
        twice = die(dead)
        self.assertEqual(locations(twice), {"ancient-effigy-1": "death_office"})
        self.assertFalse(actions.redeem_lamp_pure(twice, token, "attack")[1])
        self.assertFalse(actions.destroy_lamp_pure(twice, token)[1])


class RecoveryTest(unittest.TestCase):
    def test_grave_reclaim_restores_the_same_copy_and_the_held_lamp(self):
        data = fighter(starved=2, carried={"Starved ancient effigy": 1}, lamps=1)
        dead = die(data)
        reclaimed = walk_back(dead)
        self.assertEqual(reclaimed[INSTANCES_KEY], data[INSTANCES_KEY])
        self.assertEqual(reclaimed["inventory"]["Starved ancient effigy"], 2)
        self.assertNotIn("Dragonkin lamp", reclaimed["inventory"], "no Bank lamp entry")
        _updated, ok, _info = actions.redeem_lamp_pure(reclaimed, actions.lamp_token_pure("ancient-effigy-3"), "attack")
        self.assertTrue(ok)

    def test_office_reclaim_restores_the_same_copy(self):
        data = fighter(starved=1, carried={"Starved ancient effigy": 1}, lamps=1, coins=10_000)
        twice = die(die(data))
        self.assertEqual(locations(twice), {"ancient-effigy-1": "death_office", "ancient-effigy-2": "death_office"})
        reclaimed, ok, _reason = reclaim_death_office_items_pure(twice)
        self.assertTrue(ok)
        reclaimed = synchronize_effigy_custody_pure(reclaimed)
        self.assertEqual(reclaimed[INSTANCES_KEY], data[INSTANCES_KEY])
        self.assertNotIn("Dragonkin lamp", reclaimed["inventory"], "no Bank lamp entry")

    def test_grave_expiry_loses_the_copies_without_minting_replacements(self):
        dead = die(fighter(starved=2, carried={"Starved ancient effigy": 1}, lamps=1))
        for _ in range(500):
            dead = advance_combat_grave_review_pure(dead)
            if not dead["combat_grave"]:
                break
        expired = synchronize_effigy_custody_pure(dead)
        self.assertEqual(locations(expired), {"ancient-effigy-2": "bank"})
        self.assertEqual(expired[NEXT_ID_KEY], 4)

    def test_a_second_death_moves_the_old_copy_to_the_office_and_graves_the_new_one(self):
        data = fighter(starved=2, carried={"Starved ancient effigy": 1}, coins=10_000)
        first = die(data)
        self.assertEqual(locations(first), {"ancient-effigy-1": "grave", "ancient-effigy-2": "bank"})
        first["carried_inventory"]["goblin"] = {"Starved ancient effigy": 1}
        second = die(first)
        self.assertEqual(locations(second), {"ancient-effigy-1": "death_office", "ancient-effigy-2": "grave"})
        self.assertEqual(second["death_office"]["items"], ["Starved ancient effigy"])
        self.assertEqual(second["combat_grave"]["items"], ["Starved ancient effigy"])
        synced = synchronize_effigy_custody_pure(second)
        self.assertEqual(synced[INSTANCES_KEY], second[INSTANCES_KEY], "same-name copies do not swap requests")
        from_grave = walk_back(synced)
        self.assertEqual(locations(from_grave), {"ancient-effigy-1": "death_office", "ancient-effigy-2": "bank"})
        self.assertEqual(from_grave[INSTANCES_KEY]["ancient-effigy-2"], data[INSTANCES_KEY]["ancient-effigy-2"])
        from_office, ok, _reason = reclaim_death_office_items_pure(from_grave)
        self.assertTrue(ok)
        from_office = synchronize_effigy_custody_pure(from_office)
        self.assertEqual(from_office[INSTANCES_KEY], data[INSTANCES_KEY])

    def test_ordinary_carried_death_behavior_is_unchanged(self):
        data = fighter(carried={"Shark": 3}, equipment={"weapon": "Iron sword"})
        data["inventory"]["Shark"] = 2
        dead = die(data)
        self.assertEqual(sorted(dead["combat_grave"]["items"]), ["Iron sword", "Shark", "Shark"])
        self.assertEqual(dead["inventory"]["Shark"], 0)
        self.assertEqual(dead["equipment"], {})
        self.assertEqual(dead[INSTANCES_KEY], {})


class RecoveryUndoTest(unittest.TestCase):
    def setUp(self):
        from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package
        from tests.test_direct_action_undo_seam import _DummyMW, _FakeCollection

        self._modules = dict(sys.modules)
        self._random_state = random.getstate()
        _install_runtime_fakes()
        self.addon = _load_addon_as_package("ankiscape_effigy_recovery_undo")
        self.addon.mw = _DummyMW(_FakeCollection())
        self.addon.save_player_data = lambda: None

    def tearDown(self):
        random.setstate(self._random_state)
        sys.modules.clear()
        sys.modules.update(self._modules)

    def _undo(self):
        self.addon._on_state_did_undo(type("Changes", (), {"operation": "AnkiScape direct action"})())

    def test_death_and_reclaim_undo_and_replay_exactly(self):
        addon = self.addon
        addon._state.player_data = fighter(starved=2, carried={"Starved ancient effigy": 1}, lamps=1, coins=10_000)
        start = copy.deepcopy(addon._state.player_data)

        def death(current):
            return die(current), True

        self.assertTrue(addon.commit_direct_action(death))
        after_death = copy.deepcopy(addon._state.player_data)
        self._undo()
        self.assertEqual(addon._state.player_data, start)
        self.assertTrue(addon.commit_direct_action(death))
        self.assertEqual(addon._state.player_data, after_death)

        self.assertTrue(addon.commit_direct_action(death))
        twice = copy.deepcopy(addon._state.player_data)

        def reclaim(current):
            updated, ok, _reason = reclaim_death_office_items_pure(current)
            return synchronize_effigy_custody_pure(updated), ok

        self.assertTrue(addon.commit_direct_action(reclaim))
        reclaimed = copy.deepcopy(addon._state.player_data)
        self.assertEqual(reclaimed[INSTANCES_KEY]["ancient-effigy-1"], start[INSTANCES_KEY]["ancient-effigy-1"])
        self._undo()
        self.assertEqual(addon._state.player_data, twice)
        self.assertTrue(addon.commit_direct_action(reclaim))
        self.assertEqual(addon._state.player_data, reclaimed)


if __name__ == "__main__":
    unittest.main()
