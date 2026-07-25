"""Period-pinned TzHaar Fight Cave waves, enemies, and rewards."""

from __future__ import annotations

from typing import Any


FIGHT_CAVES_ACTIVITY_ID = "fight_caves"
FIGHT_CAVES_COMBAT_TARGET_ID = "fight_caves"
FIGHT_CAVES_TOKKUL_ITEM = "Tokkul"
FIGHT_CAVES_CAPE_ITEM = "Fire cape"
FIGHT_CAVES_COMPLETION_TOKKUL = 16_064
FIGHT_CAVES_PARTIAL_TOKKUL_BASE = 8_032
FIGHT_CAVES_WAVE_COUNT = 63

FIGHT_CAVES_SOURCE = (
    "RuneScape Wiki TzHaar Fight Cave oldid=6584235 "
    "(2012-11-19T10:51:07Z); Darkan FightCavesController.java"
)

# Darkan's literal controller table matches the period page's powers-of-two
# construction and 63-wave breakdown. Large Tz-Keks split at death, so only the
# large form appears in the initial wave table.
FIGHT_CAVES_WAVES: tuple[tuple[str, ...], ...] = (
    ("tz_kih",),
    ("tz_kih", "tz_kih"),
    ("tz_kek",),
    ("tz_kek", "tz_kih"),
    ("tz_kek", "tz_kih", "tz_kih"),
    ("tz_kek", "tz_kek"),
    ("tok_xil",),
    ("tok_xil", "tz_kih"),
    ("tok_xil", "tz_kih", "tz_kih"),
    ("tok_xil", "tz_kek"),
    ("tok_xil", "tz_kek", "tz_kih"),
    ("tok_xil", "tz_kek", "tz_kih", "tz_kih"),
    ("tok_xil", "tz_kek", "tz_kek"),
    ("tok_xil", "tok_xil"),
    ("yt_mejkot",),
    ("yt_mejkot", "tz_kih"),
    ("yt_mejkot", "tz_kih", "tz_kih"),
    ("yt_mejkot", "tz_kek"),
    ("yt_mejkot", "tz_kek", "tz_kih"),
    ("yt_mejkot", "tz_kek", "tz_kih", "tz_kih"),
    ("yt_mejkot", "tz_kek", "tz_kek"),
    ("yt_mejkot", "tok_xil"),
    ("yt_mejkot", "tok_xil", "tz_kih"),
    ("yt_mejkot", "tok_xil", "tz_kih", "tz_kih"),
    ("yt_mejkot", "tok_xil", "tz_kek"),
    ("yt_mejkot", "tok_xil", "tz_kek", "tz_kih"),
    ("yt_mejkot", "tok_xil", "tz_kek", "tz_kih", "tz_kih"),
    ("yt_mejkot", "tok_xil", "tz_kek", "tz_kek"),
    ("yt_mejkot", "tok_xil", "tok_xil"),
    ("yt_mejkot", "yt_mejkot"),
    ("ket_zek",),
    ("ket_zek", "tz_kih"),
    ("ket_zek", "tz_kih", "tz_kih"),
    ("ket_zek", "tz_kek"),
    ("ket_zek", "tz_kek", "tz_kih"),
    ("ket_zek", "tz_kek", "tz_kih", "tz_kih"),
    ("ket_zek", "tz_kek", "tz_kek"),
    ("ket_zek", "tok_xil"),
    ("ket_zek", "tok_xil", "tz_kih"),
    ("ket_zek", "tok_xil", "tz_kih", "tz_kih"),
    ("ket_zek", "tok_xil", "tz_kek"),
    ("ket_zek", "tok_xil", "tz_kek", "tz_kih"),
    ("ket_zek", "tok_xil", "tz_kek", "tz_kih", "tz_kih"),
    ("ket_zek", "tok_xil", "tz_kek", "tz_kek"),
    ("ket_zek", "tok_xil", "tok_xil"),
    ("ket_zek", "yt_mejkot"),
    ("ket_zek", "yt_mejkot", "tz_kih"),
    ("ket_zek", "yt_mejkot", "tz_kih", "tz_kih"),
    ("ket_zek", "yt_mejkot", "tz_kek"),
    ("ket_zek", "yt_mejkot", "tz_kek", "tz_kih"),
    ("ket_zek", "yt_mejkot", "tz_kek", "tz_kih", "tz_kih"),
    ("ket_zek", "yt_mejkot", "tz_kek", "tz_kek"),
    ("ket_zek", "yt_mejkot", "tok_xil"),
    ("ket_zek", "yt_mejkot", "tok_xil", "tz_kih"),
    ("ket_zek", "yt_mejkot", "tok_xil", "tz_kih", "tz_kih"),
    ("ket_zek", "yt_mejkot", "tok_xil", "tz_kek"),
    ("ket_zek", "yt_mejkot", "tok_xil", "tz_kek", "tz_kih"),
    ("ket_zek", "yt_mejkot", "tok_xil", "tz_kek", "tz_kih", "tz_kih"),
    ("ket_zek", "yt_mejkot", "tok_xil", "tz_kek", "tz_kek"),
    ("ket_zek", "yt_mejkot", "tok_xil", "tok_xil"),
    ("ket_zek", "yt_mejkot", "yt_mejkot"),
    ("ket_zek", "ket_zek"),
    ("tztok_jad",),
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
    magic: int,
    ranged: int,
    source: str,
    **extra: Any,
) -> dict[str, Any]:
    return {
        "display_name": display_name,
        "npc_id": npc_id,
        "level": level,
        "group": "Fight Caves",
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
        "source": source,
        **extra,
    }


FIGHT_CAVES_ENEMY_DATA: dict[str, dict[str, Any]] = {
    "tz_kih": _enemy(
        "Tz-Kih", 2734, 22, 100, 44, "melee", 6,
        attack=20, strength=30, defence=15, magic=15, ranged=30,
        source="RuneScape Wiki Tz-Kih oldid=6451296; Darkan combatdefs 2734",
        prayer_drain_base=10,
        prayer_drain_damage=True,
        priority=0,
    ),
    "tz_kek": _enemy(
        "Tz-Kek", 2736, 45, 200, 74, "melee", 6,
        attack=40, strength=60, defence=30, magic=30, ranged=60,
        source="RuneScape Wiki Tz-Kek oldid=6235920; Darkan combatdefs 2736",
        melee_recoil_damage=10,
        splits_into=("tz_kek_small", "tz_kek_small"),
        priority=4,
    ),
    "tz_kek_small": _enemy(
        "Tz-Kek (small)", 2738, 22, 100, 44, "melee", 6,
        attack=20, strength=30, defence=15, magic=15, ranged=30,
        source="RuneScape Wiki Tz-Kek oldid=6235920; Darkan combatdefs 2738",
        priority=4,
    ),
    "tok_xil": _enemy(
        "Tok-Xil", 2739, 90, 400, 170, "ranged", 6,
        attack=80, strength=120, defence=60, magic=60, ranged=120,
        source="RuneScape Wiki Tok-Xil oldid=6207144; Darkan combatdefs 2739",
        priority=1,
    ),
    "yt_mejkot": _enemy(
        "Yt-MejKot", 2741, 180, 800, 280, "melee", 6,
        attack=160, strength=240, defence=120, magic=120, ranged=240,
        source="RuneScape Wiki Yt-MejKot oldid=6548201; Darkan combatdefs 2741",
        heal_amount=100,
        heal_every_attacks=2,
        priority=3,
    ),
    "ket_zek": _enemy(
        "Ket-Zek", 2743, 360, 1600, 540, "magic", 6,
        attack=320, strength=480, defence=240, magic=240, ranged=480,
        source="RuneScape Wiki Ket-Zek oldid=6207126; Darkan combatdefs 2743",
        priority=2,
    ),
    "tztok_jad": _enemy(
        "TzTok-Jad", 2745, 702, 2550, 970, "ranged", 2,
        attack=640, strength=960, defence=480, magic=480, ranged=960,
        source="RuneScape Wiki TzTok-Jad oldid=6547334; Darkan combatdefs 2745",
        melee_max_hit=980,
        priority=1,
    ),
    "yt_hurkot": _enemy(
        "Yt-HurKot", 2746, 108, 600, 140, "melee", 6,
        attack=140, strength=100, defence=60, magic=120, ranged=120,
        source="RuneScape Wiki Yt-HurKot oldid=6054672; Darkan combatdefs 2746",
        heal_amount=100,
        priority=0,
    ),
}


def fight_caves_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        FIGHT_CAVES_ACTIVITY_ID: {
            "display_name": "TzHaar Fight Cave",
            "requirements": {},
            "batch_size": 1,
            "group": "minigames",
            "outputs": (FIGHT_CAVES_TOKKUL_ITEM, FIGHT_CAVES_CAPE_ITEM),
            "source": FIGHT_CAVES_SOURCE,
        }
    }


def fight_caves_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    return {
        FIGHT_CAVES_CAPE_ITEM: {
            "category": "equipment",
            "item_id": 6570,
            "stackable": False,
            "tradeable": False,
            "source": "RuneScape Wiki Fire cape oldid=6591500",
        },
        FIGHT_CAVES_TOKKUL_ITEM: {
            "category": "material",
            "item_id": 6529,
            "stackable": True,
            "tradeable": False,
            "source": "RuneScape Wiki TzHaar Fight Cave oldid=6584235",
        },
    }
