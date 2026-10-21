"""A familiar's last ticks cap the foreground card before the world tick removes it."""

import unittest
from dataclasses import replace
from unittest.mock import patch

import pkg_alias  # noqa: F401
from tests.pace.test_short_timers import _HostCase, _summoned
from tests.test_combat_logic import _player
from tests.test_runtime_actions import _context
from ankiscape.runtime.runtime_actions_context import spend_card_budget


class FamiliarDangerStopTests(_HostCase):
    def test_expiring_familiar_caps_combat_at_its_pre_drain_lifetime(self):
        player = {**_player(combat_auto_flee=False), **_summoned("bunyip", "Bunyip pouch")}
        player["combat_lifepoints"] = 990
        player["summoning_state"]["active_follower"]["remaining_ticks"] = 17
        addon = self._addon(10, player)
        addon._state.current_skill = "Combat"
        contexts = []
        spend = addon._spend_card_on_action

        def record(ctx, key, handler):
            contexts.append(ctx)
            return spend(ctx, key, handler)

        with patch.object(addon, "_spend_card_on_action", record), patch.object(addon.random, "random", lambda: 0.999999):
            after = self._answer(addon, 3)
            self.assertEqual(after["combat_last_result"]["ticks_elapsed"], 17)
            self.assertEqual(contexts[-1].card.stop_reason, "familiar_ended")
            self.assertEqual(after["summoning_state"]["active_follower"], {})
            self.assertTrue(after["combat_encounter"])
            self._answer(addon, 3)
            self.assertEqual(contexts[-1].card.stop_reason, "")
            self.assertEqual(addon._state.player_data["combat_last_result"]["ticks_elapsed"], 60)

    def test_expiry_at_the_card_boundary_does_not_forfeit_any_ticks(self):
        player = {**_player(combat_auto_flee=False), **_summoned("bunyip", "Bunyip pouch")}
        player["combat_lifepoints"] = 990
        player["summoning_state"]["active_follower"]["remaining_ticks"] = 60
        addon = self._addon(10, player)
        addon._state.current_skill = "Combat"
        with patch.object(addon.random, "random", lambda: 0.999999):
            after = self._answer(addon, 3)
        self.assertEqual(after["combat_last_result"]["ticks_elapsed"], 60)
        self.assertEqual(after["summoning_state"]["active_follower"], {})


class FamiliarStepBudgetTests(unittest.TestCase):
    def test_a_partial_step_carries_its_debt_after_the_familiar_cap(self):
        ctx = replace(_context({}, review_action_multiplier=10), familiar_ticks_before=17)
        offered = []

        def step(step_ctx):
            offered.append(step_ctx.card.ticks_remaining)
            return True

        spend_card_budget(ctx, "woodcutting", step, can_continue=lambda: True)
        self.assertEqual(offered, [17, 11, 5])
        self.assertEqual(ctx.card.stop_reason, "familiar_ended")
        self.assertEqual(ctx.card.ticks_remaining, 0)
        self.assertEqual(ctx.player_data["card_tick_debt"], 1)

    def test_an_earlier_danger_keeps_its_reason_instead_of_familiar_expiry(self):
        ctx = replace(_context(_player(), review_action_multiplier=10), familiar_ticks_before=17)

        def step(step_ctx):
            step_ctx.player_data["combat_lifepoints"] = 35
            return True

        spend_card_budget(ctx, "agility", step, can_continue=lambda: True)
        self.assertEqual(ctx.card.stop_reason, "low_lp_no_food")
        self.assertEqual(ctx.card.ticks_remaining, 11)
