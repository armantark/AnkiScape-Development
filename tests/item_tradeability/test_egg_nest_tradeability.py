"""Period egg nests preserve their contents and custody without being tradeable."""
import copy
import dataclasses
import json
import sys
import types
import unittest
from unittest.mock import patch

from tests import test_integration_smoke as runtime_fixture


EGG_NESTS = (
    ("Bird's nest (Zamorak egg)", 5070, "Zamorak bird's egg", 0.655),
    ("Bird's nest (Guthix egg)", 5071, "Guthix bird's egg", 0.665),
    ("Bird's nest (Saradomin egg)", 5072, "Saradomin bird's egg", 0.675),
)


class EggNestTradeabilityTest(unittest.TestCase):
    def setUp(self):
        modules = patch.dict(sys.modules)
        modules.start()
        self.addCleanup(modules.stop)
        runtime_fixture._install_runtime_fakes()
        self.collection = runtime_fixture._DummyCol()
        self.collection.set_config("ankiscape_cadence_kernel", False)
        sys.modules["aqt"].mw = runtime_fixture._DummyMW(self.collection)
        self.addon = runtime_fixture._load_addon_as_package("ankiscape_egg_nest_tradeability")
        addon = self.addon
        addon._state.player_data, addon._state.current_skill = addon.storage_load_player_data()
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._update_review_context_surface = lambda: None
        addon.check_achievements = lambda _data: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.save_player_data()
        addon._state.player_data, addon._state.current_skill = addon.storage_load_player_data()
        self.initial = copy.deepcopy(addon._state.player_data)

    def module(self, name):
        return sys.modules[f"{self.addon.__name__}.{name}"]

    def reload(self, expected_carried=None):
        addon = self.addon
        addon.save_player_data()
        expected = copy.deepcopy(addon._state.player_data)
        if expected_carried is not None:
            expected["carried_inventory"] = expected_carried
        self.collection._store = json.loads(json.dumps(self.collection._store))
        addon._state.player_data, addon._state.current_skill = addon.storage_load_player_data()
        self.assertEqual(addon._state.player_data, expected)

    def answer(self):
        addon = self.addon
        addon._state.card_turned = addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(runtime_fixture._FakeReviewer(), 4, lambda *_args: "answered")

    def undo(self):
        self.addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card", changes=types.SimpleNamespace(study_queues=True, card=True)))

    def test_exact_metadata_projects_without_changing_other_nests_or_ge(self):
        constants = self.module("core.constants")
        definitions = {item.storage_key: item for item in constants.ITEM_DEFINITIONS}
        ge = self.module("data.grand_exchange_data")
        self.assertEqual(len(ge.PERIOD_GE_GUIDE_PRICES), 1443)
        self.assertEqual(len(ge.PERIOD_GE_BUY_LIMITS), 1838)
        for name, item_id, _egg, _roll in EGG_NESTS:
            for catalog in (constants.WOODCUTTING_EXTRA_ITEM_DATA, constants.EXTRA_ITEM_DATA):
                self.assertEqual((catalog[name]["item_id"], catalog[name]["tradeable"],
                                  catalog[name]["stackable"]), (item_id, False, False))
            self.assertEqual((definitions[name].source_item_id, definitions[name].tradeable,
                              definitions[name].stackable), (item_id, False, False))
            for catalog in (ge.GE_ITEM_CATALOG, ge.PERIOD_GE_GUIDE_PRICES, ge.PERIOD_GE_BUY_LIMITS):
                self.assertNotIn(name, catalog)
        generic = definitions["Bird's nest"]
        self.assertEqual((generic.source_item_id, generic.tradeable, generic.stackable), (5070, False, False))
        for name in ("Bird's nest (seeds)", "Bird's nest (ring)", "Bird's nest (empty)"):
            self.assertEqual((definitions[name].source_item_id, definitions[name].tradeable,
                              definitions[name].stackable), (None, True, True))

    def test_review_earns_each_egg_nest_then_opens_undoes_and_reloads(self):
        addon = self.addon
        original_context = addon._runtime_action_context
        for name, _item_id, egg, nest_roll in EGG_NESTS:
            with self.subTest(item=name):
                addon._state.player_data = copy.deepcopy(self.initial)
                addon._state.player_data.update({
                    "woodcutting_level": 99, "current_tree": "tree",
                })
                addon._state.player_data["toolbelt"]["woodcutting"] = ["bronze_hatchet"]
                addon._state.player_data["shattered_heart"]["auto_discard"] = True
                addon._state.current_skill = "Woodcutting"
                rolls = iter((0.0, 0.0, nest_roll))
                with patch.object(addon, "_runtime_action_context", side_effect=lambda: dataclasses.replace(
                    original_context(), random_random=lambda: next(rolls), review_action_multiplier=1)):
                    before = copy.deepcopy(addon._state.player_data["inventory"])
                    self.answer()
                self.assertEqual(addon._state.player_data["inventory"], {**before, "Logs": 1, name: 1})
                self.undo()
                self.assertEqual(addon._state.player_data["inventory"], before)
                rolls = iter((0.0, 0.0, nest_roll))
                with patch.object(addon, "_runtime_action_context", side_effect=lambda: dataclasses.replace(
                    original_context(), random_random=lambda: next(rolls), review_action_multiplier=1)):
                    self.answer()
                self.reload()
                addon._state.player_data["current_utility"] = "open_bird_nest"
                addon._state.current_skill = "Utility / Activities"
                before = copy.deepcopy(addon._state.player_data["inventory"])
                self.answer()
                expected = {**before, "Logs": 1, name: 0, "Bird's nest (empty)": 1, egg: 1}
                self.assertEqual(addon._state.player_data["inventory"], expected)
                self.undo()
                self.assertEqual(addon._state.player_data["inventory"], before)
                self.answer()
                self.assertEqual(addon._state.player_data["inventory"], expected)
                self.reload(expected_carried={"tree": {"Logs": 1}})

    def test_multiple_saved_nests_keep_counts_and_use_one_carried_slot_each(self):
        addon = self.addon
        inventory = self.module("logic.inventory_pure")
        stackables = self.module("data.item_values").STACKABLE_ITEM_NAMES
        plunder = self.module("logic.pyramid_plunder_logic")
        for name, _item_id, _egg, _roll in EGG_NESTS:
            with self.subTest(item=name):
                layout = {name: 30}
                addon._state.player_data = copy.deepcopy(self.initial)
                addon._state.player_data["inventory"].update(layout)
                addon._state.player_data.update({
                    "carried_inventory": {"tree": layout.copy()},
                    "carried_layout": {"tree": layout.copy()},
                })
                self.reload()
                self.assertEqual(addon._state.player_data["inventory"], {**self.initial["inventory"], **layout})
                self.assertEqual(addon._state.player_data["carried_inventory"], {"tree": layout})
                self.assertEqual(addon._state.player_data["carried_layout"], {"tree": layout})
                self.assertNotIn(name, stackables)
                self.assertEqual(inventory.carried_slots_used(layout, stackables), 30)
                self.assertFalse(inventory.carried_has_room_for({name: 28}, name, 1, stackables))
                self.assertTrue(inventory.carried_has_room_for({name: 27}, name, 1, stackables))
                self.assertEqual(inventory.apply_carried_layout_pure(layout, layout, 28, stackables), {name: 28})
                self.assertEqual(inventory.layout_to_grid_cells_pure({name: 2}, stackables),
                                 [(name, 1), (name, 1)] + [(None, 0)] * 26)
                player = copy.deepcopy(addon._state.player_data)
                player["thieving_level"] = 99
                player["quests"]["icthlarins_little_helper"]["started"] = True
                player["carried_advanced_targets"] = {"pyramid_plunder": True}
                player["carried_layout"] = {"pyramid_plunder": layout}
                entered, ok, result = plunder.enter_pyramid_plunder_pure(player)
                self.assertTrue(ok, result)
                self.assertEqual(result["pack"], {name: 28})
                self.assertEqual(entered["inventory"][name], 30)
                self.assertEqual(plunder.pyramid_plunder_view_pure(entered)["pack_slots"], 28)

    def test_shop_alchemy_and_strange_rocks_preserve_unchanged_nest_control(self):
        shop = self.module("logic.shop_logic")
        constants = self.module("core.constants")
        magic = self.module("logic_pure.logic_pure_magic")
        runtime_magic = self.module("runtime.runtime_actions_magic")
        heart = self.module("logic.shattered_heart_logic")
        shop_id = next(row["id"] for row in shop.SHOP_DATA.values()
                       if row["visibility"] == "visible" and row["general_store"])
        control = "Bird's nest (seeds)"
        for name in [row[0] for row in EGG_NESTS] + ["Bird's nest"]:
            with self.subTest(item=name):
                player = {"inventory": {name: 1, control: 1, "Fire rune": 5, "Nature rune": 1},
                          "magic_level": 99, "magic_alchemy_item": name}
                denied, sale = shop.apply_shop_sell_pure(player, shop_id, name, 1)
                self.assertEqual((sale["allowed"], sale["reason"]), (False, "item_not_tradeable"))
                self.assertEqual(denied["inventory"], player["inventory"])
                self.assertTrue(shop._item_tradeable(control))
                denied, sale = shop.apply_shop_sell_pure(player, shop_id, control, 1)
                self.assertEqual((sale["allowed"], sale["reason"]), (False, "sell_price_unresolved"))
                self.assertEqual(denied["inventory"], player["inventory"])
                for values in (constants.ALCH_VALUES, runtime_magic._magic_alch_values()):
                    self.assertNotIn(name, values)
                    self.assertNotIn(control, values)
                    for item in (name, control):
                        player["magic_alchemy_item"] = item
                        for spell in ("low_alchemy", "high_alchemy"):
                            self.assertEqual(magic.magic_target_locked_reasons_pure(
                                player, spell, runtime_magic.MAGIC_DATA, values),
                                ("Choose a tradeable bank item",))
                self.assertNotIn(name, heart._output_replacement_items())
                self.assertIn(control, heart._output_replacement_items())
                draws = iter((0.0, 1.0))
                updated, awarded, result = heart.apply_shattered_heart_skilling_hook_pure(
                    player, "woodcutting", lambda: next(draws), {name: 1, control: 1})
                self.assertTrue(awarded, result)
                self.assertEqual(result["replaced_outputs"], {control: 1})
                self.assertEqual(updated["inventory"], {**player["inventory"], control: 0,
                                 "Strange rock (Woodcutting 1)": 1})

    def test_ge_refuses_new_offers_and_retained_escrow_never_fills(self):
        addon = self.addon
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon._on_main_menu()
        action = captured["on_ge_action"]
        ge = self.module("logic.grand_exchange_logic")
        for name, _item_id, _egg, _roll in EGG_NESTS:
            with self.subTest(item=name):
                addon._state.player_data = copy.deepcopy(self.initial)
                addon._state.player_data["inventory"].update({name: 3, "Coins": 17})
                for side, coins, items in (("buy", 111, 0), ("sell", 0, 3)):
                    held = copy.deepcopy(addon._state.player_data["inventory"])
                    before = copy.deepcopy(addon._state.player_data)
                    result = action("place_offer", {"side": side, "item_name": name,
                                    "quantity": 1, "unit_price": 10, "confirmed": True})
                    self.assertEqual((result["ok"], result["reason"]), (False, "unknown_item"))
                    self.assertEqual(addon._state.player_data, before)
                    addon._state.player_data["ge_player_orders"] = [{
                        "id": 1, "side": side, "item_name": name, "status": "open",
                        "original_quantity": 3, "remaining_quantity": 3, "submitted_unit_price": 37,
                        "escrow_items": items, "escrow_coins": coins,
                    }]
                    addon._state.player_data.update(ge.sanitize_ge_state_pure(addon._state.player_data))
                    self.reload()
                    self.assertEqual(len(addon._state.player_data["ge_player_orders"]), 1)
                    for draw in (0.0, 0.9999999999999999):
                        player = copy.deepcopy(addon._state.player_data)
                        player["shop_market_clock"] = {"answered_cards": 1, "market_tick": 1}
                        updated, result = ge.advance_ge_market_tick_pure(
                            player, item_catalog=addon.GE_ITEM_CATALOG, random_draw=lambda: draw)
                        self.assertEqual(result["fills"], [])
                        self.assertEqual(updated["ge_player_orders"], player["ge_player_orders"])
                    self.assertTrue(action("cancel_offer", {"order_id": 1})["ok"])
                    self.reload()
                    collected = action("collect_offer", {"order_id": 1})
                    self.assertTrue(collected["ok"], collected)
                    self.assertEqual((collected["coins"], collected["items"]), (coins, items))
                    self.assertEqual(addon._state.player_data["inventory"],
                                     {**held, name: held[name] + items, "Coins": held["Coins"] + coins})
                    self.assertEqual(addon._state.player_data["ge_player_orders"], [])
                    self.reload()
                    before = copy.deepcopy(addon._state.player_data)
                    self.assertEqual(action("collect_offer", {"order_id": 1})["reason"], "unknown_order")
                    self.assertEqual(addon._state.player_data, before)
