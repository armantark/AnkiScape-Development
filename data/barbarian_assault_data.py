"""Period Barbarian Assault tables and bounded horizontal abstractions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .equipment_data import EquipmentBonuses, EquipmentItem


BARBARIAN_ASSAULT_ACTIVITY_ID = "barbarian_assault"
BARBARIAN_ASSAULT_COMBAT_TARGET_ID = "barbarian_assault_penance_front"
BARBARIAN_ASSAULT_SOURCE = (
    "RuneScape Wiki Barbarian Assault oldid=6288360 (2012-09-24T04:51:33Z); "
    "Barbarian Assault/Gameplay oldid=6288484 (2012-09-24T05:21:46Z); "
    "Rewards (Barbarian Assault) oldid=6316912 (2012-09-29T08:02:25Z); "
    "Penance Queen oldid=5795133 (2012-06-21T10:22:41Z); "
    "Runner boots oldid=6367883 (2012-10-08T06:01:12Z)"
)

BARBARIAN_ASSAULT_ROLES = (
    ("attacker", "Attacker"),
    ("collector", "Collector"),
    ("defender", "Defender"),
    ("healer", "Healer"),
)
BARBARIAN_ASSAULT_ROLE_IDS = tuple(role_id for role_id, _label in BARBARIAN_ASSAULT_ROLES)
BARBARIAN_ASSAULT_POINT_STORAGE_MAX = 2_147_483_647
BARBARIAN_ASSAULT_QUEEN_LIFEPOINTS = 2_500
BARBARIAN_ASSAULT_QUEEN_EGGS = 8
BARBARIAN_ASSAULT_OMEGA_DAMAGE = 313
BARBARIAN_ASSAULT_QUEEN_PRESSURE_DAMAGE = 65


@dataclass(frozen=True)
class BarbarianAssaultWave:
    wave: int
    fighters: int
    rangers: int
    healers: int
    runners: int
    fighter_level: int
    fighter_lifepoints: int
    ranger_level: int
    ranger_lifepoints: int
    healer_lifepoints: int
    fighter_max_hit: int
    ranger_max_hit: int


BARBARIAN_ASSAULT_WAVES = (
    BarbarianAssaultWave(1, 4, 4, 2, 2, 30, 280, 21, 200, 220, 40, 37),
    BarbarianAssaultWave(2, 5, 4, 3, 3, 32, 290, 25, 280, 270, 43, 38),
    BarbarianAssaultWave(3, 5, 6, 3, 4, 37, 320, 32, 290, 320, 46, 48),
    BarbarianAssaultWave(4, 6, 6, 4, 4, 42, 370, 38, 340, 380, 52, 54),
    BarbarianAssaultWave(5, 6, 6, 5, 5, 47, 380, 43, 410, 460, 57, 59),
    BarbarianAssaultWave(6, 6, 7, 6, 6, 56, 490, 51, 500, 500, 62, 66),
    BarbarianAssaultWave(7, 7, 7, 7, 6, 61, 500, 57, 500, 550, 69, 76),
    BarbarianAssaultWave(8, 7, 8, 7, 7, 68, 550, 64, 540, 620, 75, 84),
    BarbarianAssaultWave(9, 8, 8, 8, 9, 77, 560, 72, 580, 710, 87, 92),
    BarbarianAssaultWave(10, 7, 7, 7, 6, 61, 500, 57, 500, 550, 69, 76),
)
BARBARIAN_ASSAULT_WAVES_BY_NUMBER = {row.wave: row for row in BARBARIAN_ASSAULT_WAVES}


RUNNER_BOOTS_ITEM_ID = 10552
RUNNER_BOOTS_COST_PER_ROLE = 100


def barbarian_assault_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        BARBARIAN_ASSAULT_ACTIVITY_ID: {
            "display_name": "Barbarian Assault",
            "requirements": {},
            "skill_requirements": {},
            "outputs": ("Runner boots",),
            "batch_size": 1,
            "group": "minigames",
            "source": BARBARIAN_ASSAULT_SOURCE,
        }
    }


def barbarian_assault_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    return {
        "Runner boots": {
            "category": "equipment",
            "source_item_id": RUNNER_BOOTS_ITEM_ID,
            "stackable": False,
            "tradeable": False,
            "source": BARBARIAN_ASSAULT_SOURCE + "; OpenRS2 rev-742 item 10552",
        }
    }


def barbarian_assault_equipment_data_as_dict() -> dict[str, EquipmentItem]:
    return {
        "Runner boots": EquipmentItem(
            item_name="Runner boots",
            slot="feet",
            combat_skill="defense",
            required_level=40,
            two_handed=False,
            equipment_type="barbarian_assault_reward",
            bonuses=EquipmentBonuses(
                attack_magic=-3,
                attack_ranged=-1,
                defence_stab=12,
                defence_slash=13,
                defence_crush=14,
                melee_strength=2,
            ),
            attack_speed=4,
            source_item_id=RUNNER_BOOTS_ITEM_ID,
            source=(
                "2011Scape rev-667 data/cfg/items.yml item 10552; "
                + BARBARIAN_ASSAULT_SOURCE
            ),
            source_status="period item identity and unchanged equipment block",
            skill_requirements=(("defense", 40),),
            weapon_type=-1,
        )
    }


def barbarian_assault_role_scores_pure(wave_number: int) -> dict[str, int]:
    """Return the source-formula competent-team role contributions."""
    wave = BARBARIAN_ASSAULT_WAVES_BY_NUMBER[max(1, min(int(wave_number), 10))]
    if wave.wave == 10:
        return {role_id: 0 for role_id in BARBARIAN_ASSAULT_ROLE_IDS}
    return {
        "attacker": max(0, wave.fighters - 1) + max(0, wave.rangers - 1),
        # The source caps collected eggs at 60 and divides by 4.35.
        "collector": int(60 / 4.35),
        "defender": int(wave.runners * 1.8),
        # This smallest honest row uses healer kills only; optional LP-healing
        # points remain later performance depth rather than invented healing.
        "healer": int(wave.healers * 0.7),
    }


def barbarian_assault_wave_points_pure(wave_number: int, role_id: str) -> dict[str, int]:
    if int(wave_number) == 10:
        return {
            candidate: 80 if candidate == role_id else 5
            for candidate in BARBARIAN_ASSAULT_ROLE_IDS
        }
    scores = barbarian_assault_role_scores_pure(wave_number)
    team_points = sum(scores.values())
    return {
        candidate: team_points + scores[role_id] if candidate == role_id else 0
        for candidate in BARBARIAN_ASSAULT_ROLE_IDS
    }


def barbarian_assault_front_enemy_pure(wave_number: int) -> dict[str, Any]:
    wave = BARBARIAN_ASSAULT_WAVES_BY_NUMBER[max(1, min(int(wave_number), 10))]
    total_lifepoints = (
        wave.fighters * wave.fighter_lifepoints
        + wave.rangers * wave.ranger_lifepoints
    )
    return {
        "display_name": f"Wave {wave.wave} Penance front",
        "level": max(wave.fighter_level, wave.ranger_level),
        "group": "Barbarian Assault",
        "stats": {
            "attack": max(wave.fighter_level, wave.ranger_level),
            "strength": max(wave.fighter_level, wave.ranger_level),
            "defence": max(wave.fighter_level, wave.ranger_level),
            "magic": 1,
            "ranged": wave.ranger_level,
            "hitpoints": total_lifepoints,
        },
        "bonuses": {},
        "attack_style": "ranged",
        "attack_speed": 6,
        "max_hit": max(wave.fighter_max_hit, wave.ranger_max_hit),
        "xp_multiplier": 0.0,
        "drops": {"guaranteed": (), "tables": ()},
        "source": BARBARIAN_ASSAULT_SOURCE + "; aggregate front abstraction",
    }
