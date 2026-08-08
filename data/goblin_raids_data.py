"""Pinned Goblin Raids world clock, goblin roster, Raider set and boss loop.

Every combat row here is derived from a stat block AnkiScape already carries with
an emulator citation, rather than from a placeholder: the period Goblin Raider is
a level-2 goblin with 50 lifepoints and `goblin_level_2_armed` already is exactly
that, and Hollowtoof and the three village bosses are level-5 goblins whose
stated lifepoints are the only field that differs from `goblin_level_5`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .equipment_data import EquipmentBonuses, EquipmentItem


GOBLIN_RAIDS_ACTIVITY_ID = "goblin_raids"
GOBLIN_RAIDS_RAID_MODE = "raid"
GOBLIN_RAIDS_VILLAGE_MODE = "village"

GOBLIN_RAIDS_SOURCE = (
    "RuneScape Wiki Goblin Raids oldid=6545250 (2012-11-09T20:21:45Z); "
    "Update:What's Mine is Yours oldid=6434891 (2012-10-17T15:08:44Z); "
    "Hollowtoof oldid=6522288 (2012-11-03T04:29:15Z); Goblin Raider "
    "oldid=6464537 (2012-10-24T16:33:38Z); Commander Yodri oldid=6548002 "
    "(2012-11-11T11:02:18Z); Brokeface oldid=6444343 (2012-10-19T21:29:58Z); "
    "Stinkears oldid=6447564 (2012-10-20T21:27:42Z); Lumpnose oldid=6550383 "
    "(2012-11-12T23:45:38Z); Raider axe oldid=6464509; Raider chainbody "
    "oldid=6464451; Raider shield oldid=6464501; Goblin cower shield "
    "oldid=6444335 (2012-10-19T21:29:09Z); Tip.It Goblin Raids guide last "
    "updated 2012-10-24, Wayback 20121228205432; OpenRS2 rev-741 cache item "
    "definitions 25350-25353"
)

# The article says a notice goes out server-wide every thirty minutes with the
# latest incursion's location. The house review clock runs 240 answered cards to
# the game day, so the settled Evil Tree-style discovery opportunity opens every
# five answered cards. This is the notice cadence, not a recovered server spawn
# timer.
GOBLIN_RAIDS_SPAWN_REVIEWS = 5

# PLACEHOLDER(goblin_raids.raid_active_reviews): how long a raid stays up. The
# announcement cadence is stated; the raid's own duration, its despawn timer and
# what happens when nobody clears it are all unstated. The complete pre-cutoff
# article/talk history, rev-741/742 client interfaces and current Darkan tree add
# no server timer. Fifteen reviews is three announcement intervals, which is long
# enough for the sourced raider-then-leader sequence to actually be completed.
GOBLIN_RAIDS_ACTIVE_REVIEWS = 15

# Exact through independent period convergence. The official rule pays one
# Yodri item per raider slain; Tip.It's 2012-10-24 guide caps the location
# payout at ten, and the pinned release-day screenshot visibly shows nine
# ordinary Raiders with Hollowtoof separate.
GOBLIN_RAIDS_RAIDER_COUNT = 10

# Exact: every fifteen goblins killed inside the village gates summons one of the
# three bosses, and goblins outside the gates do not count.
GOBLIN_RAIDS_VILLAGE_BOSS_KILLS = 15

# PLACEHOLDER(goblin_raids.intimidation_combat_level): the combat level at which
# Hollowtoof hands over the whole Raider set rather than being fought. The pinned
# revision gives two conflicting approximations in the same article, "around
# level 95" near the top and "approx. level 90" in its gameplay section.
GOBLIN_RAIDS_INTIMIDATION_COMBAT_LEVEL = 90

# Exact, from the release update: the shield grants 25% bonus Attack, Defence
# and/or Constitution experience up to 1,000 bonus experience in total, after
# which it is purely cosmetic.
GOBLIN_COWER_SHIELD = "Goblin cower shield"
GOBLIN_COWER_SHIELD_BONUS_RATE = 0.25
GOBLIN_COWER_SHIELD_BONUS_BUDGET = 1000.0
GOBLIN_COWER_SHIELD_EXP_KEYS = (
    "attack_exp",
    "defense_exp",
    "constitution_exp",
)

# PLACEHOLDER(goblin_raids.cower_shield_drop_chance): each village boss is stated
# to have "a chance" of dropping the shield; no revision gives the rate.
GOBLIN_COWER_SHIELD_DROP_CHANCE = 0.25


@dataclass(frozen=True)
class GoblinRaidSite:
    id: str
    display_name: str
    # Exact: farms give seeds, forests give logs, mines give ores.
    spoil_kind: str
    materials: tuple[str, ...]


# The three site kinds the article names. It shows a potato field in its own
# screenshot but never names a raid location, so the sites are the kinds rather
# than invented place names.
#
# PLACEHOLDER(goblin_raids.raided_material_tables): which items each kind yields
# and at what rate. The forest row is the one the source states by example, "two
# logs and one oak log"; the seed and ore rows use the most basic period item of
# the stated kind because no revision lists them.
GOBLIN_RAID_SITES = (
    GoblinRaidSite("farm", "a farm", "seeds", ("Potato seed",)),
    GoblinRaidSite("forest", "a woodcutting site", "logs", ("Logs", "Oak logs")),
    GoblinRaidSite("mine", "a mine", "ores", ("Copper ore", "Tin ore")),
)
GOBLIN_RAID_SITES_BY_ID = {site.id: site for site in GOBLIN_RAID_SITES}
GOBLIN_RAID_SITE_IDS = tuple(site.id for site in GOBLIN_RAID_SITES)


# Sourced roster. `base` names the registered goblin row each entry inherits its
# emulator-cited offensive stats from; `lifepoints` and `attack_style` are the
# fields the period pages state directly.
@dataclass(frozen=True)
class GoblinRaidEnemy:
    id: str
    display_name: str
    base: str
    level: int
    lifepoints: int
    attack_style: str
    examine: str
    # Lifepoints-scale maximum hit. Only stated for Lumpnose, and only needed by
    # the engine for a non-melee attacker, which a melee row derives correctly.
    max_hit: int = 0


GOBLIN_RAIDER = GoblinRaidEnemy(
    "goblin_raids_raider",
    "Goblin Raider",
    "goblin_level_2_armed",
    2,
    50,
    "melee",
    "Stealing everything that isn't nailed down.",
)
HOLLOWTOOF = GoblinRaidEnemy(
    "goblin_raids_hollowtoof",
    "Hollowtoof",
    "goblin_level_5",
    5,
    140,
    "melee",
    "Overseeing the raid",
)
GOBLIN_RAID_VILLAGE_BOSSES = (
    GoblinRaidEnemy(
        "goblin_raids_brokeface",
        "Brokeface",
        "goblin_level_5",
        5,
        120,
        "melee",
        "Stabbin' time!",
    ),
    GoblinRaidEnemy(
        "goblin_raids_stinkears",
        "Stinkears",
        "goblin_level_5",
        5,
        120,
        "magic",
        "Zap! Dat's da way!",
        # PLACEHOLDER(goblin_raids.stinkears_max_hit): Lumpnose's pinned revision
        # states a maximum hit of 20 and Stinkears' does not, so its
        # same-level, same-lifepoints sibling's figure stands in. A magic
        # attacker with no declared maximum would otherwise fall back to the
        # melee-strength derivation, which is wrong for a caster.
        20,
    ),
    GoblinRaidEnemy(
        "goblin_raids_lumpnose",
        "Lumpnose",
        "goblin_level_5",
        5,
        120,
        "ranged",
        "Death from a distance!",
        # Exact, from the pinned Lumpnose revision.
        20,
    ),
)
# The village's ordinary goblins. Unnamed in the period but plainly period
# content, and the fifteen-kill boss trigger counts them, so they inherit the
# level-5 goblin row unchanged.
VILLAGE_GOBLIN = GoblinRaidEnemy(
    "goblin_raids_village_goblin",
    "Goblin (Goblin Village)",
    "goblin_level_5",
    5,
    120,
    "melee",
    "An ugly green creature inside the village gates.",
)
GOBLIN_RAID_ENEMIES = (
    GOBLIN_RAIDER,
    HOLLOWTOOF,
    VILLAGE_GOBLIN,
) + GOBLIN_RAID_VILLAGE_BOSSES
GOBLIN_RAID_ENEMIES_BY_ID = {row.id: row for row in GOBLIN_RAID_ENEMIES}
GOBLIN_RAID_VILLAGE_BOSS_IDS = tuple(
    row.id for row in GOBLIN_RAID_VILLAGE_BOSSES
)


# Exact: Hollowtoof drops one piece per kill in this order, and a player who
# already holds the whole set is dropped the chainbody again.
@dataclass(frozen=True)
class RaiderSetPiece:
    item_name: str
    slot: str
    source_item_id: int
    required_attack: int


RAIDER_SET = (
    RaiderSetPiece("Raider chainbody", "body", 25_352, 1),
    # Exact: the pinned Raider axe revision states 8 Attack to wield. Neither
    # the chainbody nor the shield revision states a Defence requirement.
    RaiderSetPiece("Raider axe", "weapon", 25_351, 8),
    RaiderSetPiece("Raider shield", "shield", 25_353, 1),
)
RAIDER_SET_ITEM_NAMES = tuple(piece.item_name for piece in RAIDER_SET)

RAIDER_SET_SOURCE_STATUS = "rev-741 cache item definitions"

# PLACEHOLDER(goblin_raids.yodri_reward_table): what Commander Yodri hands over.
# The article says he gives "an item from the black guard's store for every
# goblin slain" plus a location-appropriate extra, and his own page calls it a
# small reward suiting the raid's place and the goblins killed. Neither states
# the store's contents. The per-goblin unit is sourced; the item is not, so the
# reward pays the raid site's own stated material kind, which is the one thing
# the source does name.
GOBLIN_RAIDS_YODRI_ITEMS_PER_GOBLIN = 1

GOBLIN_COWER_SHIELD_ITEM_ID = 25_350

RAIDER_SET_BONUSES = {
    "Raider axe": EquipmentBonuses(
        attack_stab=-2,
        attack_slash=18,
        attack_crush=13,
        defence_ranged=-1,
        melee_strength=22,
    ),
    "Raider chainbody": EquipmentBonuses(
        attack_magic=-15,
        defence_stab=20,
        defence_slash=29,
        defence_crush=35,
        defence_magic=-3,
        defence_ranged=22,
    ),
    "Raider shield": EquipmentBonuses(
        attack_magic=-6,
        attack_ranged=-2,
        defence_stab=14,
        defence_slash=15,
        defence_crush=13,
        defence_ranged=14,
    ),
}
GOBLIN_COWER_SHIELD_BONUSES = EquipmentBonuses(
    attack_magic=-8,
    attack_ranged=-2,
    defence_stab=13,
    defence_slash=15,
    defence_crush=14,
    defence_magic=-1,
    defence_ranged=14,
)


GOBLIN_RAIDS_ASSET_MANIFEST = (
    {
        "item_name": "Goblin Raids",
        "wiki_title": "Goblin raid.png",
        "output_path": "activityicons/goblin_raids.png",
        "size": 64,
    },
    {
        "item_name": "Hollowtoof",
        "wiki_title": "Hollowtoof.png",
        "output_path": "combatenemies/goblin_raids_hollowtoof.png",
        "size": 64,
    },
    {
        "item_name": "Goblin Raider",
        "wiki_title": "Goblin Raider.png",
        "output_path": "combatenemies/goblin_raids_raider.png",
        "size": 64,
    },
    {
        "item_name": "Brokeface",
        "wiki_title": "Brokeface.png",
        "output_path": "combatenemies/goblin_raids_brokeface.png",
        "size": 64,
    },
    {
        "item_name": "Stinkears",
        "wiki_title": "Stinkears.png",
        "output_path": "combatenemies/goblin_raids_stinkears.png",
        "size": 64,
    },
    {
        "item_name": "Lumpnose",
        "wiki_title": "Lumpnose.png",
        "output_path": "combatenemies/goblin_raids_lumpnose.png",
        "size": 64,
    },
)


def goblin_raids_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        GOBLIN_RAIDS_ACTIVITY_ID: {
            "display_name": "Goblin Raids",
            "requirements": {},
            "skill_requirements": {},
            "outputs": (),
            "batch_size": 1,
            "group": "distractions_and_diversions",
            "source": GOBLIN_RAIDS_SOURCE,
        }
    }


def goblin_raids_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    """Register the four reward items the generated tables have no row for."""
    items: dict[str, dict[str, Any]] = {
        piece.item_name: {
            "category": "equipment",
            "source_item_id": piece.source_item_id,
            "stackable": False,
            "tradeable": False,
            "equipment_slot": piece.slot,
            "source": GOBLIN_RAIDS_SOURCE,
        }
        for piece in RAIDER_SET
    }
    items[GOBLIN_COWER_SHIELD] = {
        "category": "equipment",
        "source_item_id": GOBLIN_COWER_SHIELD_ITEM_ID,
        "stackable": False,
        "tradeable": False,
        "equipment_slot": "shield",
        "source": GOBLIN_RAIDS_SOURCE,
    }
    return items


def goblin_raids_equipment_data_as_dict() -> dict[str, EquipmentItem]:
    rows = {
        piece.item_name: EquipmentItem(
            item_name=piece.item_name,
            slot=piece.slot,
            combat_skill="attack" if piece.slot == "weapon" else None,
            required_level=piece.required_attack,
            two_handed=False,
            equipment_type="raider_set",
            bonuses=RAIDER_SET_BONUSES[piece.item_name],
            attack_speed=5 if piece.slot == "weapon" else 4,
            source_item_id=piece.source_item_id,
            source=GOBLIN_RAIDS_SOURCE,
            source_status=RAIDER_SET_SOURCE_STATUS,
            skill_requirements=(),
            weapon_type=-1,
        )
        for piece in RAIDER_SET
    }
    rows[GOBLIN_COWER_SHIELD] = EquipmentItem(
        item_name=GOBLIN_COWER_SHIELD,
        slot="shield",
        combat_skill=None,
        required_level=1,
        two_handed=False,
        equipment_type="goblin_cower_shield",
        bonuses=GOBLIN_COWER_SHIELD_BONUSES,
        attack_speed=4,
        source_item_id=GOBLIN_COWER_SHIELD_ITEM_ID,
        source=GOBLIN_RAIDS_SOURCE,
        source_status="pinned period bonus-experience shield, no combat bonuses",
        skill_requirements=(),
        weapon_type=-1,
    )
    return rows


def goblin_raids_enemies_pure(
    base_enemies: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Build the raid roster from the registered goblin rows it inherits from.

    Only the fields a period page states are overridden: the display name, the
    stated lifepoints, the stated attack style, and the examine text. Everything
    else — the attack and defence stats, the bonus block, the drop tables — stays
    exactly as the emulator-cited goblin row has it, so no roster stat has to be
    a placeholder.
    """
    roster: dict[str, dict[str, Any]] = {}
    for row in GOBLIN_RAID_ENEMIES:
        base = base_enemies.get(row.base)
        if base is None:
            continue
        enemy = {key: value for key, value in base.items()}
        enemy["stats"] = {**base["stats"], "hitpoints": row.lifepoints}
        enemy["display_name"] = row.display_name
        enemy["level"] = row.level
        enemy["attack_style"] = row.attack_style
        enemy["group"] = "Goblin Raids"
        enemy["examine"] = row.examine
        if row.max_hit:
            enemy["max_hit"] = row.max_hit
        enemy["source"] = (
            f"{GOBLIN_RAIDS_SOURCE}; offensive stats inherited from "
            f"{row.base}"
        )
        roster[row.id] = enemy
    return roster
