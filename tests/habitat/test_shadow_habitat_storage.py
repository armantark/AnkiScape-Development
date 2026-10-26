"""Habitat defaults, unconditional sanitation and real collection persistence."""

import copy
import json
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ORE_DATA, ITEM_DEFINITIONS
from ankiscape.core.storage_pure import CURRENT_CONFIG_VERSION, default_player_data, migrate_loaded_data
from ankiscape.logic.farming.habitat_state import (
    default_herblore_habitat_state_pure, sanitize_herblore_habitat_state_pure,
    shadow_attraction_reasons_pure,
)
from tests.habitat.fixtures import established_state, CollectionFacade
from tests.test_storage_runtime import _load_storage_module


class ShadowHabitatStorageTest(unittest.TestCase):
    def test_defaults_have_only_one_new_flat_key(self):
        self.assertEqual(default_herblore_habitat_state_pure(), {"habitat_feature": None})
        self.assertIsNone(default_player_data(ORE_DATA, ITEM_DEFINITIONS)["habitat_feature"])

    def test_feature_sanitized_on_current_version_and_legacy_loads(self):
        for version in (1, CURRENT_CONFIG_VERSION):
            for value in (None, "", "   ", 57, False, [], {}):
                with self.subTest(version=version, value=value):
                    data = {"config_version": version, "habitat_feature": value, "unknown_owner_field": {"kept": True}}
                    loaded = migrate_loaded_data(data, ORE_DATA, ITEM_DEFINITIONS)
                    self.assertIsNone(loaded["habitat_feature"])
                    self.assertEqual(loaded["unknown_owner_field"], {"kept": True})
                    self.assertEqual(loaded["config_version"], CURRENT_CONFIG_VERSION)

    def test_missing_feature_never_backfills_house_or_charges(self):
        data = established_state()
        data.pop("habitat_feature")
        data["config_version"] = CURRENT_CONFIG_VERSION
        loaded = migrate_loaded_data(data, ORE_DATA, ITEM_DEFINITIONS)
        self.assertIsNone(loaded["habitat_feature"])
        self.assertEqual({k: v for k, v in loaded["inventory"].items() if v}, {k: v for k, v in data["inventory"].items() if v})
        self.assertEqual(loaded["farm_patches"]["habitat_vine_flower"], data["farm_patches"]["habitat_vine_flower"])

    def test_unknown_nonempty_identity_preserved_without_attraction(self):
        for feature in ("boneyard", "future_feature", " unknown "):
            self.assertEqual(sanitize_herblore_habitat_state_pure({"habitat_feature": feature}), {"habitat_feature": feature})
            data = established_state()
            data.update(config_version=CURRENT_CONFIG_VERSION, habitat_feature=feature)
            loaded = migrate_loaded_data(data, ORE_DATA, ITEM_DEFINITIONS)
            self.assertEqual(loaded["habitat_feature"], feature)
            self.assertEqual(shadow_attraction_reasons_pure(loaded), ("Abandoned house",))

    def test_json_migration_roundtrip_preserves_real_plant_and_feature(self):
        data = established_state()
        data.update(config_version=CURRENT_CONFIG_VERSION, current_hunter="track_diseased_jadinko")
        before = copy.deepcopy(data)
        loaded = migrate_loaded_data(json.loads(json.dumps(data)), ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(loaded["habitat_feature"], "abandoned_house")
        self.assertEqual(loaded["farm_patches"]["habitat_vine_flower"], before["farm_patches"]["habitat_vine_flower"])
        self.assertEqual({k: v for k, v in loaded["inventory"].items() if v}, {k: v for k, v in before["inventory"].items() if v})
        self.assertEqual(shadow_attraction_reasons_pure(loaded), ())
        self.assertEqual(data, before)

    def test_actual_save_load_collection_roundtrip_has_no_reconstruction_payment_or_progress(self):
        collection = CollectionFacade()
        storage = _load_storage_module(collection)
        data = established_state()
        data["config_version"] = CURRENT_CONFIG_VERSION
        data["inventory"] = {"Noose wand": 1}
        storage.save_player_data(data, "Hunter")
        loaded, skill = storage.load_player_data()
        self.assertEqual(skill, "Hunter")
        self.assertEqual({k: v for k, v in loaded["inventory"].items() if v}, {k: v for k, v in data["inventory"].items() if v})
        self.assertEqual(loaded["farm_clock_minutes"], data["farm_clock_minutes"])
        self.assertEqual(loaded["farm_patches"]["habitat_vine_flower"], data["farm_patches"]["habitat_vine_flower"])
        self.assertEqual(shadow_attraction_reasons_pure(loaded), ())
        self.assertEqual(loaded["construction_exp"], 0)
