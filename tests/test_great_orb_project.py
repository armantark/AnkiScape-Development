from __future__ import annotations

import copy
import json
from pathlib import Path
import struct
import sys
import types
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic import cadence_coverage
from ankiscape.core import constants
from ankiscape.data.great_orb_project_data import (
    GREAT_ORB_PROJECT_ACTIVITY_ID,
    GREAT_ORB_PROJECT_TALISMAN_REWARDS,
    MASTER_RUNECRAFTER_REWARDS,
    OMNI_TALISMAN_ACCESS_PAIRS,
    OMNI_TALISMAN_XP,
    STANDARD_RUNECRAFTER_PIECE_XP_RATE,
    STANDARD_RUNECRAFTER_REWARDS,
)
from ankiscape.logic.great_orb_project_logic import (
    apply_great_orb_project_xp_bonuses_pure,
    apply_master_runecrafter_xp_bonus_pure,
    apply_great_orb_project_review_pure,
    buy_great_orb_project_reward_pure,
    enter_great_orb_project_pure,
    great_orb_project_view_pure,
    leave_great_orb_project_pure,
    set_great_orb_project_policy_pure,
)
from ankiscape.core.storage_pure import CURRENT_CONFIG_VERSION, default_player_data, migrate_loaded_data
from tests.test_integration_smoke import (
    _DummyCol,
    _DummyMW,
    _install_runtime_fakes,
    _load_addon_as_package,
)


ROOT = Path(__file__).resolve().parents[1]


def _player(**updates):
    player = {
        "inventory": {},
        "runecrafting_level": 50,
        "runecrafting_exp": 0.0,
        "activity_session": {"active_id": ""},
    }
    player.update(updates)
    return player


class GreatOrbProjectDataTests(unittest.TestCase):
    def test_activity_reward_items_and_normalized_asset_are_registered(self):
        spec = constants.UTILITY_ACTIVITY_DATA[GREAT_ORB_PROJECT_ACTIVITY_ID]
        self.assertEqual(spec["skill_requirements"], {"runecrafting": 50})
        self.assertEqual(spec["surface"], "activities")
        registered = {item.display_name for item in constants.ITEM_DEFINITIONS}
        self.assertIn("Pure essence", registered)
        self.assertTrue(
            {
                item
                for _reward_id, item, _tokens, _item_id in (
                    GREAT_ORB_PROJECT_TALISMAN_REWARDS
                )
            }
            <= registered
        )
        self.assertIn("Elemental talisman", registered)
        self.assertIn("Omni-talisman", registered)
        self.assertIn("Omni-tiara", registered)

        for _reward_id, item, _tokens, item_id, slot, bonus, _xp_rate in (
            STANDARD_RUNECRAFTER_REWARDS + MASTER_RUNECRAFTER_REWARDS
        ):
            self.assertIn(item, registered)
            self.assertEqual(
                constants.EXTRA_ITEM_DATA[item]["source_item_id"], item_id
            )
            equipment = constants.EQUIPMENT_DATA[item]
            self.assertEqual(equipment.slot, slot)
            self.assertEqual(equipment.source_item_id, item_id)
            self.assertEqual(equipment.bonuses.attack_magic, bonus)
            self.assertEqual(equipment.bonuses.defence_stab, bonus)
            self.assertEqual(equipment.bonuses.defence_ranged, bonus)

        provenance = json.loads((ROOT / "assets_provenance.json").read_text())
        for relative in (
            "activityicons/great_orb_project.png",
            "activityitems/master_runecrafter_hat.png",
            "activityitems/master_runecrafter_body.png",
            "activityitems/master_runecrafter_skirt.png",
            "activityitems/master_runecrafter_boots.png",
        ):
            self.assertIn(relative, provenance)
            self.assertLessEqual(
                provenance[relative]["timestamp"], "2012-11-20T23:59:59Z"
            )
            header = (ROOT / relative).read_bytes()[:26]
            self.assertEqual(header[:8], b"\x89PNG\r\n\x1a\n")
            width, height, bit_depth, color_type = struct.unpack(">IIBB", header[16:26])
            self.assertEqual((bit_depth, color_type), (8, 6))
            self.assertLessEqual(max(width, height), 64)

        for _reward_id, item, _tokens, _item_id, _slot, _bonus, _xp_rate in (
            STANDARD_RUNECRAFTER_REWARDS
        ):
            relative = f"activityitems/{item.lower().replace(' ', '_')}.png"
            self.assertIn(relative, provenance)
            entry = provenance[relative]
            if item.endswith(" hat"):
                self.assertEqual(entry["source_wiki"], "rs3-visual-fallback")
                self.assertIn("visual art only", entry["source_note"])
            else:
                self.assertLessEqual(
                    entry["timestamp"], "2012-11-20T23:59:59Z"
                )
            header = (ROOT / relative).read_bytes()[:26]
            self.assertEqual(header[:8], b"\x89PNG\r\n\x1a\n")
            width, height, bit_depth, color_type = struct.unpack(
                ">IIBB", header[16:26]
            )
            self.assertEqual((bit_depth, color_type), (8, 6))
            self.assertLessEqual(max(width, height), 64)

    def test_ordinary_talisman_catalog_has_exact_cutoff_costs_and_item_ids(self):
        self.assertEqual(
            GREAT_ORB_PROJECT_TALISMAN_REWARDS,
            (
                ("air_talisman", "Air talisman", 50, 1438),
                ("mind_talisman", "Mind talisman", 50, 1448),
                ("water_talisman", "Water talisman", 50, 1444),
                ("earth_talisman", "Earth talisman", 50, 1440),
                ("fire_talisman", "Fire talisman", 50, 1442),
                ("body_talisman", "Body talisman", 50, 1446),
                ("cosmic_talisman", "Cosmic talisman", 125, 1454),
                ("chaos_talisman", "Chaos talisman", 125, 1452),
                ("nature_talisman", "Nature talisman", 125, 1462),
                ("law_talisman", "Law talisman", 125, 1458),
            ),
        )

    def test_cadence_ledger_names_one_round_per_review(self):
        row = next(
            row
            for row in cadence_coverage.cadence_coverage_rows_pure()
            if row["handler_key"] == "utility"
            and row["action_id"] == GREAT_ORB_PROJECT_ACTIVITY_ID
        )
        self.assertEqual(row["route_kind"], "activity")
        self.assertIn("one complete altar round", row["source_reason"])
        self.assertIn("cannot begin another match", row["multiplier_behavior"])


class GreatOrbProjectLogicTests(unittest.TestCase):
    def test_entry_requires_level_fifty(self):
        _blocked, ok, info = enter_great_orb_project_pure(
            _player(runecrafting_level=49)
        )
        self.assertFalse(ok)
        self.assertIn("level 50", info["reason"])
        entered, ok, info = enter_great_orb_project_pure(_player())
        self.assertTrue(ok, info)
        self.assertEqual(
            entered["activity_session"]["active_id"],
            GREAT_ORB_PROJECT_ACTIVITY_ID,
        )

    def test_casual_match_resolves_eight_altars_xp_runes_and_exact_tokens(self):
        player, ok, info = enter_great_orb_project_pure(_player())
        self.assertTrue(ok, info)
        xp = 0.0
        for _ in range(8):
            player, result = apply_great_orb_project_review_pure(player, 0.99, 0.0)
            xp += result["xp"]
        self.assertTrue(result["terminal"])
        self.assertEqual(player["great_orb_project"]["tokens"], 1000)
        self.assertEqual(player["great_orb_project"]["games_completed"], 1)
        self.assertEqual(player["great_orb_project"]["games_won"], 1)
        self.assertEqual(player["activity_session"]["active_id"], "")
        self.assertEqual(xp, 990.0)
        self.assertEqual(player["inventory"]["Air rune"], 45)
        self.assertEqual(player["inventory"]["Nature rune"], 9)

    def test_advanced_barrier_and_save_policy_preserve_tradeoffs(self):
        player, ok, info = set_great_orb_project_policy_pure(
            _player(),
            {
                "automation_mode": "advanced",
                "doctrine": "barrier",
                "crafting_policy": "save_for_nature",
            },
        )
        self.assertTrue(ok, info)
        player, ok, info = enter_great_orb_project_pure(player)
        self.assertTrue(ok, info)
        dropped = 0
        for _ in range(8):
            player, result = apply_great_orb_project_review_pure(player, 0.99, 0.0)
            dropped += result["essence_dropped"]
        self.assertTrue(result["terminal"])
        self.assertFalse(result["participating"])
        self.assertGreater(dropped, 0)
        self.assertEqual(result["majority_bonus"], 200)
        self.assertEqual(player["great_orb_project"]["tokens"], 200)
        self.assertEqual(player["inventory"]["Nature rune"], 28)
        self.assertEqual(result["xp"], 504.0)

    def test_leave_forfeits_pending_tokens_but_keeps_already_crafted_runes(self):
        player, ok, _info = enter_great_orb_project_pure(_player())
        self.assertTrue(ok)
        player, result = apply_great_orb_project_review_pure(player, 0.99, 0.0)
        self.assertEqual(result["round_tokens"], 100)
        left, ok, info = leave_great_orb_project_pure(player)
        self.assertTrue(ok, info)
        self.assertEqual(left["great_orb_project"]["tokens"], 0)
        self.assertEqual(left["inventory"]["Air rune"], 45)
        self.assertIn("100 pending tokens forfeited", info["message"])

    def test_reward_shop_supports_buy_x_and_rejects_active_matches(self):
        player = _player(
            great_orb_project={
                "tokens": 1000,
                "automation_mode": "casual",
                "doctrine": "balanced",
                "crafting_policy": "craft_each_round",
                "active": {},
            }
        )
        player, ok, info = buy_great_orb_project_reward_pure(
            player, "pure_essence", 125
        )
        self.assertTrue(ok, info)
        self.assertEqual(player["inventory"]["Pure essence"], 125)
        self.assertEqual(player["great_orb_project"]["tokens"], 875)
        player, ok, info = buy_great_orb_project_reward_pure(
            player, "air_talisman", 99
        )
        self.assertTrue(ok, info)
        self.assertEqual(player["inventory"]["Air talisman"], 1)
        self.assertEqual(player["great_orb_project"]["tokens"], 825)
        player, ok, info = buy_great_orb_project_reward_pure(
            player, "elemental_talisman"
        )
        self.assertTrue(ok, info)
        self.assertEqual(player["inventory"]["Elemental talisman"], 1)
        self.assertEqual(player["great_orb_project"]["tokens"], 700)
        active, ok, _info = enter_great_orb_project_pure(player)
        self.assertTrue(ok)
        _same, ok, info = buy_great_orb_project_reward_pure(
            active, "air_talisman"
        )
        self.assertFalse(ok)
        self.assertIn("Finish or leave", info["reason"])

    def test_every_ordinary_talisman_is_a_one_at_a_time_token_purchase(self):
        player = _player(
            great_orb_project={
                "tokens": 800,
                "automation_mode": "casual",
                "doctrine": "balanced",
                "crafting_policy": "craft_each_round",
                "active": {},
            }
        )
        for reward_id, item, tokens, _item_id in (
            GREAT_ORB_PROJECT_TALISMAN_REWARDS
        ):
            before = player["great_orb_project"]["tokens"]
            player, ok, info = buy_great_orb_project_reward_pure(
                player, reward_id, 99
            )
            self.assertTrue(ok, info)
            self.assertEqual(player["inventory"][item], 1)
            self.assertEqual(
                player["great_orb_project"]["tokens"], before - tokens
            )
        self.assertEqual(player["great_orb_project"]["tokens"], 0)

    def test_master_runecrafter_pieces_cost_fifteen_thousand_each(self):
        player = _player(
            great_orb_project={
                "tokens": 60_000,
                "automation_mode": "casual",
                "doctrine": "balanced",
                "crafting_policy": "craft_each_round",
                "active": {},
            }
        )
        for reward_id, item, tokens, _item_id, _slot, _bonus, _xp_rate in (
            MASTER_RUNECRAFTER_REWARDS
        ):
            before = player["great_orb_project"]["tokens"]
            player, ok, info = buy_great_orb_project_reward_pure(
                player, reward_id, 99
            )
            self.assertTrue(ok, info)
            self.assertEqual(player["inventory"][item], 1)
            self.assertEqual(
                player["great_orb_project"]["tokens"], before - tokens
            )
        self.assertEqual(player["great_orb_project"]["tokens"], 0)

    def test_standard_runecrafter_pieces_cost_one_thousand_each(self):
        player = _player(
            great_orb_project={
                "tokens": 12_000,
                "automation_mode": "casual",
                "doctrine": "balanced",
                "crafting_policy": "craft_each_round",
                "active": {},
            }
        )
        for reward_id, item, tokens, _item_id, _slot, _bonus, _xp_rate in (
            STANDARD_RUNECRAFTER_REWARDS
        ):
            before = player["great_orb_project"]["tokens"]
            player, ok, info = buy_great_orb_project_reward_pure(
                player, reward_id, 99
            )
            self.assertTrue(ok, info)
            self.assertEqual(player["inventory"][item], 1)
            self.assertEqual(
                player["great_orb_project"]["tokens"], before - tokens
            )
        self.assertEqual(player["great_orb_project"]["tokens"], 0)

    def test_standard_runecrafter_bonus_is_gop_only_and_counts_mixed_colours(self):
        mixed = _player(
            equipment={
                "head": "Green runecrafter hat",
                "body": "Blue runecrafter robe",
                "legs": "Yellow runecrafter skirt",
                "hands": "Green runecrafter gloves",
            }
        )
        self.assertEqual(STANDARD_RUNECRAFTER_PIECE_XP_RATE, 0.0025)
        self.assertAlmostEqual(
            apply_great_orb_project_xp_bonuses_pure(mixed, 100), 101.0
        )
        self.assertEqual(apply_master_runecrafter_xp_bonus_pure(mixed, 100), 100)

        player, ok, info = enter_great_orb_project_pure(mixed)
        self.assertTrue(ok, info)
        player, result = apply_great_orb_project_review_pure(player, 0.99, 0.0)
        self.assertAlmostEqual(result["xp"], 90.9)
        self.assertAlmostEqual(
            player["great_orb_project"]["active"]["xp_earned"], result["xp"]
        )
        self.assertIn("90.9 Runecrafting XP", result["status"])

    def test_master_runecrafter_bonus_uses_piece_rates_full_set_and_cap(self):
        self.assertEqual(apply_master_runecrafter_xp_bonus_pure(_player(), 100), 100)
        one = _player(equipment={"head": "Master runecrafter hat"})
        self.assertAlmostEqual(apply_master_runecrafter_xp_bonus_pure(one, 100), 100.8)
        full = _player(
            equipment={
                "head": "Master runecrafter hat",
                "body": "Master runecrafter body",
                "legs": "Master runecrafter skirt",
                "feet": "Master runecrafter boots",
            }
        )
        self.assertAlmostEqual(
            apply_master_runecrafter_xp_bonus_pure(full, 10_000), 10_500
        )
        self.assertAlmostEqual(
            apply_master_runecrafter_xp_bonus_pure(full, 20_000), 20_700
        )

    def test_master_runecrafter_bonus_is_in_pure_match_status_and_tracker(self):
        player = _player(
            equipment={
                "head": "Master runecrafter hat",
                "body": "Master runecrafter body",
                "legs": "Master runecrafter skirt",
                "feet": "Master runecrafter boots",
            }
        )
        player, ok, info = enter_great_orb_project_pure(player)
        self.assertTrue(ok, info)
        player, result = apply_great_orb_project_review_pure(player, 0.99, 0.0)
        self.assertAlmostEqual(result["xp"], 94.5)
        self.assertAlmostEqual(
            player["great_orb_project"]["active"]["xp_earned"], 94.5
        )
        self.assertIn("94.5 Runecrafting XP", result["status"])

    def test_elriss_claim_and_korvak_conversion_make_omni_feeds_reachable(self):
        player = _player()
        blocked, ok, info = buy_great_orb_project_reward_pure(
            player, "omni_talisman"
        )
        self.assertFalse(ok)
        self.assertIn("Show Elriss", info["reason"])
        self.assertNotIn("Omni-talisman", blocked["inventory"])

        player["inventory"] = {
            talisman: 1 for talisman, _tiara in OMNI_TALISMAN_ACCESS_PAIRS
        }
        claimed, ok, info = buy_great_orb_project_reward_pure(
            player, "omni_talisman"
        )
        self.assertTrue(ok, info)
        self.assertEqual(claimed["inventory"]["Omni-talisman"], 1)
        self.assertEqual(claimed["runecrafting_exp"], OMNI_TALISMAN_XP)
        self.assertTrue(
            claimed["great_orb_project"]["omni_talisman_xp_claimed"]
        )
        for talisman, _tiara in OMNI_TALISMAN_ACCESS_PAIRS:
            self.assertEqual(claimed["inventory"][talisman], 1)

        claimed["inventory"] = {}
        replacement, ok, info = buy_great_orb_project_reward_pure(
            claimed, "omni_talisman"
        )
        self.assertTrue(ok, info)
        self.assertEqual(replacement["runecrafting_exp"], OMNI_TALISMAN_XP)

        replacement["inventory"]["Tiara"] = 1
        converted, ok, info = buy_great_orb_project_reward_pure(
            replacement, "omni_tiara"
        )
        self.assertTrue(ok, info)
        self.assertEqual(converted["inventory"]["Omni-talisman"], 0)
        self.assertEqual(converted["inventory"]["Tiara"], 0)
        self.assertEqual(converted["inventory"]["Omni-tiara"], 1)

    def test_view_exposes_lock_policy_shop_and_active_round(self):
        locked = great_orb_project_view_pure(_player(runecrafting_level=49))
        self.assertFalse(locked["eligible"])
        self.assertEqual(len(locked["rewards"]), 30)
        self.assertTrue(
            all(reward["locked_reason"] for reward in locked["rewards"])
        )
        active, ok, _info = enter_great_orb_project_pure(_player())
        self.assertTrue(ok)
        view = great_orb_project_view_pure(active)
        self.assertTrue(view["active"])
        self.assertEqual(view["round_number"], 1)
        self.assertEqual(view["altar"], "Air altar")


class GreatOrbProjectStorageTests(unittest.TestCase):
    def test_default_and_v66_migration_sanitize_state(self):
        default = default_player_data(constants.ORE_DATA, constants.ITEM_DEFINITIONS)
        self.assertEqual(default["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(default["great_orb_project"]["tokens"], 0)
        self.assertFalse(default["great_orb_project"]["omni_talisman_xp_claimed"])
        migrated = migrate_loaded_data(
            {
                "config_version": 65,
                "runecrafting_level": 50,
                "great_orb_project": {
                    "tokens": -4,
                    "automation_mode": "invalid",
                    "active": {"round": 999, "saved_essence": 999},
                },
                "activity_session": {"active_id": GREAT_ORB_PROJECT_ACTIVITY_ID},
            },
            constants.ORE_DATA,
            constants.ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["great_orb_project"]["tokens"], 0)
        self.assertEqual(migrated["great_orb_project"]["automation_mode"], "casual")
        self.assertEqual(migrated["great_orb_project"]["active"]["round"], 7)
        self.assertEqual(migrated["great_orb_project"]["active"]["saved_essence"], 28)


class GreatOrbProjectHookTests(unittest.TestCase):
    def setUp(self):
        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_multiplier_finishes_one_match_and_undo_restores_state(self):
        addon = _load_addon_as_package("ankiscape_great_orb_project_hook")
        logic = sys.modules[f"{addon.__name__}.logic.great_orb_project_logic"]
        storage = sys.modules[f"{addon.__name__}.core.storage_pure"]
        package_constants = sys.modules[f"{addon.__name__}.core.constants"]
        player = storage.default_player_data(
            package_constants.ORE_DATA,
            package_constants.ITEM_DEFINITIONS,
        )
        player["runecrafting_level"] = 50
        player["equipment"] = {
            "head": "Master runecrafter hat",
            "body": "Master runecrafter body",
            "legs": "Master runecrafter skirt",
            "feet": "Master runecrafter boots",
        }
        player, ok, _info = logic.enter_great_orb_project_pure(player)
        self.assertTrue(ok)
        addon.player_data = player
        addon.current_skill = "Activities"
        addon.exp_awarded = False
        addon._review_action_multiplier = lambda: 20
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _message: None
        addon._show_exp = lambda _amount: None
        addon._advance_world_events_after_review = lambda: None
        addon._save_player_data_if_anki_ready = lambda: None
        before = copy.deepcopy(addon.player_data)
        with patch.object(addon.random, "random", side_effect=[0.99, 0.0] * 8) as rng:
            addon.on_good_answer(before)
        self.assertEqual(rng.call_count, 16)
        self.assertEqual(addon.player_data["great_orb_project"]["games_completed"], 1)
        self.assertAlmostEqual(addon.player_data["runecrafting_exp"], 1_039.5)

        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
        self.assertEqual(addon.player_data, before)

    def test_omni_talisman_claim_xp_is_direct_and_undoable(self):
        addon = _load_addon_as_package("ankiscape_great_orb_omni_direct")
        storage = sys.modules[f"{addon.__name__}.core.storage_pure"]
        package_constants = sys.modules[f"{addon.__name__}.core.constants"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._show_activity_gain = lambda *_args: None
        addon._show_quest_exp_delta = lambda *_args: None
        addon.current_skill = "Activities"
        initial = storage.default_player_data(
            package_constants.ORE_DATA, package_constants.ITEM_DEFINITIONS
        )
        initial["runecrafting_level"] = 50
        initial["inventory"].update(
            {
                talisman: 1
                for talisman, _tiara in OMNI_TALISMAN_ACCESS_PAIRS
            }
        )
        addon.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_great_orb_project_command"](
            "buy_great_orb_project_reward",
            {"reward_id": "omni_talisman", "quantity": 1},
        )

        self.assertTrue(result["ok"], result)
        self.assertEqual(addon.player_data["inventory"]["Omni-talisman"], 1)
        self.assertEqual(addon.player_data["runecrafting_exp"], OMNI_TALISMAN_XP)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon.player_data, initial)

    def test_master_runecrafter_purchase_is_direct_and_undoable(self):
        addon = _load_addon_as_package("ankiscape_great_orb_master_direct")
        storage = sys.modules[f"{addon.__name__}.core.storage_pure"]
        package_constants = sys.modules[f"{addon.__name__}.core.constants"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._show_activity_gain = lambda *_args: None
        addon._show_quest_exp_delta = lambda *_args: None
        addon.current_skill = "Activities"
        initial = storage.default_player_data(
            package_constants.ORE_DATA, package_constants.ITEM_DEFINITIONS
        )
        initial["runecrafting_level"] = 50
        initial["great_orb_project"]["tokens"] = 15_000
        addon.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_great_orb_project_command"](
            "buy_great_orb_project_reward",
            {"reward_id": "master_runecrafter_hat", "quantity": 99},
        )

        self.assertTrue(result["ok"], result)
        self.assertEqual(
            addon.player_data["inventory"]["Master runecrafter hat"], 1
        )
        self.assertEqual(addon.player_data["great_orb_project"]["tokens"], 0)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon.player_data, initial)


if __name__ == "__main__":
    unittest.main()
