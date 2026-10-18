"""Ordinary Cabbage keeps its identity and uses one carried slot per copy."""
import copy
import json
import sys
import types
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import EXTRA_ITEM_DATA, ITEM_DEFINITIONS
from ankiscape.core.item_registry import item_definitions_by_storage_key
from ankiscape.data.cooking_data import cooking_extra_items_as_dict
from ankiscape.data.grand_exchange_data import GE_ITEM_CATALOG
from ankiscape.logic.inventory_pure import apply_carried_layout_pure, carried_slots_used
from tests import test_integration_smoke as runtime_fixture
from tests.test_farming import _plant_ready


class CabbageStackabilityTest(unittest.TestCase):
    def test_ordinary_metadata_retains_identity_and_market_values(self):
        for metadata in (cooking_extra_items_as_dict()["Cabbage"], EXTRA_ITEM_DATA["Cabbage"]):
            self.assertEqual(metadata["item_id"], 1965)
            self.assertTrue(metadata["tradeable"])
            self.assertFalse(metadata.get("stackable", True))
        item = item_definitions_by_storage_key(ITEM_DEFINITIONS)["Cabbage"]
        self.assertEqual((item.id, item.source_item_id, item.storage_key),
                         ("food_cabbage", 1965, "Cabbage"))
        self.assertTrue(item.tradeable)
        self.assertFalse(item.stackable)
        market = GE_ITEM_CATALOG["Cabbage"]
        self.assertEqual((market["source_item_id"], market["guide_price"], market["buy_limit"],
                          market["cache_value"], market["low_alchemy_value"], market["high_alchemy_value"]),
                         (1965, 56, 1000, 1, 0, 0))
        stackable = frozenset(row.storage_key for row in ITEM_DEFINITIONS if row.stackable)
        self.assertEqual(carried_slots_used({"Cabbage": 29}, stackable), 29)
        owned = {"Cabbage": 29}
        self.assertEqual(apply_carried_layout_pure(owned, owned, 28, stackable), {"Cabbage": 28})
        self.assertEqual(owned, {"Cabbage": 29})

    def test_farmed_cabbage_becomes_garden_pies_with_review_undo_and_reload(self):
        modules = patch.dict(sys.modules)
        modules.start()
        self.addCleanup(modules.stop)
        runtime_fixture._install_runtime_fakes()
        collection = runtime_fixture._DummyCol()
        sys.modules["aqt"].mw = runtime_fixture._DummyMW(collection)
        addon = runtime_fixture._load_addon_as_package("ankiscape_cabbage_review")
        addon.level_up_check = lambda *_args: None
        addon.check_achievements = lambda _data: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda _exp: None
        addon._show_activity_gain = lambda _message: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        player, _skill = addon.storage_load_player_data()
        player.update(farming_level=7, farming_exp=650.0,
                      inventory={"Pie shell": 3, "Tomato": 3, "Onion": 3, "Coins": 17})
        farming = sys.modules[f"{addon.__name__}.logic.farming_logic"]
        planted = _plant_ready(player, crop_id="cabbage")
        mature, _info = farming.advance_farm_clock_pure(planted, 8)
        queued, step_id, message = farming.add_farm_queue_step_pure(
            mature, "harvest", "falador_allotment_north")
        self.assertIsNotNone(step_id, message)
        addon._state.player_data, addon._state.current_skill = queued, "Utilities"
        addon.save_player_data()
        collection._store = json.loads(json.dumps(collection._store))
        addon._state.player_data, addon._state.current_skill = addon.storage_load_player_data()
        self.enterContext(patch.object(addon.random, "random", return_value=0.99))

        for target, expected in (("bankstanding", (3, 0)), ("assemble_garden_pie", (0, 3))):
            addon._state.player_data["current_utility"] = target
            before = copy.deepcopy(addon._state.player_data)
            before_rng = addon.random.getstate()
            for undo in (True, False):
                addon.on_card_did_show(None)
                addon.on_show_answer(None)
                addon.on_answer_card(runtime_fixture._FakeReviewer(), 3, lambda _self, _ease: "answered")
                answered = addon._state.player_data
                self.assertEqual((answered["inventory"].get("Cabbage", 0),
                                  answered["inventory"].get("Raw garden pie", 0)), expected)
                self.assertEqual(answered["farming_exp"], 650.0 + 10.0 + 3 * 11.5)
                self.assertEqual(answered["inventory"]["Coins"], 17)
                if undo:
                    addon._on_state_did_undo(types.SimpleNamespace(
                        operation="Answer Card",
                        changes=types.SimpleNamespace(study_queues=True, card=True)))
                    self.assertEqual(addon._state.player_data, before)
                    self.assertEqual(addon._state.current_skill, "Utilities")
                    self.assertEqual(addon.random.getstate(), before_rng)
            addon.save_player_data()
            saved = copy.deepcopy(addon._state.player_data)
            collection._store = json.loads(json.dumps(collection._store))
            addon._state.player_data, addon._state.current_skill = addon.storage_load_player_data()
            self.assertEqual(addon._state.player_data, saved)
        self.assertEqual(tuple(addon._state.player_data["inventory"][name]
                               for name in ("Pie shell", "Tomato", "Onion")), (0, 0, 0))
