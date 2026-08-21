"""Surface stat and point-restoration potions.

Boost formulas (game-balance facts from the Apache-2.0 source, computed off the
BASE/max level, capped — potions cure a drained stat and boost to base+boost,
they do not stack past that ceiling):
  regular ("r"): floor(base / 10) + 3
  super   ("s"): floor(15 * base / 100) + 5

Herblore produces the potion families registered here. Drinking and Bob
Barter's dose-preserving decant service both consume this shared registry.
"""

from __future__ import annotations

from typing import Dict, Tuple

POTION_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/items/potion/PotionType.kt"
)
DARKAN_ITEM_CONFIG_SOURCE = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
    "data/items/config.json"
)
DARKAN_POTION_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
    "src/main/java/com/rs/game/content/Potions.kt"
)
OPENRS2_JUJU_HUNTER_POTION_DOSE_SOURCE = (
    "/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/"
    "727-2012-07-24/cache (archive sha256 "
    "ba79072542d1bda4d8140be38839b540133e79bc40c80665ef1772be178b29f8); "
    "741-2012-11-04/cache (archive sha256 "
    "61855e4c9f18e5ae25124277506c5b4d24317caf96f8e0a5cd1b06a037db7180); "
    "742-2012-11-07/cache (archive sha256 "
    "9f5fdba0d22cdc1b4ad86c984cc0ba4bcd4b3c22039f3290ba48f5083bc100b8)"
)
JUJU_HUNTER_POTION_DOSE_IDS: Dict[int, int] = {
    1: 20026,
    2: 20025,
    3: 20024,
    4: 20023,
}
JUJU_HUNTER_POTION_SOURCE = (
    f"{DARKAN_POTION_SOURCE_PATH}:522 JUJU_HUNTER_POTION refuses player drinking "
    "and handles only Habitat reagent use; "
    "https://runescape.wiki/w/Juju_hunter_potion?oldid=6258636: used on the "
    "Habitat flower patch rather than drunk; "
    f"{OPENRS2_JUJU_HUNTER_POTION_DOSE_SOURCE}: index 19, group 78, "
    "files 55-58 decode items 20023-20026 as doses 4-1"
)

VIAL_ITEM = ("Vial", 229)
# Potion flasks (1)-(6) are a documented post-baseline exception (released Feb
# 2012, ~4 months after the Oct-4-2011 rev-667 baseline — same category as the
# Money pouch). A flask holds up to six doses and, when drained, leaves an empty
# Potion flask (crafted from red sandstone). Flask item ids are the Darkan cache
# ids (`data/items/config.json`, uidName `<family>_flask_<dose>`); the (1)-(4)
# vial ids above come from the 2011 source `PotionType.kt`.
EMPTY_FLASK_ITEM = ("Potion flask", 23191)

# base display name -> item-state and supported-use metadata
POTION_FAMILIES: Dict[str, Dict[str, object]] = {
    "Juju hunter potion": {
        "role": "habitat_reagent",
        "drinkable": False,
        "doses": JUJU_HUNTER_POTION_DOSE_IDS,
        "source": JUJU_HUNTER_POTION_SOURCE,
    },
    "Attack potion": {"skills": ("attack",), "strategy": "r", "doses": {1: 125, 2: 123, 3: 121, 4: 2428},
                      "flask_doses": {1: 23205, 2: 23203, 3: 23201, 4: 23199, 5: 23197, 6: 23195}},
    "Strength potion": {"skills": ("strength",), "strategy": "r", "doses": {1: 119, 2: 117, 3: 115, 4: 113},
                        "flask_doses": {1: 23217, 2: 23215, 3: 23213, 4: 23211, 5: 23209, 6: 23207}},
    "Defence potion": {"skills": ("defense",), "strategy": "r", "doses": {1: 137, 2: 135, 3: 133, 4: 2432},
                       "flask_doses": {1: 23241, 2: 23239, 3: 23237, 4: 23235, 5: 23233, 6: 23231}},
    "Combat potion": {"skills": ("attack", "strength"), "strategy": "r", "doses": {1: 9745, 2: 9743, 3: 9741, 4: 9739},
                      "flask_doses": {1: 23457, 2: 23455, 3: 23453, 4: 23451, 5: 23449, 6: 23447}},
    "Super attack": {"skills": ("attack",), "strategy": "s", "doses": {1: 149, 2: 147, 3: 145, 4: 2436},
                     "flask_doses": {1: 23265, 2: 23263, 3: 23261, 4: 23259, 5: 23257, 6: 23255}},
    "Super strength": {"skills": ("strength",), "strategy": "s", "doses": {1: 161, 2: 159, 3: 157, 4: 2440},
                       "flask_doses": {1: 23289, 2: 23287, 3: 23285, 4: 23283, 5: 23281, 6: 23279}},
    "Super defence": {"skills": ("defense",), "strategy": "s", "doses": {1: 167, 2: 165, 3: 163, 4: 2442},
                      "flask_doses": {1: 23301, 2: 23299, 3: 23297, 4: 23295, 5: 23293, 6: 23291}},
    "Ranging potion": {"skills": ("ranged",), "strategy": "r", "doses": {1: 173, 2: 171, 3: 169, 4: 2444},
                       "flask_doses": {1: 23313, 2: 23311, 3: 23309, 4: 23307, 5: 23305, 6: 23303}},
    "Magic potion": {"skills": ("magic",), "strategy": "r", "doses": {1: 3046, 2: 3044, 3: 3042, 4: 3040},
                     "flask_doses": {1: 23433, 2: 23431, 3: 23429, 4: 23427, 5: 23425, 6: 23423}},
    # PotionType.kt: floor(base/4)+7 prayer points. Prayer flask ids are the
    # pre-EOC cache family used by the same six-dose flask convention above.
    "Prayer potion": {"skills": ("prayer",), "strategy": "prayer", "doses": {1: 143, 2: 141, 3: 139, 4: 2434},
                      "flask_doses": {1: 23253, 2: 23251, 3: 23249, 4: 23247, 5: 23245, 6: 23243}},
    # PotionType.kt: floor(base*0.35)+7 prayer points.
    "Super prayer": {"skills": ("prayer",), "strategy": "s_prayer", "doses": {1: 15331, 2: 15330, 3: 15329, 4: 15328},
                     "flask_doses": {1: 23530, 2: 23529, 3: 23528, 4: 23527, 5: 23526, 6: 23525}},
    # Darkan Potions.kt: adjustStat(7, 0.25, false, SUMMONING), capped at the
    # base Summoning level. Vial and flask ids are the pre-EOC cache family.
    "Summoning potion": {"skills": ("summoning",), "strategy": "summoning", "doses": {1: 12146, 2: 12144, 3: 12142, 4: 12140},
                         "flask_doses": {1: 23631, 2: 23629, 3: 23627, 4: 23625, 5: 23623, 6: 23621},
                         "special_points": 15},
    # PotionType.kt uses the exact ``r_skill`` strategy: +3 current levels.
    # Rev-742 supplies the live dose/flask identities and Drink option.
    "Crafting potion": {
        "skills": ("crafting",),
        "strategy": "flat_skill",
        "doses": {1: 14844, 2: 14842, 3: 14840, 4: 14838},
        "flask_doses": {1: 23469, 2: 23467, 3: 23465, 4: 23463, 5: 23461, 6: 23459},
    },
    "Fletching potion": {
        "skills": ("fletching",),
        "strategy": "flat_skill",
        "doses": {1: 14852, 2: 14850, 3: 14848, 4: 14846},
        "flask_doses": {1: 23481, 2: 23479, 3: 23477, 4: 23475, 5: 23473, 6: 23471},
    },
    # PotionType.kt and Darkan Potions.kt: floor(base/4)+8 restores drained
    # combat stats, Prayer, and Summoning to (but never above) their base pools.
    "Super restore": {
        "skills": ("attack", "strength", "defense", "ranged", "magic", "prayer", "summoning"),
        "strategy": "super_restore",
        "doses": {1: 3030, 2: 3028, 3: 3026, 4: 3024},
        "flask_doses": {1: 23409, 2: 23407, 3: 23405, 4: 23403, 5: 23401, 6: 23399},
    },
    # Darkan Potions.kt and Antifire oldid=6469134: every dose protects for
    # exactly six game-minutes (600 ticks). Regular antifire is one protection
    # layer; super antifire is complete protection by itself.
    "Antifire": {
        "skills": (),
        "strategy": "antifire",
        "duration_ticks": 600,
        "protection_level": 1,
        "source": DARKAN_POTION_SOURCE_PATH,
        "doses": {1: 2458, 2: 2456, 3: 2454, 4: 2452},
        "flask_doses": {1: 23373, 2: 23371, 3: 23369, 4: 23367, 5: 23365, 6: 23363},
    },
    "Super antifire": {
        "skills": (),
        "strategy": "super_antifire",
        "duration_ticks": 600,
        "protection_level": 2,
        "source": DARKAN_POTION_SOURCE_PATH,
        "doses": {1: 15307, 2: 15306, 3: 15305, 4: 15304},
        "flask_doses": {1: 23494, 2: 23493, 3: 23492, 4: 23491, 5: 23490, 6: 23489},
    },
}


def potion_dose_name(base: str, dose: int) -> str:
    return f"{base} ({dose})"


def potion_flask_name(base: str, dose: int) -> str:
    """Cache display name for a flask, e.g. 'Attack potion' -> 'Attack flask (6)',
    'Super strength' -> 'Super strength flask (6)' (the cache drops 'potion')."""
    return f"{base.replace(' potion', '')} flask ({dose})"


def potion_items_as_dict() -> Dict[str, Dict[str, object]]:
    """Every vial + flask dose variant plus the empty Vial and Potion flask, for
    item-registry registration."""
    rows: Dict[str, Dict[str, object]] = {
        VIAL_ITEM[0]: {
            "category": "material",
            "tradeable": True,
            "stackable": False,
            "item_id": VIAL_ITEM[1],
            "source": POTION_SOURCE_PATH,
        },
        EMPTY_FLASK_ITEM[0]: {
            "category": "material",
            "tradeable": True,
            "stackable": False,
            "item_id": EMPTY_FLASK_ITEM[1],
            "source": POTION_SOURCE_PATH,
        },
    }
    for base, spec in POTION_FAMILIES.items():
        source = str(spec.get("source", POTION_SOURCE_PATH))
        for dose, item_id in spec["doses"].items():  # type: ignore[union-attr]
            rows[potion_dose_name(base, dose)] = {
                "category": "material",
                "tradeable": True,
                "stackable": False,
                "item_id": item_id,
                "source": source,
            }
        for dose, item_id in spec.get("flask_doses", {}).items():  # type: ignore[union-attr]
            rows[potion_flask_name(base, dose)] = {
                "category": "material",
                "tradeable": True,
                "stackable": False,
                "item_id": item_id,
                "source": f"{source}; {DARKAN_ITEM_CONFIG_SOURCE}: {base} flask",
            }
    return rows


def potion_consumables_as_dict() -> Dict[str, Dict[str, object]]:
    """Drinkable vial and flask doses, excluding reagent-only families."""
    rows: Dict[str, Dict[str, object]] = {}
    for base, spec in POTION_FAMILIES.items():
        if not spec.get("drinkable", True):
            continue
        source = str(spec.get("source", POTION_SOURCE_PATH))
        for dose in spec["doses"]:  # type: ignore[union-attr]
            rows[potion_dose_name(base, dose)] = {
                "kind": "potion",
                "skills": tuple(spec["skills"]),  # type: ignore[arg-type]
                "strategy": spec["strategy"],
                "special_points": spec.get("special_points", 0),
                "duration_ticks": spec.get("duration_ticks", 0),
                "protection_level": spec.get("protection_level", 0),
                "leaves": potion_dose_name(base, dose - 1) if dose > 1 else VIAL_ITEM[0],
                "message": f"You drink some of your {base.lower()}.",
                "source": source,
            }
        for dose in spec.get("flask_doses", {}):  # type: ignore[union-attr]
            rows[potion_flask_name(base, dose)] = {
                "kind": "potion",
                "skills": tuple(spec["skills"]),  # type: ignore[arg-type]
                "strategy": spec["strategy"],
                "special_points": spec.get("special_points", 0),
                "duration_ticks": spec.get("duration_ticks", 0),
                "protection_level": spec.get("protection_level", 0),
                "leaves": potion_flask_name(base, dose - 1) if dose > 1 else EMPTY_FLASK_ITEM[0],
                "message": f"You drink some of your {base.lower()}.",
                "source": f"{source}; {DARKAN_ITEM_CONFIG_SOURCE}: {base} flask",
            }
    return rows


def potion_item_names() -> Tuple[str, ...]:
    return tuple(potion_items_as_dict().keys())


def skilling_potion_items_for_skill(skill_id: str) -> Tuple[str, ...]:
    """Matching dose containers, fullest first, for one noncombat skill."""
    rows = []
    for base, spec in POTION_FAMILIES.items():
        if (
            not spec.get("drinkable", True)
            or spec.get("strategy") != "flat_skill"
            or skill_id not in spec["skills"]
        ):
            continue
        rows.extend(
            (dose, 1, potion_flask_name(base, dose))
            for dose in spec.get("flask_doses", {})
        )
        rows.extend(
            (dose, 0, potion_dose_name(base, dose))
            for dose in spec.get("doses", {})
        )
    return tuple(name for _dose, _flask, name in sorted(rows, reverse=True))
