"""Nest custody and ordinary rod values survive review, Undo and persistence."""
import copy
import dataclasses
import importlib
import json
import runpy
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from tests import test_integration_smoke as runtime_fixture
from tests.test_storage_runtime import Collection
from tools.gen_item_values import build


NESTS = (("Bird's nest (seeds)", 5073), ("Bird's nest (ring)", 5074),
         ("Bird's nest (empty)", 5075))
ROD = "Fly fishing rod"


class NestAndRodContractTest(unittest.TestCase):
    def setUp(self):
        modules = patch.dict(sys.modules)
        modules.start()
        self.addCleanup(modules.stop)
        runtime_fixture._install_runtime_fakes()
        self.load_addon(runtime_fixture._DummyCol())

    def load_addon(self, collection):
        self.collection = collection
        sys.modules["aqt"].mw = runtime_fixture._DummyMW(collection)
        self.addon = runtime_fixture._load_addon_as_package("ankiscape_nest_rod_contracts")
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
        self.assertTrue(addon._cadence_kernel_enabled())

    def module(self, name):
        return importlib.import_module(f"{self.addon.__name__}.{name}")

    def reload(self):
        addon = self.addon
        addon.save_player_data()
        expected = copy.deepcopy(addon._state.player_data)
        if isinstance(self.collection, runtime_fixture._DummyCol):
            self.collection._store = json.loads(json.dumps(self.collection._store))
        addon._state.player_data, addon._state.current_skill = addon.storage_load_player_data()
        self.assertEqual(addon._state.player_data, expected)

    def answer(self):
        addon = self.addon
        addon._state.card_turned = addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(runtime_fixture._FakeReviewer(), 4, lambda *_args: "answered")

    def undo(self, expected):
        self.addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card", changes=types.SimpleNamespace(study_queues=True, card=True)))
        self.assertEqual(self.addon._state.player_data, expected)

    def test_exact_nest_metadata_excludes_trade_consumers(self):
        constants = self.module("core.constants")
        definitions = {item.storage_key: item for item in constants.ITEM_DEFINITIONS}
        ge = self.module("data.grand_exchange_data")
        heart = self.module("logic.shattered_heart_logic")
        shop = self.module("logic.shop_logic")
        general = next(row["id"] for row in shop.SHOP_DATA.values()
                       if row["visibility"] == "visible" and row["general_store"])
        self.assertEqual(len(ge.PERIOD_GE_GUIDE_PRICES), 1446)
        self.assertEqual(len(ge.PERIOD_GE_BUY_LIMITS), 1841)
        for name, item_id in NESTS:
            with self.subTest(item=name):
                for catalog in (constants.WOODCUTTING_EXTRA_ITEM_DATA, constants.EXTRA_ITEM_DATA):
                    self.assertEqual((catalog[name]["item_id"], catalog[name]["tradeable"],
                                      catalog[name]["stackable"]), (item_id, False, False))
                self.assertEqual((definitions[name].source_item_id, definitions[name].tradeable,
                                  definitions[name].stackable), (item_id, False, False))
                for catalog in (ge.GE_ITEM_CATALOG, ge.PERIOD_GE_GUIDE_PRICES,
                                ge.PERIOD_GE_BUY_LIMITS, constants.ALCH_VALUES,
                                self.module("runtime.runtime_actions_magic")._magic_alch_values()):
                    self.assertNotIn(name, catalog)
                self.assertNotIn(name, heart._output_replacement_items())
                player = {"inventory": {name: 2}}
                denied, sale = shop.apply_shop_sell_pure(player, general, name, 1)
                self.assertEqual(sale["reason"], "item_not_tradeable")
                self.assertEqual(denied["inventory"], player["inventory"])
                draws = iter((0.0, 1.0))
                updated, awarded, result = heart.apply_shattered_heart_skilling_hook_pure(
                    player, "woodcutting", lambda: next(draws), {name: 1})
                self.assertTrue(awarded, result)
                self.assertEqual(result["replaced_outputs"], {})
                self.assertEqual(updated["inventory"][name], 2)

    def test_each_base_stackable_saved_pack_reloads_at_28_without_losing_ownership(self):
        addon = self.addon
        plunder = self.module("logic.pyramid_plunder_logic")
        target = plunder.PYRAMID_PLUNDER_ACTIVITY_ID
        for name, _item_id in NESTS:
            with self.subTest(item=name):
                player = copy.deepcopy(self.initial)
                layout = {name: 2, "Shark": 27}
                player["inventory"].update({**layout, "Coins": 37})
                player.update(thieving_level=91,
                              carried_advanced_targets={target: True},
                              carried_layout={target: layout.copy()})
                player["quests"]["icthlarins_little_helper"]["started"] = True
                player, ok, info = plunder.enter_pyramid_plunder_pure(player)
                self.assertTrue(ok, info)
                player["carried_inventory"] = {target: layout.copy()}
                addon._state.player_data, addon._state.current_skill = player, "Activities"
                addon.save_player_data()
                saved = json.loads(json.dumps(self.collection.get_config("ankiscape_player_data")))
                self.assertEqual(saved["carried_inventory"][target], layout)
                self.assertEqual(plunder.pyramid_plunder_view_pure(saved)["pack_slots"], 28)
                addon._state.player_data, addon._state.current_skill = addon.storage_load_player_data()
                loaded = addon._state.player_data
                self.assertEqual(loaded["carried_inventory"][target], {name: 2, "Shark": 26})
                self.assertEqual(loaded["carried_layout"][target], layout)
                self.assertEqual(loaded["inventory"], saved["inventory"])
                self.assertEqual(plunder.pyramid_plunder_view_pure(loaded)["pack_slots"], 28)
                self.reload()

    def test_default_cadence_earns_opens_and_grinds_nests_with_complete_undo(self):
        addon = self.addon
        original_context = addon._runtime_action_context
        for name, roll, content in ((NESTS[0][0], 0.0, "Acorn"),
                                    (NESTS[1][0], 0.99, "Sapphire ring")):
            with self.subTest(item=name):
                addon._state.player_data = copy.deepcopy(self.initial)
                addon._state.player_data.update(woodcutting_level=99, current_tree="tree")
                addon._state.player_data["toolbelt"]["woodcutting"] = ["bronze_hatchet"]
                addon._state.player_data["shattered_heart"]["auto_discard"] = True
                addon._state.current_skill = "Woodcutting"
                self.reload()
                before = copy.deepcopy(addon._state.player_data)
                for attempt in range(3):
                    # Live cadence admits the chop; the draws select its nest.
                    draws = iter((0.0, roll))
                    with patch.object(addon, "_runtime_action_context", side_effect=lambda: dataclasses.replace(
                            original_context(), random_random=lambda: next(draws), review_action_multiplier=1)):
                        self.answer()
                    self.assertEqual(addon._state.player_data["inventory"].get(name), 1)
                    if attempt < 2:
                        self.undo(before)
                self.reload()
                addon._state.player_data["current_utility"] = "open_bird_nest"
                addon._state.current_skill = "Utility / Activities"
                self.reload()
                before = copy.deepcopy(addon._state.player_data)
                with patch.object(addon, "_runtime_action_context", side_effect=lambda: dataclasses.replace(
                        original_context(), random_random=lambda: 0.0)):
                    self.answer()
                self.assertEqual(addon._state.player_data["inventory"][name], 0)
                self.assertEqual(addon._state.player_data["inventory"][content], 1)
                self.assertEqual(addon._state.player_data["inventory"][NESTS[2][0]], 1)
                self.undo(before)
        addon._state.player_data = copy.deepcopy(self.initial)
        addon._state.player_data["inventory"][NESTS[2][0]] = 2
        addon._state.player_data["current_utility"] = "grind_birds_nest"
        addon._state.current_skill = "Utility / Activities"
        self.reload()
        before = copy.deepcopy(addon._state.player_data)
        self.answer()
        self.assertEqual(addon._state.player_data["inventory"]["Crushed nest"], 2)
        self.undo(before)
        self.answer()
        self.reload()

    def test_generator_uses_ordinary_rod_id_in_either_duplicate_order(self):
        rows = {"309": {"name": ROD, "value": 5, "exchangeable": True},
                "17794": {"name": ROD, "value": 50, "exchangeable": False},
                "1511": {"name": "Logs", "value": 4, "exchangeable": True}}
        with tempfile.TemporaryDirectory() as directory:
            raw, output = Path(directory) / "raw.json", Path(directory) / "generated.py"
            for entries in (list(rows.items()), list(reversed(rows.items()))):
                raw.write_text(json.dumps({"items": dict(entries)}))
                self.assertEqual(build(raw, output), (2, 0, 2))
                generated = runpy.run_path(str(output))
                self.assertEqual(generated["ITEM_VALUES_GENERATED"], {ROD: 5, "Logs": 4})
                self.assertIn(ROD, generated["EXCHANGEABLE_ITEM_NAMES_GENERATED"])

    def test_rod_value_consumers_keep_exact_market_and_shop_prices(self):
        values = self.module("data.item_values")
        constants = self.module("core.constants")
        self.assertEqual(values.item_store_value(ROD), 5)
        self.assertEqual(self.module("generated.item_values_generated").ITEM_VALUES_GENERATED[ROD], 5)
        self.assertEqual(constants.ALCH_VALUES[ROD], 5)
        self.assertEqual(self.module("runtime.runtime_actions_magic")._magic_alch_values()[ROD], 5)
        ge = self.module("data.grand_exchange_data").GE_ITEM_CATALOG[ROD]
        self.assertEqual((ge["source_item_id"], ge["cache_value"], ge["low_alchemy_value"],
                          ge["high_alchemy_value"], ge["guide_price"], ge["buy_limit"]),
                         (309, 5, 2, 3, 20, 100))
        self.assertEqual(ge["guide_price_provenance"]["oldid"], 6561944)
        shop = self.module("logic.shop_logic")
        shop_id = "lumbridge_fishing_supplies"
        player = self.module("logic.shop_fixtures").build_shop_fixture_player_data()
        player["inventory"].update({ROD: 2, "Coins": 10})
        sold, result = shop.apply_shop_sell_pure(player, shop_id, ROD, 1)
        self.assertTrue(result["allowed"], result)
        self.assertEqual(sold["inventory"]["Coins"], 11)
        row = next(row for row in shop.SHOP_DATA[shop_id]["stock"] if row["item_name"] == ROD)
        bought, result = shop.apply_shop_buy_pure(player, shop_id, row["id"], 1)
        self.assertTrue(result["allowed"], result)
        self.assertEqual(bought["inventory"]["Coins"], 5)
        inventory = self.module("logic.inventory_pure")
        self.assertEqual(inventory.filter_loot_pure({ROD: 1}, values.ITEM_VALUES, 4,
                                                  values.STACKABLE_ITEM_NAMES), ({}, {ROD: 1}))
        combat = self.module("logic_pure.logic_pure_combat_model")
        self.assertEqual(combat._combat_no_grave_protected_items(
            {}, {ROD: 1, "Bronze hatchet": 1}, 1, False), (set(), {"Bronze hatchet": 1}))
        armies = self.module("logic.mobilising_armies_logic")
        option = next(row for row in armies.mobilising_armies_view_pure(player)["investment_options"]
                      if row["id"] == ROD)
        self.assertEqual(option["credits_each"], 2)
        heart = self.module("logic.shattered_heart_logic")
        self.assertIn(ROD, heart._output_replacement_items())
        draws = iter((0.0, 1.0))
        replaced, awarded, result = heart.apply_shattered_heart_skilling_hook_pure(
            player, "fishing", lambda: next(draws), {ROD: 1})
        self.assertTrue(awarded, result)
        self.assertEqual(result["replaced_outputs"], {ROD: 1})
        self.assertEqual(replaced["inventory"][ROD], 1)

    @unittest.skipIf(Collection is None, "Anki runtime is not installed")
    def test_magic_pays_two_or_three_coins_with_full_undo_and_real_collection_reload(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "collection.anki2")
            collection = Collection(path)
            try:
                self.load_addon(collection)
                addon = self.addon
                original_context = addon._runtime_action_context
                for spell, payout, fires in (("low_alchemy", 2, 3), ("high_alchemy", 3, 5)):
                    with self.subTest(spell=spell):
                        addon._state.player_data = copy.deepcopy(self.initial)
                        addon._state.player_data.update(magic_level=99, current_magic=spell,
                                                        magic_alchemy_item=ROD)
                        addon._state.player_data["inventory"].update(
                            {ROD: 1, "Coins": 17, "Nature rune": 1, "Fire rune": fires})
                        addon._state.player_data["shattered_heart"]["auto_discard"] = True
                        addon._state.current_skill = "Magic"
                        self.reload()
                        for _attempt in range(2):
                            before = copy.deepcopy(addon._state.player_data)
                            with patch.object(addon, "_runtime_action_context", side_effect=lambda: dataclasses.replace(
                                    original_context(), random_random=lambda: 0.5, review_action_multiplier=1)):
                                self.answer()
                            expected = {**before["inventory"], ROD: 0, "Coins": 17 + payout,
                                        "Nature rune": 0, "Fire rune": 0}
                            self.assertEqual(addon._state.player_data["inventory"], expected)
                            self.undo(before)
                        with patch.object(addon, "_runtime_action_context", side_effect=lambda: dataclasses.replace(
                                original_context(), random_random=lambda: 0.5, review_action_multiplier=1)):
                            self.answer()
                        self.reload()
                        expected = copy.deepcopy(addon._state.player_data)
                        collection.close()
                        collection = Collection(path)
                        self.collection = collection
                        addon.mw.col = collection
                        addon._state.player_data, addon._state.current_skill = addon.storage_load_player_data()
                        self.assertEqual(addon._state.player_data, expected)
            finally:
                collection.close()
