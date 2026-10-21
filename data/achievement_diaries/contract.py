"""Shared data contracts for generated achievement-diary modules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Tuple


ACHIEVEMENTS_SOURCE = (
    "https://runescape.wiki/w/Special:PermanentLink/6579331"
    " (Achievements, 2012-11-18T20:23:14Z)"
)


@dataclass(frozen=True)
class DiaryCondition:
    kind: str
    key: str
    amount: int = 1
    label: str = ""
    # Only ``any_of`` populates this. The task is satisfied when any single
    # alternative is satisfied; an empty tuple is unsatisfiable, never free.
    alternatives: Tuple["DiaryCondition", ...] = ()
    # Only ``state_equals`` populates this. ``None`` is deliberately invalid so
    # an absent path can never equal the default and hand out free completion.
    expected: Any = None


@dataclass(frozen=True)
class DiaryLamp:
    """The sourced lamp or Bank Claim a tier hands over on claim."""

    experience: int
    minimum_level: int = 1
    # Empty means the player may point the lamp at any skill above the minimum.
    skills: Tuple[str, ...] = ()
    source: str = ""


@dataclass(frozen=True)
class DiaryTask:
    id: str
    name: str
    description: str
    conditions: Tuple[DiaryCondition, ...]
    source: str
    source_id: int
    coin_reward: int = 0
    # True only for an owner-approved generic progression row used to
    # complete a twelve-task curated tier when the period family has fewer
    # than 48 deeds.
    curation_anchor: bool = False
    # Source-backed level and quest prerequisites are presentation-only access
    # gates. Completion reads ``conditions`` and never these rows.
    access_gates: Tuple[DiaryCondition, ...] = ()

    @property
    def dormant(self) -> bool:
        return not self.conditions


@dataclass(frozen=True)
class DiaryTier:
    id: str
    name: str
    index: int
    # The single upgradeable equipment item, for the eight families that have
    # one. Burthorpe/Taverley has none — its period reward is the bundle below.
    reward_item: str
    reward_summary: str
    tasks: Tuple[DiaryTask, ...]
    lamp: "DiaryLamp | None" = None
    source: str = ""
    # (item name, quantity) pairs handed over whole on claim, for a tier whose
    # period reward is a set of starter equipment rather than one worn item.
    reward_bundle: Tuple[Tuple[str, int], ...] = ()
    # The fixed cutoff denominator. It can exceed the number of named rows
    # while the pinned source roster is incomplete; zero keeps small synthetic
    # tiers and old callers using their explicit task tuple as the denominator.
    designed_task_count: int = 0
    extra_lamps: Tuple[DiaryLamp, ...] = ()

    @property
    def lamps(self) -> Tuple[DiaryLamp, ...]:
        return ((self.lamp,) if self.lamp is not None else ()) + self.extra_lamps

    @property
    def total_tasks(self) -> int:
        return self.designed_task_count or len(self.tasks)

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
    taskmaster_chathead_asset_path: str = ""
    source: str = ACHIEVEMENTS_SOURCE


# These classes remain publicly owned by achievement_diary_data so saved
# values, qualified names, and existing imports keep the same identity.
_PUBLIC_MODULE = __name__.rsplit(".", 2)[0] + ".achievement_diary_data"
_PUBLIC_CLASSES = (
    DiaryCondition,
    DiaryLamp,
    DiaryTask,
    DiaryTier,
    DiaryFamily,
)
for _public_class in _PUBLIC_CLASSES:
    _public_class.__module__ = _PUBLIC_MODULE
del _public_class
