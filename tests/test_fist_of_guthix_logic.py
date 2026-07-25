import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.fist_of_guthix_data import FIST_OF_GUTHIX_INITIAL_SUPPLIES
from ankiscape.logic.fist_of_guthix_logic import (
    apply_fist_of_guthix_command_pure,
    apply_fist_of_guthix_review_pure,
    default_fist_of_guthix_state_pure,
    fist_of_guthix_view_pure,
    sanitize_fist_of_guthix_state_pure,
    start_fist_of_guthix_match_pure,
)


def _player():
    return {
        "inventory": {},
        "equipment": {},
        "equipment_instances": {},
        "equipment_instance_next_id": 1,
        "attack_level": 50,
        "strength_level": 50,
        "defense_level": 50,
        "constitution_level": 50,
        "magic_level": 50,
        "ranged_level": 50,
        "prayer_level": 1,
        "summoning_level": 1,
        "attack_exp": 0.0,
        "constitution_exp": 0.0,
        "fist_of_guthix": default_fist_of_guthix_state_pure(),
    }


def _combat_result(*, ticks=6, killed=False, died=False, xp=None, runes=None):
    return {
        "ticks_elapsed": ticks,
        "player_lifepoints": 500,
        "killed": killed,
        "died": died,
        "xp_rewards": dict(xp or {}),
        "runes_used": dict(runes or {}),
    }


class FistOfGuthixLogicTest(unittest.TestCase):
    def _started(self, *, role="hunted", stance="centre"):
        player = _player()
        player["fist_of_guthix"]["tutorial_complete"] = True
        player, ok, _ = start_fist_of_guthix_match_pure(
            player, iter((0.4, 0.5, 0.2, 0.8, 0.1)).__next__
        )
        self.assertTrue(ok)
        active = player["fist_of_guthix"]["active_match"]
        active["first_player_role"] = role
        active["player_role"] = role
        active["player_stance"] = stance
        return player

    def test_fiara_tutorial_gates_matchmaking_and_pairing_is_not_level_banded(self):
        player = _player()
        blocked, ok, result = start_fist_of_guthix_match_pure(player)
        self.assertFalse(ok)
        self.assertIn("Fiara", result["reason"])

        player, ok, _ = apply_fist_of_guthix_command_pure(player, "talk_fiara")
        self.assertTrue(ok)
        player, ok, result = start_fist_of_guthix_match_pure(
            player, iter((0.999, 0.5, 0.2, 0.8, 0.1)).__next__
        )
        self.assertTrue(ok)
        self.assertGreater(result["opponent"]["combat_level"], 100)
        self.assertEqual(blocked["fist_of_guthix"]["active_match"], {})

    def test_charge_rate_uses_exact_residual_and_temporary_supplies_never_leak(self):
        player = self._started(role="hunted", stance="centre")
        original_inventory = dict(player["inventory"])
        with patch(
            "ankiscape.logic.fist_of_guthix_logic.apply_combat_burst_pure",
            return_value=({"combat_encounter": {}}, True, _combat_result()),
        ):
            first, ok, result = apply_fist_of_guthix_review_pure(player)
            second, ok2, result2 = apply_fist_of_guthix_review_pure(first)
        self.assertTrue(ok and ok2)
        self.assertEqual(result["charge_gained"], 100)
        self.assertEqual(result2["charge_gained"], 101)
        self.assertEqual(second["fist_of_guthix"]["active_match"]["player_charges"], 201)
        self.assertEqual(second["inventory"], original_inventory)
        self.assertEqual(
            second["fist_of_guthix"]["active_match"]["temporary_supplies"],
            FIST_OF_GUTHIX_INITIAL_SUPPLIES,
        )

    def test_real_combat_engine_advances_one_exact_six_tick_review(self):
        player = _player()
        player["fist_of_guthix"]["tutorial_complete"] = True
        player["combat_attack_style"] = "accurate"
        player["current_combat_spell"] = "wind_strike"
        rolls = iter((0.4, 0.5, 0.2, 0.8, 0.1, *(0.5 for _ in range(200))))
        updated, ok, result = apply_fist_of_guthix_review_pure(
            player, rng=lambda: next(rolls, 0.5)
        )
        self.assertTrue(ok)
        self.assertEqual(result["ticks_elapsed"], 6)
        self.assertEqual(updated["fist_of_guthix"]["active_match"]["round_ticks"], 6)
        self.assertGreater(sum(result["xp_rewards"].values()), 0)

    def test_all_combat_xp_is_halved_including_fixed_magic_xp(self):
        player = self._started(role="hunted")
        with patch(
            "ankiscape.logic.fist_of_guthix_logic.apply_combat_burst_pure",
            return_value=(
                {"combat_encounter": {}},
                True,
                _combat_result(xp={"magic_exp": 20.0, "constitution_exp": 4.0}),
            ),
        ):
            updated, ok, result = apply_fist_of_guthix_review_pure(player)
        self.assertTrue(ok)
        self.assertEqual(result["xp_rewards"], {"magic_exp": 10.0, "constitution_exp": 2.0})
        self.assertEqual(updated["magic_exp"], 10.0)
        self.assertEqual(updated["constitution_exp"], 2.0)

    def test_safe_arena_death_does_not_discharge_equipped_gauntlets(self):
        player = self._started(role="hunted")
        player["equipment"] = {"hands": "Bronze gauntlets"}
        player["equipment_instances"] = {
            "equipment-1": {
                "family_id": "bronze_gauntlets",
                "item_name": "Bronze gauntlets",
                "condition": 1,
                "location": "equipped:hands",
                "last_slot": "hands",
            }
        }
        player["equipment_instance_next_id"] = 2
        with patch(
            "ankiscape.logic.fist_of_guthix_logic.apply_combat_burst_pure",
            return_value=({"combat_encounter": {}}, True, _combat_result(died=True)),
        ):
            updated, ok, result = apply_fist_of_guthix_review_pure(player)
        self.assertTrue(ok)
        self.assertTrue(result["round_complete"])
        self.assertEqual(updated["equipment"]["hands"], "Bronze gauntlets")
        self.assertEqual(updated["equipment_instances"]["equipment-1"]["condition"], 1)

    def test_round_boundary_reports_completed_role_then_swaps_roles(self):
        player = self._started(role="hunter")
        with patch(
            "ankiscape.logic.fist_of_guthix_logic.apply_combat_burst_pure",
            return_value=({"combat_encounter": {}}, True, _combat_result(killed=True)),
        ):
            updated, ok, result = apply_fist_of_guthix_review_pure(player)
        self.assertTrue(ok)
        self.assertEqual(result["player_role"], "hunter")
        self.assertEqual(result["next_role"], "hunted")
        self.assertEqual(updated["fist_of_guthix"]["active_match"]["player_role"], "hunted")

    def test_forfeit_penalty_halves_only_the_next_win_reward(self):
        player = self._started(role="hunted")
        player, ok, result = apply_fist_of_guthix_command_pure(player, "forfeit")
        self.assertTrue(ok)
        self.assertEqual(result["tokens"], 0)
        self.assertTrue(player["fist_of_guthix"]["forfeit_penalty"])

        player, ok, _ = start_fist_of_guthix_match_pure(
            player, iter((0.2, 0.5, 0.1, 0.8, 0.1)).__next__
        )
        self.assertTrue(ok)
        active = player["fist_of_guthix"]["active_match"]
        active["round_index"] = 2
        active["player_charges"] = 5_000
        active["opponent_charges"] = 1
        active["round_ticks"] = 999
        with patch(
            "ankiscape.logic.fist_of_guthix_logic.apply_combat_burst_pure",
            return_value=({"combat_encounter": {}}, True, _combat_result(ticks=1)),
        ):
            won, ok, result = apply_fist_of_guthix_review_pure(player)
        self.assertTrue(ok)
        self.assertEqual(result["match_result"]["outcome"], "win")
        self.assertGreater(result["match_result"]["tokens"], 0)
        self.assertFalse(won["fist_of_guthix"]["forfeit_penalty"])

    def test_reward_shop_preserves_per_copy_condition_and_free_uncharge(self):
        player = _player()
        player["fist_of_guthix"]["tokens"] = 100
        player, ok, bought = apply_fist_of_guthix_command_pure(
            player, "buy_reward", {"reward_id": "combat_hood"}
        )
        self.assertTrue(ok)
        instance_id = bought["instance_id"]
        self.assertEqual(player["inventory"]["Combat hood 100"], 1)
        self.assertEqual(player["equipment_instances"][instance_id]["condition"], 90_000)

        player, ok, result = apply_fist_of_guthix_command_pure(
            player, "uncharge_reward", {"reward_id": "combat_hood"}
        )
        self.assertTrue(ok)
        self.assertEqual(result["tokens_spent"], 0)
        self.assertEqual(player["inventory"]["Combat hood 0"], 1)
        player, ok, _ = apply_fist_of_guthix_command_pure(
            player, "recharge_reward", {"reward_id": "combat_hood"}
        )
        self.assertTrue(ok)
        self.assertEqual(player["inventory"]["Combat hood 100"], 1)

    def test_sanitizer_and_view_clamp_corrupt_state(self):
        state = sanitize_fist_of_guthix_state_pure(
            {"tokens": -5, "rating": "bad", "selected_stance": "teleport"}
        )
        self.assertEqual(state["tokens"], 0)
        self.assertEqual(state["rating"], 1_000)
        self.assertEqual(state["selected_stance"], "hybrid")
        view = fist_of_guthix_view_pure({"fist_of_guthix": state})
        self.assertFalse(view["active"])
        self.assertEqual(view["match"], {})


if __name__ == "__main__":
    unittest.main()
