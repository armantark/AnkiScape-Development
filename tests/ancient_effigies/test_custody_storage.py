"""Per-copy effigy custody through synchronization and the real storage facade."""

from __future__ import annotations

import copy
import json
import math
import random
import sys
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.persistence.item_instances import (
    default_item_instance_state_pure,
    sanitize_item_instance_state_pure,
)
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from ankiscape.data.equipment_condition_data import EQUIPMENT_CONDITION_DATA
from ankiscape.logic.ancient_effigies import actions
from ankiscape.logic.ancient_effigies.custody import (
    INSTANCES_KEY,
    NEXT_ID_KEY,
    synchronize_effigy_custody_pure,
)
from ankiscape.logic.equipment_instance_logic import (
    default_equipment_instance_state_pure,
    sanitize_equipment_instance_state_pure,
)
from tests.test_cold_war_greeting import GREETING, SAMPLER
from tests.test_storage_runtime import _LegacyTextCollection, _load_storage_module

PLAYER_KEY = "ankiscape_player_data"
SEED_1 = "00000000000000000000000000000001"
SEED_2 = "00000000000000000000000000000002"


def record(item_id, location, seed=SEED_1, step=0, pair=None):
    return {"item_id": item_id, "location": location, "request_seed": seed, "request_step": step, "pair_index": pair}


def counting_bits(start=1):
    """A deterministic getrandbits stand-in that records each draw."""
    draws = []

    def getrandbits(bits):
        draws.append(bits)
        return start + len(draws) - 1

    return getrandbits, draws


def sync(data, **kwargs):
    return synchronize_effigy_custody_pure(data, **kwargs)


class SynchronizationTest(unittest.TestCase):
    def test_count_only_copies_get_ids_and_hidden_seeds_without_a_pair(self):
        bits, draws = counting_bits(5)
        synced = sync({"inventory": {"Starved ancient effigy": 2, "Gorged ancient effigy": 1}}, getrandbits=bits)
        self.assertEqual(draws, [128, 128, 128])
        self.assertEqual(
            synced[INSTANCES_KEY],
            {
                "ancient-effigy-1": record(18778, "bank", f"{5:032x}"),
                "ancient-effigy-2": record(18778, "bank", f"{6:032x}"),
                "ancient-effigy-3": record(18781, "bank", f"{7:032x}"),
            },
        )
        self.assertEqual(synced[NEXT_ID_KEY], 4)

    def test_the_shared_random_module_supplies_seeds(self):
        random.seed(99)
        expected = f"{random.getrandbits(128):032x}"
        random.seed(99)
        synced = sync({"inventory": {"Starved ancient effigy": 1}})
        self.assertEqual(synced[INSTANCES_KEY]["ancient-effigy-1"]["request_seed"], expected)

    def test_normalized_and_empty_saves_allocate_nothing(self):
        bits, draws = counting_bits()
        self.assertEqual(sync({"inventory": {}}, getrandbits=bits)[INSTANCES_KEY], {})
        data = {
            "inventory": {"Starved ancient effigy": 2},
            INSTANCES_KEY: {"ancient-effigy-1": record(18778, "bank", SEED_1, 0, 0), "ancient-effigy-4": record(18778, "bank", SEED_2)},
            NEXT_ID_KEY: 9,
        }
        before = copy.deepcopy(data)
        synced = sync(data, getrandbits=bits)
        self.assertEqual(draws, [])
        self.assertEqual(data, before, "the caller's nested objects are not mutated")
        self.assertEqual(synced[INSTANCES_KEY], before[INSTANCES_KEY])
        self.assertEqual(synced[NEXT_ID_KEY], 9)

    def test_malformed_fields_are_repaired_one_by_one(self):
        bits, draws = counting_bits(10)
        data = {
            "inventory": {"Starved ancient effigy": 3, "Sated ancient effigy": 1},
            INSTANCES_KEY: {
                "ancient-effigy-2": {**record(18778, "bank", "NOT-HEX", 0, 4)},
                "ancient-effigy-3": {**record(18778, "bank"), "request_step": True, "pair_index": 2.5},
                "ancient-effigy-5": {**record(18778, "bank", SEED_2), "request_step": math.inf, "pair_index": 3.0},
                "ancient-effigy-30": {"item_id": 99999, "location": "bank"},
                "ancient-effigy-7": {**record(18780, "held", SEED_1, 2, 6)},
                "ancient-effigy-007": record(18778, "bank"),
                "effigy-50": record(18778, "bank"),
                "ancient-effigy-8": "not a record",
            },
            NEXT_ID_KEY: True,
        }
        synced = sync(data, getrandbits=bits)
        instances = synced[INSTANCES_KEY]
        self.assertEqual(list(instances), ["ancient-effigy-2", "ancient-effigy-3", "ancient-effigy-5", "ancient-effigy-7"])
        self.assertEqual(instances["ancient-effigy-2"], record(18778, "bank", f"{10:032x}", 0, 4), "the valid pair survives a seed repair")
        self.assertEqual(instances["ancient-effigy-3"], record(18778, "bank", SEED_1, 0, None))
        self.assertEqual(instances["ancient-effigy-5"], record(18778, "bank", SEED_2, 0, 3))
        self.assertEqual(instances["ancient-effigy-7"], record(18780, "bank", SEED_1, 2, 6), "a misplaced copy fills the Bank shortfall")
        self.assertEqual(draws, [128])
        self.assertEqual(synced[NEXT_ID_KEY], 31, "discarded numeric IDs still raise the high-water mark")

    def test_lamp_records_never_keep_a_pair_or_a_bank_location(self):
        data = {
            "inventory": {"Dragonkin lamp": 1},
            INSTANCES_KEY: {
                "ancient-effigy-1": record(18782, "held", SEED_1, 3, 5),
                "ancient-effigy-2": record(18782, "bank", SEED_2, 3, None),
            },
            NEXT_ID_KEY: 3,
        }
        synced = sync(data)
        self.assertEqual(
            synced[INSTANCES_KEY],
            {"ancient-effigy-1": record(18782, "held", SEED_1, 3, None), "ancient-effigy-2": record(18782, "held", SEED_2, 3, None)},
        )
        self.assertEqual(synced["inventory"], {}, "no Bank lamp entry remains")

    def test_holder_reconciliation_preserves_assignments_then_moves_in_numeric_order(self):
        bits, _draws = counting_bits(40)
        data = {
            "inventory": {"Starved ancient effigy": 2},
            "combat_grave": {"items": ["Starved ancient effigy"]},
            "death_office": {"items": ["Starved ancient effigy", "Starved ancient effigy"]},
            INSTANCES_KEY: {
                "ancient-effigy-1": record(18778, "grave", SEED_1, 0, 1),
                "ancient-effigy-2": record(18778, "grave", SEED_2, 0, 2),
                "ancient-effigy-3": record(18778, "bank", SEED_1, 0, 3),
                "ancient-effigy-9": record(18778, "death_office", SEED_2, 0, 4),
            },
            NEXT_ID_KEY: 10,
        }
        synced = sync(data, getrandbits=bits)
        locations = {key: value["location"] for key, value in synced[INSTANCES_KEY].items()}
        self.assertEqual(
            locations,
            {
                "ancient-effigy-1": "grave",
                "ancient-effigy-2": "bank",
                "ancient-effigy-3": "bank",
                "ancient-effigy-9": "death_office",
                "ancient-effigy-10": "death_office",
            },
        )
        self.assertEqual(synced[INSTANCES_KEY]["ancient-effigy-2"]["pair_index"], 2)
        self.assertEqual(synced[NEXT_ID_KEY], 11)
        surplus = sync({**data, "inventory": {}, "combat_grave": {}, "death_office": {}})
        self.assertEqual(surplus[INSTANCES_KEY], {})
        self.assertEqual(surplus[NEXT_ID_KEY], 10)

    def test_legacy_lamp_units_are_adopted_once_and_carried_views_never_hold_lamps(self):
        bits, draws = counting_bits(70)
        data = {
            "inventory": {"Dragonkin lamp": 2, "Coins": 5},
            "carried_inventory": {"bork": {"Dragonkin lamp": 2, "Shark": 3}, "goblin": {"Shark": 1}},
        }
        synced = sync(data, getrandbits=bits)
        self.assertEqual(
            synced[INSTANCES_KEY],
            {"ancient-effigy-1": record(18782, "held", f"{70:032x}"), "ancient-effigy-2": record(18782, "held", f"{71:032x}")},
        )
        self.assertEqual(synced["inventory"], {"Coins": 5})
        self.assertEqual(synced["carried_inventory"], {"bork": {"Shark": 3}, "goblin": {"Shark": 1}})
        self.assertEqual(data["inventory"]["Dragonkin lamp"], 2, "the caller's Bank is rebuilt, not edited")
        again = sync(synced, getrandbits=bits)
        self.assertEqual(again[INSTANCES_KEY], synced[INSTANCES_KEY])
        self.assertEqual(len(draws), 2)
        carried_only = sync({"inventory": {}, "carried_inventory": {"bork": {"Dragonkin lamp": 1}}}, getrandbits=bits)
        self.assertEqual(carried_only[INSTANCES_KEY], {}, "a pack view never creates a lamp")

    def test_a_stored_zero_lamp_entry_is_removed_without_touching_the_held_lamp(self):
        bits, draws = counting_bits(90)
        data = {"inventory": {"Dragonkin lamp": 0, "Coins": 5}, INSTANCES_KEY: {"ancient-effigy-1": record(18782, "held")}, NEXT_ID_KEY: 2}
        synced = sync(data, getrandbits=bits)
        self.assertEqual(synced["inventory"], {"Coins": 5})
        self.assertEqual(data["inventory"], {"Dragonkin lamp": 0, "Coins": 5}, "the caller's Bank is rebuilt, not edited")
        self.assertEqual(synced[INSTANCES_KEY], data[INSTANCES_KEY])
        self.assertEqual(sync(synced, getrandbits=bits), synced)
        self.assertEqual(draws, [])

    def test_migration_leaves_no_lamp_entry_and_is_idempotent(self):
        self.assertNotIn("Dragonkin lamp", default_player_data(ORE_DATA, ITEM_DEFINITIONS)["inventory"])
        for lamp_units in (0, 1):
            with self.subTest(lamp_units=lamp_units):
                player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
                player["inventory"]["Dragonkin lamp"] = lamp_units
                loaded = migrate_loaded_data(player, ORE_DATA, ITEM_DEFINITIONS)
                self.assertNotIn("Dragonkin lamp", loaded["inventory"])
                self.assertEqual(sum(value["item_id"] == 18782 for value in loaded[INSTANCES_KEY].values()), lamp_units)
                self.assertEqual(migrate_loaded_data(loaded, ORE_DATA, ITEM_DEFINITIONS), loaded)

    def test_a_consumed_lamp_is_not_reconstructed(self):
        data = sync({"inventory": {}, INSTANCES_KEY: {"ancient-effigy-4": record(18782, "held")}, NEXT_ID_KEY: 5})
        redeemed, ok, _info = actions.redeem_lamp_pure(data, actions.lamp_token_pure("ancient-effigy-4"), "attack")
        self.assertTrue(ok)
        resynced = sync(redeemed)
        self.assertEqual(resynced[INSTANCES_KEY], {})
        self.assertEqual(resynced[NEXT_ID_KEY], 5)


class ComposedSanitationTest(unittest.TestCase):
    def test_defaults_compose_equipment_and_effigies(self):
        self.assertEqual(
            default_item_instance_state_pure(),
            {**default_equipment_instance_state_pure(), INSTANCES_KEY: {}, NEXT_ID_KEY: 1},
        )
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual((player[INSTANCES_KEY], player[NEXT_ID_KEY]), ({}, 1))

    def test_equipment_sanitation_is_unchanged(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["equipment"] = {"weapon": "Dragon scimitar", "hands": "Barrows gloves"}
        player["inventory"]["Starved ancient effigy"] = 1
        equipment_only = sanitize_equipment_instance_state_pure(player, EQUIPMENT_CONDITION_DATA)
        composed = sanitize_item_instance_state_pure(player, EQUIPMENT_CONDITION_DATA)
        for key in ("equipment", "equipment_instances", "equipment_instance_next_id"):
            self.assertEqual(composed[key], equipment_only[key])
        self.assertEqual(len(composed[INSTANCES_KEY]), 1)

    def test_migration_adopts_counts_and_is_idempotent(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["inventory"]["Starved ancient effigy"] = 2
        player["unrelated_marker"] = {"keep": [1, 2]}
        migrated = migrate_loaded_data(json.loads(json.dumps(player)), ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(len(migrated[INSTANCES_KEY]), 2)
        self.assertEqual(migrated["unrelated_marker"], {"keep": [1, 2]})
        self.assertEqual(migrate_loaded_data(json.loads(json.dumps(migrated)), ORE_DATA, ITEM_DEFINITIONS), migrated)


class StorageFacadeTest(unittest.TestCase):
    def setUp(self):
        self._modules = dict(sys.modules)
        self._random_state = random.getstate()
        random.seed(1520)

    def tearDown(self):
        random.setstate(self._random_state)
        sys.modules.clear()
        sys.modules.update(self._modules)

    def _collection(self, raw, *, legacy=False):
        collection = _LegacyTextCollection()
        collection.legacy_row = legacy
        collection.values = {PLAYER_KEY: raw, "ankiscape_current_skill": "Crafting"}
        return collection

    def _raw(self, **extra):
        raw = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        raw["inventory"]["Starved ancient effigy"] = 2
        raw["equipment"] = {"weapon": "Dragon scimitar"}
        raw["unrelated_marker"] = {"keep": [1, {"nested": True}]}
        raw.pop(INSTANCES_KEY)
        raw.pop(NEXT_ID_KEY)
        raw.update(extra)
        return json.loads(json.dumps(raw))

    def test_adopted_identities_are_saved_before_exposure_and_survive_reopen(self):
        raw = self._raw()
        collection = self._collection(raw)
        storage = _load_storage_module(collection)
        with patch.object(collection, "set_config", wraps=collection.set_config) as save:
            loaded, skill = storage.load_player_data()
            self.assertEqual(save.call_count, 1)
        stored = collection.values[PLAYER_KEY]
        self.assertEqual(stored[INSTANCES_KEY], loaded[INSTANCES_KEY])
        self.assertEqual(len(stored[INSTANCES_KEY]), 2)
        self.assertEqual(stored["unrelated_marker"], raw["unrelated_marker"])
        self.assertEqual(stored["equipment"], raw["equipment"])
        self.assertEqual({key: value for key, value in stored.items() if key not in (INSTANCES_KEY, NEXT_ID_KEY)}, raw)
        seeds = {value["request_seed"] for value in stored[INSTANCES_KEY].values()}
        self.assertEqual(len(seeds), 2, "two same-stage copies get different requests")
        with patch.object(collection, "set_config", wraps=collection.set_config) as save:
            reopened, _skill = storage.load_player_data()
            self.assertEqual(save.call_count, 0, "a normalized save is not rewritten")
        self.assertEqual(reopened[INSTANCES_KEY], loaded[INSTANCES_KEY])
        storage.save_player_data(reopened, skill)
        storage.save_player_data(reopened, skill)
        third, _skill = storage.load_player_data()
        self.assertEqual(third[INSTANCES_KEY], loaded[INSTANCES_KEY])
        self.assertEqual(third[NEXT_ID_KEY], loaded[NEXT_ID_KEY])

    def test_two_copies_keep_distinct_requests_through_inspection_and_reopen(self):
        raw = self._raw(**{
            INSTANCES_KEY: {"ancient-effigy-1": record(18778, "bank", SEED_1), "ancient-effigy-2": record(18778, "bank", SEED_2)},
            NEXT_ID_KEY: 3,
        })
        collection = self._collection(raw)
        storage = _load_storage_module(collection)
        loaded, skill = storage.load_player_data()
        for instance_id in ("ancient-effigy-1", "ancient-effigy-2"):
            loaded, ok, _info = actions.inspect_effigy_pure(loaded, instance_id)
            self.assertTrue(ok)
        pairs = [loaded[INSTANCES_KEY][key]["pair_index"] for key in ("ancient-effigy-1", "ancient-effigy-2")]
        self.assertEqual(pairs, [2, 7])
        loaded["cooking_level"] = 91
        token = actions.stage_token_pure("ancient-effigy-1", loaded[INSTANCES_KEY]["ancient-effigy-1"])
        refused, ok, _info = actions.investigate_effigy_pure(loaded, token, "firemaking")
        self.assertFalse(ok)
        storage.save_player_data(refused, skill)
        reopened, _skill = storage.load_player_data()
        self.assertEqual([reopened[INSTANCES_KEY][key]["pair_index"] for key in ("ancient-effigy-1", "ancient-effigy-2")], [2, 7])
        advanced, ok, _info = actions.investigate_effigy_pure(reopened, token, "cooking")
        self.assertTrue(ok)
        storage.save_player_data(advanced, skill)
        final, _skill = storage.load_player_data()
        self.assertEqual(final[INSTANCES_KEY]["ancient-effigy-2"], record(18778, "bank", SEED_2, 0, 7))
        self.assertEqual(final[INSTANCES_KEY]["ancient-effigy-1"]["item_id"], 18779)
        self.assertEqual(final["inventory"]["Starved ancient effigy"], 1)
        self.assertEqual(final["inventory"]["Nourished ancient effigy"], 1)

    def test_text_row_recovery_still_repairs_while_custody_is_saved(self):
        raw = self._raw(config_version=125)
        collection = self._collection(raw, legacy=True)
        storage = _load_storage_module(collection)
        loaded, skill = storage.load_player_data()
        self.assertFalse(collection.legacy_row, "the TEXT row was recreated")
        self.assertNotIn("ankiscape_player_data_recovery", collection.values)
        self.assertEqual(collection.values[PLAYER_KEY][INSTANCES_KEY], loaded[INSTANCES_KEY])
        loaded["inventory"]["Dragonkin lamp"] = 1
        storage.save_player_data(loaded, skill)
        stored = collection.values[PLAYER_KEY]
        self.assertNotIn("Dragonkin lamp", stored["inventory"])
        self.assertEqual(sum(value["item_id"] == 18782 for value in stored[INSTANCES_KEY].values()), 1)

    def test_quest_repairs_and_custody_adoption_are_both_kept(self):
        raw = self._raw(config_version=125)
        raw["quests"]["cold_war"] = {"started": True, "completed": False, "progress": 3}
        raw.pop("cold_war_greeting", None)
        raw.pop("cold_war_suit_backfilled", None)
        raw["inventory"].pop("Clockwork suit", None)
        collection = self._collection(raw)
        storage = _load_storage_module(collection)
        with patch(SAMPLER, return_value=list(GREETING)):
            loaded, _skill = storage.load_player_data()
        stored = collection.values[PLAYER_KEY]
        self.assertEqual(stored["cold_war_greeting"], list(GREETING))
        self.assertEqual(stored["inventory"]["Clockwork suit"], 1)
        self.assertEqual(stored[INSTANCES_KEY], loaded[INSTANCES_KEY])
        self.assertEqual(len(stored[INSTANCES_KEY]), 2)
        self.assertEqual(stored["unrelated_marker"], raw["unrelated_marker"])

    def test_legacy_lamp_unit_is_removed_from_the_stored_bank(self):
        raw = self._raw()
        raw["inventory"]["Dragonkin lamp"] = 1
        collection = self._collection(raw)
        storage = _load_storage_module(collection)
        loaded, _skill = storage.load_player_data()
        stored = collection.values[PLAYER_KEY]
        self.assertNotIn("Dragonkin lamp", stored["inventory"])
        self.assertNotIn("Dragonkin lamp", loaded["inventory"])
        lamps = [key for key, value in stored[INSTANCES_KEY].items() if value["item_id"] == 18782]
        self.assertEqual(len(lamps), 1)
        self.assertEqual(stored[INSTANCES_KEY][lamps[0]]["location"], "held")
        self.assertEqual(storage.load_player_data()[0][INSTANCES_KEY], loaded[INSTANCES_KEY])

    def test_consumed_and_destroyed_lamps_stay_gone_after_save_and_reopen(self):
        raw = self._raw(**{
            INSTANCES_KEY: {"ancient-effigy-1": record(18782, "held"), "ancient-effigy-2": record(18782, "held", SEED_2)},
            NEXT_ID_KEY: 3,
        })
        raw["inventory"]["Starved ancient effigy"] = 0
        collection = self._collection(raw)
        storage = _load_storage_module(collection)
        loaded, skill = storage.load_player_data()
        redeemed, ok, _ = actions.redeem_lamp_pure(loaded, actions.lamp_token_pure("ancient-effigy-1"), "attack")
        self.assertTrue(ok)
        destroyed, ok, _ = actions.destroy_lamp_pure(redeemed, actions.lamp_token_pure("ancient-effigy-2"))
        self.assertTrue(ok)
        storage.save_player_data(destroyed, skill)
        reopened, _skill = storage.load_player_data()
        self.assertEqual(reopened[INSTANCES_KEY], {})
        self.assertEqual(reopened[NEXT_ID_KEY], 3)
        self.assertNotIn("Dragonkin lamp", reopened["inventory"])
        self.assertFalse(any("Dragonkin lamp" in view for view in (reopened.get("carried_inventory") or {}).values()))


if __name__ == "__main__":
    unittest.main()
