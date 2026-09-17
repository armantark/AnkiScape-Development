"""The two period-qualified capes retain their identity through ordinary trade."""
import copy
import dataclasses
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, MAGIC_DATA
from ankiscape.data.grand_exchange_data import GE_ITEM_CATALOG
from ankiscape.data.shop_data import SHOP_DATA
from ankiscape.logic.shop_fixtures import build_shop_fixture_player_data
from ankiscape.logic.shop_logic import apply_shop_sell_pure
from ankiscape.logic_pure.logic_pure import apply_magic_action_pure
from ankiscape.runtime.runtime_actions_magic import _magic_alch_values
from tests import test_integration_smoke as runtime_fixture
from tests import test_storage_runtime as storage_fixture


ROOT = Path(__file__).resolve().parents[2]
CAPES = {
    "Spotted cape": (10069, 406, 400, 6563180),
    "Spottier cape": (10071, 633, 800, 6571613),
}


class CapeTradeabilityDataTest(unittest.TestCase):
    def test_registry_and_market_preserve_equipment_identity(self):
        snapshot = json.loads((ROOT / "memory-bank/source-audits/"
            "cape-tradeability-implementation-2026-09-05/owner-snapshot.json").read_text())
        definitions = {item.storage_key: item for item in ITEM_DEFINITIONS}
        self.assertEqual(
            {retained["fields"]["storage_key"] for retained in snapshot["definitions"]},
            set(CAPES),
        )
        for retained in snapshot["definitions"]:
            expected = dict(retained["fields"])
            name = expected["storage_key"]
            item_id, price, value, oldid = CAPES[name]
            with self.subTest(item=name):
                expected.update(tradeable=True, source_item_id=item_id)
                item = definitions[name]
                actual = dataclasses.asdict(item)
                actual["asset_path"] = "<repo>/" + Path(item.asset_path).relative_to(ROOT).as_posix()
                self.assertEqual(actual, expected)
                self.assertTrue(Path(item.asset_path).is_file())
                row = GE_ITEM_CATALOG[name]
                self.assertEqual((row["source_item_id"], row["guide_price"], row["cache_value"], row["buy_limit"]),
                                 (item_id, price, value, 100))
                self.assertEqual(row["guide_price_source"], "period_grand_exchange_database")
                self.assertEqual(row["guide_price_provenance"]["oldid"], oldid)
                self.assertNotIn("buy_limit", row["guide_price_provenance"])
                self.assertEqual((row["low_alchemy_value"], row["high_alchemy_value"]),
                                 (int(value * 0.4), int(value * 0.6)))

    def test_existing_shop_and_alchemy_consumers_use_unchanged_values(self):
        shop = next(shop for shop in SHOP_DATA.values()
                    if shop["visibility"] == "visible" and shop["general_store"])
        alch_values = _magic_alch_values()
        for name, (_item_id, _price, value, _oldid) in CAPES.items():
            with self.subTest(item=name):
                player = build_shop_fixture_player_data()
                player["inventory"].update({name: 1, "Coins": 0})
                sold, result = apply_shop_sell_pure(player, shop["id"], name, 1)
                self.assertTrue(result["allowed"], result)
                self.assertEqual(sold["inventory"][name], 0)
                self.assertEqual(sold["inventory"]["Coins"], int(value * 0.3))
                self.assertEqual(alch_values[name], value)
                for spell, fraction in (("low_alchemy", 0.4), ("high_alchemy", 0.6)):
                    with self.subTest(spell=spell):
                        player = {"magic_level": 99, "magic_alchemy_item": name,
                                  "inventory": {name: 1, "Nature rune": 1, "Fire rune": 5}}
                        updated, _xp, _secondary, outputs, ok, message = apply_magic_action_pure(
                            player, spell, MAGIC_DATA, alch_values)
                        self.assertTrue(ok, message)
                        self.assertEqual(outputs, {"Coins": int(value * fraction)})
                        self.assertEqual(updated["inventory"][name], 0)


class _JsonCollection(runtime_fixture._DummyCol):
    def set_config(self, key, value):
        self._store[key] = json.loads(json.dumps(value))

    def get_config(self, key, default=None):
        return copy.deepcopy(self._store.get(key, default))


class CapeTradeabilityRuntimeTest(unittest.TestCase):
    def setUp(self):
        modules = patch.dict(sys.modules)
        modules.start()
        self.addCleanup(modules.stop)
        runtime_fixture._install_runtime_fakes()

    def test_buy_sell_collection_and_reload(self):
        self.assert_lifecycle(_JsonCollection())

    @unittest.skipIf(storage_fixture.Collection is None, "Anki runtime is not installed")
    def test_buy_sell_persist_in_real_anki_collection(self):
        with tempfile.TemporaryDirectory() as directory:
            collection = storage_fixture.Collection(str(Path(directory) / "collection.anki2"))
            try:
                self.assert_lifecycle(collection)
            finally:
                collection.close()

    def assert_lifecycle(self, collection):
        sys.modules["aqt"].mw = runtime_fixture._DummyMW(collection)
        addon = runtime_fixture._load_addon_as_package("ankiscape_cape_tradeability_runtime")
        addon._state.player_data, addon._state.current_skill = addon.storage_load_player_data()
        addon.save_player_data()
        addon._state.player_data, addon._state.current_skill = addon.storage_load_player_data()
        addon._state.player_data["inventory"]["Coins"] = 10_000
        addon._state.player_data["equipment"] = {"cape": "Spotted cape"}
        equipment = copy.deepcopy(addon._state.player_data["equipment"])
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._on_main_menu()
        action = captured["on_ge_action"]
        ge_logic = sys.modules[f"{addon.__name__}.logic.grand_exchange_logic"]
        shop_logic = sys.modules[f"{addon.__name__}.logic.shop_logic"]

        def reload():
            expected = json.loads(json.dumps(addon._state.player_data))
            self.assertEqual(collection.get_config("ankiscape_player_data"), expected)
            addon._state.player_data, addon._state.current_skill = addon.storage_load_player_data()
            for key in ("inventory", "equipment", "ge_player_orders", "ge_buy_limit_usage"):
                self.assertEqual(addon._state.player_data[key], expected[key])
            self.assertEqual(addon._state.player_data["equipment"], equipment)

        for name, (_item_id, guide_price, _value, _oldid) in CAPES.items():
            for side, unit_price in (("buy", guide_price * 2), ("sell", guide_price // 2)):
                with self.subTest(item=name, side=side):
                    before_coins = addon._state.player_data["inventory"]["Coins"]
                    result = action("place_offer", {"side": side, "item_name": name,
                                    "quantity": 1, "unit_price": unit_price, "confirmed": True})
                    self.assertTrue(result["ok"], result)
                    self.assertEqual(len(addon._state.player_data["ge_player_orders"]), 1)
                    order = addon._state.player_data["ge_player_orders"][0]
                    self.assertEqual(order["item_name"], name)
                    if side == "buy":
                        self.assertEqual(order["escrow_coins"], unit_price)
                        self.assertEqual(addon._state.player_data["inventory"]["Coins"], before_coins - unit_price)
                    else:
                        self.assertEqual(order["escrow_items"], 1)
                        self.assertEqual(addon._state.player_data["inventory"][name], 0)
                    reload()
                    clocked = shop_logic.advance_shop_market_clock_pure(addon._state.player_data)
                    addon._state.player_data, fill = ge_logic.advance_ge_market_tick_pure(
                        clocked, item_catalog=addon.GE_ITEM_CATALOG, random_draw=lambda: 0.0)
                    self.assertEqual(len(fill["fills"]), 1, fill)
                    order = addon._state.player_data["ge_player_orders"][0]
                    self.assertEqual(order["status"], "complete")
                    collectible_coins = order["collectible_coins"]
                    coins_before_collection = addon._state.player_data["inventory"]["Coins"]
                    addon.save_player_data()
                    reload()
                    collected = action("collect_offer", {"order_id": order["id"]})
                    self.assertTrue(collected["ok"], collected)
                    self.assertEqual(addon._state.player_data["inventory"].get(name, 0), 1 if side == "buy" else 0)
                    self.assertEqual(addon._state.player_data["inventory"]["Coins"], coins_before_collection + collectible_coins)
                    self.assertEqual(addon._state.player_data["ge_player_orders"], [])
                    reload()
