"""Cutoff Castle Wars values and disclosed review-scale translations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:
    from .equipment_data import EquipmentBonuses, EquipmentItem
except ImportError:  # pragma: no cover - flat test imports
    from equipment_data import EquipmentBonuses, EquipmentItem  # type: ignore


CASTLE_WARS_ACTIVITY_ID = "castle_wars"
CASTLE_WARS_COMBAT_TARGET_ID = "castle_wars_raider"
CASTLE_WARS_SOURCE = (
    "RuneScape Wiki Castle Wars oldid=6528924 (2012-11-03T13:56:56Z); "
    "Saradomin halo oldid=6268461 (2012-09-19T17:25:22Z); "
    "OpenRS2 cache rev 742"
)

# The source match is twenty minutes and requires ten minutes of participation.
# The settled event-scale adaptation uses one consequential review per two
# source minutes. This is foreground grouping, never wall-clock simulation.
CASTLE_WARS_MATCH_REVIEWS = 10
CASTLE_WARS_REWARD_MINIMUM_REVIEWS = 5
CASTLE_WARS_MAX_BARRICADES = 10
CASTLE_WARS_COMBAT_TICKS_PER_REVIEW = 6

# Hidden team composition and opponent rolls are not published. These bounded
# event-scale constants keep the ten-beat match useful without pretending to
# recover a historical bot population.
CASTLE_WARS_CAPTURE_PROGRESS = 4
CASTLE_WARS_PLAYER_CROWD_PROGRESS = 1
CASTLE_WARS_OPPONENT_CROWD_PROGRESS = 1
CASTLE_WARS_OPPONENT_BURST_CHANCE = 0.25
CASTLE_WARS_GATE_MAX = 100
CASTLE_WARS_CATAPULT_MAX = 100
CASTLE_WARS_PRESSURE_DAMAGE = 15

CASTLE_WARS_DUTIES = (
    ("capture", "Capture the standard"),
    ("defend", "Defend against a raider"),
    ("barricade", "Deploy a barricade"),
    ("repair", "Repair the gate and catapult"),
    ("catapult", "Fire the catapult"),
    ("support", "Use bandages and support"),
)
CASTLE_WARS_TEAMS = (
    ("balance", "Guthix · balance teams"),
    ("saradomin", "Saradomin"),
    ("zamorak", "Zamorak"),
)

CASTLE_WARS_ITEM_IDS = {
    "Castle wars ticket": 4067,
    "Basic decorative platebody": 4069,
    "Basic decorative platelegs": 4070,
    "Basic decorative shield": 4072,
    "Ballista base": 18710,
    "Ballista bolt stack": 18711,
    "Ballista bow": 18712,
    "Ballista chamber": 18713,
    "Ballista ammo": 18714,
    "Saradomin halo": 18745,
    "Castle wars hobbyist cape": 24162,
    "Castlewars chinchompa": 21531,
}

CASTLE_WARS_BASIC_SET = frozenset(
    {
        "Basic decorative platebody",
        "Basic decorative platelegs",
        "Basic decorative shield",
    }
)
CASTLE_WARS_BALLISTA_PARTS = (
    "Ballista base",
    "Ballista bolt stack",
    "Ballista bow",
    "Ballista chamber",
)


@dataclass(frozen=True)
class CastleWarsReward:
    reward_id: str
    item_name: str
    ticket_cost: int
    quantity: int = 1
    minimum_games: int = 0


CASTLE_WARS_REWARDS = (
    CastleWarsReward("basic_body", "Basic decorative platebody", 8),
    CastleWarsReward("basic_legs", "Basic decorative platelegs", 6),
    CastleWarsReward("basic_shield", "Basic decorative shield", 6),
    CastleWarsReward("saradomin_halo", "Saradomin halo", 300),
    CastleWarsReward(
        "hobbyist_cape",
        "Castle wars hobbyist cape",
        2,
        minimum_games=500,
    ),
    CastleWarsReward("ballista_base", "Ballista base", 2),
    CastleWarsReward("ballista_stack", "Ballista bolt stack", 2),
    CastleWarsReward("ballista_bow", "Ballista bow", 2),
    CastleWarsReward("ballista_chamber", "Ballista chamber", 2),
    CastleWarsReward("ballista_ammo", "Ballista ammo", 4, quantity=100),
    CastleWarsReward("chinchompas", "Castlewars chinchompa", 1, quantity=3),
)
CASTLE_WARS_REWARDS_BY_ID = {
    reward.reward_id: reward for reward in CASTLE_WARS_REWARDS
}


def castle_wars_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        CASTLE_WARS_ACTIVITY_ID: {
            "display_name": "Castle Wars",
            "requirements": {},
            "skill_requirements": {},
            "outputs": ("Castle wars ticket",),
            "batch_size": 1,
            "group": "minigames",
            "source": CASTLE_WARS_SOURCE,
        }
    }


def castle_wars_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    equipment = CASTLE_WARS_BASIC_SET | {
        "Saradomin halo",
        "Castle wars hobbyist cape",
    }
    stackable = {
        "Castle wars ticket",
        "Ballista ammo",
        "Castlewars chinchompa",
    }
    return {
        item_name: {
            "category": "equipment" if item_name in equipment else "activity_reward",
            "source_item_id": item_id,
            "stackable": item_name in stackable,
            "tradeable": False,
            "source": CASTLE_WARS_SOURCE,
        }
        for item_name, item_id in CASTLE_WARS_ITEM_IDS.items()
    }


def castle_wars_equipment_data_as_dict() -> dict[str, EquipmentItem]:
    rows = {
        "Basic decorative platebody": EquipmentItem(
            item_name="Basic decorative platebody",
            slot="body",
            combat_skill="defense",
            required_level=5,
            two_handed=False,
            equipment_type="platebody",
            bonuses=EquipmentBonuses(
                attack_magic=-30,
                attack_ranged=-10,
                defence_stab=32,
                defence_slash=31,
                defence_crush=24,
                defence_magic=-6,
                defence_ranged=31,
            ),
            attack_speed=4,
            source_item_id=4069,
            source=CASTLE_WARS_SOURCE + "; Steel platebody-equivalent cutoff row",
            source_status="period equipment equivalence",
            skill_requirements=(("defense", 5),),
            weapon_type=-1,
        ),
        "Basic decorative platelegs": EquipmentItem(
            item_name="Basic decorative platelegs",
            slot="legs",
            combat_skill="defense",
            required_level=5,
            two_handed=False,
            equipment_type="platelegs",
            bonuses=EquipmentBonuses(
                attack_magic=-21,
                attack_ranged=-7,
                defence_stab=17,
                defence_slash=16,
                defence_crush=15,
                defence_magic=-4,
                defence_ranged=16,
            ),
            attack_speed=4,
            source_item_id=4070,
            source=CASTLE_WARS_SOURCE + "; Steel platelegs-equivalent cutoff row",
            source_status="period equipment equivalence",
            skill_requirements=(("defense", 5),),
            weapon_type=-1,
        ),
        "Basic decorative shield": EquipmentItem(
            item_name="Basic decorative shield",
            slot="shield",
            combat_skill="defense",
            required_level=5,
            two_handed=False,
            equipment_type="kite_shield",
            bonuses=EquipmentBonuses(
                attack_magic=-8,
                attack_ranged=-2,
                defence_stab=13,
                defence_slash=15,
                defence_crush=14,
                defence_magic=-1,
                defence_ranged=14,
            ),
            attack_speed=4,
            source_item_id=4072,
            source=CASTLE_WARS_SOURCE + "; Steel kiteshield-equivalent cutoff row",
            source_status="period equipment equivalence",
            skill_requirements=(("defense", 5),),
            weapon_type=-1,
        ),
        "Saradomin halo": EquipmentItem(
            item_name="Saradomin halo",
            slot="head",
            combat_skill=None,
            required_level=1,
            two_handed=False,
            equipment_type="castle_wars_reward",
            bonuses=EquipmentBonuses(
                defence_stab=11,
                defence_slash=12,
                defence_crush=10,
                defence_magic=11,
                defence_ranged=-1,
            ),
            attack_speed=4,
            source_item_id=18745,
            source=CASTLE_WARS_SOURCE,
            source_status="literal period bonus table",
            skill_requirements=(),
            weapon_type=-1,
        ),
        "Castle wars hobbyist cape": EquipmentItem(
            item_name="Castle wars hobbyist cape",
            slot="cape",
            combat_skill=None,
            required_level=1,
            two_handed=False,
            equipment_type="castle_wars_reward",
            bonuses=EquipmentBonuses(),
            attack_speed=4,
            source_item_id=24162,
            source=CASTLE_WARS_SOURCE,
            source_status="period cosmetic milestone reward",
            skill_requirements=(),
            weapon_type=-1,
        ),
    }
    return rows


def castle_wars_raider_enemy_pure() -> dict[str, Any]:
    """Return the isolated opponent abstraction used by the defensive duty."""
    return {
        "display_name": "Enemy standard raider",
        "level": 50,
        "group": "Castle Wars",
        "stats": {
            "attack": 50,
            "strength": 50,
            "defence": 50,
            "magic": 1,
            "ranged": 1,
            "hitpoints": 500,
        },
        "bonuses": {},
        "attack_style": "melee",
        "attack_speed": 4,
        "max_hit": 60,
        "xp_multiplier": 1.0,
        "drops": {"guaranteed": (), "tables": ()},
        "source": CASTLE_WARS_SOURCE + "; bounded opponent abstraction/source_blocked",
    }
