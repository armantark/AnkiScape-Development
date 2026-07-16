import unittest

from shop_data import SHOP_DATA
from shop_fixtures import build_shop_fixture_player_data, build_shop_frontend_fixtures
from shop_logic import (
    DECANTABLE_FOUR_DOSE_POTION_BASES,
    advance_shop_market_clock_pure,
    apply_shop_buy_pure,
    apply_shop_sell_pure,
    apply_shop_service_pure,
    apply_shop_transaction_pure,
    apply_shop_vendor_action_pure,
    default_shop_state_pure,
    preview_shop_buy_pure,
    preview_shop_sell_pure,
    preview_shop_service_pure,
    preview_shop_vendor_action_pure,
    rollback_shop_event_pure,
    sanitize_shop_state_pure,
    search_shop_catalog_pure,
    shop_history_rows_pure,
    shop_view_model_pure,
)


def _live_shop_and_row():
    for shop in SHOP_DATA.values():
        for row in shop["stock"]:
            if shop["visibility"] == "visible" and row["disposition"] == "live":
                return shop, row
    raise AssertionError("no live stock row")


def _locked_shop_and_row():
    for shop in SHOP_DATA.values():
        for row in shop["stock"]:
            if row["visibility"] == "visible_locked":
                return shop, row
    raise AssertionError("no locked stock row")


def _general_store():
    for shop in SHOP_DATA.values():
        if shop["visibility"] == "visible" and shop["general_store"]:
            return shop
    raise AssertionError("no visible general store")


def _specialist_without_beer():
    for shop in SHOP_DATA.values():
        if shop["visibility"] == "visible" and not shop["general_store"] and all(row["item_name"] != "Beer" for row in shop["stock"]):
            return shop
    raise AssertionError("no visible specialist shop without beer")


class TestShopLogic(unittest.TestCase):
    def test_default_and_sanitize_shop_state(self):
        default_state = default_shop_state_pure()
        self.assertEqual(default_state["shop_data_version"], 1)
        self.assertEqual(default_state["shop_market_clock"]["market_tick"], 0)

        sanitized = sanitize_shop_state_pure(
            {
                "shop_market_clock": {"answered_cards": "4", "market_tick": "7"},
                "shop_stock_state": {"bad": {"rows": {"row": {"current_quantity": "-10"}}}},
                "shop_events": [{"event_id": "shop_evt_1"}],
                "shop_next_event_id": "3",
            }
        )
        self.assertEqual(sanitized["shop_market_clock"]["answered_cards"], 4)
        self.assertEqual(sanitized["shop_market_clock"]["market_tick"], 7)
        self.assertEqual(sanitized["shop_next_event_id"], 3)

    def test_saved_lantern_shop_rows_and_undo_events_migrate_exact_item_names(self):
        row_id = "miltogs_lamps:4:5014"
        saved = {
            "inventory": {"Coins": 900, "Mining helmet (unlit)": 1},
            "shop_market_clock": {"answered_cards": 0, "market_tick": 0},
            "shop_stock_state": {
                "miltogs_lamps": {
                    "shop_id": "miltogs_lamps",
                    "last_market_tick": 0,
                    "rows": {
                        row_id: {
                            "item_id": 5014,
                            "item_name": "Mining helmet",
                            "current_quantity": 9,
                            "default_quantity": 10,
                            "restock_ticks": 50,
                            "restock_amount": 1,
                            "buy_price": 900,
                            "sell_price": 270,
                            "tradeable": True,
                            "temporary": False,
                        }
                    },
                }
            },
            "shop_events": [
                {
                    "event_id": "shop_evt_1",
                    "type": "buy",
                    "shop_id": "miltogs_lamps",
                    "row_id": row_id,
                    "item_name": "Mining helmet",
                    "inventory_delta": {"Coins": -900, "Mining helmet": 1},
                    "inverse": {
                        "inventory_delta": {"Coins": 900, "Mining helmet": -1},
                        "stock_set": {
                            "miltogs_lamps": {
                                row_id: {
                                    "item_id": 5014,
                                    "item_name": "Mining helmet",
                                    "current_quantity": 10,
                                    "default_quantity": 10,
                                    "temporary": False,
                                }
                            }
                        },
                    },
                    "display": "Bought 1 x Mining helmet from Miltog's Lamps",
                }
            ],
            "shop_next_event_id": 2,
        }

        sanitized = sanitize_shop_state_pure(saved)
        self.assertEqual(
            sanitized["shop_stock_state"]["miltogs_lamps"]["rows"][row_id]["item_name"],
            "Mining helmet (unlit)",
        )
        event = sanitized["shop_events"][0]
        self.assertEqual(event["item_name"], "Mining helmet (unlit)")
        self.assertEqual(event["inverse"]["inventory_delta"]["Mining helmet (unlit)"], -1)
        self.assertEqual(
            event["inverse"]["stock_set"]["miltogs_lamps"][row_id]["item_name"],
            "Mining helmet (unlit)",
        )

        restored, result = rollback_shop_event_pure({**saved, **sanitized}, "shop_evt_1")
        self.assertTrue(result["allowed"])
        self.assertEqual(restored["inventory"]["Mining helmet (unlit)"], 0)

    def test_market_clock_advances_on_answered_cards(self):
        data = build_shop_fixture_player_data()
        advanced = advance_shop_market_clock_pure(data, answered_cards=10)
        self.assertEqual(advanced["shop_market_clock"]["answered_cards"], 10)
        self.assertEqual(advanced["shop_market_clock"]["market_tick"], 10)
        self.assertEqual(data["shop_market_clock"]["market_tick"], 0)

    def test_buy_live_stock_records_event_and_rollback_restores_state(self):
        shop, row = _live_shop_and_row()
        data = build_shop_fixture_player_data()
        before_stock = row["default_quantity"]

        updated, result = apply_shop_buy_pure(data, shop["id"], row["id"], 2)
        self.assertTrue(result["allowed"])
        self.assertEqual(result["quantity"], min(2, before_stock))
        self.assertEqual(updated["inventory"][row["item_name"]], data["inventory"].get(row["item_name"], 0) + result["quantity"])
        self.assertEqual(updated["inventory"]["Coins"], data["inventory"]["Coins"] - result["total_price"])
        view = shop_view_model_pure(updated, shop["id"])
        bought_row = next(view_row for view_row in view["rows"] if view_row["id"] == row["id"])
        self.assertEqual(bought_row["current_quantity"], before_stock - result["quantity"])

        rolled_back, rollback_result = rollback_shop_event_pure(updated, result["event_id"])
        self.assertTrue(rollback_result["allowed"])
        self.assertEqual(rolled_back["inventory"]["Coins"], data["inventory"]["Coins"])
        self.assertEqual(rolled_back["inventory"].get(row["item_name"], 0), data["inventory"].get(row["item_name"], 0))
        rolled_back_view = shop_view_model_pure(rolled_back, shop["id"])
        restored_row = next(view_row for view_row in rolled_back_view["rows"] if view_row["id"] == row["id"])
        self.assertEqual(restored_row["current_quantity"], before_stock)

    def test_locked_stock_fails_closed(self):
        shop, row = _locked_shop_and_row()
        data = build_shop_fixture_player_data()
        preview = preview_shop_buy_pure(data, shop["id"], row["id"], 1)
        self.assertFalse(preview["allowed"])
        self.assertEqual(preview["reason"], "currency_not_implemented")

    def test_previews_include_current_player_state_counts(self):
        shop, row = _live_shop_and_row()
        data = build_shop_fixture_player_data()
        data["inventory"]["Coins"] = 0

        buy_preview = preview_shop_buy_pure(data, shop["id"], row["id"], 1)
        self.assertFalse(buy_preview["allowed"])
        self.assertEqual(buy_preview["reason"], "insufficient_currency")
        self.assertEqual(buy_preview["currency_owned"], 0)
        self.assertEqual(buy_preview["required_currency"], row["buy_price"])
        self.assertEqual(buy_preview["currency_item_name"], "Coins")

        sell_shop = _general_store()
        sell_preview = preview_shop_sell_pure(data, sell_shop["id"], "Beer", 1)
        self.assertTrue(sell_preview["allowed"])
        self.assertEqual(sell_preview["owned_quantity"], data["inventory"]["Beer"])

        data["inventory"]["Beer glass"] = 0
        vendor_preview = preview_shop_vendor_action_pure(data, "bartender_sell_beer_glass", 1)
        self.assertFalse(vendor_preview["allowed"])
        self.assertEqual(vendor_preview["reason"], "missing_requirements")
        self.assertIn(
            {"item_name": "Beer glass", "required_quantity": 1, "owned_quantity": 0, "shortfall": 1, "kind": "item"},
            vendor_preview["missing_requirements"],
        )

    def test_restock_uses_market_tick_for_touched_shop(self):
        shop, row = _live_shop_and_row()
        data = build_shop_fixture_player_data()
        updated, result = apply_shop_buy_pure(data, shop["id"], row["id"], 2)
        self.assertTrue(result["allowed"])
        advanced = advance_shop_market_clock_pure(updated, answered_cards=row["restock_ticks"])
        view = shop_view_model_pure(advanced, shop["id"])
        restocked_row = next(view_row for view_row in view["rows"] if view_row["id"] == row["id"])
        self.assertGreaterEqual(restocked_row["current_quantity"], row["default_quantity"] - result["quantity"] + 1)

    def test_general_store_accepts_tradeable_player_sold_temp_stock(self):
        shop = _general_store()
        data = build_shop_fixture_player_data()
        updated, result = apply_shop_sell_pure(data, shop["id"], "Beer", 1)
        self.assertTrue(result["allowed"])
        self.assertTrue(result["temporary_stock"])
        self.assertEqual(updated["inventory"]["Beer"], data["inventory"]["Beer"] - 1)
        self.assertEqual(updated["inventory"]["Coins"], data["inventory"]["Coins"] + result["total_price"])
        view = shop_view_model_pure(updated, shop["id"])
        self.assertTrue(any(row["item_name"] == "Beer" and row["current_quantity"] == 1 for row in view["rows"]))

    def test_specialist_shop_rejects_non_stock_sells(self):
        shop = _specialist_without_beer()
        data = build_shop_fixture_player_data()
        preview = preview_shop_sell_pure(data, shop["id"], "Beer", 1)
        self.assertFalse(preview["allowed"])
        self.assertEqual(preview["reason"], "specialist_shop_stock_only")

    def test_services_vendor_actions_and_generic_transaction_wrapper(self):
        data = build_shop_fixture_player_data()
        service_preview = preview_shop_service_pure(data, "al_kharid_tanner_soft_leather", 1)
        self.assertFalse(service_preview["allowed"])
        self.assertEqual(service_preview["reason"], "unknown_service")

        after_news, news_result = apply_shop_vendor_action_pure(data, "benny_buy_varrock_herald", 1)
        self.assertTrue(news_result["allowed"])
        self.assertEqual(after_news["inventory"]["Newspaper"], 1)

        after_beer, beer_result = apply_shop_transaction_pure(after_news, "vendor_action", action_id="bartender_buy_beer", quantity=1)
        self.assertTrue(beer_result["allowed"])
        self.assertEqual(after_beer["inventory"]["Beer"], after_news["inventory"]["Beer"] + 1)

    def test_bob_barter_decants_every_inventory_family_to_four_doses(self):
        data = build_shop_fixture_player_data()
        data["inventory"].update(
            {
                "Agility potion (1)": 4,
                "Agility potion (3)": 4,
                "Attack potion (2)": 2,
            }
        )
        before_clock = dict(data["shop_market_clock"])
        before_coins = data["inventory"]["Coins"]

        preview = preview_shop_service_pure(data, "bob_barter_decant_four", 4)
        self.assertTrue(preview["allowed"])
        self.assertEqual(preview["quantity"], 1)
        self.assertFalse(preview["clamped"])
        self.assertEqual(preview["target_dose"], 4)
        self.assertEqual(preview["decanted_families"], ["Agility potion", "Attack potion"])
        self.assertEqual(preview["total_doses"], 20)
        self.assertEqual(preview["returned_vials"], 5)

        updated, result = apply_shop_service_pure(data, "bob_barter_decant_four", 4)
        self.assertTrue(result["allowed"])
        self.assertEqual(updated["inventory"]["Agility potion (1)"], 0)
        self.assertEqual(updated["inventory"]["Agility potion (3)"], 0)
        self.assertEqual(updated["inventory"]["Agility potion (4)"], 4)
        self.assertEqual(updated["inventory"]["Attack potion (2)"], 0)
        self.assertEqual(updated["inventory"]["Attack potion (4)"], 1)
        self.assertEqual(updated["inventory"]["Vial"], 5)
        self.assertEqual(updated["inventory"]["Coins"], before_coins)
        self.assertEqual(updated["shop_market_clock"], before_clock)

    def test_bob_barter_preserves_doses_and_rolls_back_independently(self):
        data = build_shop_fixture_player_data()
        data["inventory"].update(
            {
                "Prayer potion (1)": 1,
                "Prayer potion (2)": 2,
                "Prayer potion (3)": 1,
                "Prayer potion (4)": 1,
                "Vial": 2,
            }
        )
        before = dict(data["inventory"])
        before_doses = sum(dose * before[f"Prayer potion ({dose})"] for dose in range(1, 5))

        updated, result = apply_shop_service_pure(data, "bob_barter_decant_four", 4)
        after_doses = sum(
            dose * updated["inventory"].get(f"Prayer potion ({dose})", 0)
            for dose in range(1, 5)
        )
        self.assertEqual(after_doses, before_doses)
        self.assertEqual(updated["inventory"]["Prayer potion (4)"], 3)
        self.assertEqual(updated["inventory"]["Vial"], 4)

        restored, undo = rollback_shop_event_pure(updated, result["event_id"])
        self.assertTrue(undo["allowed"])
        for item_name, quantity in before.items():
            self.assertEqual(restored["inventory"].get(item_name, 0), quantity)

    def test_bob_barter_decants_to_two_doses_and_preserves_partial_remainder(self):
        data = build_shop_fixture_player_data()
        data["inventory"].update(
            {
                "Prayer potion (3)": 1,
                "Prayer potion (4)": 1,
                "Vial": 2,
            }
        )

        preview = preview_shop_service_pure(data, "bob_barter_decant_four", 2)
        self.assertTrue(preview["allowed"])
        self.assertEqual(preview["target_dose"], 2)
        self.assertEqual(preview["total_doses"], 7)
        self.assertEqual(preview["required_vials"], 2)

        updated, result = apply_shop_service_pure(data, "bob_barter_decant_four", 2)
        self.assertTrue(result["allowed"])
        self.assertEqual(updated["inventory"]["Prayer potion (1)"], 1)
        self.assertEqual(updated["inventory"]["Prayer potion (2)"], 3)
        self.assertEqual(updated["inventory"]["Prayer potion (3)"], 0)
        self.assertEqual(updated["inventory"]["Prayer potion (4)"], 0)
        self.assertEqual(updated["inventory"]["Vial"], 0)

    def test_bob_barter_requires_vials_for_smaller_doses_and_rejects_one_dose(self):
        data = build_shop_fixture_player_data()
        data["inventory"]["Prayer potion (4)"] = 2
        preview = preview_shop_service_pure(data, "bob_barter_decant_four", 3)
        self.assertFalse(preview["allowed"])
        self.assertEqual(preview["reason"], "missing_decant_vials")
        self.assertEqual(preview["required_vials"], 1)

        one_dose = preview_shop_service_pure(data, "bob_barter_decant_four", 1)
        self.assertFalse(one_dose["allowed"])
        self.assertEqual(one_dose["reason"], "unsupported_decant_dose")

    def test_bob_barter_rejects_inventory_that_needs_no_consolidation(self):
        self.assertIn("Agility potion", DECANTABLE_FOUR_DOSE_POTION_BASES)
        data = build_shop_fixture_player_data()
        data["inventory"].update({"Agility potion (3)": 1, "Attack potion (4)": 3})
        preview = preview_shop_service_pure(data, "bob_barter_decant_four", 4)
        self.assertFalse(preview["allowed"])
        self.assertEqual(preview["reason"], "no_potions_to_decant")

    def test_shop_access_gates_evaluate_against_the_save(self):
        # Owner-grilled hybrid gating: quest walls lock buys/sells with a
        # human-readable reason and open when the save satisfies the rule;
        # every gated quest id must exist in the catalog.
        from shop_data import SHOP_DATA
        from quest_data import QUESTS_BY_ID
        from shop_logic import shop_access_lock_reason_pure

        for shop in SHOP_DATA.values():
            rule = shop.get("access")
            if rule and rule.get("kind") == "quest":
                self.assertIn(rule["quest_id"], QUESTS_BY_ID, shop["id"])

        data = build_shop_fixture_player_data()
        view = shop_view_model_pure(data, "zanaris_general_store")
        self.assertEqual(view["lock_reason"], "Requires Lost City")
        self.assertFalse(any(row["can_buy"] for row in view["rows"]))
        preview = preview_shop_buy_pure(data, "zanaris_general_store", view["rows"][0]["id"], 1)
        self.assertFalse(preview["allowed"])
        self.assertEqual(preview["reason"], "Requires Lost City")

        data["quests"] = {"lost_city": {"started": True, "progress": 6, "completed": True}}
        unlocked = shop_view_model_pure(data, "zanaris_general_store")
        self.assertEqual(unlocked["lock_reason"], "")
        self.assertTrue(any(row["can_buy"] for row in unlocked["rows"]))

        # Guild skill wall and started-stage wall.
        low = build_shop_fixture_player_data()
        self.assertEqual(
            shop_access_lock_reason_pure(low, SHOP_DATA["fishing_guild_shop"]),
            "Requires 68 Fishing",
        )
        low["fishing_level"] = 68
        self.assertIsNone(shop_access_lock_reason_pure(low, SHOP_DATA["fishing_guild_shop"]))
        self.assertEqual(
            shop_access_lock_reason_pure(low, SHOP_DATA["keldagrim_stonemason"]),
            "Requires starting The Giant Dwarf",
        )
        # Wilderness shops stay access-open; the flag drives the ambush risk.
        wild = shop_view_model_pure(low, "mage_arena_staves")
        self.assertTrue(wild["wilderness"])
        self.assertEqual(wild["lock_reason"], "")

    def test_wilderness_ambush_slots_trigger_damage_and_rollback(self):
        # Owner-declared mechanic: every completed 28 purchase-slot block from
        # a Wilderness shop rolls 1% for a PKer-style hit (1..249 lifepoints,
        # can kill via the normal grave path). Stackables occupy one slot per
        # purchase; unstackables one per item. Rollback restores everything.
        from shop_data import SHOP_DATA

        shop = SHOP_DATA["william_team_cape_shop"]
        rows = [r for r in shop["stock"] if r["disposition"] == "live"]
        data = build_shop_fixture_player_data()
        data["combat_lifepoints"] = 100
        data["equipment"] = {"weapon": "Bronze sword"}

        safe = lambda: 0.5
        data, first = apply_shop_buy_pure(data, shop["id"], rows[0]["id"], 10, rng=safe)
        self.assertEqual(first["wilderness_ambush"], {"slots": 10, "slots_before": 0, "triggered": False})
        data, _second = apply_shop_buy_pure(data, shop["id"], rows[1]["id"], 10, rng=safe)

        deadly = iter([0.005, 0.9])
        data, third = apply_shop_buy_pure(data, shop["id"], rows[2]["id"], 10, rng=lambda: next(deadly))
        ambush = third["wilderness_ambush"]
        self.assertTrue(ambush["triggered"])
        self.assertTrue(ambush["died"])
        self.assertEqual(ambush["damage"], 1 + int(0.9 * 249))
        self.assertEqual(data["combat_grave"]["source"], "wilderness_shop_ambush")
        self.assertEqual(data["combat_grave"]["items"], ["Bronze sword"])
        self.assertEqual(data["equipment"], {})

        back, rollback = rollback_shop_event_pure(data, third["event_id"])
        self.assertTrue(rollback["allowed"])
        self.assertEqual(back["combat_lifepoints"], 100)
        self.assertEqual(back["wilderness_shop_slots"], 20)
        self.assertNotIn("combat_grave", back)
        self.assertEqual(back["equipment"], {"weapon": "Bronze sword"})

    def test_wilderness_stackables_occupy_one_slot_per_purchase(self):
        from shop_data import SHOP_DATA

        shop = SHOP_DATA["lundails_arena_rune_shop"]
        row = next(r for r in shop["stock"] if r["disposition"] == "live" and r["stackable"])
        data = build_shop_fixture_player_data()
        data, result = apply_shop_buy_pure(data, shop["id"], row["id"], 50, rng=lambda: 0.5)
        self.assertEqual(result["wilderness_ambush"]["slots"], 1)
        self.assertEqual(data["wilderness_shop_slots"], 1)
        # Non-wilderness purchases never touch the accumulator.
        open_shop, open_row = _live_shop_and_row()
        data, open_result = apply_shop_buy_pure(data, open_shop["id"], open_row["id"], 2)
        self.assertNotIn("wilderness_ambush", open_result)
        self.assertEqual(data["wilderness_shop_slots"], 1)

    def test_vendor_actions_are_one_per_interaction(self):
        # Dialogue parity: Karim hands over exactly one kebab per
        # conversation; requested bulk quantities clamp to a single use.
        data = build_shop_fixture_player_data()
        preview = preview_shop_vendor_action_pure(data, "karim_buy_kebab", 50)
        self.assertTrue(preview["allowed"])
        self.assertEqual(preview["quantity"], 1)
        updated, result = apply_shop_vendor_action_pure(data, "karim_buy_kebab", 50)
        self.assertTrue(result["allowed"])
        self.assertEqual(result["quantity"], 1)
        self.assertEqual(updated["inventory"].get("Kebab", 0), data["inventory"].get("Kebab", 0) + 1)
        self.assertEqual(updated["inventory"]["Coins"], data["inventory"]["Coins"] - 1)

    def test_search_history_and_fixture_bundle(self):
        data = build_shop_fixture_player_data()
        search = search_shop_catalog_pure(data, "Feather", include_locked=True, limit=10)
        self.assertGreaterEqual(len(search["results"]), 1)
        fixtures = build_shop_frontend_fixtures()
        for key in (
            "normal_coin_stock_shop",
            "feather_multi_shop_search",
            "locked_read_only_shop",
            "player_sold_stock",
            "vendor_action_transaction",
            "history",
        ):
            self.assertIn(key, fixtures)
        self.assertTrue(fixtures["player_sold_stock"]["result"]["allowed"])
        self.assertGreaterEqual(len(fixtures["history"]), 3)

        shop, row = _live_shop_and_row()
        updated, result = apply_shop_buy_pure(data, shop["id"], row["id"], 1)
        self.assertTrue(result["allowed"])
        history = shop_history_rows_pure(updated, shop["id"])
        self.assertEqual(history[0]["type"], "buy")

    def test_primary_skill_outputs_sell_at_general_stores(self):
        # Coin-loop guarantee: representative gathered/crafted/combat outputs
        # must resolve a Shop.java sell price even when no shop stocks them
        # (SHOP_PLAYER_SELL_PRICES fallback), so income is never fail-closed.
        outputs = (
            "Logs", "Oak logs", "Willow logs", "Maple logs", "Yew logs",
            "Iron ore", "Coal", "Gold ore", "Mithril ore",
            "Bronze bar", "Iron bar", "Steel bar", "Silver bar",
            "Raw shrimps", "Raw trout", "Raw lobster", "Raw swordfish",
            "Uncut sapphire", "Uncut emerald", "Uncut ruby",
            "Bones", "Big bones", "Cowhide", "Leather", "Hard leather",
            "Wool", "Ball of wool", "Flax", "Bow string",
            "Grey wolf fur", "Feather", "Arrow shaft", "Sapphire ring",
        )
        general = _general_store()
        data = build_shop_fixture_player_data()
        for item_name in outputs:
            data["inventory"][item_name] = 5
            preview = preview_shop_sell_pure(data, general["id"], item_name, 1)
            self.assertTrue(preview["allowed"], f"{item_name}: {preview.get('reason')}")
            self.assertGreaterEqual(int(preview["unit_price"]), 1, item_name)

    def test_sell_price_is_uniform_across_shop_types(self):
        # Darkan getSellPrice depends only on the item: the same Swordfish
        # pays the same at a shop that stocks it and at a general store.
        from shop_data import SHOP_PLAYER_SELL_PRICES

        stocking_shop = next(
            shop for shop in SHOP_DATA.values()
            if shop["visibility"] == "visible"
            and any(r["item_name"] == "Swordfish" and r["disposition"] == "live" for r in shop["stock"])
        )
        general = _general_store()
        data = build_shop_fixture_player_data()
        data["inventory"]["Swordfish"] = 2
        at_stocking = preview_shop_sell_pure(data, stocking_shop["id"], "Swordfish", 1)
        at_general = preview_shop_sell_pure(data, general["id"], "Swordfish", 1)
        self.assertTrue(at_stocking["allowed"] and at_general["allowed"])
        self.assertEqual(at_stocking["unit_price"], SHOP_PLAYER_SELL_PRICES["Swordfish"])
        self.assertEqual(at_general["unit_price"], SHOP_PLAYER_SELL_PRICES["Swordfish"])

    def test_selling_the_currency_item_is_refused(self):
        general = _general_store()
        data = build_shop_fixture_player_data()
        preview = preview_shop_sell_pure(data, general["id"], "Coins", 1)
        self.assertFalse(preview["allowed"])
        self.assertEqual(preview["reason"], "currency_item")

    def test_general_store_refuses_new_items_when_slot_pool_is_full(self):
        # Shop.java: general stock holds MAX_SHOP_ITEMS(40) - main stock
        # slots; a sale needing a new slot fails when the pool is full.
        general = _general_store()
        capacity = max(0, 40 - len(general["stock"]))
        data = build_shop_fixture_player_data()
        group = data["shop_stock_state"].setdefault(general["shared_stock_group"], {"rows": {}})
        for index in range(capacity):
            group["rows"][f"{general['id']}:temporary:filler_{index}"] = {
                "item_name": f"Filler {index}",
                "current_quantity": 1,
                "default_quantity": 0,
                "temporary": True,
            }
        data["inventory"]["Swordfish"] = 1
        preview = preview_shop_sell_pure(data, general["id"], "Swordfish", 1)
        self.assertFalse(preview["allowed"])
        self.assertEqual(preview["reason"], "shop_full")
        # An item with an existing slot still sells into it.
        data["inventory"]["Beer"] = 2
        group["rows"][f"{general['id']}:temporary:beer"] = {
            "item_name": "Beer",
            "current_quantity": 1,
            "default_quantity": 0,
            "temporary": True,
        }
        still_allowed = preview_shop_sell_pure(data, general["id"], "Beer", 1)
        self.assertTrue(still_allowed["allowed"], still_allowed.get("reason"))

    def test_selling_into_main_stock_decays_toward_default_not_zero(self):
        # Selling an item its shop stocks raises that row above default;
        # restock then decays it back toward the default (ShopItem.capStock),
        # and the row is never flagged temporary.
        shop = next(
            s for s in SHOP_DATA.values()
            if s["visibility"] == "visible" and not s["buy_only"]
            and any(r["item_name"] == "Feather" and r["disposition"] == "live" for r in s["stock"])
        )
        row = next(r for r in shop["stock"] if r["item_name"] == "Feather")
        data = build_shop_fixture_player_data()
        data["inventory"]["Feather"] = 5
        data, result = apply_shop_sell_pure(data, shop["id"], "Feather", 5)
        self.assertTrue(result["allowed"], result.get("reason"))
        view = shop_view_model_pure(data, shop["id"])
        sold_row = next(v for v in view["rows"] if v["id"] == row["id"])
        self.assertEqual(sold_row["current_quantity"], row["default_quantity"] + 5)
        advanced = advance_shop_market_clock_pure(data, answered_cards=row["restock_ticks"])
        decayed = next(v for v in shop_view_model_pure(advanced, shop["id"])["rows"] if v["id"] == row["id"])
        self.assertEqual(decayed["current_quantity"], row["default_quantity"] + 4)

    def test_player_sold_stock_buys_back_at_darkan_buy_price(self):
        from shop_data import SHOP_PLAYER_BUY_PRICES

        general = _general_store()
        data = build_shop_fixture_player_data()
        data, result = apply_shop_sell_pure(data, general["id"], "Beer", 1)
        self.assertTrue(result["allowed"])
        view = shop_view_model_pure(data, general["id"])
        beer_row = next(v for v in view["rows"] if v["item_name"] == "Beer" and v["current_quantity"] == 1)
        self.assertEqual(beer_row["buy_price"], SHOP_PLAYER_BUY_PRICES["Beer"])

    def test_gather_sell_buy_coin_loop_end_to_end(self):
        # A coinless player sells gathered goods to a general store, then
        # spends the proceeds on shop stock; both legs record history events.
        general = _general_store()
        feather_shop = next(
            shop for shop in SHOP_DATA.values()
            if shop["visibility"] == "visible"
            and any(r["item_name"] == "Feather" and r["disposition"] == "live" for r in shop["stock"])
        )
        feather_row = next(r for r in feather_shop["stock"] if r["item_name"] == "Feather")

        data = build_shop_fixture_player_data()
        data["inventory"]["Coins"] = 0
        data["inventory"]["Oak logs"] = 20

        sell_preview = preview_shop_sell_pure(data, general["id"], "Oak logs", 20)
        self.assertTrue(sell_preview["allowed"], sell_preview.get("reason"))
        data, sell_result = apply_shop_sell_pure(data, general["id"], "Oak logs", 20)
        self.assertTrue(sell_result["allowed"])
        earned = int(sell_result["total_price"])
        self.assertGreater(earned, 0)
        self.assertEqual(data["inventory"]["Coins"], earned)
        self.assertEqual(data["inventory"]["Oak logs"], 0)

        unit = int(feather_row["buy_price"])
        affordable = max(1, min(5, earned // unit))
        data, buy_result = apply_shop_buy_pure(data, feather_shop["id"], feather_row["id"], affordable)
        self.assertTrue(buy_result["allowed"], buy_result.get("reason"))
        self.assertEqual(data["inventory"].get("Feather", 0), int(buy_result["quantity"]))
        self.assertEqual(
            data["inventory"]["Coins"],
            earned - int(buy_result["total_price"]),
        )
        types = [event["type"] for event in shop_history_rows_pure(data, limit=4)]
        self.assertIn("sell", types)
        self.assertIn("buy", types)


if __name__ == "__main__":
    unittest.main()
