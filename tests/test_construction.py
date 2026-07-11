import os
import json
import unittest

from constants import ITEM_DEFINITIONS, ORE_DATA, UTILITY_ACTIVITY_DATA
from construction_data import (
    CONSTRUCTION_BUILD_TARGETS, CONSTRUCTION_DATA, DEFAULT_CONSTRUCTION_TARGET,
    FLATPACK_TARGETS, HOUSE_STYLE_DATA, NAIL_DATA, ROOM_DATA, SERVANT_DATA,
    TABLET_TARGETS, WORKBENCH_TIERS,
)
from logic_pure import (
    apply_construction_action_pure, construction_target_locked_reasons_pure,
    owned_gilded_altar_burner_count_pure, purchase_house_option_pure,
    purchase_house_pure,
)
from runtime_actions import RuntimeActionContext, answer_handler_for_key, handle_construction_answer, handle_prayer_answer
from shop_data import SHOP_PLAYER_BUY_PRICES
from storage_pure import CURRENT_CONFIG_VERSION, migrate_loaded_data
from target_metadata import construction_target_rows
from tools.fetch_construction_assets import asset_manifest


def _house(**updates):
    data = {
        "construction_level": 99, "magic_level": 99,
        "inventory": {}, "quests": {}, "house_owned": True,
        "house_rooms_bought": {key: True for key in ROOM_DATA},
        "house_servant": "", "house_built_flags": {}, "house_style": "basic_wood",
    }
    data.update(updates)
    return data


class ConstructionDataAndMechanicsTest(unittest.TestCase):
    @staticmethod
    def _context(player, calls):
        def award(key, xp):
            player[key] = float(player.get(key, 0) or 0) + xp
            return xp
        return RuntimeActionContext(
            player_data=player, random_random=lambda: .9,
            show_error_message=lambda title, text: calls.setdefault("errors", []).append((title, text)),
            deactivate_current_skill=lambda: calls.__setitem__("deactivated", True),
            award_skill_exp=award, award_hidden_skill_exp=lambda key, _level, xp: award(key, xp),
            level_up_check=lambda *_: None, check_achievements=lambda *_: None,
            save_player_data=lambda: calls.__setitem__("saves", calls.get("saves", 0) + 1),
            refresh_skill_availability=lambda: None, refresh_skill_availability_partial=lambda *_: None,
            can_smith_any=lambda: False, show_exp=lambda xp: calls.setdefault("xp", []).append(xp),
            show_activity_gain=lambda text: calls.setdefault("activity", []).append(text),
            implemented_exp_keys_snapshot=lambda: {}, show_quest_exp_delta=lambda *_: None,
        )
    def test_complete_tables_have_stable_unique_ids_and_citations(self):
        self.assertEqual(len(CONSTRUCTION_BUILD_TARGETS), 447)
        self.assertEqual(len(FLATPACK_TARGETS), 82)
        self.assertEqual(len(TABLET_TARGETS), 15)
        self.assertEqual(len(CONSTRUCTION_DATA), 544)
        self.assertEqual(len(CONSTRUCTION_DATA), len(set(CONSTRUCTION_DATA)))
        self.assertTrue(all("7e7d67b481f1b94599de38a98c470419ab7c96b3" in row["source"] for row in CONSTRUCTION_BUILD_TARGETS))
        self.assertTrue(all("oldid=6579365" in row["source"] for row in FLATPACK_TARGETS))

    def test_v31_migration_is_additive_and_idempotent(self):
        original = {"config_version": 30, "inventory": {"Future item": 9}, "future_house_key": {"keep": True}}
        first = migrate_loaded_data(original, ORE_DATA, ITEM_DEFINITIONS)
        second = migrate_loaded_data(first, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(first, second)
        self.assertEqual(first["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(first["inventory"]["Future item"], 9)
        self.assertEqual(first["future_house_key"], {"keep": True})
        self.assertFalse(first["house_owned"])

    def test_house_purchase_is_rung_zero_and_preserves_unknown_state(self):
        bought, ok = purchase_house_pure({"inventory": {"Coins": 1500}, "unknown": 4})
        self.assertTrue(ok)
        self.assertEqual(bought["inventory"]["Coins"], 500)
        self.assertEqual(bought["house_rooms_bought"], {"garden": True, "parlour": True})
        self.assertEqual(bought["unknown"], 4)

    def test_build_consumes_materials_awards_exact_xp_and_sets_stateful_flag(self):
        data = _house(inventory={"Marble block": 2, "Bolt of cloth": 2, "Gold leaf": 4})
        result, rewards, ok = apply_construction_action_pure(data, "guilded_altar", CONSTRUCTION_DATA, SERVANT_DATA, NAIL_DATA, lambda: .9)
        self.assertTrue(ok)
        self.assertEqual(rewards["construction"], 2230.0)
        self.assertTrue(result["house_built_flags"]["guilded_altar"])
        self.assertEqual(result["inventory"]["Gold leaf"], 0)

    def test_servant_batches_material_builds_and_takes_one_stint_wage(self):
        data = _house(house_servant="rick", inventory={"Plank": 12, "Rune nails": 12, "Coins": 375})
        result, rewards, ok = apply_construction_action_pure(data, "crude_wooden_chair", CONSTRUCTION_DATA, SERVANT_DATA, NAIL_DATA, lambda: .9)
        self.assertTrue(ok)
        self.assertEqual(rewards["count"], 6)
        self.assertEqual(rewards["construction"], 396.0)
        self.assertEqual(result["inventory"]["Coins"], 0)

    def test_crystal_saw_adds_three_only_to_non_water_builds_after_quest(self):
        data = _house(construction_level=72, inventory={"Crystal saw": 1}, quests={"the_eyes_of_glouphrie": {"completed": True}})
        non_water = construction_target_locked_reasons_pure(data, "guilded_altar", CONSTRUCTION_DATA, ROOM_DATA, SERVANT_DATA, NAIL_DATA, WORKBENCH_TIERS)
        self.assertNotIn("Construction level 75", non_water)
        water_target = next(row for row in CONSTRUCTION_BUILD_TARGETS if row["water"] and row["level"] > 72)
        water = construction_target_locked_reasons_pure(data, water_target["id"], CONSTRUCTION_DATA, ROOM_DATA, SERVANT_DATA, NAIL_DATA, WORKBENCH_TIERS)
        self.assertIn(f"Construction level {water_target['level']}", water)

    def test_flatpacks_need_workbench_and_create_tradeable_output(self):
        target = next(row for row in FLATPACK_TARGETS if row["id"] == "flatpack_crude_wooden_chair")
        data = _house(inventory={"Plank": 2, "Rune nails": 2})
        reasons = construction_target_locked_reasons_pure(data, target["id"], CONSTRUCTION_DATA, ROOM_DATA, SERVANT_DATA, NAIL_DATA, WORKBENCH_TIERS)
        self.assertIn("Build the required workbench tier", reasons)
        data["house_built_flags"] = {"wooden_workbench": True}
        result, rewards, ok = apply_construction_action_pure(data, target["id"], CONSTRUCTION_DATA, SERVANT_DATA, NAIL_DATA, lambda: .9)
        self.assertTrue(ok)
        self.assertEqual((rewards["construction"], result["inventory"]["Crude wooden chair"]), (66.0, 1))

    def test_tablet_uses_compatible_lectern_and_awards_magic_xp(self):
        target = CONSTRUCTION_DATA["tablet_varrock_teleport"]
        data = _house(house_built_flags={"mahogany_eagle_lecturn": True}, inventory=dict(target["requirements"]))
        reasons = construction_target_locked_reasons_pure(data, target["id"], CONSTRUCTION_DATA, ROOM_DATA, SERVANT_DATA, NAIL_DATA, WORKBENCH_TIERS)
        self.assertEqual(reasons, ())
        result, rewards, ok = apply_construction_action_pure(data, target["id"], CONSTRUCTION_DATA, SERVANT_DATA, NAIL_DATA, lambda: .9)
        self.assertTrue(ok)
        self.assertEqual(rewards["magic"], 35.0)
        self.assertEqual(result["inventory"]["Varrock teleport tablet"], 1)

    def test_owned_gilded_altar_requires_chapel_altar_and_burner(self):
        data = _house(house_built_flags={"guilded_altar": True, "marble_burner": True})
        self.assertEqual(owned_gilded_altar_burner_count_pure(data), 1)
        data["house_built_flags"]["mahogany_burner"] = True
        self.assertEqual(owned_gilded_altar_burner_count_pure(data), 2)

    def test_owned_altar_skips_search_consumes_marrentill_once_and_scales_xp(self):
        player = _house(
            prayer_level=99, prayer_exp=0, current_prayer="gilded_altar_dragon_bones",
            prayer_gilded_mode="owned", prayer_owned_altar_stint={},
            house_built_flags={"guilded_altar": True, "marble_burner": True},
            inventory={"Dragon bones": 2, "Clean marrentill": 1}, completed_achievements=[],
        )
        calls = {}
        self.assertTrue(handle_prayer_answer(self._context(player, calls)))
        self.assertEqual(player["prayer_exp"], 216.0)
        self.assertEqual(player["inventory"]["Clean marrentill"], 0)
        self.assertNotIn("activity", calls)
        self.assertTrue(handle_prayer_answer(self._context(player, calls)))
        self.assertEqual(player["prayer_exp"], 432.0)

    def test_room_style_and_servant_ladders_use_closed_values(self):
        self.assertEqual(SERVANT_DATA["demon_butler"]["wage"], 7500)
        self.assertEqual(SERVANT_DATA["demon_butler"]["batch_size"], 26)
        self.assertEqual(HOUSE_STYLE_DATA["fremennik_wood"]["price"], 25000)
        self.assertEqual(ROOM_DATA["treasure_room"]["price"], 250000)

    def test_specialty_materials_are_live_shop_rows_at_closed_prices(self):
        self.assertEqual(SHOP_PLAYER_BUY_PRICES["Bolt of cloth"], 650)
        self.assertEqual(SHOP_PLAYER_BUY_PRICES["Gold leaf"], 130000)
        self.assertEqual(SHOP_PLAYER_BUY_PRICES["Marble block"], 325000)
        self.assertEqual(SHOP_PLAYER_BUY_PRICES["Magic stone"], 975000)

    def test_teak_and_mahogany_sawmill_rows_use_darkan_prices(self):
        teak = UTILITY_ACTIVITY_DATA["convert_teak_logs_to_teak_planks"]
        mahogany = UTILITY_ACTIVITY_DATA["convert_mahogany_logs_to_mahogany_planks"]
        self.assertEqual(teak["requirements"], {"Teak logs": 1, "Coins": 500})
        self.assertEqual(mahogany["requirements"], {"Mahogany logs": 1, "Coins": 1500})

    def test_house_sheet_option_purchases_are_instant_coin_sinks(self):
        data = _house(construction_level=99, inventory={"Coins": 600000})
        room, ok = purchase_house_option_pure(data, "chapel", ROOM_DATA, kind="room")
        self.assertFalse(ok)  # _house already owns every room
        data["house_rooms_bought"] = {"garden": True, "parlour": True}
        room, ok = purchase_house_option_pure(data, "chapel", ROOM_DATA, kind="room")
        self.assertTrue(ok)
        self.assertTrue(room["house_rooms_bought"]["chapel"])

    def test_metadata_keeps_locked_rows_non_selectable(self):
        rows = construction_target_rows(_house(inventory={}), CONSTRUCTION_DATA, ROOM_DATA, SERVANT_DATA, NAIL_DATA, WORKBENCH_TIERS, {}, DEFAULT_CONSTRUCTION_TARGET)
        row = next(row for row in rows if row.target_id == "crude_wooden_chair")
        self.assertFalse(row.enabled)
        self.assertIn("Plank x2", row.locked_reasons)

    def test_runtime_handler_registered(self):
        self.assertIs(answer_handler_for_key("construction"), handle_construction_answer)

    def test_every_manifest_asset_path_exists(self):
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets_provenance.json"), encoding="utf-8") as file_obj:
            provenance = json.load(file_obj)
        for request in asset_manifest():
            self.assertTrue(os.path.exists(request.output_path), request.output_path)
            relative = os.path.relpath(request.output_path, os.path.dirname(os.path.dirname(__file__)))
            self.assertIn(relative, provenance)


if __name__ == "__main__":
    unittest.main()
