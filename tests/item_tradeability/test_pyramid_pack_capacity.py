"""Prepared packs from existing saves obey capacity without changing ownership."""
import copy
import json
import sys
import types
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
        self.addon.level_up_check = lambda *_args: None
        self.addon.check_achievements = lambda _data: None
        self.addon.update_review_hud = lambda *_args: None
        self.addon._refresh_skill_availability = lambda: None
        self.addon._show_exp = lambda _exp: None
        self.addon._show_activity_gain = lambda _message: None
        self.addon.show_error_message = lambda _title, message: self.fail(message)

    def test_saved_active_pack_loads_at_capacity_with_every_item_still_owned(self):
        addon = self.addon
        plunder = sys.modules[f"{addon.__name__}.logic.pyramid_plunder_logic"]
        target = plunder.PYRAMID_PLUNDER_ACTIVITY_ID
        for item_name in ("Shark", "Cabbage"):
            with self.subTest(item_name=item_name):
                self.collection._store.clear()
                player, skill = addon.storage_load_player_data()
                player.update(thieving_level=91, inventory={item_name: 29},
                              carried_advanced_targets={target: True},
                              carried_layout={target: {item_name: 29}})
                player["quests"]["icthlarins_little_helper"] = {"started": True, "completed": False}
                player, entered, info = plunder.enter_pyramid_plunder_pure(player)
                self.assertTrue(entered, info)
                self.assertEqual(info["pack"], {item_name: 28})
                player["carried_inventory"] = {target: {item_name: 29}, "other_target": {item_name: 1}}
                addon._state.player_data, addon._state.current_skill = player, skill
                addon.save_player_data()
                self.collection._store = json.loads(json.dumps(self.collection._store))
                self.assertEqual(self.collection._store["ankiscape_player_data"]["carried_inventory"][target],
                                 {item_name: 29})
                loaded, _skill = addon.storage_load_player_data()
                self.assertEqual(loaded["carried_inventory"], {target: {item_name: 28}, "other_target": {item_name: 1}})
                self.assertEqual(loaded["carried_layout"][target], {item_name: 29})
                self.assertEqual(loaded["inventory"][item_name], 29)
                before = copy.deepcopy(loaded)
                self.assertEqual(plunder.pyramid_plunder_view_pure(loaded)["pack_slots"], 28)
                self.assertEqual(loaded, before)
                addon._state.player_data = loaded
                addon.save_player_data()
                self.collection._store = json.loads(json.dumps(self.collection._store))
                reloaded, _skill = addon.storage_load_player_data()
                self.assertEqual(reloaded, loaded)
                addon._state.player_data, addon._state.current_skill = reloaded, "Utilities"
                before = copy.deepcopy(reloaded)
                before_rng = addon.random.getstate()
                addon.on_card_did_show(None)
                addon.on_show_answer(None)
                addon.on_answer_card(runtime_fixture._FakeReviewer(), 3, lambda _self, _ease: "answered")
                self.assertNotEqual(addon._state.player_data, before)
                addon._on_state_did_undo(types.SimpleNamespace(
                    operation="Answer Card",
                    changes=types.SimpleNamespace(study_queues=True, card=True)))
                self.assertEqual(addon._state.player_data, before)
                self.assertEqual(addon._state.current_skill, "Utilities")
                self.assertEqual(addon.random.getstate(), before_rng)
                addon.save_player_data()
                self.collection._store = json.loads(json.dumps(self.collection._store))
                restored, _skill = addon.storage_load_player_data()
                self.assertEqual(restored, before)
