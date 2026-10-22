"""Owner-approved provisional effects for an admitted Barcrawl drink review."""

from __future__ import annotations

import random
from math import floor

from ...data.quest.definitions.miniquests.alfred_grimhands_barcrawl import (
    BAR_CRAWL_DAMAGE_CAPS,
    BAR_CRAWL_DAMAGE_REFERENCE_LIFEPOINTS,
    BAR_CRAWL_DRINKS,
    BAR_CRAWL_HEART_STOPPER_PERCENT_BOUNDS,
    BAR_CRAWL_STAT_DRAIN_REFERENCES,
    BAR_CRAWL_STAT_REFERENCE_LEVEL,
)
from ...logic_pure.logic_pure_combat_model import (
    apply_combat_stat_delta_pure,
    combat_max_lifepoints_pure,
)


def apply_bar_crawl_drink_effects_pure(player_data, stage, *, rng=None):
    """Return effects on existing combat resources, leaving the input untouched."""
    data = dict(player_data)
    if not 2 <= stage <= 11:
        return data
    drink = BAR_CRAWL_DRINKS[stage - 2][0]
    for skill, reference in BAR_CRAWL_STAT_DRAIN_REFERENCES[drink].items():
        base = max(1, int(data.get(f"{skill}_level", 1)))
        # PLACEHOLDER(bar_crawl.stat_drain_magnitudes): needs actual per-skill formulas, units and rounding.
        loss = max(1, (base * reference) // BAR_CRAWL_STAT_REFERENCE_LEVEL)
        if skill == "prayer":
            data["combat_prayer_points"] = max(
                0, data.get("combat_prayer_points", base * 10) - loss,
            )
        else:
            apply_combat_stat_delta_pure(data, skill, -loss)

    maximum = combat_max_lifepoints_pure(data)
    if drink in BAR_CRAWL_DAMAGE_CAPS:
        cap = BAR_CRAWL_DAMAGE_CAPS[drink]
        # PLACEHOLDER(bar_crawl.gutrot_damage_formula): needs actual Gutrot maximum, scaling and transaction.
        # PLACEHOLDER(bar_crawl.drink_damage_transaction): needs actual capped scaling and inclusive roll bounds.
        lower, upper = 0, max(1, min(cap, (cap * maximum) // BAR_CRAWL_DAMAGE_REFERENCE_LIFEPOINTS))
    elif drink == "Heart Stopper":
        # PLACEHOLDER(bar_crawl.drink_damage_transaction): needs exact percentage bounds and rounding.
        lower, upper = (percent * maximum // 100 for percent in BAR_CRAWL_HEART_STOPPER_PERCENT_BOUNDS)
    else:
        return data

    # PLACEHOLDER(bar_crawl.gutrot_damage_formula): needs Gutrot distribution and direct damage evidence.
    # PLACEHOLDER(bar_crawl.drink_damage_transaction): needs random arithmetic and protection/death behavior; nonlethal floor is owner policy.
    draw = random.random if rng is None else rng
    damage = lower + floor(draw() * (upper - lower + 1))
    health = data.get("combat_lifepoints", maximum)
    data["combat_lifepoints"] = max(1, health - damage) if health > 0 else health
    return data
