"""The live combat runtime stops on the exact danger tick (decision 5)."""

import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.logic_pure import logic_pure_combat_engine as engine
from ankiscape.runtime import runtime_actions_combat as combat
from tests.test_combat_logic import _player
from tests.test_runtime_actions import _context


ENEMY = {
    "display_name": "Pace target", "level": 1, "group": "Test",
    "stats": {"attack": 1, "strength": 1, "defence": 1, "hitpoints": 1000},
    "bonuses": {}, "attack_speed": 4,
    "drops": {"guaranteed": (("Bones", 1),), "tables": ()}, "source": "test",
}


def answer_combat(player=None, *, enemy=None, hits=()):
    player = _player(current_combat_target="chicken", combat_auto_flee=False) if player is None else player
    if not player.get("combat_encounter"):
        player["combat_encounter"] = {
            "target_id": player["current_combat_target"],
            "enemy_lifepoints": (enemy or ENEMY)["stats"]["hitpoints"],
            "enemy_attack_ticks_remaining": 0,
        }
    calls = {"xp": [], "saves": 0, "errors": []}
    ctx = _context(player, calls, review_action_multiplier=10)
    ctx.cadence_live_enabled = True
    rolls = iter(()) if callable(hits) else iter(hits)
    with patch.object(combat, "COMBAT_ENEMY_DATA", {player["current_combat_target"]: enemy or ENEMY}), patch.object(
        engine, "_combat_roll_hit", side_effect=hits if callable(hits) else lambda *_args, **_kw: next(rolls, (False, 0))
    ):
        progressed = combat.handle_combat_answer(ctx)
    return ctx, calls, progressed


class CombatDangerStopsTests(unittest.TestCase):
    def test_low_lifepoints_without_food_carries_the_encounter_on_the_hit_tick(self):
        ctx, _calls, ok = answer_combat(hits=((True, 1), (True, 65)))
        self.assertTrue(ok)
        self.assertEqual(ctx.card.stop_reason, "low_lp_no_food")
        result = ctx.player_data["combat_last_result"]
        self.assertEqual((result["ticks_elapsed"], result["player_lifepoints"]), (1, 35))
        self.assertEqual(ctx.player_data["combat_encounter"]["enemy_lifepoints"], 999)

    def test_auto_flee_has_priority_over_the_low_lifepoints_hold(self):
        player = _player(combat_auto_flee=True)
        ctx, _calls, ok = answer_combat(player, hits=((True, 1), (True, 65)))
        self.assertTrue(ok)
        self.assertEqual(ctx.card.stop_reason, "fled")
        self.assertEqual(ctx.player_data["combat_last_result"]["ticks_elapsed"], 1)
        self.assertEqual(ctx.player_data["combat_encounter"], {})

    def test_poison_start_stops_on_its_application_tick(self):
        ctx, _calls, ok = answer_combat(enemy={**ENEMY, "poison_damage": 10})
        self.assertTrue(ok)
        self.assertEqual(ctx.card.stop_reason, "poison_started")
        self.assertEqual(ctx.player_data["combat_last_result"]["ticks_elapsed"], 1)
        self.assertIn("poison", ctx.player_data["combat_status_effects"])
        self.assertEqual(ctx.player_data["combat_encounter"]["enemy_lifepoints"], 1000)

    def test_prayer_empty_stops_on_the_drain_tick(self):
        player = _player(prayer_level=99, combat_prayer_points=1,
                         combat_prayer_drain_counter=59.0,
                         combat_selected_prayers=["thick_skin"], combat_prayer_uptime="100")
        ctx, _calls, ok = answer_combat(player)
        self.assertTrue(ok)
        self.assertEqual(ctx.card.stop_reason, "prayer_empty")
        self.assertEqual(ctx.player_data["combat_last_result"]["ticks_elapsed"], 1)
        self.assertEqual(ctx.player_data["combat_prayer_points"], 0)
        self.assertEqual(ctx.player_data["combat_encounter"]["enemy_lifepoints"], 1000)

    def test_death_uses_the_settled_stop_name_and_drops_the_encounter(self):
        ctx, _calls, ok = answer_combat(hits=((False, 0), (True, 100)))
        self.assertTrue(ok)
        self.assertEqual(ctx.card.stop_reason, "died")
        self.assertEqual(ctx.player_data["combat_last_result"]["ticks_elapsed"], 1)
        self.assertEqual(ctx.player_data["combat_encounter"], {})

    def test_empty_ammo_or_runes_carries_the_fight_at_the_next_attack(self):
        cases = (
            ("out_of_ammo", "ranged_rapid", "Shortbow", {"ammo": {"Bronze arrows": 1}}, 4),
            ("out_of_runes", "magic_standard", "Staff", {"runes": {"Air rune": 1, "Mind rune": 1}}, 6),
        )
        for reason, style, weapon, loadout, elapsed in cases:
            with self.subTest(reason=reason):
                player = _player(combat_auto_flee=False, combat_attack_style=style,
                                 equipment={"weapon": weapon}, combat_supply_loadout=loadout,
                                 combat_encounter={"target_id": "chicken", "enemy_lifepoints": 999})
                ctx, _calls, ok = answer_combat(player)
                self.assertTrue(ok)
                self.assertEqual(ctx.card.stop_reason, reason)
                self.assertEqual(ctx.player_data["combat_last_result"]["ticks_elapsed"], elapsed)
                self.assertEqual(ctx.player_data["combat_encounter"]["enemy_lifepoints"], 999)

    def test_bank_trip_stops_after_the_kill_without_starting_the_trip(self):
        player = _player(combat_auto_flee=False, combat_attack_style="magic_standard",
                         equipment={"weapon": "Staff"},
                         inventory={"Air rune": 5, "Mind rune": 5},
                         combat_supply_loadout={"runes": {"Air rune": 1, "Mind rune": 1}},
                         combat_encounter={"target_id": "chicken", "enemy_lifepoints": 1})
        ctx, _calls, ok = answer_combat(player, hits=((True, 1),))
        self.assertTrue(ok)
        result = ctx.player_data["combat_last_result"]
        self.assertEqual(ctx.card.stop_reason, "bank_trip")
        self.assertEqual((result["kills"], result["ticks_elapsed"]), (1, 1))
        self.assertEqual(ctx.player_data["combat_encounter"], {})
        self.assertFalse(ctx.player_data.get("combat_bank_run"))

    def test_same_tick_antipoison_cure_keeps_the_card_running(self):
        player = _player(combat_auto_flee=False,
                         combat_supply_loadout={"potions": {"Antipoison (4)": 1}})
        ctx, _calls, ok = answer_combat(player, enemy={**ENEMY, "poison_damage": 10})
        self.assertTrue(ok)
        self.assertEqual(ctx.card.stop_reason, "")
        self.assertEqual(ctx.player_data["combat_last_result"]["ticks_elapsed"], 60)
        self.assertNotIn("poison", ctx.player_data["combat_status_effects"])

    def test_the_last_slayer_kill_stops_before_another_enemy_spawns(self):
        player = _player(current_combat_target="cow", combat_auto_flee=False,
                         slayer_assignment={"master_id": "turael_spria", "family_id": "cows",
                                            "initial_count": 1, "remaining": 1},
                         combat_encounter={"target_id": "cow", "enemy_lifepoints": 1})
        ctx, _calls, ok = answer_combat(player, hits=((True, 1),))
        self.assertTrue(ok)
        result = ctx.player_data["combat_last_result"]
        self.assertEqual((result["kills"], result["ticks_elapsed"]), (1, 1))
        self.assertEqual(ctx.card.stop_reason, "slayer_task_complete")
        self.assertEqual(ctx.player_data["slayer_assignment"]["remaining"], 0)
        self.assertEqual(ctx.player_data["combat_encounter"], {})
