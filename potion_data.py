"""Standard combat stat potions (2011Scape `PotionType.kt`).

Boost formulas (game-balance facts from the Apache-2.0 source, computed off the
BASE/max level, capped — potions cure a drained stat and boost to base+boost,
they do not stack past that ceiling):
  regular ("r"): floor(base / 10) + 3
  super   ("s"): floor(15 * base / 100) + 5

Prayer / restore / super-restore potions are deferred (they need a Prayer skill
and the drain path respectively). Herblore mixing is a separate future skill;
until it (or shops) source these, the potions are live-but-inert like any other
material-gated content.
"""

from __future__ import annotations

from typing import Dict, Tuple

POTION_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/items/potion/PotionType.kt"
)

VIAL_ITEM = ("Vial", 229)
# Potion flasks (1)-(6) are a documented post-baseline exception (released Feb
# 2012, ~4 months after the Oct-4-2011 rev-667 baseline — same category as the
# Money pouch). A flask holds up to six doses and, when drained, leaves an empty
# Potion flask (crafted from red sandstone). Flask item ids are the Darkan cache
# ids (`data/items/config.json`, uidName `<family>_flask_<dose>`); the (1)-(4)
# vial ids above come from the 2011 source `PotionType.kt`.
EMPTY_FLASK_ITEM = ("Potion flask", 23191)

# base display name -> (affected skill ids, strategy, {dose: vial_id}, {dose: flask_id})
POTION_FAMILIES: Dict[str, Dict[str, object]] = {
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
        VIAL_ITEM[0]: {"category": "material", "tradeable": True, "item_id": VIAL_ITEM[1], "source": POTION_SOURCE_PATH},
        EMPTY_FLASK_ITEM[0]: {"category": "material", "tradeable": True, "item_id": EMPTY_FLASK_ITEM[1], "source": POTION_SOURCE_PATH},
    }
    for base, spec in POTION_FAMILIES.items():
        for dose, item_id in spec["doses"].items():  # type: ignore[union-attr]
            rows[potion_dose_name(base, dose)] = {
                "category": "material", "tradeable": True, "item_id": item_id, "source": POTION_SOURCE_PATH,
            }
        for dose, item_id in spec.get("flask_doses", {}).items():  # type: ignore[union-attr]
            rows[potion_flask_name(base, dose)] = {
                "category": "material", "tradeable": True, "item_id": item_id, "source": POTION_SOURCE_PATH,
            }
    return rows


def potion_consumables_as_dict() -> Dict[str, Dict[str, object]]:
    """CONSUMABLE_DATA entries: each vial and flask dose is drinkable, applies the
    boost, and leaves the next-lower dose (an empty Vial / Potion flask at dose 1)."""
    rows: Dict[str, Dict[str, object]] = {}
    for base, spec in POTION_FAMILIES.items():
        for dose in spec["doses"]:  # type: ignore[union-attr]
            rows[potion_dose_name(base, dose)] = {
                "kind": "potion",
                "skills": tuple(spec["skills"]),  # type: ignore[arg-type]
                "strategy": spec["strategy"],
                "leaves": potion_dose_name(base, dose - 1) if dose > 1 else VIAL_ITEM[0],
                "message": f"You drink some of your {base.lower()}.",
                "source": POTION_SOURCE_PATH,
            }
        for dose in spec.get("flask_doses", {}):  # type: ignore[union-attr]
            rows[potion_flask_name(base, dose)] = {
                "kind": "potion",
                "skills": tuple(spec["skills"]),  # type: ignore[arg-type]
                "strategy": spec["strategy"],
                "leaves": potion_flask_name(base, dose - 1) if dose > 1 else EMPTY_FLASK_ITEM[0],
                "message": f"You drink some of your {base.lower()}.",
                "source": POTION_SOURCE_PATH,
            }
    return rows


def potion_item_names() -> Tuple[str, ...]:
    return tuple(potion_items_as_dict().keys())
