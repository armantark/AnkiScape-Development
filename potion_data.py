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

# base display name -> (affected skill ids, strategy, {dose: item_id})
POTION_FAMILIES: Dict[str, Dict[str, object]] = {
    "Attack potion": {"skills": ("attack",), "strategy": "r", "doses": {1: 125, 2: 123, 3: 121, 4: 2428}},
    "Strength potion": {"skills": ("strength",), "strategy": "r", "doses": {1: 119, 2: 117, 3: 115, 4: 113}},
    "Defence potion": {"skills": ("defense",), "strategy": "r", "doses": {1: 137, 2: 135, 3: 133, 4: 2432}},
    "Combat potion": {"skills": ("attack", "strength"), "strategy": "r", "doses": {1: 9745, 2: 9743, 3: 9741, 4: 9739}},
    "Super attack": {"skills": ("attack",), "strategy": "s", "doses": {1: 149, 2: 147, 3: 145, 4: 2436}},
    "Super strength": {"skills": ("strength",), "strategy": "s", "doses": {1: 161, 2: 159, 3: 157, 4: 2440}},
    "Super defence": {"skills": ("defense",), "strategy": "s", "doses": {1: 167, 2: 165, 3: 163, 4: 2442}},
    "Ranging potion": {"skills": ("ranged",), "strategy": "r", "doses": {1: 173, 2: 171, 3: 169, 4: 2444}},
    "Magic potion": {"skills": ("magic",), "strategy": "r", "doses": {1: 3046, 2: 3044, 3: 3042, 4: 3040}},
}


def potion_dose_name(base: str, dose: int) -> str:
    return f"{base} ({dose})"


def potion_items_as_dict() -> Dict[str, Dict[str, object]]:
    """Every dose variant + the empty Vial, for item-registry registration."""
    rows: Dict[str, Dict[str, object]] = {
        VIAL_ITEM[0]: {"category": "material", "tradeable": True, "item_id": VIAL_ITEM[1], "source": POTION_SOURCE_PATH},
    }
    for base, spec in POTION_FAMILIES.items():
        for dose, item_id in spec["doses"].items():  # type: ignore[union-attr]
            rows[potion_dose_name(base, dose)] = {
                "category": "material",
                "tradeable": True,
                "item_id": item_id,
                "source": POTION_SOURCE_PATH,
            }
    return rows


def potion_consumables_as_dict() -> Dict[str, Dict[str, object]]:
    """CONSUMABLE_DATA entries: each dose is drinkable, applies the boost, and
    leaves the next-lower dose (or an empty Vial at dose 1)."""
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
    return rows


def potion_item_names() -> Tuple[str, ...]:
    return tuple(potion_items_as_dict().keys())
