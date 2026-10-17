"""Prepared packs from existing saves obey capacity without changing ownership."""
import copy
import json
import sys
import unittest
from unittest.mock import patch

from tests import test_integration_smoke as runtime_fixture


class PyramidPackCapacityTest(unittest.TestCase):
    def setUp(self):
        modules = patch.dict(sys.modules)
        modules.start()
        self.addCleanup(modules.stop)
        runtime_fixture._install_runtime_fakes()
        self.collection = runtime_fixture._DummyCol()
        sys.modules["aqt"].mw = runtime_fixture._DummyMW(self.collection)
        self.addon = runtime_fixture._load_addon_as_package("ankiscape_pyramid_pack_capacity")

    def test_saved_active_pack_loads_at_capacity_with_every_item_still_owned(self):
        addon = self.addon
        plunder = sys.modules[f"{addon.__name__}.logic.pyramid_plunder_logic"]
        target = plunder.PYRAMID_PLUNDER_ACTIVITY_ID
        player, skill = addon.storage_load_player_data()
        player.update(thieving_level=91, inventory={"Shark": 29},
                      carried_advanced_targets={target: True},
                      carried_layout={target: {"Shark": 29}})
        player["quests"]["icthlarins_little_helper"] = {"started": True, "completed": False}
        player, entered, info = plunder.enter_pyramid_plunder_pure(player)
        self.assertTrue(entered, info)
        self.assertEqual(info["pack"], {"Shark": 28})
        player["carried_inventory"] = {target: {"Shark": 29}, "other_target": {"Shark": 1}}
        addon._state.player_data, addon._state.current_skill = player, skill
        addon.save_player_data()
        self.collection._store = json.loads(json.dumps(self.collection._store))
        self.assertEqual(self.collection._store["ankiscape_player_data"]["carried_inventory"][target],
                         {"Shark": 29})
        loaded, _skill = addon.storage_load_player_data()
        self.assertEqual(loaded["carried_inventory"], {target: {"Shark": 28}, "other_target": {"Shark": 1}})
        self.assertEqual(loaded["carried_layout"][target], {"Shark": 29})
        self.assertEqual(loaded["inventory"]["Shark"], 29)
        before = copy.deepcopy(loaded)
        self.assertEqual(plunder.pyramid_plunder_view_pure(loaded)["pack_slots"], 28)
        self.assertEqual(loaded, before)
        addon._state.player_data = loaded
        addon.save_player_data()
        self.collection._store = json.loads(json.dumps(self.collection._store))
        reloaded, _skill = addon.storage_load_player_data()
        self.assertEqual(reloaded, loaded)
