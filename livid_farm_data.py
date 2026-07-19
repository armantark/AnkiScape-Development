"""Period-pinned Livid Farm cycle, unlock, and reward data."""

from __future__ import annotations

from typing import Final


LIVID_FARM_ACTIVITY_ID: Final = "livid_farm"
LIVID_FARM_SOURCE: Final = (
    "RuneScape Wiki Livid Farm oldid=6569596 "
    "(2012-11-17T21:40:18Z); "
    "memory-bank/source-audits/livid-farm-loop-2026-07-18.md"
)

LIVID_FARM_ENTRY_LEVELS: Final = {
    "magic": 70,
    "agility": 60,
    "crafting": 60,
    "farming": 60,
    "construction": 50,
}

LIVID_FARM_DUTIES: Final = (
    {
        "id": "cure_plant",
        "display_name": "Cure Plant",
        "count": 15,
        "magic_level": 66,
        "points_each": 20,
        "magic_xp_each": 60.0,
        "secondary_skill": "farming",
        "secondary_xp_each": 91.8,
        "rune_cost": {"Astral rune": 1, "Earth rune": 8},
    },
    {
        "id": "fertile_soil",
        "display_name": "Fertile Soil",
        "count": 15,
        "magic_level": 83,
        "points_each": 20,
        "magic_xp_each": 87.0,
        "secondary_skill": "farming",
        "secondary_xp_each": 91.8,
        "rune_cost": {
            "Astral rune": 3,
            "Nature rune": 2,
            "Earth rune": 15,
        },
    },
    {
        "id": "plank_make",
        "display_name": "Plank Make",
        "count": 10,
        "magic_level": 86,
        "points_each": 20,
        "magic_xp_each": 90.0,
        "secondary_skill": "construction",
        "secondary_xp_each": 54.6,
        "rune_cost": {
            "Astral rune": 2,
            "Nature rune": 1,
            "Earth rune": 15,
        },
    },
    {
        "id": "string_jewellery",
        "display_name": "String Jewellery",
        "count": 4,
        "magic_level": 80,
        "points_each": 120,
        "magic_xp_each": 83.0,
        "secondary_skill": "crafting",
        "secondary_xp_each": 270.0,
        "rune_cost": {
            "Astral rune": 2,
            "Earth rune": 10,
            "Water rune": 5,
        },
    },
    {
        "id": "energy_transfer",
        "display_name": "Energy Transfer",
        "count": 3,
        "magic_level": 91,
        "points_each": 100,
        "magic_xp_each": 100.0,
        "secondary_skill": "agility",
        "secondary_xp_each": 169.7,
        "rune_cost": {
            "Astral rune": 3,
            "Law rune": 2,
            "Nature rune": 1,
        },
    },
)

LIVID_FARM_DISTRACTIONS: Final = (
    {
        "id": "sick_ibis",
        "display_name": "Sick ibis",
        "magic_level": 66,
        "magic_xp": 61.0,
        "rune_cost": {
            "Astral rune": 1,
            "Cosmic rune": 1,
            "Mind rune": 1,
        },
        "rune_reward": {
            "Water rune": 10,
            "Astral rune": 1,
            "Earth rune": 16,
            "Cosmic rune": 1,
            "Mind rune": 1,
        },
    },
    {
        "id": "suqah_attack",
        "display_name": "Suqah attack",
        "magic_level": 91,
        "magic_xp": 100.0,
        "rune_cost": {
            "Astral rune": 3,
            "Law rune": 2,
            "Nature rune": 1,
        },
        "rune_reward": {
            "Water rune": 10,
            "Astral rune": 3,
            "Earth rune": 16,
            "Law rune": 2,
            "Nature rune": 1,
        },
    },
    {
        "id": "murky_pat",
        "display_name": "Murky Pat",
        "magic_level": 93,
        "magic_xp": 108.0,
        "rune_cost": {
            "Astral rune": 3,
            "Earth rune": 10,
            "Death rune": 2,
        },
        "rune_reward": {
            "Water rune": 15,
            "Astral rune": 3,
            "Earth rune": 20,
            "Death rune": 2,
        },
    },
)

# The first ten unlocks are cumulative and free. Borrowed Power is the source
# capstone transaction: crossing its threshold spends 850,000 Produce points.
LIVID_FARM_UNLOCKS: Final = (
    ("south_falador_teleport", "South Falador Teleport", 69_840),
    ("repair_rune_pouch", "Repair Rune Pouch", 139_760),
    ("north_ardougne_teleport", "North Ardougne Teleport", 227_120),
    ("remote_farm", "Remote Farm", 314_480),
    ("spiritualise_food", "Spiritualise Food", 401_840),
    ("make_leather", "Make Leather", 489_200),
    ("disruption_shield", "Disruption Shield", 576_560),
    ("vengeance_group", "Vengeance Group", 663_920),
    ("teleport_to_trollheim", "Teleport to Trollheim", 744_400),
    (
        "group_teleport_to_trollheim",
        "Group Teleport to Trollheim",
        806_400,
    ),
    ("borrowed_power", "Borrowed Power", 850_000),
)

LIVID_FARM_BORROWED_POWER_COST: Final = 850_000
LIVID_FARM_WALLET_CAP: Final = 850_000
LIVID_FARM_DISTRACTION_INTERVAL: Final = 12


def livid_farm_activity_as_dict(icon_path: str) -> dict[str, dict[str, object]]:
    return {
        LIVID_FARM_ACTIVITY_ID: {
            "display_name": "Livid Farm",
            "requirements": {},
            "batch_size": 1,
            "livid_farm_activity": True,
            "icon_path": icon_path,
            "group": "minigames",
            "source": LIVID_FARM_SOURCE,
        }
    }
