"""An earned Brimhaven reward must retain custody through ordinary trade."""
import copy
import json
import sys
import types
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.logic.agility_logic import apply_agility_review_pure
from tests import test_integration_smoke as runtime_fixture


class PiratesHookTradeabilityTest(unittest.TestCase):
    def setUp(self):
        modules = patch.dict(sys.modules)
        modules.start()
        self.addCleanup(modules.stop)
        runtime_fixture._install_runtime_fakes()

    def test_earned_hook_exchange_escrow_settlement_undo_and_reload(self):
        player = {"agility_level": 99, "current_agility": "brimhaven_arena",
                  "inventory": {"Coins": 200}, "equipment": {}}
        for review in range(801):
            player, result = apply_agility_review_pure(player, (0.0, 0.0, 1.0, 1.0))
            self.assertTrue(result["allowed"], result)
            self.assertEqual(result["tickets"], 0 if review == 0 else 1)
        self.assertEqual(player["inventory"], {"Coins": 0, "Agility arena ticket": 800})

        collection = runtime_fixture._DummyCol()
        sys.modules["aqt"].mw = runtime_fixture._DummyMW(collection)
        addon = runtime_fixture._load_addon_as_package("ankiscape_pirates_hook_tradeability")
        addon._state.player_data, addon._state.current_skill = addon.storage_load_player_data()
        addon._state.player_data.update(player)
        addon._state.current_skill = "Activities"
        addon.save_player_data()
        addon._state.player_data, addon._state.current_skill = addon.storage_load_player_data()
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._update_review_context_surface = lambda: None
        addon.check_achievements = lambda _data: None
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon._on_main_menu()
        command = captured["on_agility_command"]
        action = captured["on_ge_action"]

        before_reward = copy.deepcopy(addon._state.player_data)
        exchanged = command("redeem_brimhaven_item", {"tickets": 800})
        self.assertTrue(exchanged["ok"], exchanged)
        self.assertEqual(addon._state.player_data["inventory"]["Agility arena ticket"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Pirate's hook"], 1)
        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(addon._state.player_data, before_reward)
        self.assertTrue(command("redeem_brimhaven_item", {"tickets": 800})["ok"])

        payload = {"side": "sell", "item_name": "Pirate's hook", "quantity": 1,
                   "unit_price": 1_726_388, "confirmed": True}
        preview = action("preview_offer", payload)
        self.assertTrue(preview["ok"], {key: value for key, value in preview.items() if key != "projection"})
        spec = addon.GE_ITEM_CATALOG["Pirate's hook"]
        self.assertEqual((spec["source_item_id"], spec["guide_price"], spec["buy_limit"]),
                         (2997, 1_726_388, 10))
        self.assertEqual(spec["guide_price_provenance"]["oldid"], 6112017)
        self.assertEqual(spec["cache_value"], 89)

        before_sale = copy.deepcopy(addon._state.player_data)
        placed = action("place_offer", payload)
        self.assertTrue(placed["ok"], placed)
        self.assertEqual(addon._state.player_data["inventory"]["Pirate's hook"], 0)
        self.assertEqual(addon._state.player_data["ge_player_orders"][0]["escrow_items"], 1)
        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(addon._state.player_data, before_sale)
        self.assertTrue(action("place_offer", payload)["ok"])

        addon.save_player_data()
        collection._store = json.loads(json.dumps(collection._store))
        addon._state.player_data, addon._state.current_skill = addon.storage_load_player_data()
        self.assertEqual(addon._state.player_data["ge_player_orders"][0]["escrow_items"], 1)
        ge_logic = sys.modules[f"{addon.__name__}.logic.grand_exchange_logic"]
        shop_logic = sys.modules[f"{addon.__name__}.logic.shop_logic"]
        clocked = shop_logic.advance_shop_market_clock_pure(addon._state.player_data)
        addon._state.player_data, filled = ge_logic.advance_ge_market_tick_pure(
            clocked, item_catalog=addon.GE_ITEM_CATALOG, random_draw=lambda: 0.0)
        self.assertEqual(len(filled["fills"]), 1, filled)
        order = addon._state.player_data["ge_player_orders"][0]
        self.assertEqual((order["status"], order["escrow_items"], order["collectible_coins"]),
                         ("complete", 0, 1_726_388))
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 0)
        collected = action("collect_offer", {"order_id": order["id"]})
        self.assertTrue(collected["ok"], collected)
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 1_726_388)
        self.assertEqual(addon._state.player_data["ge_player_orders"], [])
        addon.save_player_data()
        saved = json.loads(json.dumps(collection.get_config("ankiscape_player_data")))
        addon._state.player_data, addon._state.current_skill = addon.storage_load_player_data()
        for key in ("inventory", "equipment", "ge_player_orders", "agility_activity_state"):
            self.assertEqual(addon._state.player_data[key], saved[key])
