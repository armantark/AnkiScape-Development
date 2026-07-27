"""Achievement diary catalog: regional families, tiers, tasks and rewards.

The owner's design contract is
``memory-bank/achievement-diary-item-grants-design.md``. It fixes the shape:
eight regional equipment families, a Beginner-only Burthorpe/Taverley onboarding
set, and a Miscellaneous pool that keeps its sourced coin payouts.

Task conditions are declared as data rather than as lambdas so the panel can
render a requirement line and a progress figure from the same object the engine
evaluates, and so a task cannot quietly acquire a rule the logic layer does not
own.

The generated catalog takes its task identity and membership from Darkan's
period achievement system. Regional tiers keep up to twelve source-order tasks
with evaluable requirements; Burthorpe/Taverley and Miscellaneous keep every
source task for which AnkiScape has an honest durable predicate.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Tuple


ACHIEVEMENTS_SOURCE = (
    "https://runescape.wiki/w/Special:PermanentLink/6579331"
    " (Achievements, 2012-11-18T20:23:14Z)"
)


# Condition kinds. Each names a state surface that already exists in the save,
# which is what makes retroactive credit honest: a task is credited because the
# proving counter is there, never because the player's XP makes it plausible.
CONDITION_KINDS: Tuple[str, ...] = (
    "skill_level",      # key: skill id, amount: level
    "quest",            # key: quest id
    "ledger_output",    # key: "<skill id>:<item name>", amount: quantity
    "ledger_action",    # key: "<skill id>:<action id>", amount: successes
    "counter",          # key: dotted player_data path, amount: threshold
    "hold_item",        # key: item name, amount: quantity held or worn
)


@dataclass(frozen=True)
class DiaryCondition:
    kind: str
    key: str
    amount: int = 1
    label: str = ""


@dataclass(frozen=True)
class DiaryLamp:
    """The sourced lamp or Bank Claim a tier hands over on claim."""

    experience: int
    minimum_level: int = 1
    # Empty means the player may point the lamp at any skill above the minimum.
    skills: Tuple[str, ...] = ()


@dataclass(frozen=True)
class DiaryTask:
    id: str
    name: str
    description: str
    conditions: Tuple[DiaryCondition, ...]
    source: str
    source_id: int
    coin_reward: int = 0


@dataclass(frozen=True)
class DiaryTier:
    id: str
    name: str
    index: int
    reward_item: str
    reward_summary: str
    tasks: Tuple[DiaryTask, ...]
    lamp: "DiaryLamp | None" = None
    source: str = ""

    @property
    def effort_multiplier(self) -> int:
        """Design contract: 1x, 2x, 3x, 4x by tier position within a family."""

        return self.index


@dataclass(frozen=True)
class DiaryFamily:
    id: str
    name: str
    kind: str  # "regional" | "onboarding" | "miscellaneous"
    tiers: Tuple[DiaryTier, ...]
    taskmaster: str = ""
    source: str = ACHIEVEMENTS_SOURCE


# The live catalog. Regional families are generated from Darkan's tier tables
# joined to the pinned pre-cutoff wiki requirement columns; see
# ``tools/generate_achievement_diary_data.py``.
from .achievement_diary_catalog import (  # noqa: E402  (avoids a cycle at import)
    DIARY_FAMILIES,
    diary_equipment_data_as_dict,
)

ACHIEVEMENT_DIARY_CATALOG: Tuple[DiaryFamily, ...] = DIARY_FAMILIES

__all__ = [
    "ACHIEVEMENT_DIARY_CATALOG",
    "ACHIEVEMENTS_SOURCE",
    "CONDITION_KINDS",
    "DiaryCondition",
    "DiaryFamily",
    "DiaryLamp",
    "DiaryTask",
    "DiaryTier",
    "diary_equipment_data_as_dict",
]
