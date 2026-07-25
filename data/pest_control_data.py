"""Period Pest Control values and disclosed shared-assault abstractions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .equipment_data import EquipmentBonuses, EquipmentItem


PEST_CONTROL_ACTIVITY_ID = "pest_control"
PEST_CONTROL_COMBAT_TARGET_ID = "pest_control_portal_front"
PEST_CONTROL_SOURCE = (
    "RuneScape Wiki Pest Control oldid=6571065 (2012-11-18T04:51:21Z); "
    "Void knight commendations oldid=6441647 (2012-10-19T04:44:16Z); "
    "2011Scape rev-667 items.yml"
)

PEST_CONTROL_PORTAL_COUNT = 4
PEST_CONTROL_VOID_KNIGHT_LIFEPOINTS = 2_000
PEST_CONTROL_PORTAL_HEAL = 500
PEST_CONTROL_PARTICIPATION_DAMAGE = 500
PEST_CONTROL_COMMENDATION_CAP = 500

# The source game lasts twenty minutes but does not publish a discrete action
# count. The owner-settled event-scaled translation compresses it into three
# consequential shared-assault beats per portal. These rates are disclosed
# provisional/source abstractions; the attested portal and knight LP stay real.
PEST_CONTROL_EVENT_REVIEWS = 12
PEST_CONTROL_DEFENCE_RELIEF = 400
PEST_CONTROL_SEAL_RELIEF = 300


@dataclass(frozen=True)
class PestControlLander:
    lander_id: str
    display_name: str
    combat_level: int
    portal_lifepoints: int
    commendations: int
    crowd_portal_damage: int


PEST_CONTROL_LANDERS = (
    PestControlLander("novice", "Novice lander", 40, 2_000, 2, 900),
    PestControlLander("intermediate", "Intermediate lander", 70, 2_500, 3, 1_120),
    PestControlLander("veteran", "Veteran lander", 100, 2_500, 4, 1_120),
)
PEST_CONTROL_LANDERS_BY_ID = {
    lander.lander_id: lander for lander in PEST_CONTROL_LANDERS
}


@dataclass(frozen=True)
class PestControlFront:
    role_id: str
    display_name: str
    knight_pressure: int
    portal_healing: int = 0
    crowd_damage_numerator: int = 100
    crowd_damage_bonus: int = 0
    attack_style: str = "melee"


# Each front names the authentic pest behavior represented by its aggregate
# terms. It does not claim an historical spawn count or per-beat damage rate.
PEST_CONTROL_FRONTS = (
    PestControlFront(
        "brawlers",
        "Brawlers blocking the assault",
        250,
        crowd_damage_numerator=85,
    ),
    PestControlFront(
        "spinners",
        "Spinners healing the portal",
        300,
        portal_healing=120,
    ),
    PestControlFront(
        "defilers_torchers",
        "Defilers and Torchers pressuring the knight",
        425,
        attack_style="ranged",
    ),
    PestControlFront(
        "shifters_splatters",
        "Shifters and Splatters breaking through",
        500,
    ),
)


PEST_CONTROL_DUTIES = (
    ("assault", "Assault the portal"),
    ("defend", "Defend the Void Knight"),
    ("seal", "Discharge a Void seal"),
)


VOID_SEAL_ITEM_IDS = {
    charge: 11674 - charge for charge in range(8, 0, -1)
}
VOID_SEAL_ITEMS = tuple(f"Void seal ({charge})" for charge in range(8, 0, -1))
VOID_SEAL_COST = 10


def pest_control_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        PEST_CONTROL_ACTIVITY_ID: {
            "display_name": "Pest Control",
            "requirements": {},
            "skill_requirements": {},
            "outputs": ("Void seal (8)",),
            "batch_size": 1,
            "group": "minigames",
            "source": PEST_CONTROL_SOURCE,
        }
    }


def pest_control_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    return {
        item_name: {
            "category": "equipment",
            "source_item_id": VOID_SEAL_ITEM_IDS[charge],
            "stackable": False,
            "tradeable": False,
            "source": PEST_CONTROL_SOURCE,
        }
        for charge, item_name in zip(range(8, 0, -1), VOID_SEAL_ITEMS)
    }


def pest_control_equipment_data_as_dict() -> dict[str, EquipmentItem]:
    return {
        item_name: EquipmentItem(
            item_name=item_name,
            slot="neck",
            combat_skill=None,
            required_level=1,
            two_handed=False,
            equipment_type="pest_control_reward",
            bonuses=EquipmentBonuses(
                defence_stab=1,
                defence_slash=1,
                defence_crush=1,
                defence_magic=1,
                defence_ranged=1,
            ),
            attack_speed=4,
            source_item_id=VOID_SEAL_ITEM_IDS[charge],
            source="2011Scape rev-667 items.yml; " + PEST_CONTROL_SOURCE,
            source_status="period item identity and equipment block",
            skill_requirements=(),
            weapon_type=-1,
        )
        for charge, item_name in zip(range(8, 0, -1), VOID_SEAL_ITEMS)
    }


def pest_control_portal_enemy_pure(
    lander_id: str,
    front_index: int,
) -> dict[str, Any]:
    lander = PEST_CONTROL_LANDERS_BY_ID.get(
        lander_id, PEST_CONTROL_LANDERS_BY_ID["novice"]
    )
    front = PEST_CONTROL_FRONTS[max(0, min(int(front_index), 3))]
    # The portal is an immobile object. Defence 1 and zero retaliation avoid
    # inventing NPC stats while the front's sourced role supplies pressure.
    return {
        "display_name": f"{front.display_name} · portal",
        "level": 0,
        "group": "Pest Control",
        "stats": {
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
            "hitpoints": lander.portal_lifepoints,
        },
        "bonuses": {},
        "attack_style": front.attack_style,
        "attack_speed": 6,
        "max_hit": 0,
        "retaliation_stop_lifepoints": lander.portal_lifepoints,
        "xp_multiplier": 0.5,
        "drops": {"guaranteed": (), "tables": ()},
        "source": PEST_CONTROL_SOURCE + "; portal combat stats disclosed abstraction",
    }
