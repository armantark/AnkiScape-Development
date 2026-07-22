from __future__ import annotations

import copy
import unittest
from dataclasses import asdict
from unittest.mock import patch

from barbarian_assault_data import (
    BARBARIAN_ASSAULT_QUEEN_EGGS,
    BARBARIAN_ASSAULT_WAVES,
    RUNNER_BOOTS_ITEM_ID,
    barbarian_assault_equipment_data_as_dict,
    barbarian_assault_role_scores_pure,
    barbarian_assault_wave_points_pure,
)
from barbarian_assault_logic import (
    apply_barbarian_assault_review_pure,
    buy_runner_boots_pure,
    complete_barbarian_assault_tutorial_pure,
    enter_barbarian_assault_pure,
    leave_barbarian_assault_pure,
    sanitize_barbarian_assault_state_pure,
    set_barbarian_assault_policy_pure,
)


def _player(**overrides):
    player = {
        "activity_session": {"active_id": ""},
        "current_utility": "make_soft_clay",
        "current_combat_target": "chicken",
        "combat_encounter": {},
        "combat_lifepoints": 400,
        "constitution_level": 40,
        "inventory": {},
        "equipment": {},
    }
    player.update(overrides)
    return player


def _ready(**overrides):
    player = _player(**overrides)
    player, ok, info = complete_barbarian_assault_tutorial_pure(player)
    assert ok, info
    return player


def _entered(**overrides):
    player, ok, info = enter_barbarian_assault_pure(_ready(**overrides))
    assert ok, info
    return player


def _combat_stub(*, died=False):
    def _apply(data, enemies, _equipment, **kwargs):
        updated = copy.deepcopy(data)
        encounter = dict(updated.get("combat_encounter") or {})
        encounter["enemy_lifepoints"] = max(
            1, int(encounter.get("enemy_lifepoints", 1)) - 100
        )
        updated["combat_encounter"] = encounter
        if died:
            updated["combat_lifepoints"] = 400
        return updated, True, {
            "died": died,
            "safe_death": died,
            "player_damage": 100,
            "enemy_lifepoints": encounter["enemy_lifepoints"],
            "xp_rewards": {},
            "captured_ticks": kwargs.get("ticks"),
            "captured_live": kwargs.get("live_cadence"),
            "enemy": next(iter(enemies.values())),
        }

    return _apply


class BarbarianAssaultDataTests(unittest.TestCase):
    def test_period_wave_rosters_and_point_formulas_are_explicit(self):
        self.assertEqual(len(BARBARIAN_ASSAULT_WAVES), 10)
        self.assertEqual(
            (BARBARIAN_ASSAULT_WAVES[0].fighters, BARBARIAN_ASSAULT_WAVES[0].runners),
            (4, 2),
        )
        self.assertEqual(
            (BARBARIAN_ASSAULT_WAVES[8].fighters, BARBARIAN_ASSAULT_WAVES[8].runners),
            (8, 9),
        )
        self.assertEqual(
            barbarian_assault_role_scores_pure(1),
            {"attacker": 6, "collector": 13, "defender": 3, "healer": 1},
        )
        self.assertEqual(
            barbarian_assault_wave_points_pure(10, "defender"),
            {"attacker": 5, "collector": 5, "defender": 80, "healer": 5},
        )

    def test_runner_boots_keep_period_identity_and_equipment_block(self):
        boots = barbarian_assault_equipment_data_as_dict()["Runner boots"]
        self.assertEqual(boots.source_item_id, RUNNER_BOOTS_ITEM_ID)
        self.assertEqual(boots.slot, "feet")
        self.assertEqual(boots.skill_requirements, (("defense", 40),))
        bonuses = asdict(boots.bonuses)
        self.assertEqual(bonuses["defence_stab"], 12)
        self.assertEqual(bonuses["defence_crush"], 14)
        self.assertEqual(bonuses["melee_strength"], 2)
        self.assertEqual(bonuses["attack_magic"], -3)


class BarbarianAssaultStateTests(unittest.TestCase):
    def test_entry_requires_the_period_tutorial_and_owns_the_session(self):
        original = _player()
        unchanged, ok, info = enter_barbarian_assault_pure(original)
        self.assertFalse(ok)
        self.assertTrue(info["requires_tutorial"])
        self.assertEqual(unchanged, original)

        entered, ok, info = enter_barbarian_assault_pure(_ready())
        self.assertTrue(ok, info)
        self.assertEqual(entered["activity_session"], {"active_id": "barbarian_assault"})
        self.assertEqual(entered["barbarian_assault"]["wave"], 1)
        self.assertEqual(entered["barbarian_assault"]["role"], "attacker")
        self.assertEqual(entered["barbarian_assault"]["previous_combat_target"], "chicken")

    def test_sanitizer_preserves_wallets_and_rejects_foreign_session_ownership(self):
        state = sanitize_barbarian_assault_state_pure(
            _player(
                barbarian_assault={"wave": 99, "role": "unknown"},
                barbarian_assault_points={"attacker": 999, "collector": -2},
                activity_session={"active_id": "barrows"},
            )
        )
        self.assertEqual(state["barbarian_assault"], {})
        self.assertEqual(state["barbarian_assault_points"]["attacker"], 999)
        self.assertEqual(state["barbarian_assault_points"]["collector"], 0)

    def test_casual_rotates_to_the_lowest_wallet_and_advanced_keeps_role(self):
        data = _entered()
        with patch("barbarian_assault_logic.apply_combat_burst_pure", _combat_stub()):
            data, ok, result = apply_barbarian_assault_review_pure(
                data, lambda: 0.5, productive=True
            )
        self.assertTrue(ok, result)
        self.assertEqual(result["wave_completed"], 1)
        self.assertGreater(data["barbarian_assault_points"]["attacker"], 0)
        self.assertEqual(data["barbarian_assault"]["role"], "collector")

        player, ok, info = set_barbarian_assault_policy_pure(
            _ready(), {"automation_mode": "advanced", "role": "healer"}
        )
        self.assertTrue(ok, info)
        player, ok, info = enter_barbarian_assault_pure(player)
        self.assertTrue(ok, info)
        self.assertEqual(player["barbarian_assault"]["role"], "healer")

    def test_role_cannot_change_during_the_persistent_queen_wave(self):
        data = _entered()
        data["barbarian_assault"].update({"wave": 10, "phase": "queen"})
        unchanged, ok, info = set_barbarian_assault_policy_pure(
            data, {"automation_mode": "advanced", "role": "healer"}
        )
        self.assertFalse(ok)
        self.assertIn("wave 10", info["reason"])
        self.assertEqual(unchanged, data)


class BarbarianAssaultWaveTests(unittest.TestCase):
    def test_attacker_uses_one_live_six_tick_combat_slice(self):
        data = _entered()
        with patch("barbarian_assault_logic.apply_combat_burst_pure", _combat_stub()):
            updated, ok, result = apply_barbarian_assault_review_pure(
                data, lambda: 0.5, productive=True
            )
        self.assertTrue(ok, result)
        self.assertEqual(result["captured_ticks"], 6)
        self.assertTrue(result["captured_live"])
        self.assertEqual(result["enemy"]["xp_multiplier"], 0.0)
        self.assertEqual(updated["barbarian_assault"]["wave"], 2)

    def test_again_keeps_the_same_wave_without_an_invented_miss_roll(self):
        data = _entered()
        updated, ok, result = apply_barbarian_assault_review_pure(
            data, lambda: 0.5, productive=False
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["duty"], "idle")
        self.assertEqual(updated["barbarian_assault"]["wave"], 1)
        self.assertEqual(updated["barbarian_assault_points"], {
            "attacker": 0,
            "collector": 0,
            "defender": 0,
            "healer": 0,
        })

    def test_safe_attacker_death_restarts_the_wave_for_zero_points(self):
        data = _entered()
        with patch(
            "barbarian_assault_logic.apply_combat_burst_pure", _combat_stub(died=True)
        ):
            updated, ok, result = apply_barbarian_assault_review_pure(
                data, lambda: 0.5, productive=True
            )
        self.assertTrue(ok, result)
        self.assertTrue(result["safe_death"])
        self.assertTrue(result["wave_restarted"])
        self.assertEqual(updated["barbarian_assault"]["wave"], 1)
        self.assertEqual(updated["barbarian_assault_points"]["attacker"], 0)

    def test_complete_run_builds_eight_omega_eggs_and_pays_exact_wave_ten_points(self):
        data, ok, info = set_barbarian_assault_policy_pure(
            _ready(), {"automation_mode": "advanced", "role": "defender"}
        )
        self.assertTrue(ok, info)
        data, ok, info = enter_barbarian_assault_pure(data)
        self.assertTrue(ok, info)

        for _ in range(10):
            data, ok, result = apply_barbarian_assault_review_pure(
                data, lambda: 0.5, productive=True
            )
            self.assertTrue(ok, result)
        self.assertTrue(result["queen_started"])
        self.assertEqual(data["barbarian_assault"]["phase"], "queen")

        before = dict(data["barbarian_assault_points"])
        for _ in range(BARBARIAN_ASSAULT_QUEEN_EGGS):
            data, ok, result = apply_barbarian_assault_review_pure(
                data, lambda: 0.5, productive=True
            )
            self.assertTrue(ok, result)

        self.assertTrue(result["terminal"])
        self.assertTrue(result["queen_defeated"])
        self.assertEqual(result["points"], {
            "attacker": 5,
            "collector": 5,
            "defender": 80,
            "healer": 5,
        })
        self.assertEqual(data["barbarian_assault_queen_kills"], 1)
        self.assertTrue(data["barbarian_assault_queen_credit"])
        self.assertEqual(data["barbarian_assault"], {})
        self.assertEqual(data["current_combat_target"], "chicken")
        self.assertEqual(
            data["barbarian_assault_points"]["defender"] - before["defender"],
            80,
        )

    def test_queen_safe_death_restarts_all_of_wave_ten(self):
        data = _entered(combat_lifepoints=10)
        data["barbarian_assault"].update(
            {"wave": 10, "phase": "queen", "omega_eggs": 3, "queen_lifepoints": 1561}
        )
        updated, ok, result = apply_barbarian_assault_review_pure(
            data, lambda: 0.5, productive=False
        )
        self.assertTrue(ok, result)
        self.assertTrue(result["safe_death"])
        self.assertTrue(result["wave_restarted"])
        self.assertEqual(updated["barbarian_assault"]["phase"], "wave")
        self.assertEqual(updated["barbarian_assault"]["omega_eggs"], 0)
        self.assertEqual(updated["combat_lifepoints"], 400)


class BarbarianAssaultRewardAndExitTests(unittest.TestCase):
    def test_runner_boots_cost_one_hundred_points_in_every_role(self):
        points = {role_id: 100 for role_id in ("attacker", "collector", "defender", "healer")}
        bought, ok, info = buy_runner_boots_pure(
            _ready(barbarian_assault_points=points)
        )
        self.assertTrue(ok, info)
        self.assertEqual(bought["barbarian_assault_points"], {
            "attacker": 0,
            "collector": 0,
            "defender": 0,
            "healer": 0,
        })
        self.assertEqual(bought["inventory"]["Runner boots"], 1)

        _same, ok, info = buy_runner_boots_pure(_ready())
        self.assertFalse(ok)
        self.assertIn("every role", info["reason"])

    def test_leaving_forfeits_only_the_current_run_and_restores_combat_target(self):
        data = _entered(
            barbarian_assault_points={
                "attacker": 12,
                "collector": 13,
                "defender": 14,
                "healer": 15,
            }
        )
        left, ok, info = leave_barbarian_assault_pure(data)
        self.assertTrue(ok, info)
        self.assertEqual(left["barbarian_assault"], {})
        self.assertEqual(left["current_combat_target"], "chicken")
        self.assertEqual(left["barbarian_assault_points"]["healer"], 15)


if __name__ == "__main__":
    unittest.main(verbosity=2)
