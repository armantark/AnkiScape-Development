"""Exact Mystic hat variants retain custody through the ordinary market."""

import copy
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ALCH_VALUES, ITEM_DEFINITIONS
from ankiscape.data.grand_exchange_data import GE_ITEM_CATALOG
from ankiscape.data.item_values import ITEM_VALUES, STACKABLE_ITEM_NAMES
from ankiscape.data.shop_data import SHOP_DATA
from ankiscape.logic.shop_fixtures import build_shop_fixture_player_data
from ankiscape.logic.shop_logic import apply_shop_sell_pure
from ankiscape.runtime.runtime_actions_magic import _magic_alch_values
from tests import test_integration_smoke as runtime_fixture
from tests.test_combat_quest_gate import _answer_review
from tests.test_storage_runtime import Collection


HATS = {
    "Mystic hat (dark)": (4099, 33058, 6571021),
    "Mystic hat (light)": (4109, 8786, 6571022),
}


class MysticHatMarketDataTest(unittest.TestCase):
    def test_exact_markets_preserve_equipment_and_separate_shop_consumers(self):
        definitions = {item.storage_key: item for item in ITEM_DEFINITIONS}
        shop = next(row for row in SHOP_DATA.values() if row["visibility"] == "visible"
                    and row["general_store"] and not row.get("required_quests"))
        for name, (item_id, price, oldid) in HATS.items():
            with self.subTest(name=name):
                item, spec = definitions[name], GE_ITEM_CATALOG[name]
                self.assertEqual((item.source_item_id, item.tradeable, item.stackable),
                                 (item_id, True, False))
                self.assertEqual((spec["source_item_id"], spec["guide_price"], spec["buy_limit"]),
                                 (item_id, price, 100))
                self.assertEqual(spec["guide_price_provenance"]["oldid"], oldid)
                self.assertEqual(spec["buy_limit_source"]["oldid"], 6457777)
                self.assertEqual((ITEM_VALUES[name], spec["low_alchemy_value"], spec["high_alchemy_value"]),
                                 (15000, 6000, 9000))
                self.assertNotIn(name, STACKABLE_ITEM_NAMES)
                self.assertNotIn(name, ALCH_VALUES)
                self.assertNotIn(name, _magic_alch_values())
                player = build_shop_fixture_player_data()
                player["inventory"][name] = 1
                before = copy.deepcopy(player)
                sold, result = apply_shop_sell_pure(player, shop["id"], name, 1)
                self.assertEqual((result["allowed"], result["reason"]), (False, "sell_price_unresolved"))
                self.assertEqual(sold["inventory"], before["inventory"])
                self.assertEqual(player, before)
        blue = GE_ITEM_CATALOG["Mystic hat"]
        self.assertEqual((blue["source_item_id"], blue["guide_price"], blue["buy_limit"]), (4089, 16225, 100))
        self.assertEqual(ALCH_VALUES["Mystic hat"], 15000)


class MysticHatMarketRuntimeTest(unittest.TestCase):
    def setUp(self):
        modules = patch.dict(sys.modules)
        modules.start()
        self.addCleanup(modules.stop)
        runtime_fixture._install_runtime_fakes()

    def _open(self, collection):
        self.collection = collection
        collection.set_config("ankiscape_review_action_multiplier", 10)
        sys.modules["aqt"].mw = runtime_fixture._DummyMW(collection)
        self.addon = runtime_fixture._load_addon_as_package("ankiscape_mystic_hat_markets")
        addon = self.addon
        addon.load_player_data()
        addon._state.current_skill = "Bankstanding"
        addon._state.player_data["inventory"].update({"Coins": 200000, "Logs": 7})
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._update_review_context_surface = lambda: None
        addon.check_achievements = lambda _data: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon._on_main_menu()
        self.action = captured["on_ge_action"]
        addon.save_player_data()
        addon.load_player_data()
        self._reload()

    def _reload(self):
        addon = self.addon
        addon.save_player_data()
        expected = copy.deepcopy(addon._state.player_data)
        expected.setdefault("skilling_bank_run_requested", "")
        skill = addon._state.current_skill
        if isinstance(self.collection, runtime_fixture._DummyCol):
            self.collection._store = json.loads(json.dumps(self.collection._store))
        else:
            self.collection.close()
            self.collection.reopen()
        addon.load_player_data()
        self.assertEqual((addon._state.player_data, addon._state.current_skill), (expected, skill))

    def _action_with_undo(self, action, payload):
        addon = self.addon
        before = copy.deepcopy(addon._state.player_data), addon._state.current_skill
        result = self.action(action, payload)
        self.assertTrue(result["ok"], result)
        after = copy.deepcopy(addon._state.player_data), addon._state.current_skill
        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual((addon._state.player_data, addon._state.current_skill), before)
        self.assertTrue(self.action(action, payload)["ok"])
        self.assertEqual((addon._state.player_data, addon._state.current_skill), after)
        self._reload()

    def _fill_on_reviews(self):
        addon = self.addon
        for _ in range(200):
            before = copy.deepcopy(addon._state.player_data), addon._state.current_skill
            _answer_review(addon)
            after = copy.deepcopy(addon._state.player_data), addon._state.current_skill
            addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
            self.assertEqual((addon._state.player_data, addon._state.current_skill), before)
            _answer_review(addon)
            self.assertEqual((addon._state.player_data, addon._state.current_skill), after)
            if addon._state.player_data["ge_player_orders"][0]["status"] == "complete":
                self._reload()
                return
        self.fail("the seeded ordinary review route did not fill the offer")

    def assert_lifecycle(self):
        addon = self.addon
        for name, (_item_id, guide, _oldid) in HATS.items():
            for side, price in (("buy", guide * 2), ("sell", guide // 2)):
                with self.subTest(name=name, side=side):
                    payload = {"item_name": name, "side": side, "quantity": 1,
                               "unit_price": price, "confirmed": True}
                    inventory = copy.deepcopy(addon._state.player_data["inventory"])
                    self._action_with_undo("place_offer", payload)
                    order = addon._state.player_data["ge_player_orders"][0]
                    self.assertEqual(order["escrow_coins"] if side == "buy" else order["escrow_items"],
                                     price if side == "buy" else 1)
                    self._action_with_undo("cancel_offer", {"order_id": order["id"]})
                    self._action_with_undo("collect_offer", {"order_id": order["id"]})
                    self.assertEqual(addon._state.player_data["inventory"], inventory)
                    self._action_with_undo("place_offer", payload)
                    self._fill_on_reviews()
                    order = addon._state.player_data["ge_player_orders"][0]
                    self.assertEqual((order["escrow_coins"], order["escrow_items"]), (0, 0))
                    self.assertEqual(order["collectible_items"], 1 if side == "buy" else 0)
                    coins = addon._state.player_data["inventory"]["Coins"] + order["collectible_coins"]
                    self._action_with_undo("collect_offer", {"order_id": order["id"]})
                    self.assertEqual(addon._state.player_data["inventory"].get(name, 0), 1 if side == "buy" else 0)
                    self.assertEqual(addon._state.player_data["inventory"]["Coins"], coins)
                    self.assertEqual(addon._state.player_data["inventory"]["Logs"], 7)
                    self.assertEqual(addon._state.player_data["ge_player_orders"], [])

    def test_buy_sell_fill_cancel_collect_complete_undo_and_reload(self):
        self._open(runtime_fixture._DummyCol())
        self.assert_lifecycle()

    def test_review_fills_stop_at_each_hats_period_buy_limit(self):
        self._open(runtime_fixture._DummyCol())
        addon = self.addon
        for name, (_item_id, guide, _oldid) in HATS.items():
            with self.subTest(name=name):
                tick = addon._state.player_data["shop_market_clock"]["market_tick"]
                addon._state.player_data["ge_buy_limit_usage"][name] = {"window_start_tick": tick, "bought": 99}
                self._action_with_undo("place_offer", {"item_name": name, "side": "buy", "quantity": 3,
                                                      "unit_price": guide * 2, "confirmed": True})
                for _ in range(200):
                    _answer_review(addon)
                    if addon._state.player_data["ge_buy_limit_usage"][name]["bought"] == 100:
                        break
                self.assertEqual(addon._state.player_data["ge_buy_limit_usage"][name]["bought"], 100)
                for _ in range(3):
                    _answer_review(addon)
                    order = addon._state.player_data["ge_player_orders"][0]
                    self.assertEqual((order["remaining_quantity"], order["collectible_items"]), (2, 1))
                self._action_with_undo("cancel_offer", {"order_id": order["id"]})
                self._action_with_undo("collect_offer", {"order_id": order["id"]})
                self.assertEqual(addon._state.player_data["inventory"][name], 1)
                self.assertEqual(addon._state.player_data["ge_player_orders"], [])

    @unittest.skipIf(Collection is None, "Anki runtime is not installed")
    def test_lifecycle_survives_real_collection_close_and_reopen(self):
        with tempfile.TemporaryDirectory() as directory:
            collection = Collection(str(Path(directory) / "collection.anki2"))
            try:
                self._open(collection)
                self.assert_lifecycle()
            finally:
                collection.close()
