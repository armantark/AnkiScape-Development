"""An ordinary combat card spends its remaining play time on the same target (decision 6)."""

import unittest

import pkg_alias  # noqa: F401
from tests.pace.test_combat_danger_stops import ENEMY, answer_combat
from tests.test_combat_logic import _player


def player_hits_only(*_args, **kwargs):
    return (True, 10) if "blocked" in kwargs else (False, 0)


class CombatChainTests(unittest.TestCase):
    def test_a_killing_hit_that_also_kills_the_player_reports_death(self):
        enemy = {**ENEMY, "melee_recoil_damage": 100, "stats": {**ENEMY["stats"], "hitpoints": 1}}
        ctx, _calls, ok = answer_combat(enemy=enemy, hits=player_hits_only)
        self.assertTrue(ok)
        result = ctx.player_data["combat_last_result"]
        self.assertEqual((result["kills"], result["ticks_elapsed"]), (1, 1))
        self.assertTrue(result["died"])
        self.assertEqual(ctx.card.stop_reason, "died")
        self.assertEqual(ctx.player_data["combat_encounter"], {})

    def test_a_reflected_kill_keeps_the_same_tick_low_lifepoint_stop(self):
        player = _player(combat_auto_flee=False, combat_attack_style="magic_standard",
                         current_combat_spell="confuse", equipment={"weapon": "Staff"},
                         combat_supply_loadout={"runes": {"Water rune": 100, "Earth rune": 100, "Body rune": 100}},
                         combat_encounter={"target_id": "chicken", "enemy_lifepoints": 1,
                                           "player_attack_ticks_remaining": 99,
                                           "enemy_attack_ticks_remaining": 0, "vengeance_pending": True})
        ctx, _calls, ok = answer_combat(player, hits=((True, 65),))
        self.assertTrue(ok)
        result = ctx.player_data["combat_last_result"]
        self.assertEqual((result["kills"], result["ticks_elapsed"]), (1, 1))
        self.assertEqual(ctx.card.stop_reason, "low_lp_no_food")
        self.assertEqual(ctx.player_data["combat_encounter"], {})

    def test_two_kills_and_the_half_fought_third_enemy_share_one_speed_ten_card(self):
        enemy = {**ENEMY, "stats": {**ENEMY["stats"], "hitpoints": 60}}
        ctx, _calls, ok = answer_combat(enemy=enemy, hits=player_hits_only)
        self.assertTrue(ok)
        result = ctx.player_data["combat_last_result"]
        self.assertEqual((result["kills"], result["ticks_elapsed"]), (2, 60))
        self.assertEqual(result["drops"], {"Bones": 2})
        self.assertEqual(ctx.player_data["combat_encounter"]["enemy_lifepoints"], 30)
        self.assertEqual(ctx.player_data["combat_encounter"]["player_attack_ticks_remaining"], 0)
        self.assertEqual(ctx.card.stop_reason, "")

    def test_slayer_finishes_at_the_last_assigned_kill_without_overshoot(self):
        player = _player(current_combat_target="cow", combat_auto_flee=False,
                         slayer_assignment={"master_id": "turael_spria", "family_id": "cows",
                                            "initial_count": 2, "remaining": 2})
        enemy = {**ENEMY, "slayer_xp": 60, "stats": {**ENEMY["stats"], "hitpoints": 60}}
        ctx, _calls, ok = answer_combat(player, enemy=enemy, hits=player_hits_only)
        self.assertTrue(ok)
        result = ctx.player_data["combat_last_result"]
        self.assertEqual((result["kills"], result["ticks_elapsed"]), (2, 45))
        self.assertEqual(ctx.card.stop_reason, "slayer_task_complete")
        self.assertEqual(ctx.player_data["slayer_assignment"]["remaining"], 0)
        self.assertEqual(result["slayer"]["credited_kills"], 2)
        self.assertEqual(ctx.player_data["slayer_exp"], 120)
        self.assertEqual(ctx.player_data["combat_encounter"], {})

    def test_the_next_enemy_starts_with_fresh_magic_effects_and_curse_ramp(self):
        player = _player(combat_auto_flee=False, combat_attack_style="magic_standard",
                         current_combat_spell="confuse", equipment={"weapon": "Staff"},
                         combat_supply_loadout={"runes": {"Water rune": 100, "Earth rune": 100, "Body rune": 100}},
                         combat_encounter={"target_id": "chicken", "enemy_lifepoints": 1,
                                           "magic_effects_applied": ("attack_drain",),
                                           "spell_enemy_attack_factor": 0.2,
                                           "spell_enemy_defence_factor": 0.3,
                                           "curse_attack_count": 8})
        ctx, _calls, ok = answer_combat(player, hits=player_hits_only)
        self.assertTrue(ok)
        result = ctx.player_data["combat_last_result"]
        self.assertEqual((result["kills"], result["ticks_elapsed"]), (1, 60))
        encounter = ctx.player_data["combat_encounter"]
        self.assertEqual(encounter["magic_effects_applied"], ("attack_drain",))
        self.assertAlmostEqual(encounter["spell_enemy_attack_factor"], 0.95)
        self.assertEqual(encounter["spell_enemy_defence_factor"], 1.0)
        self.assertEqual(encounter["curse_attack_count"], 11)

    def test_a_reflected_kill_also_resets_the_next_enemys_magic_and_curse_state(self):
        player = _player(combat_auto_flee=False, constitution_level=99, combat_lifepoints=990,
                         combat_attack_style="magic_standard", current_combat_spell="confuse",
                         equipment={"weapon": "Staff"},
                         combat_supply_loadout={"runes": {"Water rune": 100, "Earth rune": 100, "Body rune": 100}},
                         combat_encounter={"target_id": "chicken", "enemy_lifepoints": 1,
                                           "player_attack_ticks_remaining": 99,
                                           "enemy_attack_ticks_remaining": 0, "vengeance_pending": True,
                                           "magic_effects_applied": ("attack_drain",),
                                           "spell_enemy_attack_factor": 0.2,
                                           "spell_enemy_defence_factor": 0.3, "curse_attack_count": 8})
        ctx, _calls, ok = answer_combat(player, hits=((True, 10),))
        self.assertTrue(ok)
        self.assertEqual(ctx.player_data["combat_last_result"]["kills"], 1)
        encounter = ctx.player_data["combat_encounter"]
        self.assertEqual(encounter["enemy_lifepoints"], 1000)
        self.assertAlmostEqual(encounter["spell_enemy_attack_factor"], 0.95)
        self.assertEqual(encounter["spell_enemy_defence_factor"], 1.0)
        self.assertEqual(encounter["curse_attack_count"], 0)
