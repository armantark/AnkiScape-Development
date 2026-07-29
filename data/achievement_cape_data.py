"""Capes of Accomplishment and Distinction: skillcapes, prestige capes, milestones.

Three cape families share this module because they share one seam — a
family-owned equipment registration that ``core/constants.py`` folds into
``EQUIPMENT_DATA`` without anyone hand-editing a generated table.

Milestone capes: the wear gate the design contract asked to be repaired.

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

from dataclasses import dataclass
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
    """The period's all-skills gate, derived from the trainable registry."""

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


# ---------------------------------------------------------------------------
# Capes of Accomplishment — the skillcapes
# ---------------------------------------------------------------------------

SKILLCAPE_SOURCE = (
    "darkan-world-server c95aca409f397cab12c13b6d5269b73f6cd8abe9"
    " src/main/java/com/rs/game/content/Skillcapes.kt:16-55; item ids, the"
    " level-99 gate, the 99,000-coin price and the cape-plus-hood grant"
)
SKILLCAPE_MASTER_SOURCE = (
    "darkan-world-server c95aca409f397cab12c13b6d5269b73f6cd8abe9"
    " content/world/unorganized_dialogue/skillmasters/GenericSkillcapeOwnerD.java:30-58"
    " and the per-master dialogue classes, named through"
    " developer-information/npcList.txt (rev-727 NPC definition dump)"
)
SKILLCAPE_TRIM_SOURCE = (
    "darkan-world-server c95aca409f397cab12c13b6d5269b73f6cd8abe9"
    " src/main/java/com/rs/game/model/entity/player/Skills.java:132-138 (checkMulti99s)"
    " and :140+ (trimCapes), called on every 99 level-up at :864-866"
)

SKILLCAPE_PRICE = 99_000
SKILLCAPE_LEVEL = 99

# Every skillcape's period defensive block is identical. Prayer differs by trim:
# cache item param 11 is 0 untrimmed and 4 trimmed in every period cache.
SKILLCAPE_BONUSES: dict[str, int] = {
    "defence_stab": 9,
    "defence_slash": 9,
    "defence_crush": 9,
    "defence_magic": 9,
    "defence_ranged": 9,
    "prayer": 0,  # Period cache item param 11.
}
TRIMMED_SKILLCAPE_BONUSES: dict[str, int] = {
    **SKILLCAPE_BONUSES,
    "prayer": 4,  # Period cache item param 11.
}
SKILLCAPE_BONUS_SOURCE = (
    "data/cfg/items.yml defensive skillcape block; period cache item param 11"
    " (0 untrimmed, 4 trimmed), verified in"
    " memory-bank/source-audits/skillcape-mechanics-verification-2026-07-27.md"
)


@dataclass(frozen=True)
class Skillcape:
    """One skill's Cape of Accomplishment, its trimmed form and its hood."""

    skill_id: str
    cape: str
    trimmed_cape: str
    hood: str
    master: str
    cape_item_id: int
    trimmed_item_id: int
    hood_item_id: int
    master_note: str = ""

    @property
    def skill_label(self) -> str:
        """The period skill name, which is not always the internal skill id.

        ``defense`` sells a Defence cape and ``ranged`` a Ranging cape, so the
        label comes off the cape's own name rather than off the id.
        """

        return self.cape.rsplit(" cape", 1)[0]


# Darkan's `Skillcapes.kt` enum, joined to the master NPC each cape is bought
# from. The trailing master column is the period seller, not a modern shop.
SKILLCAPES: tuple[Skillcape, ...] = (
    Skillcape("attack", "Attack cape", "Attack cape (t)", "Attack hood", "Ajjat", 9747, 9748, 9749),
    Skillcape("defense", "Defence cape", "Defence cape (t)", "Defence hood", "Melee instructor", 9753, 9754, 9755),
    Skillcape(
        "strength",
        "Strength cape",
        "Strength cape (t)",
        "Strength hood",
        "Yadech Strongarm",
        9750,
        9751,
        9752,
        # npcList.txt carries a null name for 8269; the name comes from the
        # sibling npcListWithRenderAnims.txt dump and is corroborated by
        # game-main's spawns_11319 comment. The id itself is not in doubt.
        master_note="name from npcListWithRenderAnims.txt; npcList.txt is null at 8269",
    ),
    Skillcape("constitution", "Constitution cape", "Constitution cape (t)", "Constitution hood", "Surgeon General Tafani", 9768, 9769, 9770),
    Skillcape("ranged", "Ranging cape", "Ranging cape (t)", "Ranging hood", "Armour salesman", 9756, 9757, 9758),
    Skillcape("prayer", "Prayer cape", "Prayer cape (t)", "Prayer hood", "Brother Jered", 9759, 9760, 9761),
    Skillcape("magic", "Magic cape", "Magic cape (t)", "Magic hood", "Robe Store owner", 9762, 9763, 9764),
    Skillcape("cooking", "Cooking cape", "Cooking cape (t)", "Cooking hood", "Head chef", 9801, 9802, 9803),
    Skillcape("woodcutting", "Woodcutting cape", "Woodcutting cape (t)", "Woodcutting hood", "Wilfred", 9807, 9808, 9809),
    Skillcape("fletching", "Fletching cape", "Fletching cape (t)", "Fletching hood", "Hickton", 9783, 9784, 9785),
    Skillcape("fishing", "Fishing cape", "Fishing cape (t)", "Fishing hood", "Master fisher", 9798, 9799, 9800),
    Skillcape("firemaking", "Firemaking cape", "Firemaking cape (t)", "Firemaking hood", "Ignatius Vulcan", 9804, 9805, 9806),
    Skillcape("crafting", "Crafting cape", "Crafting cape (t)", "Crafting hood", "Master Crafter", 9780, 9781, 9782),
    Skillcape("smithing", "Smithing cape", "Smithing cape (t)", "Smithing hood", "Thurgo", 9795, 9796, 9797),
    Skillcape("mining", "Mining cape", "Mining cape (t)", "Mining hood", "Dwarf", 9792, 9793, 9794),
    Skillcape("herblore", "Herblore cape", "Herblore cape (t)", "Herblore hood", "Kaqemeex", 9774, 9775, 9776),
    Skillcape("agility", "Agility cape", "Agility cape (t)", "Agility hood", "Cap'n Izzy No-Beard", 9771, 9772, 9773),
    Skillcape("thieving", "Thieving cape", "Thieving cape (t)", "Thieving hood", "Martin Thwait", 9777, 9778, 9779),
    Skillcape("slayer", "Slayer cape", "Slayer cape (t)", "Slayer hood", "Kuradal", 9786, 9787, 9788),
    Skillcape("farming", "Farming cape", "Farming cape (t)", "Farming hood", "Martin the Master Gardener", 9810, 9811, 9812),
    Skillcape("runecrafting", "Runecrafting cape", "Runecrafting cape (t)", "Runecrafting hood", "Larriar", 9765, 9766, 9767),
    Skillcape("hunter", "Hunter cape", "Hunter cape (t)", "Hunter hood", "Hunting expert", 9948, 9949, 9950),
    Skillcape("construction", "Construction cape", "Construction cape (t)", "Construction hood", "Estate agent", 9789, 9790, 9791),
    Skillcape("summoning", "Summoning cape", "Summoning cape (t)", "Summoning hood", "Pikkupstix", 12169, 12170, 12171),
    Skillcape("dungeoneering", "Dungeoneering cape", "Dungeoneering cape (t)", "Dungeoneering hood", "Thok, Master of Dungeoneering", 18508, 18509, 18510),
)

SKILLCAPES_BY_SKILL: dict[str, Skillcape] = {cape.skill_id: cape for cape in SKILLCAPES}


def skillcape_definitions() -> tuple[Skillcape, ...]:
    """Only the capes a player can actually reach level 99 in."""

    trainable = {skill.id for skill in trainable_skill_definitions()}
    return tuple(cape for cape in SKILLCAPES if cape.skill_id in trainable)


# ---------------------------------------------------------------------------
# Capes of Distinction — quest point, Max, Completionist and Veteran
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PrestigeCape:
    """A cape bought once, from one named seller, against one durable gate."""

    id: str
    cape: str
    hood: str
    seller: str
    price: int
    requirement: str  # the kind the logic layer evaluates
    threshold: int
    cape_item_id: int
    hood_item_id: int
    prayer_bonus: int
    source: str


# The design contract's five-year and ten-year thresholds: an AnkiScape year is
# 365 independent 240-answer world days, never the wall clock.
VETERAN_ANSWERED_CARDS_PER_YEAR = 240 * 365

# Darkan rev-727 cache dumps, developer-information/itemList.txt:21873,21875
# (independently rendered in itemListCS2.txt:20769,20771). Params 0-4 are the
# five attack columns, 5-9 the five defence columns, and 11 Prayer.
PRESTIGE_CAPE_BONUSES: dict[str, dict[str, int]] = {
    "max": {
        "attack_stab": 5,
        "attack_slash": 5,
        "attack_crush": 5,
        "attack_magic": 5,
        "attack_ranged": 5,
        "defence_stab": 11,
        "defence_slash": 11,
        "defence_crush": 11,
        "defence_magic": 11,
        "defence_ranged": 11,
        "prayer": 10,
    },
    "completionist": {
        "attack_stab": 10,
        "attack_slash": 10,
        "attack_crush": 10,
        "attack_magic": 10,
        "attack_ranged": 10,
        "defence_stab": 12,
        "defence_slash": 12,
        "defence_crush": 12,
        "defence_magic": 12,
        "defence_ranged": 12,
        "prayer": 13,
    },
}
PRESTIGE_CAPE_BONUS_SOURCE = (
    "darkan-world-server developer-information/itemList.txt:21873,21875; "
    "itemListCS2.txt:20769,20771 (rev-727 cache item params)"
)

PRESTIGE_CAPES: tuple[PrestigeCape, ...] = (
    PrestigeCape(
        "quest_point",
        "Quest point cape",
        "Quest point hood",
        "Wise Old Man",
        99_000,
        "all_quests",
        0,
        9813,
        9814,
        0,
        "darkan-world-server c95aca4 content/world/areas/draynor/npcs/WiseOldMan.kt:16-33"
        " (completedAllQuests, 99,000 coins, hood 9814 + cape 9813); bonuses from"
        " data/cfg/items.yml item 9813",
    ),
    PrestigeCape(
        "max",
        "Max cape",
        "Max hood",
        "Max",
        2_475_000,
        "all_skills_99",
        99,
        20767,
        20768,
        10,
        "darkan-world-server c95aca4 content/world/npcs/max/MaxD.java:47-75"
        " (isMaxed(false), 2,475,000 coins, cape 20767 + hood 20768); "
        + PRESTIGE_CAPE_BONUS_SOURCE,
    ),
    PrestigeCape(
        "completionist",
        "Completionist cape",
        "Completionist hood",
        "Museum guard",
        5_000_000,
        "completionist",
        0,
        20769,
        20770,
        13,
        "Completionist cape oldid 6560039, 2012-11-15 (5,000,000 coins from the"
        " Varrock Museum guard); item ids 20769/20770 from darkan-world-server"
        " c95aca4 content/ItemConstants.java:412-414; "
        + PRESTIGE_CAPE_BONUS_SOURCE,
    ),
    PrestigeCape(
        "veteran_5",
        "Veteran cape (5 year)",
        "Veteran hood",
        "Hans",
        50_000,
        "answered_cards",
        VETERAN_ANSWERED_CARDS_PER_YEAR * 5,
        20763,
        20744,
        0,
        "Veteran cape (5 year) oldid 6474681 (Hans at Lumbridge Castle, 50,000"
        " coins, no stat bonuses); item id 20763 from darkan-world-server"
        " c95aca4 managers/EmotesManager.java:579-586",
    ),
    PrestigeCape(
        "veteran_10",
        "Veteran cape (10 year)",
        "Veteran hood",
        "Hans",
        100_000,
        "answered_cards",
        VETERAN_ANSWERED_CARDS_PER_YEAR * 10,
        24709,
        20744,
        0,
        "Veteran cape (10 year) oldid 6404608 (100,000 coins); item id 24709"
        " from darkan-world-server c95aca4 managers/EmotesManager.java:588-595",
    ),
)

PRESTIGE_CAPES_BY_ID: dict[str, PrestigeCape] = {cape.id: cape for cape in PRESTIGE_CAPES}


def cape_equipment_data_as_dict() -> "dict[str, Any]":
    """Every skillcape, hood and prestige cape as wearable equipment.

    ``core/constants.py`` folds this into ``EQUIPMENT_DATA``; nothing here
    touches the generated equipment table. The wear gate is the period one —
    level 99 in the skill for a skillcape, and for a prestige cape the same
    durable predicate the purchase checked, enforced by the logic layer rather
    than by ``skill_requirements``, because "every quest" is not a level.
    """

    from .equipment_data import EquipmentBonuses, EquipmentItem

    def _cape(name: str, item_id: int, requirements, bonuses, source: str, status: str, slot: str = "cape"):
        return EquipmentItem(
            item_name=name,
            slot=slot,
            combat_skill=None,
            required_level=1,
            two_handed=False,
            equipment_type="cape_of_accomplishment",
            bonuses=bonuses,
            attack_speed=4,
            source_item_id=item_id,
            source=source,
            source_status=status,
            skill_requirements=requirements,
            weapon_type=-1,
        )

    rows: dict[str, Any] = {}
    for cape in skillcape_definitions():
        gate = ((cape.skill_id, SKILLCAPE_LEVEL),)
        source = f"{SKILLCAPE_SOURCE}; bonuses from {SKILLCAPE_BONUS_SOURCE}"
        for name, item_id, bonuses in (
            (cape.cape, cape.cape_item_id, SKILLCAPE_BONUSES),
            (cape.trimmed_cape, cape.trimmed_item_id, TRIMMED_SKILLCAPE_BONUSES),
        ):
            rows[name] = _cape(
                name,
                item_id,
                gate,
                EquipmentBonuses(**bonuses),
                source,
                "items.yml defensive block; cache prayer param 11",
            )
        rows[cape.hood] = _cape(
            cape.hood,
            cape.hood_item_id,
            gate,
            EquipmentBonuses(),
            source,
            "items.yml equipment block; hoods carry no bonuses",
            slot="head",
        )

    for prestige in PRESTIGE_CAPES:
        if prestige.id == "quest_point":
            # The quest cape carries the trimmed-cape block: cache param 11
            # gives it the same prayer 4 as a trimmed skillcape.
            bonuses = EquipmentBonuses(**TRIMMED_SKILLCAPE_BONUSES)
            status = "items.yml equipment block"
        elif prestige.id in PRESTIGE_CAPE_BONUSES:
            bonuses = EquipmentBonuses(**PRESTIGE_CAPE_BONUSES[prestige.id])
            status = "rev-727 cache item-definition bonus params"
        else:
            bonuses = EquipmentBonuses(prayer=prestige.prayer_bonus)
            status = "period cape page; zero bonuses stated"
        rows[prestige.cape] = _cape(prestige.cape, prestige.cape_item_id, (), bonuses, prestige.source, status)
        rows.setdefault(
            prestige.hood,
            _cape(
                prestige.hood,
                prestige.hood_item_id,
                (),
                EquipmentBonuses(),
                prestige.source,
                "hood carries no bonuses",
                slot="head",
            ),
        )
    return rows
