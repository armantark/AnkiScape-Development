import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.storage_pure import migrate_loaded_data, default_player_data, CURRENT_CONFIG_VERSION
from ankiscape.core.constants import MINING_OUTPUT_ITEMS, ORE_DATA, QUEST_DATA
from ankiscape.logic.grand_exchange_logic import cancel_ge_offer_pure, collect_ge_offer_pure
from ankiscape.logic.shop_logic import apply_shop_buy_pure, apply_shop_sell_pure
from ankiscape.logic_pure.logic_pure_quest import quest_current_stage_blocker_reasons_pure


class TestStorageMigrationExtra(unittest.TestCase):
    def test_inventory_none_becomes_dict(self):
        data = {"inventory": None}
        out = migrate_loaded_data(data, ORE_DATA)
        self.assertIsInstance(out["inventory"], dict)
        for ore in MINING_OUTPUT_ITEMS:
            self.assertIn(ore, out["inventory"])  # seeded

    def test_missing_inventory_key(self):
        data = {}
        out = migrate_loaded_data(data, ORE_DATA)
        self.assertIsInstance(out["inventory"], dict)
        for ore in MINING_OUTPUT_ITEMS:
            self.assertIn(ore, out["inventory"])  # seeded

    def test_retired_utility_activity_saves_migrate_to_default(self):
        # Bridges retired 2026-07-06 once their outputs became live NPC shop
        # stock; stale saves must not error on the next utility review.
        for retired in ("scavenge_chicken_feathers", "gather_fishing_bait", "buy_hunter_supplies", "buy_bucket", "gather_potatoes", "scavenge_raw_yak_meat", "gather_thin_snails"):
            data = {"current_utility": retired}
            out = migrate_loaded_data(data, ORE_DATA)
            self.assertEqual(out["current_utility"], "make_soft_clay", retired)
        kept = migrate_loaded_data({"current_utility": "gather_wool"}, ORE_DATA)
        self.assertEqual(kept["current_utility"], "gather_wool")

    def test_total_exp_preserved_when_mining_exp_present(self):
        # Current behavior: if mining_exp exists, total_exp is not migrated/popped
        data = {"total_exp": 123, "mining_exp": 999}
        out = migrate_loaded_data(data, ORE_DATA)
        self.assertEqual(out["mining_exp"], 999)
        self.assertIn("total_exp", out)

    def test_default_player_data_sets_current_defaults(self):
        base = default_player_data(ORE_DATA)
        self.assertEqual(base["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(base["current_smith"], "smelt_bronze_bar")
        self.assertEqual(base["current_ore"], "rune_essence")
        self.assertEqual(base["current_tree"], "tree")
        self.assertEqual(base["current_craft"], "form_pot_unfired")
        self.assertEqual(base["current_fletch"], "arrow_shafts")
        self.assertEqual(base["current_firemaking"], "logs")
        self.assertEqual(base["current_fishing"], "catch_crayfish")
        self.assertEqual(base["current_hunter"], "catch_crimson_swift")
        self.assertEqual(base["current_utility"], "make_soft_clay")
        self.assertEqual(base["fletching_level"], 1)
        self.assertEqual(base["fletching_exp"], 0)
        self.assertEqual(base["firemaking_level"], 1)
        self.assertEqual(base["firemaking_exp"], 0)
        self.assertEqual(base["fishing_level"], 1)
        self.assertEqual(base["fishing_exp"], 0)
        self.assertEqual(base["hunter_level"], 1)
        self.assertEqual(base["hunter_exp"], 0)
        self.assertEqual(base["agility_level"], 1)
        self.assertEqual(base["agility_exp"], 0)
        self.assertEqual(base["unlocked_abilities"], [])
        self.assertEqual(base["carried_inventory"], {})
        self.assertEqual(base["loot_value_threshold"], 10)

    def test_migration_normalizes_unlocked_abilities_and_legacy_fletching_target(self):
        data = {"current_fletch": "oak_arrow_shafts", "unlocked_abilities": ["broad_fletching", 42, "broad_fletching"]}
        out = migrate_loaded_data(data, ORE_DATA)
        self.assertEqual(out["current_fletch"], "arrow_shafts")
        self.assertEqual(out["unlocked_abilities"], ["broad_fletching"])

    def test_carried_state_keys_seeded_on_old_saves(self):
        # The pouch is dormant: coins stay in the flat inventory until the coin
        # readers are repointed. Only the overlay keys are seeded here.
        data = {"config_version": 1, "inventory": {"Coins": 1000, "Oak logs": 5}}
        out = migrate_loaded_data(data, ORE_DATA)
        self.assertEqual(out["carried_inventory"], {})
        self.assertEqual(out["inventory"]["Coins"], 1000)
        self.assertEqual(out["inventory"]["Oak logs"], 5)

    def test_legacy_ghostspeak_amulet_satisfies_nature_spirit(self):
        data = {
            "inventory": {"Amulet of ghostspeak": 1},
            "quests": {"nature_spirit": {"started": True, "progress": 3, "completed": False}},
        }
        out = migrate_loaded_data(data, ORE_DATA)
        self.assertNotIn("Amulet of ghostspeak", out["inventory"])
        self.assertNotIn(
            "Needs Ghostspeak amulet x1",
            quest_current_stage_blocker_reasons_pure(out, "nature_spirit", QUEST_DATA),
        )

    def test_saved_grain_loads_as_wheat_for_eadgars_ruse(self):
        data = {
            "inventory": {"Grain": 10},
            "carried_inventory": {"gather_grain": {"Grain": 3}},
            "quests": {"eadgars_ruse": {"started": True, "progress": 1, "completed": False}},
        }
        out = migrate_loaded_data(data, ORE_DATA)
        self.assertEqual(out["inventory"]["Wheat"], 10)
        self.assertNotIn("Grain", out["inventory"])
        self.assertEqual(out["carried_inventory"]["gather_grain"], {"Wheat": 3})
        self.assertNotIn(
            "Needs Wheat x10",
            quest_current_stage_blocker_reasons_pure(out, "eadgars_ruse", QUEST_DATA),
        )

    def test_saved_grain_offers_and_shop_row_pay_out_wheat(self):
        store = "lumbridge_general_store"
        grain_row = f"{store}:temporary:grain"
        data = {
            "inventory": {"Coins": 1000, "Grain": 2},
            "ge_player_orders": [
                {"id": 1, "side": "buy", "item_name": "Grain", "status": "partial", "original_quantity": 10,
                 "remaining_quantity": 6, "completed_quantity": 4, "submitted_unit_price": 18,
                 "escrow_coins": 108, "collectible_items": 4},
                {"id": 2, "side": "sell", "item_name": "Grain", "status": "partial", "original_quantity": 5,
                 "remaining_quantity": 3, "completed_quantity": 2, "submitted_unit_price": 20,
                 "escrow_items": 3, "collectible_coins": 40},
            ],
            "shop_stock_state": {store: {"shop_id": store, "last_market_tick": 0, "rows": {grain_row: {
                "item_name": "Grain", "current_quantity": 7, "buy_price": 3, "sell_price": 1, "temporary": True,
            }}}},
        }
        out = migrate_loaded_data(data, ORE_DATA)
        self.assertEqual([order["item_name"] for order in out["ge_player_orders"]], ["Wheat", "Wheat"])
        self.assertEqual(out["shop_stock_state"][store]["rows"][grain_row]["item_name"], "Wheat")

        for order_id in (1, 2):
            out, _ = collect_ge_offer_pure(out, order_id)
            out, _ = cancel_ge_offer_pure(out, order_id)
            out, _ = collect_ge_offer_pure(out, order_id)
        # Bank Grain, bought Grain and unsold Grain all arrive as Wheat; sale
        # proceeds and the unspent buy escrow arrive as coins.
        self.assertEqual(out["inventory"]["Wheat"], 2 + 4 + 3)
        self.assertEqual(out["inventory"]["Coins"], 1000 + 40 + 108)
        self.assertNotIn("Grain", out["inventory"])
        self.assertEqual(out["ge_player_orders"], [])

        out, _ = apply_shop_buy_pure(out, store, grain_row, 1)
        self.assertEqual(out["inventory"]["Wheat"], 10)
        out, _ = apply_shop_sell_pure(out, store, "Wheat", 2)
        self.assertEqual(
            {row_id: row["current_quantity"] for row_id, row in out["shop_stock_state"][store]["rows"].items()},
            {grain_row: 8},
        )


if __name__ == "__main__":
    unittest.main()
