"""Period-pinned horizontal data for the Stronghold of Player Safety."""

from __future__ import annotations

from typing import Any

from ..data.equipment_data import EquipmentBonuses, EquipmentItem


STRONGHOLD_PLAYER_SAFETY_ACTIVITY_ID = "stronghold_player_safety"
COCKROACH_SOLDIER_TARGET_ID = "cockroach_soldier"
SAFETY_GLOVES_ITEM = "Safety gloves"
STRONGHOLD_PLAYER_SAFETY_SOURCE = (
    "RuneScape Wiki Stronghold of Player Safety oldid=6487359 "
    "(2012-10-27T21:41:27Z); Safety gloves oldid=6081806 "
    "(2012-08-12T22:00:03Z); Misthalin Training Centre of Excellence "
    "oldid=6430839 (2012-10-17T00:04:00Z); Cockroach soldier "
    "oldid=6539651 (2012-11-06T22:58:45Z); Darkan NPC 7160 identity only"
)


STRONGHOLD_LANDMARKS = (
    {
        "id": "poster_tunnel",
        "label": "Poster tunnel",
        "result": "Slipped behind the jail-cell poster and crossed the old mugger rooms.",
    },
    {
        "id": "lever_and_rope",
        "label": "Lever and surface rope",
        "result": "Reached the soldier room, pulled the old lever, and unlocked the surface crevice.",
    },
    {
        "id": "reward_passage",
        "label": "Reward passage",
        "result": "Returned through the opened jail door and reached the reward chest.",
    },
)


def stronghold_player_safety_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        STRONGHOLD_PLAYER_SAFETY_ACTIVITY_ID: {
            "display_name": "Stronghold of Player Safety",
            "requirements": {},
            "batch_size": 1,
            "group": "landmarks",
            "source": STRONGHOLD_PLAYER_SAFETY_SOURCE,
        }
    }


def stronghold_player_safety_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    return {
        SAFETY_GLOVES_ITEM: {
            "category": "equipment",
            "source_item_id": 12629,
            "stackable": False,
            "tradeable": False,
            "source": STRONGHOLD_PLAYER_SAFETY_SOURCE,
        }
    }


def stronghold_player_safety_equipment_data_as_dict() -> dict[str, EquipmentItem]:
    return {
        SAFETY_GLOVES_ITEM: EquipmentItem(
            item_name=SAFETY_GLOVES_ITEM,
            slot="hands",
            combat_skill=None,
            required_level=1,
            two_handed=False,
            equipment_type="stronghold_reward",
            bonuses=EquipmentBonuses(
                defence_stab=1,
                defence_slash=2,
                defence_crush=2,
                defence_magic=1,
                defence_ranged=2,
            ),
            attack_speed=4,
            source_item_id=12629,
            source=STRONGHOLD_PLAYER_SAFETY_SOURCE,
            source_status=(
                "period item identity and complete cutoff equipment block; "
                "the engine does not expose the separate +1 Summoning defence field"
            ),
            skill_requirements=(),
            weapon_type=-1,
        )
    }


def cockroach_soldier_enemy_as_dict() -> dict[str, Any]:
    # The cutoff page closes identity, level, LP, speed, attack styles, and
    # maximum hits, but not the five hidden combat skills or bonuses. The
    # level-equals-stat row is the neutral disclosed fallback already used for
    # breadth work; drops remain empty rather than inventing probabilities.
    return {
        "display_name": "Cockroach soldier",
        "level": 83,
        "group": "Stronghold of Player Safety",
        "attack_style": "melee",
        "attack_style_by_player_class": {
            "melee": "melee",
            "ranged": "ranged",
            "magic": "ranged",
        },
        "attack_speed": 6,
        "max_hit": 110,
        "stats": {
            "hitpoints": 960,
            "attack": 83,
            "strength": 83,
            "defence": 83,
            "magic": 1,
            "ranged": 83,
        },
        "bonuses": {},
        "drops": {"guaranteed": (), "tables": ()},
        "encounter_only": True,
        "source": STRONGHOLD_PLAYER_SAFETY_SOURCE,
        "source_status": (
            "period-exact identity, LP, attack speed, dual-style behavior, and "
            "110 ranged maximum; hidden combat skills use a disclosed "
            "level-equals-stat fallback, and drop probabilities are source_blocked"
        ),
    }
