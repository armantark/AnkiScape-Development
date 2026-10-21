"""Greeting backfills must leave the rest of the raw save untouched."""

import copy
import sys
import unittest
from unittest.mock import patch

from tests.test_cold_war_greeting.test_greeting import GREETING, SAMPLER
from tests.test_storage_runtime import _LegacyTextCollection, _load_storage_module


class ColdWarBackfillIsolationTest(unittest.TestCase):
    def test_current_version_backfill_preserves_raw_nested_save(self):
        original_modules = dict(sys.modules)
        self.addCleanup(sys.modules.update, original_modules)
        self.addCleanup(sys.modules.clear)
        for completed in (False, True):
            for record_key in ("ankiscape_player_data", "ankiscape_player_data_recovery"):
                with self.subTest(completed=completed, record=record_key):
                    raw = {
                        "config_version": 124,
                        "quests": {"cold_war": {
                            "started": not completed, "completed": completed, "progress": 3,
                        }},
                        "inventory": {"Coins": 37},
                        "unrelated_raw_field": {"nested": [1, "kept"]},
                        "quest_action_proofs": ["untouched raw proof"],
                    }
                    before = copy.deepcopy(raw)
                    collection = _LegacyTextCollection()
                    collection.legacy_row = False
                    collection.values = {record_key: raw, "ankiscape_current_skill": "Hunter"}
                    storage = _load_storage_module(collection)
                    with patch(SAMPLER, return_value=list(GREETING)) as sample, patch.object(
                        collection, "set_config", wraps=collection.set_config,
                    ) as save:
                        loaded, skill = storage.load_player_data()
                        expected = {**before, "cold_war_greeting": GREETING}
                        self.assertEqual(raw, before)
                        save.assert_called_once_with("ankiscape_player_data", expected)
                        self.assertEqual(collection.values, {
                            "ankiscape_player_data": expected, "ankiscape_current_skill": "Hunter",
                        })
                        self.assertEqual(skill, "Hunter")
                        self.assertEqual(loaded["cold_war_greeting"], GREETING)
                        self.assertGreater(len(loaded["inventory"]), 1)
                        self.assertIsNot(loaded["inventory"], raw["inventory"])
                        persisted = collection.values["ankiscape_player_data"]
                        self.assertIsNot(persisted["cold_war_greeting"], loaded["cold_war_greeting"])
                        reopened, reopened_skill = storage.load_player_data()
                        self.assertEqual(reopened, loaded)
                        self.assertEqual(reopened_skill, skill)
                        self.assertEqual(persisted, expected)
                        sample.assert_called_once()
                        save.assert_called_once()


if __name__ == "__main__":
    unittest.main()
