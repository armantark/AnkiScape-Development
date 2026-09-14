"""Runtime coverage for Slayer credit and completion callbacks."""

import unittest

import pkg_alias  # noqa: F401
from tests import test_runtime_actions as _runtime


class SlayerCompletionRuntimeTest(unittest.TestCase):
    def test_combat_handler_prompts_once_when_slayer_assignment_completes(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        completions = []
        player_data = {
            "inventory": {},
            "equipment": {},
            "current_combat_target": "black_bear",
            "combat_action": "attack",
            "combat_attack_style": "aggressive",
            "combat_attack_style_type": "crush",
            "combat_lifepoints": 990,
            "combat_auto_eat_food": ["Shrimps"],
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "slayer_level": 99,
            "slayer_exp": 0.0,
            "slayer_assignment": {
                "master_id": "turael_spria",
                "family_id": "bears",
                "initial_count": 17,
                "remaining": 2,
            },
            "completed_achievements": [],
        }

        def defeat_one_bear() -> None:
            player_data["combat_encounter"] = {
                "target_id": "black_bear",
                "enemy_lifepoints": 1,
                "player_attack_ticks_remaining": 0,
                "enemy_attack_ticks_remaining": 99,
            }
            ctx = _runtime._context(
                player_data,
                calls,
                [0.0, 0.999999] * 100,
                prompt_slayer_completion=lambda count, enemy_plural: completions.append(
                    (count, enemy_plural)
                ),
            )
            ctx.cadence_live_enabled = True
            self.assertTrue(_runtime.handle_combat_answer(ctx))

        defeat_one_bear()
        self.assertEqual(player_data["slayer_assignment"]["remaining"], 1)
        self.assertEqual(completions, [])
        defeat_one_bear()
        self.assertEqual(player_data["slayer_assignment"]["remaining"], 0)
        self.assertEqual(completions, [(17, "bears")])
        defeat_one_bear()
        self.assertEqual(completions, [(17, "bears")])

        self.assertEqual(player_data["slayer_exp"], 50.0)
        self.assertEqual(calls["level_checks"].count("Slayer"), 2)
        self.assertIn("1 Slayer kills left", calls["activity"][0])
        self.assertIn("Slayer assignment complete", calls["activity"][1])
        self.assertNotIn("Slayer", calls["activity"][2])
        self.assertEqual(calls["saves"], 3)
        self.assertNotIn("deactivated", calls)
        self.assertEqual(player_data["combat_action"], "attack")
        self.assertEqual(player_data["current_combat_target"], "black_bear")

    def test_combat_handler_does_not_credit_an_off_task_target(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        completions = []
        player_data = {
            "inventory": {},
            "equipment": {},
            "current_combat_target": "black_bear",
            "combat_attack_style": "accurate",
            "combat_lifepoints": 990,
            "combat_encounter": {
                "target_id": "black_bear",
                "enemy_lifepoints": 1,
                "player_attack_ticks_remaining": 0,
                "enemy_attack_ticks_remaining": 99,
            },
            "combat_auto_eat_food": ["Shrimps"],
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "slayer_level": 1,
            "slayer_exp": 0.0,
            "slayer_assignment": {
                "master_id": "turael_spria",
                "family_id": "bats",
                "initial_count": 50,
                "remaining": 50,
            },
            "completed_achievements": [],
        }

        ctx = _runtime._context(
            player_data,
            calls,
            [0.0, 0.999999] * 100,
            prompt_slayer_completion=lambda count, enemy_plural: completions.append(
                (count, enemy_plural)
            ),
        )
        ctx.cadence_live_enabled = True
        ok = _runtime.handle_combat_answer(ctx)

        self.assertTrue(ok)
        self.assertEqual(player_data["combat_kill_counts"]["black_bear"], 1)
        self.assertEqual(player_data["slayer_assignment"]["remaining"], 50)
        self.assertEqual(player_data["slayer_exp"], 0.0)
        self.assertNotIn("Slayer", calls.get("level_checks", []))
        self.assertEqual(completions, [])
