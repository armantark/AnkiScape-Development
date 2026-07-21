from __future__ import annotations

import unittest
import json
from pathlib import Path

from constants import ITEM_DEFINITIONS, UTILITY_ACTIVITY_DATA
from runtime_actions import RuntimeActionContext, handle_utility_answer
from storage_pure import CURRENT_CONFIG_VERSION, migrate_loaded_data
from summoning_logic import default_summoning_state_pure
from tools.trim_icons import _select_backend
from vinesweeper_data import VINESWEEPER_REWARDS, VINESWEEPER_REWARDS_BY_ID
from vinesweeper_logic import (
    apply_compost_potion_pure,
    apply_vinesweeper_command_pure,
    apply_vinesweeper_review_pure,
    default_vinesweeper_state_pure,
    sanitize_vinesweeper_state_pure,
    vinesweeper_xp_point_cost_pure,
)


def _player(**overrides):
    data = {
        "inventory": {"Spade": 1, "Coins": 10_000},
        "toolbelt": {},
        "farming_level": 40,
        "farming_exp": 0.0,
        "hunter_level": 1,
        "hunter_exp": 0.0,
        "summoning_level": 1,
        "summoning_state": default_summoning_state_pure(),
        "vinesweeper": default_vinesweeper_state_pure(),
        "current_utility": "vinesweeper",
    }
    data.update(overrides)
    return data


def _entered(**overrides):
    data = _player(**overrides)
    data, ok, _info = apply_vinesweeper_command_pure(data, "enter")
    assert ok
    return data


class VinesweeperDataTests(unittest.TestCase):
    def test_cutoff_shop_uses_literal_interface_rows(self):
        self.assertEqual(len(VINESWEEPER_REWARDS), 46)
        self.assertEqual(VINESWEEPER_REWARDS_BY_ID["flag"].point_price, 50)
        self.assertEqual(VINESWEEPER_REWARDS_BY_ID["torstol_seed"].point_price, 45_000)
        self.assertEqual(VINESWEEPER_REWARDS_BY_ID["spirit_tree_seed"].item_name, "Spirit seed")
        names = {reward.display_name for reward in VINESWEEPER_REWARDS}
        self.assertNotIn("Fellstalk seed", names)
        self.assertNotIn("Morchella mushroom spore", names)

    def test_shop_outputs_and_period_activity_icon_are_reachable(self):
        registered = {definition.storage_key for definition in ITEM_DEFINITIONS}
        missing = {
            reward.item_name
            for reward in VINESWEEPER_REWARDS
            if reward.id != "flag" and reward.item_name not in registered
        }
        self.assertEqual(missing, set())
        icon_path = Path(UTILITY_ACTIVITY_DATA["vinesweeper"]["icon_path"])
        self.assertTrue(icon_path.is_file())
        _backend_name, bbox_fn, _crop_fn = _select_backend()
        image_bounds = bbox_fn(str(icon_path))
        self.assertIsNotNone(image_bounds)
        assert image_bounds is not None
        image_size, opaque_bounds = image_bounds
        self.assertLessEqual(max(image_size), 32)
        self.assertEqual(opaque_bounds, (0, 0, *image_size))
        provenance = json.loads(
            Path("assets_provenance.json").read_text(encoding="utf-8")
        )["activityicons/vinesweeper.png"]
        self.assertLessEqual(provenance["timestamp"], "2012-11-20T23:59:59Z")

        by_key = {definition.storage_key: definition for definition in ITEM_DEFINITIONS}
        all_provenance = json.loads(
            Path("assets_provenance.json").read_text(encoding="utf-8")
        )
        for dose in range(1, 5):
            name = f"Compost potion ({dose})"
            definition = by_key[name]
            self.assertFalse(definition.stackable)
            self.assertTrue(Path(definition.asset_path or "").is_file())
            entry = all_provenance[f"activityitems/compost_potion_{dose}.png"]
            self.assertLessEqual(entry["timestamp"], "2012-11-20T23:59:59Z")

    def test_source_blocked_xp_curve_preserves_both_pinned_endpoints(self):
        self.assertEqual(vinesweeper_xp_point_cost_pure(1), 7.75)
        self.assertEqual(vinesweeper_xp_point_cost_pure(40), 1.0)
        self.assertEqual(vinesweeper_xp_point_cost_pure(99), 1.0)


class VinesweeperLogicTests(unittest.TestCase):
    def test_compost_potion_preserves_each_remainder_and_empty_vial(self):
        upgraded, ok, info = apply_compost_potion_pure(
            {"Compost": 2, "Compost potion (4)": 1}
        )
        self.assertTrue(ok)
        self.assertEqual(upgraded["Supercompost"], 1)
        self.assertEqual(upgraded["Compost potion (4)"], 0)
        self.assertEqual(upgraded["Compost potion (3)"], 1)
        self.assertEqual(info["remainder"], "Compost potion (3)")

        upgraded, ok, info = apply_compost_potion_pure(
            {"Compost": 1, "Compost potion (1)": 1}
        )
        self.assertTrue(ok)
        self.assertEqual(upgraded["Supercompost"], 1)
        self.assertEqual(upgraded["Vial"], 1)
        self.assertEqual(info["remainder"], "Vial")

    def test_entry_requires_spade_and_grants_free_flags_only_once(self):
        blocked, ok, info = apply_vinesweeper_command_pure(
            _player(inventory={"Coins": 10_000}), "enter"
        )
        self.assertFalse(ok)
        self.assertIn("spade", info["reason"].lower())
        self.assertFalse(blocked["vinesweeper"]["active"])

        entered = _entered()
        self.assertEqual(entered["vinesweeper"]["flags"], 10)
        left, ok, _ = apply_vinesweeper_command_pure(entered, "leave")
        self.assertTrue(ok)
        left["vinesweeper"]["flags"] = 3
        reentered, ok, _ = apply_vinesweeper_command_pure(left, "enter")
        self.assertTrue(ok)
        self.assertEqual(reentered["vinesweeper"]["flags"], 3)

    def test_active_follower_requires_confirmation_and_uses_normal_dismissal(self):
        data = _player()
        data["summoning_state"]["active_follower"] = {
            "kind": "familiar",
            "entity_id": "spiritwolf",
            "remaining_reviews": 5,
            "max_reviews": 5,
            "storage": {},
        }
        unchanged, ok, info = apply_vinesweeper_command_pure(data, "enter")
        self.assertFalse(ok)
        self.assertTrue(info["requires_confirmation"])
        self.assertTrue(unchanged["summoning_state"]["active_follower"])

        entered, ok, info = apply_vinesweeper_command_pure(
            data, "enter", {"confirm_dismiss_follower": True}
        )
        self.assertTrue(ok)
        self.assertEqual(info["dismissed_follower_kind"], "familiar")
        self.assertEqual(entered["summoning_state"]["active_follower"], {})

    def test_one_roll_per_operation_covers_the_complete_flattened_outcome_set(self):
        data = _entered(farming_level=50)
        updated, result = apply_vinesweeper_review_pure(
            data,
            (0.01, 0.50, 0.85, 0.92, 0.99),
            operations=5,
        )
        state = updated["vinesweeper"]
        self.assertEqual(result["completed_operations"], 5)
        self.assertEqual(state["operations"], 5)
        self.assertEqual(state["safe_uncover_count"], 1)
        self.assertEqual(state["correct_flag_count"], 1)
        self.assertEqual(state["mistake_count"], 2)
        self.assertEqual(state["rabbits_repulsed"], 1)
        self.assertEqual(state["flags"], 9)
        self.assertEqual(state["ogleroots"], 0)
        self.assertEqual(result["hunter_xp"], 30.0)
        self.assertEqual(updated["inventory"]["Coins"], 10_000)

    def test_replacement_flags_prefer_coins_then_points_then_pause(self):
        data = _entered()
        data["vinesweeper"]["flags"] = 0
        data["inventory"]["Coins"] = 500
        data["vinesweeper"]["points"] = 50
        paid_coins, result = apply_vinesweeper_review_pure(data, (0.50,))
        self.assertEqual(paid_coins["inventory"]["Coins"], 0)
        points_after_coin_payment = paid_coins["vinesweeper"]["points"]
        self.assertGreater(points_after_coin_payment, 50)
        self.assertIn("500 coins", result["status"])

        paid_coins["vinesweeper"]["flags"] = 0
        paid_points, result = apply_vinesweeper_review_pure(paid_coins, (0.50,))
        self.assertEqual(result["point_delta"], 130)
        self.assertEqual(paid_points["vinesweeper"]["points"], 360)
        self.assertIn("50 points", result["status"])

        paid_points["vinesweeper"]["flags"] = 0
        paid_points["vinesweeper"]["points"] = 0
        paused, result = apply_vinesweeper_review_pure(paid_points, (0.50,))
        self.assertTrue(result["paused"])
        self.assertFalse(paused["vinesweeper"]["active"])
        self.assertEqual(result["completed_operations"], 0)

    def test_rabbit_buys_ogleroot_or_applies_source_loss(self):
        data = _entered()
        data["inventory"]["Coins"] = 10
        defended, result = apply_vinesweeper_review_pure(data, (0.99,))
        self.assertEqual(defended["inventory"]["Coins"], 0)
        self.assertEqual(defended["vinesweeper"]["flags"], 10)
        self.assertEqual(result["hunter_xp"], 30.0)

        data["inventory"]["Coins"] = 0
        lost, result = apply_vinesweeper_review_pure(data, (0.99,))
        self.assertEqual(lost["vinesweeper"]["flags"], 9)
        self.assertEqual(result["hunter_xp"], 0.0)
        self.assertIn("no points", result["status"])

    def test_leave_refunds_excess_ogleroots(self):
        data = _entered()
        data["vinesweeper"]["ogleroots"] = 3
        data["inventory"]["Coins"] = 7
        left, ok, info = apply_vinesweeper_command_pure(data, "leave")
        self.assertTrue(ok)
        self.assertEqual(info["coin_refund"], 30)
        self.assertEqual(left["inventory"]["Coins"], 37)
        self.assertEqual(left["vinesweeper"]["ogleroots"], 0)

    def test_direct_shop_and_xp_redemption_use_real_outputs(self):
        data = _entered(farming_level=1)
        data["vinesweeper"]["points"] = 60_000
        bought, ok, info = apply_vinesweeper_command_pure(
            data,
            "buy_reward",
            {"reward_id": "spirit_tree_seed", "quantity": 1},
        )
        self.assertTrue(ok)
        self.assertEqual(info["item_name"], "Spirit seed")
        self.assertEqual(bought["inventory"]["Spirit seed"], 1)
        self.assertEqual(bought["vinesweeper"]["points"], 5_000)

        redeemed, ok, info = apply_vinesweeper_command_pure(
            bought, "redeem_farming_xp", {"points": 775}
        )
        self.assertTrue(ok)
        self.assertAlmostEqual(info["farming_xp"], 100.0)
        self.assertAlmostEqual(redeemed["farming_exp"], 100.0)
        self.assertEqual(redeemed["vinesweeper"]["points"], 4_225)

    def test_sanitizer_cannot_persist_a_hidden_board_or_timer(self):
        state = sanitize_vinesweeper_state_pure(
            {"active": True, "flags": 99, "board": [[1]], "timer": 123}
        )
        self.assertEqual(state["flags"], 10)
        self.assertNotIn("board", state)
        self.assertNotIn("timer", state)


class VinesweeperIntegrationTests(unittest.TestCase):
    def test_runtime_compost_potion_uses_one_dose_and_preserves_remainder(self):
        player = _player(
            current_utility="use_compost_potion",
            inventory={"Compost": 1, "Compost potion (4)": 1},
        )
        gains = []
        ctx = RuntimeActionContext(
            player_data=player,
            random_random=lambda: self.fail("compost potion must not consume RNG"),
            show_error_message=lambda *_args: self.fail("unexpected runtime error"),
            deactivate_current_skill=lambda: self.fail("activity should remain active"),
            award_skill_exp=lambda *_args: self.fail("compost potion grants no XP"),
            award_hidden_skill_exp=lambda *_args: None,
            level_up_check=lambda *_args: None,
            check_achievements=lambda *_args: None,
            save_player_data=lambda: None,
            refresh_skill_availability=lambda: None,
            refresh_skill_availability_partial=lambda *_args: None,
            can_smith_any=lambda: True,
            show_exp=lambda *_args: self.fail("compost potion grants no XP"),
            show_activity_gain=lambda message: gains.append(message),
            implemented_exp_keys_snapshot=lambda: {},
            show_quest_exp_delta=lambda *_args: None,
        )

        self.assertTrue(handle_utility_answer(ctx))
        self.assertEqual(player["inventory"]["Compost"], 0)
        self.assertEqual(player["inventory"]["Compost potion (4)"], 0)
        self.assertEqual(player["inventory"]["Compost potion (3)"], 1)
        self.assertEqual(player["inventory"]["Supercompost"], 1)
        self.assertEqual(
            gains,
            ["Upgraded 1 Compost to Supercompost · Compost potion (3) remains"],
        )

    def test_runtime_multiplier_is_atomic_and_awards_hunter_xp(self):
        player = _entered()
        player["inventory"]["Coins"] = 10
        gains = []
        deactivated = []
        ctx = RuntimeActionContext(
            player_data=player,
            random_random=iter((0.01, 0.99)).__next__,
            show_error_message=lambda *_args: self.fail("unexpected runtime error"),
            deactivate_current_skill=lambda: deactivated.append(True),
            award_skill_exp=lambda key, amount: player.__setitem__(
                key, float(player.get(key, 0.0)) + amount
            ) or amount,
            award_hidden_skill_exp=lambda *_args: None,
            level_up_check=lambda *_args: None,
            check_achievements=lambda *_args: None,
            save_player_data=lambda: None,
            refresh_skill_availability=lambda: None,
            refresh_skill_availability_partial=lambda *_args: None,
            can_smith_any=lambda: True,
            show_exp=lambda amount: gains.append(amount),
            show_activity_gain=lambda *_args: None,
            implemented_exp_keys_snapshot=lambda: {},
            show_quest_exp_delta=lambda *_args: None,
            review_action_multiplier=2,
        )
        self.assertTrue(handle_utility_answer(ctx))
        self.assertEqual(player["vinesweeper"]["operations"], 2)
        self.assertEqual(player["hunter_exp"], 30.0)
        self.assertEqual(gains, [30.0])
        self.assertEqual(deactivated, [])

    def test_storage_migration_adds_only_flat_vinesweeper_state(self):
        migrated = migrate_loaded_data({"config_version": 56}, {}, ())
        self.assertEqual(CURRENT_CONFIG_VERSION, 64)
        self.assertEqual(migrated["config_version"], 64)
        self.assertIn("vinesweeper", migrated)
        self.assertNotIn("board", migrated["vinesweeper"])


if __name__ == "__main__":
    unittest.main()
