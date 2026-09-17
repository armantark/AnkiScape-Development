"""Cut-gem trading behavior across the market, review dispatcher, and alchemy UI."""

import copy
import sys
import unittest

from tests import test_grand_exchange_logic as ge_support
from tests import test_integration_smoke as smoke_support
from tests import test_main_menu_widget as widget_support
from ankiscape.logic.grand_exchange_logic import (
    advance_ge_market_tick_pure,
    collect_ge_offer_pure,
    place_ge_offer_pure,
)


class CutGemTradeabilityTest(unittest.TestCase):
    def test_cut_gem_orders_stop_filling_at_the_period_buy_limit(self):
        from ankiscape.data.grand_exchange_data import GE_ITEM_CATALOG

        for item_name in ("Jade", "Red topaz"):
            with self.subTest(item_name=item_name):
                spec = GE_ITEM_CATALOG[item_name]
                player = ge_support._player()
                player["ge_market_state"]["last_processed_tick"] = 7
                player["ge_buy_limit_usage"] = {
                    item_name: {"window_start_tick": 7, "bought": 999}
                }
                player, placed = place_ge_offer_pure(
                    player,
                    side="buy",
                    item_name=item_name,
                    quantity=10,
                    unit_price=2 * spec["guide_price"],
                    item_spec=spec,
                )
                self.assertTrue(placed["ok"])

                player["shop_market_clock"] = {"answered_cards": 8, "market_tick": 8}
                player, first = advance_ge_market_tick_pure(
                    player,
                    item_catalog={item_name: spec},
                    random_draw=lambda: 0.0,
                )
                self.assertEqual(first["fills"][0]["quantity"], 1)
                self.assertEqual(player["ge_buy_limit_usage"][item_name]["bought"], 1000)

                player["shop_market_clock"] = {"answered_cards": 9, "market_tick": 9}
                player, blocked = advance_ge_market_tick_pure(
                    player,
                    item_catalog={item_name: spec},
                    random_draw=lambda: 0.0,
                )
                self.assertEqual(blocked["fills"], [])
                self.assertEqual(player["ge_player_orders"][0]["remaining_quantity"], 9)
                player, collected = collect_ge_offer_pure(player, placed["order"]["id"])
                self.assertTrue(collected["ok"])
                self.assertEqual(player["inventory"][item_name], 1)
                self.assertEqual(player["inventory"]["Logs"], 20)

    def test_cut_gem_review_output_can_be_traded_and_reloaded_without_item_loss(self):
        original_modules = dict(sys.modules)
        self.addCleanup(sys.modules.update, original_modules)
        self.addCleanup(sys.modules.clear)
        for recipe, uncut, item_name, item_id, price, xp in (
            ("cut_jade", "Uncut jade", "Jade", 1611, 89, 20.0),
            ("cut_red_topaz", "Uncut red topaz", "Red topaz", 1613, 157, 25.0),
        ):
            with self.subTest(item_name=item_name):
                smoke_support._install_runtime_fakes()
                col = smoke_support._DummyCol({"ankiscape_current_skill": "Crafting"})
                col.set_config = lambda key, value, col=col: col._store.__setitem__(
                    key, copy.deepcopy(value)
                )
                sys.modules["aqt"].mw = smoke_support._DummyMW(col)
                addon = smoke_support._load_addon_as_package(f"ankiscape_{recipe}_ge_roundtrip")
                original_random = addon.random.random
                addon.random.random = lambda: 0.5
                self.addCleanup(setattr, addon.random, "random", original_random)
                captured = {}
                addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
                addon.check_achievements = lambda _data: None
                addon._show_exp = lambda _amount: None
                addon.update_review_hud = lambda *_args: None
                addon._refresh_skill_availability = lambda: None
                addon.show_error_message = lambda _title, message: self.fail(message)
                addon.load_player_data()
                player = addon._runtime_action_context().player_data
                player.update(
                    inventory={"Coins": 10_000, "Logs": 7, "Chisel": 1, uncut: 1},
                    crafting_level=99,
                    crafting_exp=13_034_431,
                    current_craft=recipe,
                )
                addon.save_player_data()

                addon.on_card_did_show(None)
                addon.on_show_answer(None)
                addon.on_answer_card(smoke_support._FakeReviewer(), 3, lambda _self, _ease: "answered")
                player = addon._runtime_action_context().player_data
                self.assertEqual(player["inventory"][item_name], 1)
                self.assertEqual(player["inventory"][uncut], 0)
                self.assertEqual(player["crafting_exp"], 13_034_431 + xp)
                self.assertEqual(addon.GE_ITEM_CATALOG[item_name]["source_item_id"], item_id)
                self.assertEqual(addon.GE_ITEM_CATALOG[item_name]["guide_price"], price)

                addon._on_main_menu()
                placed = captured["on_ge_action"](
                    "place_offer",
                    {"side": "sell", "item_name": item_name, "quantity": 1, "unit_price": price},
                )
                self.assertTrue(placed["ok"])
                persisted = col.get_config("ankiscape_player_data")
                self.assertEqual(persisted["ge_player_orders"][0]["escrow_items"], 1)
                self.assertEqual(persisted["inventory"].get(item_name, 0), 0)

                addon.load_player_data()
                player = addon._runtime_action_context().player_data
                order_id = player["ge_player_orders"][0]["id"]
                self.assertEqual(player["ge_player_orders"][0]["escrow_items"], 1)
                self.assertTrue(captured["on_ge_action"]("cancel_offer", {"order_id": order_id})["ok"])
                self.assertTrue(captured["on_ge_action"]("collect_offer", {"order_id": order_id})["ok"])
                addon.load_player_data()
                player = addon._runtime_action_context().player_data
                self.assertEqual(player["ge_player_orders"], [])
                self.assertEqual(player["inventory"][item_name], 1)
                self.assertEqual(player["inventory"]["Logs"], 7)
                self.assertEqual(player["inventory"]["Coins"], 10_000)
                self.assertEqual(player["crafting_exp"], 13_034_431 + xp)

    @unittest.skipUnless(widget_support.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
    def test_cut_gem_alchemy_picker_uses_existing_shop_price_gate(self):
        widget_support.MainMenuWidgetTest.setUpClass()
        fixture = widget_support.MainMenuWidgetTest("runTest")
        fixture.setUp()
        self.addCleanup(fixture.tearDown)

        player = widget_support._make_player_data()
        player.update(
            magic_level=99,
            inventory={"Jade": 1, "Red topaz": 1, "Fire rune": 3, "Nature rune": 1},
            magic_alchemy_item="",
        )
        dialog = fixture._open(player, current_skill="Magic")
        tree = dialog.findChild(widget_support.QTreeWidget, "magicTargetTree")
        self.assertTrue(widget_support._tree_row(tree, "low_alchemy").isDisabled())

        picker = dialog.findChild(widget_support.QComboBox, "magicAlchemyItemCombo")
        self.assertEqual(picker.findData("Jade"), -1)
        topaz_index = picker.findData("Red topaz")
        self.assertGreaterEqual(topaz_index, 0)
        self.assertEqual(picker.itemText(topaz_index), "Red topaz (1; H 120 / L 80)")
        picker.setCurrentIndex(topaz_index)
        widget_support.QApplication.processEvents()

        tree = dialog.findChild(widget_support.QTreeWidget, "magicTargetTree")
        self.assertEqual(fixture._magic_alch_calls[-1], "Red topaz")
        self.assertFalse(widget_support._tree_row(tree, "low_alchemy").isDisabled())
