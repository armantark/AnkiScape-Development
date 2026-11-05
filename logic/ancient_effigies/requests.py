"""Stable skill-pair requests for each Ancient Effigy copy.

A copy's request comes from its own hidden seed and its stage count, through a
local generator. Nothing here touches the shared random module, so inspecting,
undoing, doing something unrelated and inspecting again shows the same pair.
"""

from __future__ import annotations

import random

from ...data.ancient_effigies.catalog import SKILL_PAIRS


# PLACEHOLDER(ancient_effigies.initial_pair_weights): independent pre-2012-11-20 pair probability evidence would replace these reconstruction weights
INITIAL_PAIR_WEIGHTS = (1, 1, 1, 1, 1, 1, 1, 1)
# PLACEHOLDER(ancient_effigies.next_pair_weights): independent pre-2012-11-20 pair probability evidence would replace these reconstruction weights
NEXT_PAIR_WEIGHTS = (1, 1, 1, 1, 1, 1, 1)


def initial_pair_index_pure(request_seed: str) -> int:
    """The pair a copy reveals on first inspection (Darkan AncientEffigies.java:109)."""
    return random.Random(f"{request_seed}:0").choices(
        range(len(SKILL_PAIRS)), weights=INITIAL_PAIR_WEIGHTS, k=1
    )[0]


def next_pair_index_pure(request_seed: str, request_step: int, previous_pair: int) -> int:
    """The pair after a successful advancement, never the immediately previous one.

    ``request_step`` is the copy's step after this advancement. Darkan draws
    one of seven and skips over the previous pair (AncientEffigies.java:123-126,
    173); an earlier pair may come back after an intervening stage.
    """
    roll = random.Random(f"{request_seed}:{request_step}").choices(
        range(len(SKILL_PAIRS) - 1), weights=NEXT_PAIR_WEIGHTS, k=1
    )[0]
    return roll + 1 if roll >= previous_pair else roll
