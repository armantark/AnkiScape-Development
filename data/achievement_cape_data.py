"""Milestone capes: the wear gate the design contract asked to be repaired.

``data/crafting_data.py`` has woven the nine capes since the Crafting work, at
the sourced Crafting level, ball-of-wool cost and experience. Two things were
missing and are fixed here:

1. None of the nine was in ``EQUIPMENT_DATA``, so a woven cape could never be
   worn. Nine craftable, unwearable rows.
2. The period gate — "can only be worn by those who have level N in all
   skills" — was never enforced, and each recipe carried a note saying it could
   not be.

Both are ordinary uses of machinery that already exists: the per-family
equipment seam, and ``skill_requirements``, which ``can_equip_item_pure``
already checks against ``<skill>_level`` for any skill, not just a combat one.

Sources:

- Wear gate, crafting cost and the absence of any bonus:
  ``Milestone cape (10)`` oldid 5907125 (2012-07-08), which states the cape
  "can only be worn by those who have level 10 in all skills" and that "the cape
  does not have any bonus effects". Its Infobox Bonuses block is all zeroes.
- Item ids 20735-20743 from the 2011Scape item config, already carried by the
  Crafting recipes.
"""

from __future__ import annotations

from typing import Any

from ..core.skill_registry import trainable_skill_definitions


MILESTONE_CAPE_SOURCE = (
    "https://runescape.wiki/w/Special:PermanentLink/5907125"
    "; Milestone cape (10), 2012-07-08; all-skills wear gate and zero bonuses"
)

MILESTONE_CAPE_LEVELS: tuple[int, ...] = tuple(range(10, 100, 10))
MILESTONE_CAPE_ITEM_IDS: dict[int, int] = {
    level: 20735 + index for index, level in enumerate(MILESTONE_CAPE_LEVELS)
}


def milestone_cape_name(level: int) -> str:
    return f"Milestone cape ({level})"


def milestone_cape_wear_requirements(level: int) -> tuple[tuple[str, int], ...]:
    """The period's all-skills gate, over the skills AnkiScape actually has.

    Dungeoneering is deliberately absent: it is a `planned` skill with no
    training loop, so including it would make every one of the nine capes
    permanently unwearable — an inert reward, which is the failure this repair
    exists to remove. The requirement is derived from the skill registry rather
    than listed, so Dungeoneering joins the gate automatically on the day it
    becomes trainable, the same way the design contract treats every other
    latent requirement.
    """

    return tuple((skill.id, level) for skill in trainable_skill_definitions())


def milestone_cape_equipment_data_as_dict() -> "dict[str, Any]":
    from .equipment_data import EquipmentBonuses, EquipmentItem

    return {
        milestone_cape_name(level): EquipmentItem(
            item_name=milestone_cape_name(level),
            slot="cape",
            combat_skill=None,
            required_level=1,
            two_handed=False,
            equipment_type="milestone_cape",
            # The period cape is purely a display of total level: the pinned
            # revision's bonus block is zero in every column.
            bonuses=EquipmentBonuses(),
            attack_speed=4,
            source_item_id=MILESTONE_CAPE_ITEM_IDS[level],
            source=MILESTONE_CAPE_SOURCE,
            source_status="period item page; zero bonuses stated",
            skill_requirements=milestone_cape_wear_requirements(level),
            weapon_type=-1,
        )
        for level in MILESTONE_CAPE_LEVELS
    }
