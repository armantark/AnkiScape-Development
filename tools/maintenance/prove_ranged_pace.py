#!/usr/bin/env python3
"""Compare a continuous no-device ranged fight over equal play at all speeds."""

import json
import random
import statistics
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tests.pace.test_ammunition_pack import (
    COMBAT_ENEMY_DATA, _player, _context, combat_runtime, handle_combat_answer,
)


def measure(speed, seed):
    player = _player(
        equipment={"weapon": "Shortbow", "ammunition": "Bronze arrows"},
        equipment_ammunition_count=100000, ranged_level=99,
        constitution_level=99, combat_lifepoints=990, combat_prayers_enabled=False,
        combat_auto_flee=False, combat_auto_eat_food=[], combat_ava_incidental_items=False,
    )
    ctx = _context(player, review_action_multiplier=speed)
    ctx.cadence_live_enabled = True
    ctx.random_random = random.Random(seed).random
    spent = 0
    for _ in range(1000):
        if spent >= 3600:
            break
        ctx.card.ticks_remaining = min(6 * speed, 3600 - spent)
        assert handle_combat_answer(ctx), ctx.player_data.get("combat_last_result")
        elapsed = ctx.player_data["combat_last_result"]["ticks_elapsed"]
        assert elapsed > 0
        spent += elapsed
    assert spent == 3600, spent
    xp = ctx.player_data.get("ranged_exp", 0) + ctx.player_data.get("constitution_exp", 0)
    assert xp > 0
    return xp / spent


def main():
    # Enlarging HP alone makes the source XP formula combine huge stats with
    # the chicken's negative bonuses. Neutral bonuses keep this fixture valid.
    enemy = {**COMBAT_ENEMY_DATA["chicken"], "bonuses": {},
             "stats": {**COMBAT_ENEMY_DATA["chicken"]["stats"], "hitpoints": 100000000}}
    with patch.dict(combat_runtime.COMBAT_ENEMY_DATA, {"chicken": enemy}):
        rates = {speed: [measure(speed, seed) for seed in range(5)] for speed in range(1, 21)}
    rows = [{"speed": speed, "mean_xp_per_play_hour": statistics.fmean(values) * 6000,
             "max_paired_xp_per_tick_difference_from_1x": max(abs(a - b) for a, b in zip(values, rates[1]))}
            for speed, values in rates.items()]
    print(json.dumps(rows, indent=2), flush=True)
    assert all(row["max_paired_xp_per_tick_difference_from_1x"] < 1e-8 for row in rows)
    print("All 20 speeds: identical paired XP per tick; 5 seeds, 3600 ticks per seed and speed.")


if __name__ == "__main__":
    main()
