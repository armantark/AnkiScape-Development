import json
import struct
import unittest
from pathlib import Path

from constants import (
    EQUIPMENT_DATA,
    ITEM_DEFINITIONS,
    ORE_DATA,
    UTILITY_ACTIVITY_DATA,
)
from equipment_data import EquipmentBonuses
from court_cases_data import COURT_CASES, COURT_CASES_ACTIVITY_ID
from court_cases_logic import (
    apply_court_case_review_pure,
    apply_court_cases_command_pure,
    court_cases_view_pure,
    enter_court_case_pure,
    filter_court_summons_outputs_pure,
    sanitize_court_cases_state_pure,
)
from logic_pure import _combat_roll_drops
from runtime_actions import RuntimeActionContext, handle_utility_answer
from storage_pure import CURRENT_CONFIG_VERSION, default_player_data, migrate_loaded_data


ROOT = Path(__file__).resolve().parents[1]


def _player(*, attack=65, defence=65, summons=0, answered_cards=0):
    inventory = {"Court summons": summons} if summons else {}
    return {
        "inventory": inventory,
        "quests": {"kings_ransom": {"completed": True}},
        "attack_level": attack,
        "attack_exp": 0.0,
        "defense_level": defence,
        "defense_exp": 0.0,
        "completed_achievements": [],
        "current_utility": COURT_CASES_ACTIVITY_ID,
        "activity_session": {"active_id": ""},
        "shop_market_clock": {"answered_cards": answered_cards},
    }


def _context(player_data, calls):
    def award_skill_exp(exp_key, amount):
        player_data[exp_key] = float(player_data.get(exp_key, 0.0) or 0.0) + amount
        return amount

    return RuntimeActionContext(
        player_data=player_data,
        random_random=lambda: 0.0,
        show_error_message=lambda title, message: calls["errors"].append((title, message)),
        deactivate_current_skill=lambda: calls.__setitem__("deactivated", True),
        award_skill_exp=award_skill_exp,
        award_hidden_skill_exp=lambda *_args: None,
        level_up_check=lambda skill, _data: calls["levels"].append(skill),
        check_achievements=lambda _data: calls.__setitem__("achievements", True),
        save_player_data=lambda: calls.__setitem__("saves", calls["saves"] + 1),
        refresh_skill_availability=lambda: calls.__setitem__("refresh", True),
        refresh_skill_availability_partial=lambda *_args: None,
        can_smith_any=lambda: False,
        show_exp=lambda amount: calls["xp"].append(amount),
        show_activity_gain=lambda message: calls["activity"].append(message),
        implemented_exp_keys_snapshot=lambda: {},
        show_quest_exp_delta=lambda _before: None,
    )


def _finish_casual_case(player):
    last = {}
    for _ in range(24):
        player, last = apply_court_case_review_pure(player)
        if last.get("terminal"):
            return player, last
    raise AssertionError("case did not finish")


class CourtCasesPureTest(unittest.TestCase):
    def test_registry_and_nonstackable_summons_identity_are_reachable(self):
        self.assertIn(COURT_CASES_ACTIVITY_ID, UTILITY_ACTIVITY_DATA)
        definition = next(
            item for item in ITEM_DEFINITIONS if item.storage_key == "Court summons"
        )
        self.assertEqual(definition.source_item_id, 18757)
        self.assertFalse(definition.stackable)
        self.assertFalse(definition.tradeable)
        self.assertTrue(definition.asset_path.endswith("activityicons/court_cases.png"))
        afro = next(item for item in ITEM_DEFINITIONS if item.storage_key == "Rainbow afro")
        self.assertEqual(afro.source_item_id, 19747)
        self.assertTrue(afro.tradeable)
        self.assertEqual(EQUIPMENT_DATA["Rainbow afro"].slot, "head")
        self.assertEqual(
            EQUIPMENT_DATA["Rainbow afro"].bonuses,
            EquipmentBonuses(),
        )
        self.assertFalse(afro.stackable)
        self.assertTrue(afro.asset_path.endswith("activityitems/rainbow_afro.png"))

    def test_period_assets_are_provenanced_tight_and_normalized(self):
        provenance = json.loads((ROOT / "assets_provenance.json").read_text())
        for relative in (
            "activityicons/court_cases.png",
            "activityitems/rainbow_afro.png",
        ):
            with self.subTest(relative=relative):
                path = ROOT / relative
                self.assertTrue(path.exists())
                self.assertIn(relative, provenance)
                self.assertLessEqual(
                    provenance[relative]["timestamp"], "2012-11-20T23:59:59Z"
                )
                header = path.read_bytes()[:26]
                self.assertEqual(header[:8], b"\x89PNG\r\n\x1a\n")
                width, height, bit_depth, color_type = struct.unpack(
                    ">IIBB", header[16:26]
                )
                self.assertEqual((bit_depth, color_type), (8, 6))
                self.assertLessEqual(max(width, height), 64)

    def test_kings_ransom_and_role_level_are_real_entry_gates(self):
        player = _player(attack=64)
        player["quests"]["kings_ransom"]["completed"] = False
        _updated, ok, info = enter_court_case_pure(player, {"role": "prosecution"})
        self.assertFalse(ok)
        self.assertEqual(
            info["locked_reasons"],
            ("complete King's Ransom", "Attack level 65"),
        )
        defender = _player(defence=64)
        _updated, ok, info = enter_court_case_pure(defender, {"role": "defence"})
        self.assertFalse(ok)
        self.assertEqual(info["locked_reasons"], ("Defence level 65",))

    def test_free_mugger_starter_runs_preparation_and_both_trial_roles(self):
        for role, skill, verdict in (
            ("prosecution", "attack", "guilty"),
            ("defence", "defense", "not guilty"),
        ):
            with self.subTest(role=role):
                player, ok, info = enter_court_case_pure(
                    _player(), {"role": role, "automation_mode": "casual"}
                )
                self.assertTrue(ok, info)
                self.assertEqual(info["case_id"], "mugger")
                for expected in (1, 2, 3):
                    player, result = apply_court_case_review_pure(player)
                    self.assertIn(f"case report {expected}", result["status"])
                player, fingerprint = apply_court_case_review_pure(player)
                self.assertIn("fingerprint", fingerprint["status"])
                player, result = _finish_casual_case(player)
                self.assertEqual(result["xp"], 2000.0)
                self.assertEqual(result["xp_skill"], skill)
                self.assertEqual(result["verdict"], verdict)
                self.assertEqual(player["court_cases_completed_ids"], ["mugger"])
                self.assertEqual(player["activity_session"], {"active_id": ""})

    def test_river_troll_consumes_summons_and_awards_sharks(self):
        player = _player(summons=1)
        player["court_cases_completed_ids"] = ["mugger"]
        player, ok, info = enter_court_case_pure(
            player, {"role": "defence", "automation_mode": "casual"}
        )
        self.assertTrue(ok, info)
        self.assertEqual(info["case_id"], "river_troll")
        self.assertNotIn("Court summons", player["inventory"])
        player, result = _finish_casual_case(player)
        self.assertEqual(result["xp"], 3500.0)
        self.assertEqual(result["xp_skill"], "defense")
        self.assertEqual(result["rewards"], {"Shark": 20})
        self.assertEqual(player["inventory"]["Shark"], 20)
        self.assertEqual(
            player["court_cases_completed_ids"], ["mugger", "river_troll"]
        )
        view = court_cases_view_pure(player)
        self.assertEqual(view["case_id"], "party_pete")
        self.assertEqual(view["cooldown_reviews"], 14 * 240)

    def test_batch_two_uses_answered_card_cooldown_and_role_specific_routes(self):
        for role, expected_reviews in (("prosecution", 15), ("defence", 14)):
            with self.subTest(role=role):
                player = _player(summons=1, answered_cards=(14 * 240) - 1)
                player["court_cases_completed_ids"] = ["mugger", "river_troll"]
                player["court_cases_batch2_ready_at_review"] = 14 * 240
                _blocked, ok, info = enter_court_case_pure(
                    player, {"role": role, "automation_mode": "casual"}
                )
                self.assertFalse(ok)
                self.assertIn("1 reviews", info["reason"])
                player["shop_market_clock"]["answered_cards"] += 1
                player, ok, info = enter_court_case_pure(
                    player, {"role": role, "automation_mode": "casual"}
                )
                self.assertTrue(ok, info)
                reviews = 0
                while True:
                    player, result = apply_court_case_review_pure(player)
                    reviews += 1
                    if result.get("terminal"):
                        break
                self.assertEqual(reviews, expected_reviews)
                self.assertEqual(result["xp"], 9000.0)
                self.assertEqual(result["rewards"], {"Rainbow afro": 1})
                self.assertEqual(player["inventory"]["Rainbow afro"], 1)

    def test_summons_is_required_after_the_starter(self):
        player = _player()
        player["court_cases_completed_ids"] = ["mugger"]
        _updated, ok, info = enter_court_case_pure(player)
        self.assertFalse(ok)
        self.assertEqual(info["reason"], "A Court summons is required for the next case.")

    def test_summons_drops_only_after_starter_and_only_one_at_a_time(self):
        outputs = {"Coins": 3, "Court summons": 4}
        player = _player()
        self.assertEqual(
            filter_court_summons_outputs_pure(player, outputs),
            {"Coins": 3},
        )
        player["court_cases_completed_ids"] = ["mugger"]
        self.assertEqual(
            filter_court_summons_outputs_pure(player, outputs),
            {"Coins": 3, "Court summons": 1},
        )
        player["inventory"]["Court summons"] = 1
        self.assertEqual(
            filter_court_summons_outputs_pure(player, outputs),
            {"Coins": 3},
        )
        player["inventory"].clear()
        player["court_cases"] = {"case_id": "river_troll"}
        self.assertEqual(
            filter_court_summons_outputs_pure(player, outputs),
            {"Coins": 3},
        )
        player["court_cases"] = {}
        player["court_cases_completed_ids"] = list(COURT_CASES)
        self.assertEqual(
            filter_court_summons_outputs_pure(player, outputs),
            {"Coins": 3},
        )

    def test_combat_drop_pipeline_applies_summons_gate(self):
        enemy = {
            "drops": {
                "guaranteed": (("Court summons", 1), ("Coins", 2)),
                "tables": (),
            }
        }
        pre_starter = _combat_roll_drops(enemy, lambda *_args: 0, _player())
        self.assertEqual(pre_starter, {"Coins": 2})
        eligible = _player()
        eligible["court_cases_completed_ids"] = ["mugger"]
        self.assertEqual(
            _combat_roll_drops(enemy, lambda *_args: 0, eligible),
            {"Court summons": 1, "Coins": 2},
        )

    def test_advanced_wrong_argument_retries_without_losing_preparation(self):
        player, ok, _ = enter_court_case_pure(
            _player(), {"automation_mode": "advanced"}
        )
        self.assertTrue(ok)
        for _ in range(4):
            player, _ = apply_court_case_review_pure(player)
        view = court_cases_view_pure(player)
        self.assertEqual(view["phase"], "trial")
        self.assertFalse(view["can_review"])
        wrong = next(
            choice
            for choice in view["trial_choices"]
            if choice != COURT_CASES["mugger"]["trial_steps"][0]["prosecution"]
        )
        player, ok, _ = apply_court_cases_command_pure(
            player, "select_choice", {"choice": wrong}
        )
        self.assertTrue(ok)
        for _ in range(6):
            view = court_cases_view_pure(player)
            if not view["pending_choice"]:
                player, ok, _ = apply_court_cases_command_pure(
                    player,
                    "select_choice",
                    {"choice": view["trial_choices"][0]},
                )
                self.assertTrue(ok)
            player, result = apply_court_case_review_pure(player)
        self.assertEqual(result["verdict"], "undecided")
        self.assertEqual(player["court_cases"]["phase"], "trial")
        self.assertEqual(player["court_cases"]["prep_index"], 4)
        self.assertEqual(player["court_cases"]["trial_index"], 0)

    def test_giving_up_loses_consumed_summons(self):
        player = _player(summons=1)
        player["court_cases_completed_ids"] = ["mugger"]
        player, ok, _ = apply_court_cases_command_pure(player, "enter")
        self.assertTrue(ok)
        player, ok, info = apply_court_cases_command_pure(player, "leave")
        self.assertTrue(ok)
        self.assertNotIn("Court summons", player["inventory"])
        self.assertIn("summons was lost", info["message"])

    def test_sanitizer_repairs_tampered_session_and_conflicting_activity(self):
        player = _player()
        player["court_cases"] = {
            "case_id": "mugger",
            "role": "invalid",
            "automation_mode": "invalid",
            "prep_index": 99,
            "trial_index": 99,
            "pending_choice": "fabricated",
        }
        player["activity_session"] = {"active_id": "barrows"}
        state = sanitize_court_cases_state_pure(player)
        self.assertEqual(state["court_cases"], {})

    def test_storage_v69_migrates_without_retroactive_progress(self):
        old = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        old["config_version"] = 68
        for key in (
            "court_cases",
            "court_cases_policy",
            "court_cases_completed_ids",
            "court_cases_attempts",
            "court_cases_last_result",
        ):
            old.pop(key, None)
        migrated = migrate_loaded_data(old, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(CURRENT_CONFIG_VERSION, 69)
        self.assertEqual(migrated["court_cases"], {})
        self.assertEqual(migrated["court_cases_completed_ids"], [])
        self.assertEqual(migrated["court_cases_attempts"], 0)
        self.assertEqual(migrated["court_cases_batch2_ready_at_review"], 0)


class CourtCasesRuntimeIntegrationTest(unittest.TestCase):
    def test_runtime_advances_review_and_awards_terminal_attack_xp(self):
        player, ok, _ = enter_court_case_pure(_player())
        self.assertTrue(ok)
        calls = {
            "errors": [],
            "levels": [],
            "xp": [],
            "activity": [],
            "saves": 0,
        }
        ctx = _context(player, calls)
        for _ in range(10):
            self.assertTrue(handle_utility_answer(ctx))
        self.assertEqual(player["attack_exp"], 2000.0)
        self.assertEqual(calls["saves"], 10)
        self.assertTrue(calls["deactivated"])
        self.assertIn("guilty", calls["activity"][-1])
        telemetry = player["action_telemetry"]["actions"]
        self.assertEqual(telemetry["utility:court_cases"]["attempts"], 10)


if __name__ == "__main__":
    unittest.main()
