"""Danger ends the current card without spending its remaining play time (decision 5)."""

import copy
import unittest

import pkg_alias  # noqa: F401
from ankiscape.runtime.runtime_actions_context import spend_card_budget
from ankiscape.runtime.runtime_actions_gates import _can_start_magic_action
from tests.test_combat_logic import _player
from tests.test_runtime_actions import _context


class StepDangerStopsTests(unittest.TestCase):
    def test_speed_ten_card_ends_at_the_first_danger_step(self):
        cases = (
            ("low_lp_no_food", {"combat_lifepoints": 40}),
            ("stun", {"thieving_stunned": True}),
            ("poison_started", {"combat_status_effects": {"poison": {"damage": 10}}}),
            ("prayer_empty", {"combat_prayer_points": 0, "combat_selected_prayers": []}),
            ("bank_trip", {"skilling_bank_run": {"reviews_remaining": 1}}),
        )
        for reason, change in cases:
            with self.subTest(reason=reason):
                player = _player(combat_prayer_points=10, combat_selected_prayers=["thick_skin"])
                ctx = _context(player, review_action_multiplier=10)
                steps = []

                def step(step_ctx):
                    steps.append(step_ctx.card.ticks_remaining)
                    step_ctx.player_data.update(copy.deepcopy(change))
                    return True

                self.assertTrue(spend_card_budget(ctx, "agility", step, can_continue=lambda: True))
                self.assertEqual(steps, [60])
                self.assertEqual(ctx.card.stop_reason, reason)
                self.assertEqual(ctx.card.ticks_remaining, 54)

    def test_loaded_food_and_existing_poison_do_not_end_a_card(self):
        player = _player(
            combat_status_effects={"poison": {"damage": 10}},
            combat_supply_loadout={"food": {"Shrimps": 10}},
        )
        ctx = _context(player, review_action_multiplier=10)
        steps = []

        def step(step_ctx):
            steps.append(1)
            step_ctx.player_data["combat_lifepoints"] = 40
            return True

        spend_card_budget(ctx, "agility", step, can_continue=lambda: True)
        self.assertEqual(len(steps), 10)
        self.assertEqual(ctx.card.stop_reason, "")
        self.assertEqual(ctx.card.ticks_remaining, 0)

    def test_magic_rune_gate_reports_why_the_remaining_card_cannot_start(self):
        player = _player(current_magic="low_alchemy", inventory={"Fire rune": 3, "Nature rune": 1})
        ctx = _context(player, review_action_multiplier=10)
        steps = []

        def step(step_ctx):
            steps.append(1)
            step_ctx.player_data["inventory"]["Nature rune"] = 0
            return True

        spend_card_budget(ctx, "magic", step, can_continue=lambda: _can_start_magic_action(ctx))
        self.assertEqual(steps, [1])
        self.assertEqual(ctx.card.stop_reason, "out_of_runes")
        self.assertEqual(ctx.card.ticks_remaining, 54)
