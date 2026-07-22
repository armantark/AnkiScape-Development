from __future__ import annotations

import unittest
from dataclasses import asdict

from trouble_brewing_data import (
    TROUBLE_BREWING_EVENT_REVIEWS,
    trouble_brewing_equipment_data_as_dict,
)
from trouble_brewing_logic import (
    apply_trouble_brewing_command_pure,
    apply_trouble_brewing_review_pure,
    buy_trouble_brewing_reward_pure,
    enter_trouble_brewing_pure,
    leave_trouble_brewing_pure,
    sanitize_trouble_brewing_state_pure,
    set_trouble_brewing_policy_pure,
    trouble_brewing_view_pure,
)


def _player(**overrides):
    player = {
        "cooking_level": 40,
        "quests": {"cabin_fever": {"completed": True}},
        "activity_session": {"active_id": ""},
        "inventory": {},
    }
    player.update(overrides)
    return player


def _entered(**overrides):
    player, ok, info = enter_trouble_brewing_pure(_player(**overrides))
    assert ok, info
    return player


class TroubleBrewingEntryTests(unittest.TestCase):
    def test_representative_reward_is_an_authentic_zero_stat_head_item(self):
        item = trouble_brewing_equipment_data_as_dict()["Blue tricorn hat"]
        self.assertEqual(item.source_item_id, 8959)
        self.assertEqual(item.slot, "head")
        self.assertTrue(all(value == 0 for value in asdict(item.bonuses).values()))

    def test_entry_requires_cooking_40_cabin_fever_and_free_activity_slot(self):
        for player, reason in (
            (_player(cooking_level=39), "Cooking"),
            (_player(quests={}), "Cabin Fever"),
            (_player(activity_session={"active_id": "barrows"}), "persistent activity"),
        ):
            with self.subTest(reason=reason):
                _unchanged, ok, info = enter_trouble_brewing_pure(player)
                self.assertFalse(ok)
                self.assertIn(reason, info["reason"])

        entered = _entered()
        self.assertEqual(entered["activity_session"], {"active_id": "trouble_brewing"})
        self.assertEqual(len(entered["trouble_brewing"]["boilers"]), 3)

    def test_policy_is_saved_before_entry_and_cannot_change_mid_game(self):
        player, ok, _info = set_trouble_brewing_policy_pure(
            _player(), {"automation_mode": "advanced", "duty": "sabotage"}
        )
        self.assertTrue(ok)
        entered, ok, _info = enter_trouble_brewing_pure(player)
        self.assertTrue(ok)
        self.assertEqual(entered["trouble_brewing"]["automation_mode"], "advanced")
        self.assertEqual(entered["trouble_brewing"]["duty"], "sabotage")
        _unchanged, ok, info = set_trouble_brewing_policy_pure(
            entered, {"duty": "water"}
        )
        self.assertFalse(ok)
        self.assertIn("current game", info["reason"])

    def test_sanitizer_repairs_malformed_session_without_deleting_other_state(self):
        malformed = _player(
            trouble_brewing={
                "review": "999",
                "stores": {"water": -4},
                "boilers": [99],
                "automation_mode": "unknown",
            },
            activity_session={"active_id": "trouble_brewing"},
            unrelated={"kept": True},
        )
        state = sanitize_trouble_brewing_state_pure(malformed)
        session = state["trouble_brewing"]
        self.assertEqual(session["review"], TROUBLE_BREWING_EVENT_REVIEWS - 1)
        self.assertEqual(session["stores"]["water"], 0)
        self.assertEqual(session["boilers"], [10, 3, 3])
        self.assertEqual(session["automation_mode"], "casual")
        self.assertEqual(malformed["unrelated"], {"kept": True})


class TroubleBrewingRaceTests(unittest.TestCase):
    def test_casual_completes_source_recipe_packs_rum_and_pays_exact_rewards(self):
        player = _entered()
        duties = []
        for _ in range(TROUBLE_BREWING_EVENT_REVIEWS):
            player, result = apply_trouble_brewing_review_pure(
                player,
                productive=True,
                opponent_roll=0.9,
                sabotage_roll=0.9,
            )
            duties.append(result["duty"])

        self.assertTrue(result["terminal"])
        self.assertEqual(result["player_rum"], 1)
        self.assertEqual(result["opponent_rum"], 1)
        self.assertEqual(result["outcome"], "drew")
        self.assertEqual(result["pieces_of_eight"], 24)
        self.assertEqual(result["skill_xp"]["crafting"], 100.0)
        self.assertEqual(result["skill_xp"]["cooking"], 810.0)
        self.assertIn("pack_rum", duties)
        self.assertIn("tend_boilers", duties)
        self.assertEqual(player["trouble_brewing"], {})
        self.assertEqual(player["activity_session"], {"active_id": ""})

    def test_again_advances_the_race_without_doing_a_player_duty(self):
        player = _entered()
        player, result = apply_trouble_brewing_review_pure(
            player,
            productive=False,
            opponent_roll=0.0,
            sabotage_roll=0.9,
        )
        session = player["trouble_brewing"]
        self.assertEqual(result["duty"], "idle")
        self.assertEqual(session["stores"], {key: 0 for key in session["stores"]})
        self.assertEqual(session["opponent_progress"], 2)
        self.assertEqual(session["review"], 1)

    def test_opponent_sabotage_forces_the_next_productive_review_to_repair(self):
        player = _entered()
        for _ in range(3):
            player, _result = apply_trouble_brewing_review_pure(
                player,
                productive=True,
                opponent_roll=0.9,
                sabotage_roll=0.0,
            )
        self.assertTrue(player["trouble_brewing"]["repair_required"])
        player, result = apply_trouble_brewing_review_pure(
            player,
            productive=True,
            duty="sabotage",
            opponent_roll=0.9,
            sabotage_roll=0.0,
        )
        self.assertEqual(result["duty"], "repair")
        self.assertIn("Repaired", result["status"])
        self.assertFalse(player["trouble_brewing"]["repair_required"])
        self.assertEqual(player["trouble_brewing"]["xp"]["crafting"], 25.0)

    def test_advanced_sabotage_reduces_and_temporarily_stops_opponent_progress(self):
        player, ok, _info = enter_trouble_brewing_pure(
            _player(), {"automation_mode": "advanced", "duty": "sabotage"}
        )
        self.assertTrue(ok)
        player["trouble_brewing"]["opponent_progress"] = 7
        player, result = apply_trouble_brewing_review_pure(
            player,
            productive=True,
            opponent_roll=0.0,
            sabotage_roll=0.9,
        )
        self.assertEqual(result["duty"], "sabotage")
        self.assertEqual(player["trouble_brewing"]["opponent_progress"], 4)
        self.assertEqual(player["trouble_brewing"]["opponent_slowed"], 1)
        self.assertEqual(player["trouble_brewing"]["xp"]["firemaking"], 50.0)

    def test_unpacked_bottle_is_lost_when_the_next_batch_finishes(self):
        player = _entered()
        session = player["trouble_brewing"]
        session["stores"] = {
            "water": 5,
            "coloured_water": 3,
            "sweetgrubs": 1,
            "scrapey_bark": 1,
            "bitternut": 1,
        }
        session["boilers"] = [10, 10, 10]
        session["pending_bottle"] = True
        player, result = apply_trouble_brewing_review_pure(
            player,
            productive=False,
            opponent_roll=0.9,
            sabotage_roll=0.9,
        )
        self.assertTrue(result["brewed"])
        self.assertTrue(player["trouble_brewing"]["pending_bottle"])
        self.assertEqual(player["trouble_brewing"]["spilled_rum"], 1)

    def test_leave_forfeits_match_rewards(self):
        player = _entered(trouble_brewing_pieces_of_eight=7)
        player["trouble_brewing"]["contribution"] = 99
        left, ok, info = leave_trouble_brewing_pure(player)
        self.assertTrue(ok)
        self.assertEqual(left["trouble_brewing_pieces_of_eight"], 7)
        self.assertEqual(left["trouble_brewing"], {})
        self.assertIn("forfeited", info["message"])


class TroubleBrewingRewardTests(unittest.TestCase):
    def test_reward_shop_spends_wallet_and_banks_the_zero_stat_hat(self):
        player = _player(trouble_brewing_pieces_of_eight=50)
        bought, ok, info = buy_trouble_brewing_reward_pure(
            player, "blue_tricorn_hat"
        )
        self.assertTrue(ok, info)
        self.assertEqual(bought["trouble_brewing_pieces_of_eight"], 0)
        self.assertEqual(bought["inventory"]["Blue tricorn hat"], 1)
        view = trouble_brewing_view_pure(bought)
        self.assertEqual(view["rewards"][0]["pieces_of_eight"], 50)

        _same, ok, info = buy_trouble_brewing_reward_pure(
            bought, "blue_tricorn_hat"
        )
        self.assertFalse(ok)
        self.assertIn("Requires 50", info["reason"])

    def test_command_router_blocks_shopping_during_a_live_game(self):
        player = _entered(trouble_brewing_pieces_of_eight=50)
        unchanged, ok, info = apply_trouble_brewing_command_pure(
            player,
            "buy_reward",
            {"reward_id": "blue_tricorn_hat"},
        )
        self.assertFalse(ok)
        self.assertIn("current game", info["reason"])
        self.assertEqual(unchanged["trouble_brewing_pieces_of_eight"], 50)
        self.assertEqual(unchanged["inventory"], {})


if __name__ == "__main__":
    unittest.main()
