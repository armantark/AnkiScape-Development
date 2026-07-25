"""Period-pinned Barrows encounter, reward, and equipment data."""

from __future__ import annotations

from typing import Any

from .equipment_data import EquipmentBonuses, EquipmentItem


BARROWS_ACTIVITY_ID = "barrows"
BARROWS_COMBAT_TARGET_ID = "barrows"
BARROWS_STATE_VERSION = 1
BARROWS_MAX_REWARD_POTENTIAL = 1_012
BARROWS_COMBAT_TICKS_PER_REVIEW = 6
BARROWS_EQUIPMENT_MAX_CONDITION = 90_000
BARROWS_SOURCE = (
    "RuneScape Wiki Barrows oldid=6555680 (2012-11-14); Barrows/Rewards "
    "oldid=5250545 (2012-02-13); Darkan BarrowsController.java"
)


def _enemy(
    display_name: str,
    npc_id: int,
    level: int,
    hitpoints: int,
    max_hit: int,
    attack_style: str,
    attack_speed: int,
    *,
    attack: int,
    strength: int,
    defence: int,
    magic: int = 1,
    ranged: int = 1,
    **extra: Any,
) -> dict[str, Any]:
    return {
        "display_name": display_name,
        "npc_id": npc_id,
        "level": level,
        "group": "Barrows",
        "stats": {
            "attack": attack,
            "strength": strength,
            "defence": defence,
            "magic": magic,
            "ranged": ranged,
            "hitpoints": hitpoints,
        },
        "bonuses": {},
        "attack_style": attack_style,
        "attack_speed": attack_speed,
        "max_hit": max_hit,
        "drops": {"guaranteed": (), "tables": ()},
        "slayer_xp": hitpoints / 10.0,
        "source": BARROWS_SOURCE,
        **extra,
    }


BARROWS_BROTHER_ORDER = (
    "dharok",
    "karil",
    "verac",
    "guthan",
    "torag",
    "ahrim",
    "akrisae",
)

BARROWS_BROTHER_DATA: dict[str, dict[str, Any]] = {
    "ahrim": _enemy(
        "Ahrim the Blighted", 2025, 130, 1_050, 200, "magic", 4,
        attack=1, strength=1, defence=100, magic=100,
        special="strength_drain", reward_item="Ahrim's staff",
    ),
    "dharok": _enemy(
        "Dharok the Wretched", 2026, 196, 1_000, 300, "melee", 3,
        attack=100, strength=100, defence=100,
        special="missing_lifepoints_max_hit", reward_item="Dharok's greataxe",
    ),
    "guthan": _enemy(
        "Guthan the Infested", 2027, 147, 1_000, 240, "melee", 5,
        attack=100, strength=100, defence=100,
        special="healing", reward_item="Guthan's warspear",
    ),
    "karil": _enemy(
        "Karil the Tainted", 2028, 121, 1_000, 207, "ranged", 6,
        attack=1, strength=1, defence=100, ranged=100,
        special="agility_drain", reward_item="Karil's crossbow",
    ),
    "torag": _enemy(
        "Torag the Corrupted", 2029, 146, 1_000, 260, "melee", 5,
        attack=100, strength=100, defence=100,
        special="run_energy_drain", reward_item="Torag's hammers",
    ),
    "verac": _enemy(
        "Verac the Defiled", 2030, 146, 1_000, 240, "melee", 5,
        attack=100, strength=100, defence=100,
        special="defiler", reward_item="Verac's flail",
    ),
    "akrisae": _enemy(
        "Akrisae the Doomed", 14297, 115, 1_000, 340, "melee", 5,
        attack=100, strength=100, defence=100, magic=100,
        special="protection_switch", reward_item="Akrisae's war mace",
        quest_gate="ritual_of_the_mahjarrat",
    ),
}

BARROWS_TUNNEL_ENEMY_DATA: dict[str, dict[str, Any]] = {
    "crypt_rat": _enemy("Crypt rat", 2033, 43, 350, 30, "melee", 6, attack=70, strength=20, defence=20),
    "bloodworm": _enemy("Bloodworm", 2031, 52, 440, 70, "melee", 6, attack=80, strength=20, defence=35),
    "crypt_spider": _enemy("Crypt spider", 2035, 56, 600, 30, "melee", 6, attack=45, strength=47, defence=45),
    "giant_crypt_rat": _enemy("Giant crypt rat", 2034, 76, 700, 90, "melee", 6, attack=80, strength=50, defence=65),
    "barrows_skeleton": _enemy("Skeleton", 2036, 77, 290, 30, "melee", 6, attack=74, strength=74, defence=74),
    "giant_crypt_spider": _enemy("Giant crypt spider", 2032, 79, 800, 100, "melee", 6, attack=65, strength=67, defence=65),
}

BARROWS_ENEMY_DATA = {**BARROWS_BROTHER_DATA, **BARROWS_TUNNEL_ENEMY_DATA}

BARROWS_ORDINARY_REWARDS = (
    (381, "Mind rune", 253, 336),
    (506, "Chaos rune", 112, 139),
    (631, "Death rune", 70, 83),
    (756, "Blood rune", 37, 43),
    (881, "Bolt rack", 35, 40),
)


_WEAPON_ROWS = {
    "ahrim": {
        "name": "Ahrim's staff", "ids": (4710, 4862, 4863, 4864, 4865, 4866),
        "speed": 6, "type": 1, "two_handed": True,
        "requirements": (("attack", 70), ("magic", 70)),
        "bonuses": dict(attack_stab=12, attack_slash=-1, attack_crush=65, attack_magic=15, defence_stab=3, defence_slash=5, defence_crush=2, defence_magic=15, melee_strength=68, magic_damage=10),
    },
    "dharok": {
        "name": "Dharok's greataxe", "ids": (4718, 4886, 4887, 4888, 4889, 4890),
        "speed": 7, "type": 2, "two_handed": True,
        "requirements": (("attack", 70), ("strength", 70)),
        "bonuses": dict(attack_stab=-4, attack_slash=103, attack_crush=95, attack_magic=-4, defence_ranged=-1, melee_strength=105),
    },
    "guthan": {
        "name": "Guthan's warspear", "ids": (4726, 4910, 4911, 4912, 4913, 4914),
        "speed": 5, "type": 14, "two_handed": True,
        "requirements": (("attack", 70),),
        "bonuses": dict(attack_stab=75, attack_slash=75, attack_crush=75, defence_stab=7, defence_slash=7, defence_crush=7, melee_strength=75),
    },
    "karil": {
        "name": "Karil's crossbow", "ids": (4734, 4934, 4935, 4936, 4937, 4938),
        "speed": 4, "type": 17, "two_handed": True,
        "requirements": (("ranged", 70),),
        "bonuses": dict(attack_ranged=84),
    },
    "torag": {
        "name": "Torag's hammers", "ids": (4747, 4958, 4959, 4960, 4961, 4962),
        "speed": 5, "type": 10, "two_handed": True,
        "requirements": (("attack", 70), ("strength", 70)),
        "bonuses": dict(attack_stab=-4, attack_slash=-4, attack_crush=85, attack_magic=-4, melee_strength=72),
    },
    "verac": {
        "name": "Verac's flail", "ids": (4755, 4982, 4983, 4984, 4985, 4986),
        "speed": 5, "type": 8, "two_handed": False,
        "requirements": (("attack", 70),),
        "bonuses": dict(attack_stab=68, attack_slash=-2, attack_crush=82, melee_strength=72, prayer=6),
    },
    "akrisae": {
        "name": "Akrisae's war mace", "ids": (21744, 21746, 21747, 21748, 21749, 21750),
        "speed": 5, "type": 8, "two_handed": False,
        "requirements": (("attack", 70), ("magic", 70), ("prayer", 70)),
        "bonuses": dict(attack_stab=52, attack_slash=-4, attack_crush=70, attack_magic=10, melee_strength=70, magic_damage=10, prayer=7),
    },
}


def barrows_condition_data_as_dict() -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for brother_id, row in _WEAPON_ROWS.items():
        full_name = str(row["name"])
        names = {
            100: f"{full_name} 100",
            75: f"{full_name} 75",
            50: f"{full_name} 50",
            25: f"{full_name} 25",
            0: f"{full_name} 0",
        }
        rows[brother_id] = {
            "display_name": full_name,
            "full_name": full_name,
            "max_condition": BARROWS_EQUIPMENT_MAX_CONDITION,
            "names_by_percent": names,
            "degrade_during_combat": True,
            "unsafe_death_percent": 0,
            "repair_cost": 100_000,
            "source": (
                "RuneScape Wiki Barrows equipment pre-EOC snapshot; "
                "Template:Barrows repair oldid=6555466; Darkan cache rev742"
            ),
        }
    return rows


BARROWS_CONDITION_DATA = barrows_condition_data_as_dict()


def barrows_equipment_data_as_dict() -> dict[str, EquipmentItem]:
    rows: dict[str, EquipmentItem] = {}
    for brother_id, raw in _WEAPON_ROWS.items():
        condition = BARROWS_CONDITION_DATA[brother_id]
        names = (condition["full_name"], *condition["names_by_percent"].values())
        ids = raw["ids"]
        for index, item_name in enumerate(names):
            rows[str(item_name)] = EquipmentItem(
                item_name=str(item_name),
                slot="weapon",
                combat_skill=None,
                required_level=70,
                two_handed=bool(raw["two_handed"]),
                equipment_type=("ranged_weapon" if brother_id == "karil" else "magic_weapon" if brother_id in {"ahrim", "akrisae"} else "weapon"),
                bonuses=EquipmentBonuses(**raw["bonuses"]),
                attack_speed=int(raw["speed"]),
                source_item_id=int(ids[min(index, len(ids) - 1)]),
                source=condition["source"],
                source_status="Darkan cache rev742 item params",
                skill_requirements=tuple(raw["requirements"]),
                weapon_type=int(raw["type"]),
            )
    return rows


def barrows_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    result = {
        "Mind rune": {"category": "material", "item_id": 558, "stackable": True, "tradeable": True, "source": BARROWS_SOURCE},
        "Chaos rune": {"category": "material", "item_id": 562, "stackable": True, "tradeable": True, "source": BARROWS_SOURCE},
        "Death rune": {"category": "material", "item_id": 560, "stackable": True, "tradeable": True, "source": BARROWS_SOURCE},
        "Blood rune": {"category": "material", "item_id": 565, "stackable": True, "tradeable": True, "source": BARROWS_SOURCE},
        "Bolt rack": {"category": "ammunition", "item_id": 4740, "stackable": True, "tradeable": True, "source": BARROWS_SOURCE},
    }
    for brother_id, raw in _WEAPON_ROWS.items():
        condition = BARROWS_CONDITION_DATA[brother_id]
        names = (condition["full_name"], *condition["names_by_percent"].values())
        ids = raw["ids"]
        for index, item_name in enumerate(names):
            result[str(item_name)] = {
                "category": "equipment",
                "item_id": int(ids[min(index, len(ids) - 1)]),
                "stackable": False,
                "tradeable": index in {0, len(names) - 1},
                "source": condition["source"],
            }
    return result


def barrows_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        BARROWS_ACTIVITY_ID: {
            "display_name": "Barrows",
            "requirements": {},
            "batch_size": 1,
            "group": "minigames",
            "outputs": tuple(row["reward_item"] for row in BARROWS_BROTHER_DATA.values()),
            "source": BARROWS_SOURCE,
        }
    }
