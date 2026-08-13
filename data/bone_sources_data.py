"""Shared pre-EOC acquisition data for the remaining Prayer bones."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


DARKAN_REV = "a2568b880390ef697b1b17e825fdef7868bed67f"
DARKAN_ROOT = "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server"
DARKAN_ITEM_SOURCE = f"{DARKAN_ROOT}/data/items/config.json @ {DARKAN_REV}"
DARKAN_LEVEL_SOURCE = (
    f"{DARKAN_ROOT}/src/main/java/com/rs/game/model/entity/npc/combat/"
    f"NPCCombatDefinitions.java:138-150,289-306 @ {DARKAN_REV}"
)
DARKAN_SPEAR_SOURCE = (
    f"{DARKAN_ROOT}/src/main/java/com/rs/game/content/skills/herblore/"
    f"WeaponPoison.java:64-72,156-192 @ {DARKAN_REV}"
)

BURNT_BONES_SOURCE = "https://runescape.wiki/w/Burnt_bones?oldid=6351913"
ZOGRE_SOURCE = (
    f"{DARKAN_ROOT}/data/npcs/combatdefs/uncategorized/zogre/"
    f"zogre_(44) .json; {DARKAN_ROOT}/data/npcs/drops/zogre.json @ {DARKAN_REV}; "
    "https://runescape.wiki/w/Zogre?oldid=6547569"
)
JOGRE_SOURCE = (
    f"{DARKAN_ROOT}/data/npcs/combatdefs/uncategorized/jogre/"
    f"jogre_(53).json; {DARKAN_ROOT}/data/npcs/drops/jogre.json @ {DARKAN_REV}; "
    "https://runescape.wiki/w/Jogre?oldid=6240856"
)
SHAIKAHAN_SOURCE = (
    f"{DARKAN_ROOT}/data/npcs/combatdefs/uncategorized/"
    f"the_shaikahan (noanims).json @ {DARKAN_REV}; "
    "https://runescape.wiki/w/The_Shaikahan?oldid=6552714"
)
FROST_DRAGON_SOURCE = (
    f"{DARKAN_ROOT}/data/npcs/combatdefs/uncategorized/frost_dragon/"
    f"frost_dragon_(166) (nostats).json; "
    f"{DARKAN_ROOT}/src/main/java/com/rs/game/content/world/npcs/"
    f"FrostDragonCombat.java; {DARKAN_ROOT}/data/npcs/drops/frost_dragon.json "
    f"@ {DARKAN_REV}; {DARKAN_LEVEL_SOURCE}; "
    "https://runescape.wiki/w/Frost_dragon?oldid=6565911"
)
COFFIN_SOURCE = "https://runescape.wiki/w/Ogre_coffin_key?oldid=6381645"
FAYRG_SOURCE = "https://runescape.wiki/w/Fayrg_bones?oldid=6105617"
RAURG_SOURCE = "https://runescape.wiki/w/Raurg_bones?oldid=6541406"
OURG_SOURCE = "https://runescape.wiki/w/Ourg_bones?oldid=6356815"
SHAIKAHAN_BONES_SOURCE = "https://runescape.wiki/w/Shaikahan_bones?oldid=6132621"


@dataclass(frozen=True)
class CombatBoneSource:
    id: str
    display_name: str
    level: int
    hitpoints: int
    attack: int
    strength: int
    defence: int
    magic: int
    ranged: int
    attack_style: str
    max_hit: int
    respawn_delay: int
    guaranteed_drops: tuple[tuple[str, int], ...]
    source: str
    source_status: str = "pinned/Darkan+period-wiki"


COMBAT_BONE_SOURCES = (
    CombatBoneSource(
        "zogre", "Zogre", 44, 710, 20, 36, 35, 1, 1, "melee", 50, 59,
        (("Zogre bones", 1), ("Ogre coffin key", 1)), ZOGRE_SOURCE,
    ),
    CombatBoneSource(
        "jogre", "Jogre", 53, 600, 43, 43, 43, 1, 1, "melee", 73, 59,
        (("Jogre bones", 1),), JOGRE_SOURCE,
    ),
    CombatBoneSource(
        "shaikahan", "The Shaikahan", 83, 1000, 80, 80, 25, 1, 1,
        "melee", 94, 59, (("Shaikahan bones", 1),), SHAIKAHAN_SOURCE,
    ),
    # PLACEHOLDER(bone_sources.frost_dragon_generated_levels): authentic Frost dragon Attack, Strength, Defence, Magic, and Ranged levels
    # Darkan marks the level-166 definition "nostats" and reconstructs every
    # offensive/defensive level as 213 with its checked-in generateLevels formula.
    CombatBoneSource(
        "frost_dragon", "Frost dragon", 166, 1600, 213, 213, 213, 213, 213,
        "ranged", 250, 59, (("Frost dragon bones", 1),), FROST_DRAGON_SOURCE,
        "emulator_reconstruction/Darkan generated levels; period-wiki drop",
    ),
)


# PLACEHOLDER(bone_sources.ogre_coffin_selector_weights): exact hidden coffin bone/non-bone selector weights
COFFIN_OUTPUT_WEIGHTS: tuple[tuple[str | None, int], ...] = (
    ("Zogre bones", 63),
    ("Fayrg bones", 14),
    ("Raurg bones", 6),
    ("Ourg bones", 3),
    (None, 39),
)


SHAIKAHAN_SPEARS: tuple[tuple[str, int], ...] = (("Steel", 3172),)


_BONE_ITEMS: tuple[tuple[str, int, float, str], ...] = (
    ("Burnt bones", 528, 4.5, BURNT_BONES_SOURCE),
    ("Zogre bones", 4812, 22.5, ZOGRE_SOURCE),
    ("Jogre bones", 3125, 15.0, JOGRE_SOURCE),
    ("Shaikahan bones", 3123, 25.0, SHAIKAHAN_BONES_SOURCE),
    ("Fayrg bones", 4830, 84.0, FAYRG_SOURCE),
    ("Raurg bones", 4832, 96.0, RAURG_SOURCE),
    ("Ourg bones", 4834, 140.0, OURG_SOURCE),
    ("Frost dragon bones", 18832, 180.0, FROST_DRAGON_SOURCE),
)


def bone_source_enemies_as_dict() -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for source in COMBAT_BONE_SOURCES:
        row: dict[str, Any] = {
            "display_name": source.display_name,
            "level": source.level,
            "group": "Bone sources",
            "stats": {
                "hitpoints": source.hitpoints,
                "attack": source.attack,
                "strength": source.strength,
                "defence": source.defence,
                "magic": source.magic,
                "ranged": source.ranged,
            },
            "bonuses": {},
            "attack_style": source.attack_style,
            "max_hit": source.max_hit,
            "respawn_delay": source.respawn_delay,
            "drops": {"guaranteed": source.guaranteed_drops, "tables": ()},
            "source": source.source,
            "source_status": source.source_status,
        }
        if source.id == "zogre":
            row["quest_gate"] = "zogre_flesh_eaters"
            row["quest_gate_state"] = "started"
            row["quest_gate_label"] = "Open Jiggig during Zogre Flesh Eaters"
            row["location_context"] = "Jiggig zogre area after the guard opens the barricade"
        elif source.id == "jogre":
            row["location_context"] = "Karamja jungle and Pothole Dungeon"
            row["access_status"] = "ordinary Karamja access; no quest gate"
        elif source.id == "shaikahan":
            row["quest_gate"] = "tai_bwo_wannai_trio"
            row["quest_gate_label"] = "Complete Tai Bwo Wannai Trio"
            row["location_context"] = "Eastern Karamja jungle"
            row["start_equipment"] = {
                "slot": "weapon",
                "items": tuple(
                    f"{metal} spear (kp)" for metal, _item_id in SHAIKAHAN_SPEARS
                ),
                "persistent": True,
                "warning": (
                    "Equip a karambwan-poisoned spear to damage The Shaikahan"
                ),
                "source_status": (
                    "period-authentic continuous weapon gate; the live prerequisite "
                    "route uses cache-decoded Steel spear (kp)"
                ),
            }
        elif source.id == "frost_dragon":
            row["skill_requirements"] = {"dungeoneering": 85}
            row["attack_styles"] = ("melee", "magic", "ranged", "dragonfire")
            row["special_max_hits"] = {
                "melee": 213,
                "magic": 250,
                "ranged": 250,
                "dragonfire": 500,
            }
        rows[source.id] = row
    return rows


def bone_source_utility_activities_as_dict() -> dict[str, dict[str, Any]]:
    activities: dict[str, dict[str, Any]] = {
        "gather_burnt_bones": {
            "display_name": "Collect burnt bones",
            "requirements": {},
            "output_item": "Burnt bones",
            "output_qty": 1,
            "batch_size": 1,
            "group": "gathering",
            "source": BURNT_BONES_SOURCE,
        },
        "loot_ogre_coffin": {
            "display_name": "Loot an Ogre coffin",
            "requirements": {"Ogre coffin key": 1},
            "batch_size": 1,
            "group": "containers_opening",
            "weighted_outputs": tuple(
                {"item": item_name, "weight": weight}
                for item_name, weight in COFFIN_OUTPUT_WEIGHTS
                if item_name is not None
            ),
            "non_bone_output_weight": dict(COFFIN_OUTPUT_WEIGHTS)[None],
            "source": COFFIN_SOURCE,
        },
    }
    for metal, _item_id in SHAIKAHAN_SPEARS:
        base_name = f"{metal} spear"
        output_name = f"{base_name} (kp)"
        activities[f"poison_{metal.lower()}_spear_with_karambwan"] = {
            "display_name": f"Poison {base_name.lower()} with karambwan paste",
            "requirements": {base_name: 1, "Karambwan paste": 1},
            "output_item": output_name,
            "output_qty": 1,
            "batch_size": 1,
            "group": "weapon_preparation",
            "source": f"{DARKAN_SPEAR_SOURCE}; {SHAIKAHAN_SOURCE}",
        }
    return activities


def bone_source_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    items = {
        item_name: {
            "category": "material",
            "source_item_id": item_id,
            "stackable": False,
            "tradeable": True,
            "exp": xp,
            "source": f"{DARKAN_ITEM_SOURCE}; {source}",
        }
        for item_name, item_id, xp, source in _BONE_ITEMS
    }
    items["Ogre coffin key"] = {
        "category": "material",
        "source_item_id": 4850,
        "stackable": False,
        "tradeable": True,
        "source": f"{DARKAN_ITEM_SOURCE}; {COFFIN_SOURCE}",
    }
    for metal, item_id in SHAIKAHAN_SPEARS:
        items[f"{metal} spear (kp)"] = {
            "category": "equipment",
            "source_item_id": item_id,
            "stackable": False,
            "tradeable": False,
            "source": (
                f"OpenRS2 cache rev 727 item {item_id}; "
                f"{DARKAN_ITEM_SOURCE}; {DARKAN_SPEAR_SOURCE}"
            ),
        }
    return items
