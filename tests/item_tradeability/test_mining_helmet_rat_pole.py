"""Period item identities must survive ordinary reviews, trading and storage."""
import copy
import json
import math
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

from tests import test_integration_smoke as runtime_fixture
from tests.test_combat_quest_gate import _answer_review, _maxed_player_for_quest


RAW = "Mining helmet (unlit)"
LIT = "Mining helmet (lit)"


class MiningHelmetRatPoleTest(unittest.TestCase):
    def setUp(self):
        modules = patch.dict(sys.modules)
        modules.start()
        self.addCleanup(modules.stop)
        runtime_fixture._install_runtime_fakes()
        self.collection = runtime_fixture._DummyCol()
        sys.modules["aqt"].mw = runtime_fixture._DummyMW(self.collection)
        self.addon = runtime_fixture._load_addon_as_package("ankiscape_helmet_rat_pole")
        self.addon._state.player_data, self.addon._state.current_skill = self.addon.storage_load_player_data()
        self.addon.update_review_hud = lambda *_args: None
        self.addon._refresh_skill_availability = lambda: None
        self.addon._update_review_context_surface = lambda: None
        self.addon.check_achievements = lambda _data: None
        self.addon.show_error_message = lambda _title, message: self.fail(message)
        captured = {}
        self.addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        self.addon._on_main_menu()
        self.action = captured["on_ge_action"]
        self.constants = sys.modules[f"{self.addon.__name__}.core.constants"]
        self.ge = sys.modules[f"{self.addon.__name__}.logic.grand_exchange_logic"]

    def _seed_save(self):
        self.addon.save_player_data()
        self.addon._state.player_data, self.addon._state.current_skill = self.addon.storage_load_player_data()

    def _reload(self):
        addon = self.addon
        addon.save_player_data()
        before = copy.deepcopy(addon._state.player_data)
        # Reviews remove this empty request; storage restores its default.
        before.setdefault("skilling_bank_run_requested", "")
        skill = addon._state.current_skill
        self.collection._store = json.loads(json.dumps(self.collection._store))
        addon._state.player_data, addon._state.current_skill = addon.storage_load_player_data()
        self.assertEqual(addon._state.player_data, before)
        self.assertEqual(addon._state.current_skill, skill)

    def _undo(self, operation):
        self.addon._on_state_did_undo(types.SimpleNamespace(operation=operation))

    def _fill(self):
        addon = self.addon
        shop = sys.modules[f"{addon.__name__}.logic.shop_logic"]
        clocked = shop.advance_shop_market_clock_pure(addon._state.player_data, calendar_ticks_before=0, calendar_ticks_after=600 * (1))
        addon._state.player_data, result = self.ge.advance_ge_market_tick_pure(
            clocked, item_catalog=addon.GE_ITEM_CATALOG, random_draw=lambda: 0.0)
        self.assertEqual(len(result["fills"]), 1)

    def test_exact_registry_catalog_and_consumer_projections(self):
        definitions = {item.storage_key: item for item in self.constants.ITEM_DEFINITIONS}
        for name, identity, tradeable in ((RAW, 5014, True), (LIT, 5013, False), ("Rat pole", 6773, False)):
            with self.subTest(name=name):
                item = definitions[name]
                self.assertEqual((item.source_item_id, item.stackable, item.tradeable),
                                 (identity, False, tradeable))
        for table in (self.constants.QUEST_REWARD_ITEM_DATA, self.constants.EXTRA_ITEM_DATA):
            self.assertEqual({key: table["Rat pole"][key] for key in
                              ("category", "item_id", "stackable", "tradeable", "source")},
                             {"category": "equipment", "item_id": 6773, "stackable": False,
                              "tradeable": False, "source": "https://runescape.wiki/w/Rat_pole?oldid=5671031"})
        spec = self.addon.GE_ITEM_CATALOG[RAW]
        self.assertEqual((spec["source_item_id"], spec["guide_price"], spec["buy_limit"], spec["cache_value"]),
                         (5014, 466, 100, 900))
        self.assertEqual(spec["guide_price_provenance"], {
            "price": 466, "page_title": "Exchange:Mining helmet", "oldid": 6562665,
            "timestamp": "2012-11-16T04:22:07Z", "price_date": "04:21, November 16, 2012 (UTC)",
            "page_item": "Mining helmet", "item_id": 5014, "cache_value": 900, "page_limit": 100})
        self.assertEqual(spec["buy_limit_source"]["oldid"], 6457777)
        projection = self.ge.ge_frontend_projection_pure(
            self.addon._state.player_data, item_catalog=self.addon.GE_ITEM_CATALOG)
        names = {row["item_name"] for row in projection["items"]}
        self.assertIn(RAW, names)
        heart = sys.modules[f"{self.addon.__name__}.logic.shattered_heart_logic"]
        replacements = heart._output_replacement_items()
        self.assertIn(RAW, replacements)
        for name in (LIT, "Rat pole"):
            self.assertNotIn(name, self.addon.GE_ITEM_CATALOG)
            self.assertNotIn(name, names)
            self.assertNotIn(name, self.constants.ALCH_VALUES)
            self.assertNotIn(name, replacements)

    def test_buy_light_review_undo_extinguish_sell_collect_and_full_reload(self):
        addon = self.addon
        addon._state.player_data.update({"inventory": {"Coins": 466, "Tinderbox": 1},
                                         "firemaking_level": 65, "current_utility": "light_mining_helmet"})
        addon._state.current_skill = "Utility / Activities"
        self._seed_save()
        self._reload()
        buy = {"side": "buy", "item_name": RAW, "quantity": 1, "unit_price": 466, "confirmed": True}
        before = copy.deepcopy(addon._state.player_data)
        self.assertTrue(self.action("place_offer", buy)["ok"])
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 0)
        self.assertEqual(addon._state.player_data["ge_player_orders"][0]["escrow_coins"], 466)
        self._undo("AnkiScape direct action")
        self.assertEqual(addon._state.player_data, before)
        self.assertTrue(self.action("place_offer", buy)["ok"])
        self._reload()
        self._fill()
        order = addon._state.player_data["ge_player_orders"][0]
        self.assertEqual((order["status"], order["collectible_items"], order["escrow_coins"]), ("complete", 1, 0))
        self.assertTrue(self.action("collect_offer", {"order_id": order["id"]})["ok"])
        self.assertEqual(addon._state.player_data["inventory"][RAW], 1)
        before = copy.deepcopy(addon._state.player_data)
        _answer_review(addon)
        self.assertEqual((addon._state.player_data["inventory"][RAW], addon._state.player_data["inventory"][LIT]), (0, 1))
        self._undo("Answer Card")
        self.assertEqual(addon._state.player_data, before)
        _answer_review(addon)
        self._reload()
        for side in ("buy", "sell"):
            before = copy.deepcopy(addon._state.player_data)
            refused = self.action("place_offer", {**buy, "side": side, "item_name": LIT})
            self.assertEqual((refused["ok"], refused["reason"]), (False, "unknown_item"))
            self.assertEqual(addon._state.player_data, before)
        addon._state.player_data["current_utility"] = "extinguish_mining_helmet"
        _answer_review(addon)
        self.assertEqual((addon._state.player_data["inventory"][RAW], addon._state.player_data["inventory"][LIT]), (1, 0))
        sell = {**buy, "side": "sell"}
        before = copy.deepcopy(addon._state.player_data)
        self.assertTrue(self.action("place_offer", sell)["ok"])
        self.assertEqual(addon._state.player_data["ge_player_orders"][0]["escrow_items"], 1)
        self._undo("AnkiScape direct action")
        self.assertEqual(addon._state.player_data, before)
        self.assertTrue(self.action("place_offer", sell)["ok"])
        self._reload()
        self._fill()
        order = addon._state.player_data["ge_player_orders"][0]
        self.assertEqual((order["status"], order["escrow_items"], order["collectible_coins"]), ("complete", 0, 482))
        self.assertTrue(self.action("collect_offer", {"order_id": order["id"]})["ok"])
        self.assertEqual((addon._state.player_data["inventory"][RAW], addon._state.player_data["inventory"]["Coins"]), (0, 482))
        self.assertEqual(addon._state.player_data["ge_player_orders"], [])
        self._reload()

    def test_saved_lit_offer_never_fills_at_both_draw_extremes_and_returns_escrow(self):
        addon = self.addon
        for draw in (0.0, math.nextafter(1.0, 0.0)):
            with self.subTest(draw=draw):
                addon._state.player_data.update({"inventory": {}, "ge_market_state": {},
                    "shop_market_clock": {"answered_cards": 1, "market_tick": 1},
                    "ge_player_orders": [{"id": 1, "side": "sell", "item_name": LIT, "status": "open",
                        "original_quantity": 1, "remaining_quantity": 1, "submitted_unit_price": 466, "escrow_items": 1}]})
                self._seed_save()
                self._reload()
                before = copy.deepcopy(addon._state.player_data["ge_player_orders"])
                addon._state.player_data, tick = self.ge.advance_ge_market_tick_pure(
                    addon._state.player_data, item_catalog=addon.GE_ITEM_CATALOG, random_draw=lambda: draw)
                self.assertEqual(tick["fills"], [])
                self.assertEqual(addon._state.player_data["ge_player_orders"], before)
                self.assertTrue(self.action("cancel_offer", {"order_id": 1})["ok"])
                self.assertTrue(self.action("collect_offer", {"order_id": 1})["ok"])
                self.assertEqual(addon._state.player_data["inventory"][LIT], 1)
                self.assertEqual(addon._state.player_data["ge_player_orders"], [])
                self._reload()

    def test_rat_reward_review_undo_reload_no_duplicate_and_existing_multiple_copies(self):
        addon = self.addon
        # This verifies reward delivery from an existing final-stage save; the
        # generated Rat Catchers action checkpoints have no playable producers.
        player = _maxed_player_for_quest("rat_catchers")
        player.update({"current_quest": "rat_catchers", "quest_action_proofs": ["Complete Rat Catchers stage 9 objective"]})
        player["quests"]["rat_catchers"] = {"started": True, "progress": 9, "completed": False}
        addon._state.player_data.update(player)
        addon._state.current_skill = "Quests"
        self._seed_save()
        self._reload()
        before = copy.deepcopy(addon._state.player_data)
        quest_logic = sys.modules[f"{addon.__name__}.logic_pure.logic_pure_quest"]
        self.assertEqual(quest_logic.quest_current_stage_blockers_pure(
            addon._state.player_data, "rat_catchers", self.constants.QUEST_DATA), ())
        self.assertTrue(addon._can_start_current_action(), addon._state.current_skill)
        notices = []
        addon.show_error_message = lambda title, message: notices.append((title, message))
        _answer_review(addon)
        self.assertEqual(notices[0][0], "Quest complete")
        self.assertEqual(addon._state.player_data["inventory"]["Rat pole"], 1)
        self.assertTrue(addon._state.player_data["quests"]["rat_catchers"]["completed"])
        self._undo("Answer Card")
        self.assertEqual(addon._state.player_data, before)
        _answer_review(addon)
        self._reload()
        addon.on_quest_answer()
        self.assertEqual(addon._state.player_data["inventory"]["Rat pole"], 1)
        addon._state.player_data["inventory"]["Rat pole"] = 3
        addon._state.player_data["carried_inventory"] = {"legacy": {"Rat pole": 3}}
        self._reload()
        self.assertEqual(addon._state.player_data["inventory"]["Rat pole"], 3)
        self.assertEqual(addon._state.player_data["carried_inventory"]["legacy"], {"Rat pole": 3})
        values = sys.modules[f"{addon.__name__}.data.item_values"]
        inventory = sys.modules[f"{addon.__name__}.logic.inventory_pure"]
        self.assertNotIn("Rat pole", values.STACKABLE_ITEM_NAMES)
        self.assertEqual(inventory.carried_slots_used({"Rat pole": 3}, values.STACKABLE_ITEM_NAMES), 3)

    def test_base_stackable_pyramid_saves_load_at_capacity_without_losing_bank_items(self):
        # The fixture retains the pack and ownership fields from Astra's real
        # saves on 3c1f481e, before all three registry stackability corrections.
        saves = json.loads(Path(__file__).with_name("pyramid_plunder_base_saves.json").read_text())["saves"]
        addon = self.addon
        plunder = sys.modules[f"{addon.__name__}.logic.pyramid_plunder_logic"]
        target = plunder.PYRAMID_PLUNDER_ACTIVITY_ID
        definitions = {item.storage_key: item for item in self.constants.ITEM_DEFINITIONS}
        for name in (LIT, RAW, "Rat pole"):
            with self.subTest(item=name):
                self.collection._store = copy.deepcopy(saves[name])
                saved = self.collection._store["ankiscape_player_data"]
                self.assertEqual(saved["carried_inventory"][target], {name: 2, "Shark": 27})
                self.assertFalse(definitions[name].stackable)
                addon._state.player_data, addon._state.current_skill = addon.storage_load_player_data()
                loaded = addon._state.player_data
                self.assertEqual(plunder.pyramid_plunder_view_pure(loaded)["pack_slots"], 28)
                self.assertEqual(loaded["carried_inventory"][target], {name: 2, "Shark": 26})
                self.assertEqual({key: amount for key, amount in loaded["inventory"].items() if amount},
                                 {name: 2, "Shark": 27})
                self.assertEqual(loaded["carried_layout"][target], {name: 2, "Shark": 27})
                self.assertEqual(loaded["pyramid_plunder"], saved["pyramid_plunder"])
                self.assertEqual(loaded["activity_session"], {"active_id": target})
                self._reload()
