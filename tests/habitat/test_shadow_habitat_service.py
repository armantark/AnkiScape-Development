"""Deliberate Papa Mambo purchases, atomic feature construction and inverse."""

import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS
from ankiscape.data.shop_data import SHOP_DATA, SHOP_SERVICES, SHOP_COVERAGE_SUMMARY
from ankiscape.logic.shop_logic import (
    preview_shop_service_pure, apply_shop_service_pure, rollback_shop_event_pure,
    search_shop_catalog_pure, apply_shop_buy_pure, preview_shop_buy_pure,
)
from ankiscape.logic.farming_logic import apply_shadow_setup_step_pure
from tests.habitat.fixtures import setup_state, PATCH
from tests.habitat.fixtures import CollectionFacade
from tests.test_storage_runtime import _load_storage_module

SERVICE = "papa_mambo_build_abandoned_house"
SEED_ROW = "papa_mambos_shop:0:19922"


class ShadowHabitatServiceTest(unittest.TestCase):
    def test_service_icon_resolves_to_existing_registered_red_seed_asset(self):
        name = SHOP_SERVICES[SERVICE]["icon_item_name"]
        definition = next(item for item in ITEM_DEFINITIONS if item.storage_key == name)
        self.assertTrue(definition.asset_path)
        self.assertTrue((Path(__file__).resolve().parents[2] / definition.asset_path).is_file())

    def test_exact_runtime_catalog_amendment_and_existing_shop_access(self):
        service = SHOP_SERVICES[SERVICE]
        expected = dict(
            id=SERVICE, display_name="Build Abandoned house", provider="Papa Mambo",
            location="Herblore Habitat", action_type="build_habitat_feature",
            feature_id="abandoned_house", currency_id=995, currency_name="Coins",
            currency_item_name="Coins", currency_implemented=True, price=57000,
            inputs=[], outputs=[], batchable=False, icon_item_name="Red blossom seed",
            visibility="visible", lock_reason="", access=SHOP_DATA["papa_mambos_shop"]["access"],
        )
        self.assertEqual({k: v for k, v in service.items() if k != "source"}, expected)
        self.assertIn("Construction oldid 5994924", service["source"])
        self.assertIn("official KB capture 20111030050144", service["source"])
        self.assertEqual(len(SHOP_SERVICES), 85)
        self.assertEqual(SHOP_COVERAGE_SUMMARY["service_count"], 85)
        seed = next(row for row in SHOP_DATA["papa_mambos_shop"]["stock"] if row["id"] == SEED_ROW)
        self.assertEqual((seed["buy_price"], seed["default_quantity"]), (50, 10))

    def test_search_finds_ordinary_service_by_feature_and_provider(self):
        for query in ("Abandoned house", "Papa Mambo"):
            results = search_shop_catalog_pure({"inventory": {}}, query)
            result = next(row for row in results["results"] if row.get("id") == SERVICE)
            self.assertEqual(result["kind"], "service")
            self.assertEqual(result["price"], 57000)
            self.assertEqual(result["visibility"], "visible")

    def test_preview_is_read_only_and_uses_ordinary_requirement_schema(self):
        data = {"inventory": {"Coins": 57000}, "construction_level": 1}
        before = copy.deepcopy(data)
        preview = preview_shop_service_pure(data, SERVICE)
        self.assertTrue(preview["allowed"])
        self.assertEqual(preview["quantity"], 1)
        self.assertEqual(preview["total_price"], 57000)
        self.assertEqual(preview["requirements"], [{"item_name": "Coins", "required_quantity": 57000, "owned_quantity": 57000, "shortfall": 0, "kind": "currency"}])
        self.assertEqual(data, before)

    def test_visibility_and_access_checks_are_not_bypassed(self):
        for change, reason in (({"visibility":
            "locked", "lock_reason": "Closed"}, "Closed"), ({"access": {"kind": "skill", "skill": "farming", "level": 99, "label": "Farming 99"}}, None)):
            spec = {**SHOP_SERVICES[SERVICE], **change}
            with patch.dict(SHOP_SERVICES, {SERVICE: spec}):
                result = preview_shop_service_pure({"inventory": {"Coins": 57000}}, SERVICE)
            self.assertFalse(result["allowed"])
            if reason:
                self.assertEqual(result["reason"], reason)

    def test_payment_succeeds_without_levels_flower_tools_or_item_outputs(self):
        data = {"inventory": {"Coins": 57000}, "construction_level": 1, "construction_exp": 13, "construction_actions_completed": 4, "habitat_feature": "boneyard"}
        before = copy.deepcopy(data)
        updated, result = apply_shop_service_pure(data, SERVICE)
        self.assertEqual(data, before)
        self.assertTrue(result["allowed"])
        self.assertEqual(updated["inventory"], {"Coins": 0})
        self.assertEqual(updated["habitat_feature"], "abandoned_house")
        self.assertEqual(updated["construction_exp"], 13)
        self.assertEqual(updated["construction_actions_completed"], 4)
        self.assertEqual(updated["shop_stock_state"], {})
        self.assertNotIn("farm_patches", updated)
        event = updated["shop_events"][-1]
        self.assertEqual(event["inventory_delta"], {"Coins": -57000})
        self.assertEqual(event["inverse"]["habitat_feature_before"], "boneyard")
        self.assertEqual(event["habitat_feature_after"], "abandoned_house")
        self.assertEqual(event["stock_delta"], {})
        self.assertEqual(event["service_id"], SERVICE)
        self.assertEqual(event["action_type"], "build_habitat_feature")

    def test_insufficient_coins_duplicate_and_quantity_refuse_without_debit_or_event(self):
        for data, quantity, reason in (
            ({"inventory": {"Coins": 56999}}, 1, "missing_requirements"),
            ({"inventory": {"Coins": 114000}}, 2, "Choose quantity 1 for construction."),
            ({"inventory": {"Coins": 57000}, "habitat_feature": "abandoned_house"}, 1, "The Abandoned house is already built."),
        ):
            before = copy.deepcopy(data)
            updated, result = apply_shop_service_pure(data, SERVICE, quantity)
            self.assertFalse(result["allowed"])
            self.assertEqual(result["reason"], reason)
            self.assertEqual(data, before)
            self.assertEqual(updated["inventory"], before["inventory"])
            self.assertEqual(updated.get("habitat_feature"), before.get("habitat_feature"))
            self.assertEqual(updated["shop_events"], [])

    def test_inverse_restores_fee_and_previous_feature_after_json_and_actual_storage_reload(self):
        for feature in (None, "boneyard"):
            data = {"inventory": {"Coins": 57000}, "habitat_feature": feature}
            built, result = apply_shop_service_pure(data, SERVICE)
            collection = CollectionFacade()
            storage = _load_storage_module(collection)
            storage.save_player_data(json.loads(json.dumps(built)), "Hunter")
            loaded, _ = storage.load_player_data()
            self.assertEqual(loaded["habitat_feature"], "abandoned_house")
            self.assertEqual(loaded["shop_events"][-1]["inverse"]["habitat_feature_before"], feature)
            restored, result = rollback_shop_event_pure(loaded, result["event_id"])
            self.assertTrue(result["allowed"])
            self.assertEqual(restored["inventory"]["Coins"], 57000)
            self.assertEqual(restored["habitat_feature"], feature)
            self.assertEqual(restored["shop_stock_state"], {})

    def test_construction_quantity_requires_exact_integer_one(self):
        data = {"inventory": {"Coins": 114000}}
        for quantity in (True, False, 1.0, "1", 0, -1, 2, None):
            before = copy.deepcopy(data)
            preview = preview_shop_service_pure(data, SERVICE, quantity)
            updated, result = apply_shop_service_pure(data, SERVICE, quantity)
            self.assertFalse(preview["allowed"])
            self.assertFalse(result["allowed"])
            self.assertEqual(updated["inventory"], before["inventory"])
            self.assertIsNone(updated.get("habitat_feature"))
            self.assertEqual(updated["shop_events"], [])
            self.assertEqual(data, before)

    def test_feature_inverse_only_applies_to_this_service_and_action_payload(self):
        built, _ = apply_shop_service_pure({"inventory": {"Coins": 57000}}, SERVICE)
        for field, wrong in (("service_id", "other_service"), ("action_type", "other_action"), ("type", "buy"), ("habitat_feature_after", "other_feature")):
            data = copy.deepcopy(built)
            data["shop_events"][-1][field] = wrong
            restored, result = rollback_shop_event_pure(data)
            self.assertTrue(result["allowed"])
            self.assertEqual(restored["habitat_feature"], "abandoned_house")
        data = copy.deepcopy(built)
        del data["shop_events"][-1]["inverse"]["habitat_feature_before"]
        restored, result = rollback_shop_event_pure(data)
        self.assertTrue(result["allowed"])
        self.assertEqual(restored["habitat_feature"], "abandoned_house")

    def test_owned_coins_and_stock_never_automatically_buy_seed_or_construction(self):
        for construction, seeds in ((56, 1), (57, 0)):
            data = setup_state()
            data["construction_level"] = construction
            data["inventory"]["Red blossom seed"] = seeds
            before = copy.deepcopy(data)
            with patch("ankiscape.logic.shop_logic.apply_shop_buy_pure", side_effect=AssertionError("automatic shop purchase")), patch("ankiscape.logic.shop_logic.apply_shop_service_pure", side_effect=AssertionError("automatic construction fee")):
                updated, info = apply_shadow_setup_step_pure(data, lambda: 1)
            self.assertEqual(info["status"], "blocked")
            self.assertEqual(updated, before)

    def test_manual_seed_purchase_uses_existing_admission_price_and_stock(self):
        data = setup_state()
        data["inventory"]["Red blossom seed"] = 0
        data["habitat_feature"] = "abandoned_house"
        preview = preview_shop_buy_pure(data, "papa_mambos_shop", SEED_ROW, 1)
        self.assertTrue(preview["allowed"])
        self.assertEqual(preview["total_price"], 50)
        bought, result = apply_shop_buy_pure(data, "papa_mambos_shop", SEED_ROW, 1)
        self.assertTrue(result["allowed"])
        self.assertEqual(bought["inventory"]["Coins"], data["inventory"]["Coins"] - 50)
        self.assertEqual(bought["inventory"]["Red blossom seed"], 1)
        self.assertEqual(bought["shop_events"][-1]["stock_delta"]["papa_mambos_shop"][SEED_ROW]["after"]["current_quantity"], 9)
        planted, info = apply_shadow_setup_step_pure(bought, lambda: 1)
        self.assertEqual(info["verb"], "plant")
        self.assertEqual(planted["inventory"]["Red blossom seed"], 0)
        self.assertEqual(planted["shop_stock_state"], bought["shop_stock_state"])
        self.assertEqual(planted["shop_events"], bought["shop_events"])
