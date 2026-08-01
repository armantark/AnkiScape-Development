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
period achievement system. Named source rows without an evaluable requirement
remain visible as latent tasks with no predicate. Fixed designed denominators
also reserve source-incomplete cutoff slots without fabricating names.
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
    "ledger_output",       # key: "<skill id>:<item name>", amount: quantity
    "ledger_action",       # key: "<skill id>:<action id>", amount: successes
    "ledger_action_family",  # key: "<skill id>:<family id>", amount: successes
    "counter",             # key: dotted player_data path, amount: threshold
    "combat_kill",         # key: combat target id, amount: lifetime kills
    "shop_transaction",    # key: "<type>|<shop id>|<row/action id>", amount: transactions
    "state_equals",        # key: dotted player_data path, expected: exact value
    "hold_item",           # key: item name, amount: quantity held or worn
    "equipped_item",       # key: "<slot>|<item name>", amount: 1
    "any_of",              # key: "", amount: 1, meaning lives in `alternatives`
    "derived_value",       # key: DIARY_DERIVED_VALUES name, amount: threshold
)

# The kinds an ``any_of`` alternative may take: the plain state reads only. A
# disjunction of disjunctions has no source behind it, and the flat form is what
# the panel can render.
BASE_CONDITION_KINDS: Tuple[str, ...] = (
    "skill_level",
    "quest",
    "ledger_output",
    "ledger_action",
    "ledger_action_family",
    "counter",
    "combat_kill",
    "shop_transaction",
    "state_equals",
    "hold_item",
    "equipped_item",
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


@dataclass(frozen=True)
class DiaryTask:
    id: str
    name: str
    description: str
    conditions: Tuple[DiaryCondition, ...]
    source: str
    source_id: int
    coin_reward: int = 0
    latent: bool = False


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
    # The fixed cutoff denominator. It can exceed the number of named rows while
    # the pinned source roster is incomplete; zero keeps small synthetic tiers
    # and old callers using their explicit task tuple as the denominator.
    designed_task_count: int = 0

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


# The live catalog. Regional families are generated from Darkan's tier tables
# joined to the pinned pre-cutoff wiki requirement columns; see
# ``tools/generate_achievement_diary_data.py``.
from .achievement_diary_catalog import (  # noqa: E402  (avoids a cycle at import)
    DIARY_FAMILIES,
    diary_equipment_data_as_dict,
)

ACHIEVEMENT_DIARY_CATALOG: Tuple[DiaryFamily, ...] = DIARY_FAMILIES


def diary_lamp_claim_id(tier_id: str) -> str:
    return f"achievement_diary_{tier_id}_xp_lamp"


DIARY_LAMP_CLAIM_IDS_BY_TIER = {
    tier.id: diary_lamp_claim_id(tier.id)
    for family in ACHIEVEMENT_DIARY_CATALOG
    for tier in family.tiers
    if tier.lamp is not None
}


def diary_lamp_claims_as_dict() -> dict[str, dict[str, Any]]:
    """Bank Claim rows created by regional diary tier claims."""

    claims: dict[str, dict[str, Any]] = {}
    for family in ACHIEVEMENT_DIARY_CATALOG:
        for tier in family.tiers:
            lamp = tier.lamp
            if lamp is None:
                continue
            claim_id = diary_lamp_claim_id(tier.id)
            claims[claim_id] = {
                "id": claim_id,
                "display_name": (
                    f"{family.name} {tier.name}: reward lamp"
                    f" ({lamp.experience:,} XP)"
                ),
                "claim_type": "xp_lamp",
                "item_name": "Reward lamp",
                "quantity": 1,
                "items": (),
                "source": tier.source or family.source,
                "required_quest": "",
                "required_runecrafting_level": 0,
                "required_diary_tier": tier.id,
                "xp_amount": float(lamp.experience),
                # Empty is the established Bank Claim representation for any
                # trainable skill; the claims logic expands it at render/spend time.
                "skill_options": lamp.skills,
                "minimum_level": lamp.minimum_level,
            }
    return claims


def _assert_derived_values_are_registered() -> None:
    """A ``derived_value`` typo must be an ImportError, never a silent row.

    The evaluator falls back to zero for an unknown name, so nothing else would
    ever say the row is impossible: the panel would render an honest-looking
    0/153 forever.
    """

    from ..logic.achievement_diary_derived import (  # noqa: E402  (avoids a cycle)
        DIARY_DERIVED_VALUE_CEILINGS,
        DIARY_DERIVED_VALUES,
    )

    for family in ACHIEVEMENT_DIARY_CATALOG:
        for tier in family.tiers:
            for task in tier.tasks:
                for condition in task.conditions:
                    if condition.kind != "derived_value":
                        continue
                    if condition.key not in DIARY_DERIVED_VALUES:
                        raise ImportError(
                            f"{task.id}: derived_value {condition.key!r} is not in"
                            " DIARY_DERIVED_VALUES"
                        )
                    if condition.key not in DIARY_DERIVED_VALUE_CEILINGS:
                        raise ImportError(
                            f"{task.id}: derived_value {condition.key!r} has no"
                            " entry in DIARY_DERIVED_VALUE_CEILINGS"
                        )


_assert_derived_values_are_registered()

__all__ = [
    "ACHIEVEMENT_DIARY_CATALOG",
    "ACHIEVEMENTS_SOURCE",
    "BASE_CONDITION_KINDS",
    "CONDITION_KINDS",
    "DiaryCondition",
    "DiaryFamily",
    "DiaryLamp",
    "DiaryTask",
    "DiaryTier",
    "diary_equipment_data_as_dict",
]
