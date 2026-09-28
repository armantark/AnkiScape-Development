"""Winter Storage must not undo the Thieving action that follows it."""

import copy
import dataclasses
import unittest

import pkg_alias  # noqa: F401
from ankiscape.runtime.runtime_actions import (
    handle_thieving_answer,
    run_answer_with_carried_overlay,
)
from tests.test_thieving import _context


def _player(target="pickpocket_man"):
    carried = {"Copper ore": 27, "Winter storage scroll": 1}
    return {
        "current_thieving": target,
        "thieving_level": 50,
        "thieving_exp": 0.0,
        "thieving_attempt_count": 0,
        "thieving_success_count": 0,
        "thieving_failure_count": 0,
        "thieving_stunned": False,
        "constitution_level": 10,
        "combat_lifepoints": 100,
        "inventory": dict(carried),
        "carried_inventory": {target: dict(carried)},
        "carried_churn": {target: 28},
        "cadence_profiles": {},
        "summoning_level": 99,
        "summoning_exp": 20.0,
        "summoning_state": {
            "active_follower": {"kind": "familiar", "entity_id": "packyak"},
            "special_move_points_current": 60,
            "target_policies": {
                target: {"winter_storage_priority": ["Copper ore"]},
            },
        },
        "quests": {},
        "completed_achievements": [],
    }


class TestWinterStorageRollback(unittest.TestCase):
    def _answer(self, player, rolls=(0.999, 0.0)):
        ctx, calls = _context(player, random_values=rolls)
        saves = []
        ctx = dataclasses.replace(
            ctx, save_player_data=lambda: saves.append(copy.deepcopy(player)),
        )
        result = run_answer_with_carried_overlay(ctx, "thieving", handle_thieving_answer)
        self.assertFalse(result)
        self.assertEqual(saves[-1], player)
        self.assertEqual(calls["errors"], [])
        target = player["current_thieving"]
        self.assertEqual(player["inventory"]["Winter storage scroll"], 0)
        self.assertEqual(player["carried_inventory"][target], {"Copper ore": 26})
        self.assertEqual(player["carried_churn"][target], 27)
        self.assertEqual(player["summoning_exp"], 24.8)
        self.assertEqual(player["summoning_state"]["special_move_points_current"], 48)
        self.assertEqual(player["summoning_state"]["event_log"][0]["kind"], "winter_storage")
        return calls

    def test_failed_pickpocket_keeps_damage_stun_and_failure_record(self):
        player = _player()
        self._answer(player)
        self.assertEqual(player["combat_lifepoints"], 90)
        self.assertTrue(player["thieving_stunned"])
        self.assertEqual(player["thieving_attempt_count"], 1)
        self.assertEqual(player["thieving_failure_count"], 1)
        self.assertEqual(player["thieving_exp"], 0.0)
        telemetry = player["action_telemetry"]["actions"]["thieving:pickpocket_man"]
        self.assertEqual(telemetry["failures"], 1)

    def test_wall_safe_failure_keeps_its_handler_owned_cadence(self):
        player = _player("wall_safe")
        self._answer(player, (85 / 255, 0.0))
        self.assertEqual(player["combat_lifepoints"], 80)
        self.assertTrue(player["thieving_stunned"])
        self.assertEqual(player["thieving_failure_count"], 1)
        self.assertEqual(player["cadence_profiles"]["thieving:wall_safe"]["assigned_reviews"], 1)

    def test_stun_recovery_is_not_undone(self):
        player = _player()
        player["thieving_stunned"] = True
        self._answer(player, ())
        self.assertFalse(player["thieving_stunned"])
        self.assertEqual(player["thieving_attempt_count"], 0)
        self.assertEqual(player["combat_lifepoints"], 100)

    def test_fatal_failure_keeps_the_grave_and_lost_familiar(self):
        player = _player()
        player["combat_lifepoints"] = 5
        player["equipment"] = {"weapon": "Bronze sword"}
        calls = self._answer(player)
        self.assertEqual(calls["deactivated"], 1)
        self.assertEqual(player["equipment"], {})
        self.assertEqual(player["combat_grave"]["items"], ["Bronze sword"])
        self.assertEqual(player["summoning_state"]["active_follower"], {})
        self.assertEqual(player["summoning_state"]["event_log"][-1]["kind"], "unsafe_player_death")
        self.assertTrue(player["thieving_stunned"])
        self.assertEqual(player["thieving_failure_count"], 1)

    def test_failure_keeps_auto_eaten_food_consumed(self):
        player = _player()
        player.update(
            combat_lifepoints=30,
            combat_auto_eat_threshold_percent=40,
            combat_auto_eat_food=["Lobster"],
            combat_supply_loadout={"food": {"Lobster": 1}},
        )
        self._answer(player)
        self.assertEqual(player["combat_lifepoints"], 100)
        self.assertEqual(player["combat_supply_loadout"]["food"], {})
        self.assertTrue(player["thieving_stunned"])

    def test_blackjack_steps_keep_progress_despite_false_return(self):
        cases = (
            ("needs_lure", "ready_to_knockout", 0, 0.0),
            ("ready_to_knockout", "knocked_out", 0, 10.0),
            ("knocked_out", "knocked_out", 60, 137.5),
        )
        for phase, expected_phase, coins, xp in cases:
            with self.subTest(phase=phase):
                player = _player("blackjack_menaphite_thug")
                player.update(
                    thieving_level=65,
                    thieving_blackjack_phase=phase,
                    thieving_blackjack_picks_remaining=2,
                    equipment={"weapon": "Willow blackjack"},
                    quests={"the_feud": {"completed": True}},
                )
                self._answer(player, (0.0,))
                self.assertEqual(player["thieving_attempt_count"], 1)
                self.assertEqual(player["thieving_blackjack_phase"], expected_phase)
                self.assertEqual(player["inventory"].get("Coins", 0), coins)
                self.assertEqual(player["thieving_exp"], xp)

    def test_locked_target_still_rolls_back_winter_storage(self):
        player = _player("wall_safe")
        player["thieving_level"] = 1
        before = copy.deepcopy(player)
        ctx, calls = _context(player)
        self.assertFalse(run_answer_with_carried_overlay(ctx, "thieving", handle_thieving_answer))
        self.assertTrue(calls["errors"])
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(player, before)
