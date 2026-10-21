"""Queued Farming combat shares the card's danger boundary with selected actions."""

import sys
from unittest.mock import patch

import pkg_alias  # noqa: F401
from tests.pace.test_short_timers import _HostCase
from tests.test_combat_logic import _player


class FarmQueueDangerTests(_HostCase):
    def test_jade_vine_stops_at_low_lp_before_another_queue_step_or_fletching(self):
        player = _player(
            constitution_level=99, combat_lifepoints=400, combat_auto_flee=False,
            inventory={"Secateurs": 1, "Logs": 1},
            equipment={"weapon": "Bronze hatchet"},
            toolbelt={"woodcutting": ["bronze_hatchet"]},
            quests={"back_to_my_roots": {"completed": True}},
            farming_level=99, woodcutting_level=99, slayer_level=99,
            fletching_level=1, fletching_exp=0.0, current_fletch="arrow_shafts",
        )
        addon = self._addon(10, player)
        addon._state.current_skill = "Fletching"
        farming = sys.modules[f"{addon.__name__}.logic.farming_logic"]
        player.update(farming.default_farming_state_pure())
        player["farm_patches"]["handelmort_jade_vine"].update(
            crop_id="jade_vine", last_crop_id="jade_vine", stage=6,
            health_checked=True, jade_state="wild",
        )
        queued, _step_id, _reason = farming.add_farm_queue_step_pure(player, "chop", "handelmort_jade_vine")
        addon._state.player_data = queued
        engine = sys.modules[f"{addon.__name__}.logic_pure.logic_pure_combat_engine"]
        contexts = []
        spend = addon._spend_card_on_action

        def record(ctx, key, handler):
            contexts.append(ctx)
            return spend(ctx, key, handler)

        with patch.object(addon, "_spend_card_on_action", record), patch.object(
            addon.random, "random", lambda: 0.2
        ), patch.object(engine, "_combat_roll_hit", side_effect=lambda *_args, **kw: (False, 0) if "blocked" in kw else (True, 10)):
            after = self._answer(addon, 3)
        self.assertEqual(after["combat_lifepoints"], 390)
        self.assertEqual(contexts[-1].card.stop_reason, "low_lp_no_food")
        self.assertEqual(contexts[-1].card.ticks_remaining, 48)
        self.assertEqual(after["inventory"]["Logs"], 1)
        self.assertNotIn("Arrow shafts", after["inventory"])
        self.assertTrue(after["farm_queue"])
        self.assertTrue(after["farm_patches"]["handelmort_jade_vine"]["jade_combat_encounter"])
