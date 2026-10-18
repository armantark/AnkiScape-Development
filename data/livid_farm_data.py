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
LIVID_FARM_MORE_PLANKS_MINUTES: Final = 20
ARCANE_CAPACITOR_UNCHARGED: Final = "Arcane capacitor amulet (u)"
ARCANE_CAPACITOR_CHARGED: Final = "Arcane capacitor (c)"
ARCANE_CAPACITOR_MAX_CHARGES: Final = 1_000
ARCANE_CAPACITOR_SOURCE: Final = (
    "RuneScape Wiki Arcane capacitor amulet (u) oldid=6587262 "
    "(2012-11-19T08:44:38Z); cache rev 742 item ids 21513/21514"
)
BORROWED_POWER_SOURCE: Final = (
    "RuneScape Wiki Borrowed Power oldid=6587752 "
    "(2012-11-19T14:23:14Z)"
)
BORROWED_POWER_NONCOMBAT_SPELLS: Final = (
    "telegrab_wine_of_zamorak",
    "teleport_to_house",
    "high_alchemy",
    "bones_to_peaches",
)
BORROWED_POWER_COMBAT_SPELLS: Final = (
    "wind_wave",
    "water_wave",
    "earth_wave",
    "fire_wave",
    "magic_dart",
    "vulnerability",
    "enfeeble",
    "entangle",
)
BORROWED_POWER_SPELLS: Final = (
    BORROWED_POWER_COMBAT_SPELLS + BORROWED_POWER_NONCOMBAT_SPELLS
)

# Wishes are repeatable direct commands after Borrowed Power. Rows without a
# complete owning substrate stay visible and honest in the reward surface.
LIVID_FARM_WISHES: Final = (
    {
        "id": "vial_my_herbs",
        "display_name": "Vial My Herbs",
        "cost": 5_500,
        "status": "ready",
        "summary": "Vial up to 50 of every carried clean herb.",
    },
    {
        "id": "lunar_lumber",
        "display_name": "Turn Lunar Lumber Into Runes",
        "cost": 5_500,
        "status": "ready",
        "summary": "Convert all carried Lunar lumber with exact residuals.",
    },
    {
        "id": "arcane_capacitor",
        "display_name": "Give me an Arcane Capacitor",
        "cost": 18_000,
        "status": "ready",
        "summary": "Receive one uncharged capacitor if none is already owned.",
    },
    {
        "id": "new_patch",
        "display_name": "I'd Like a New Patch!",
        "cost": 18_000,
        "status": "ready",
        "summary": "Create a one-use allotment that disappears after clearing.",
    },
    {
        "id": "more_planks",
        "display_name": "More Planks Please",
        "cost": 18_000,
        "status": "ready",
        "summary": "Ten answered cards of a 1-in-10 extra Plank Make output.",
    },
    {
        "id": "gimme_herbs",
        "display_name": "Gimme Herbs",
        "cost": 18_000,
        "status": "ready",
        "summary": "Receive the exact sourced grimy-herb bundle.",
    },
    {
        "id": "rain_seeds",
        "display_name": "Let it rain seeds",
        "cost": 18_000,
        "status": "source_blocked",
        "summary": "Exact period seed amounts are not sourced.",
    },
    {
        "id": "reduce_fish_burn",
        "display_name": "Reduce The Fish I Burn",
        "cost": 18_000,
        "status": "source_blocked",
        "summary": "The period burn-rate change is not sourced.",
    },
    {
        "id": "protect_patch",
        "display_name": "Protect a Patch for me!",
        "cost": 37_000,
        "status": "ready",
        "summary": "Receive a scroll that protects ten selected trees.",
    },
    {
        "id": "awesome_seeds",
        "display_name": "Let it Rain Awesome Seeds",
        "cost": 55_000,
        "status": "ready",
        "summary": "Receive the exact sourced high-level seed bundle.",
    },
)


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
