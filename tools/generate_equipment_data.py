#!/usr/bin/env python3
"""Generate source-backed AnkiScape equipment data from local 2011Scape files."""

from __future__ import annotations

import argparse
import ast
import re
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Dict, Mapping, Optional, Sequence, Tuple


DEFAULT_GAME_ROOT = Path("/Users/ArmanTarkhanian1/Downloads/game-main")
ITEMS_YML_RELATIVE = Path("data/cfg/items.yml")

SlotId = str
BonusValue = int | float | bool | str
EquipmentBlock = Dict[str, BonusValue]


SOURCE_SLOT_IDS: Mapping[int, SlotId] = {
    0: "head",
    1: "cape",
    2: "neck",
    3: "weapon",
    4: "body",
    5: "shield",
    7: "legs",
    9: "hands",
    10: "feet",
    12: "ring",
    13: "ammunition",
}
SLOT_LABELS: Tuple[Tuple[SlotId, str], ...] = (
    ("head", "Head"),
    ("cape", "Cape"),
    ("neck", "Neck"),
    ("ammunition", "Ammunition"),
    ("weapon", "Weapon"),
    ("body", "Body"),
    ("shield", "Shield"),
    ("legs", "Legs"),
    ("hands", "Hands"),
    ("feet", "Feet"),
    ("ring", "Ring"),
)
BONUS_FIELDS: Tuple[str, ...] = (
    "attack_stab",
    "attack_slash",
    "attack_crush",
    "attack_magic",
    "attack_ranged",
    "defence_stab",
    "defence_slash",
    "defence_crush",
    "defence_magic",
    "defence_ranged",
    "melee_strength",
    "ranged_strength",
    "magic_damage",
    "prayer",
)
BAR_TIER_REQUIREMENTS: Mapping[str, int] = {
    "bronze": 1,
    "blurite": 1,
    "iron": 1,
    "steel": 5,
    "mithril": 20,
    "adamant": 30,
    "adamantite": 30,
    "rune": 40,
    "runite": 40,
}
DEFENCE_TYPES = {
    "TYPE_MEDIUM_HELM",
    "TYPE_FULL_HELM",
    "TYPE_CHAINBODY",
    "TYPE_PLATEBODY",
    "TYPE_PLATE_SKIRT",
    "TYPE_PLATELEGS",
    "TYPE_SQUARE_SHIELD",
    "TYPE_KITE_SHIELD",
}
ATTACK_TYPES = {
    "TYPE_DAGGER",
    "TYPE_SWORD",
    "TYPE_SCIMITAR",
    "TYPE_LONGSWORD",
    "TYPE_MACE",
    "TYPE_WARHAMMER",
    "TYPE_BATTLE_AXE",
    "TYPE_CLAWS",
    "TYPE_TWO_HAND_SWORD",
}
RANGED_TYPES = {"TYPE_THROWING_KNIFE"}
COMBAT_SKILL_IDS: Mapping[int, str] = {
    0: "attack",
    1: "defense",
    2: "strength",
    4: "ranged",
    6: "magic",
}
FALLBACK_SLOT_BY_SMITHING_TYPE: Mapping[str, SlotId] = {
    "TYPE_MEDIUM_HELM": "head",
    "TYPE_FULL_HELM": "head",
    "TYPE_CHAINBODY": "body",
    "TYPE_PLATEBODY": "body",
    "TYPE_PLATE_SKIRT": "legs",
    "TYPE_PLATELEGS": "legs",
    "TYPE_SQUARE_SHIELD": "shield",
    "TYPE_KITE_SHIELD": "shield",
    "TYPE_THROWING_KNIFE": "weapon",
    **{smithing_type: "weapon" for smithing_type in ATTACK_TYPES},
}
NORMALIZED_MINING_BONUS_SLOTS: Mapping[str, SlotId] = {
    "amulet": "neck",
    "chest": "body",
}
EQUIPMENT_ITEM_NAME_OVERRIDES: Mapping[int, str] = {
    4600: "Willow blackjack",
    5013: "Mining helmet (lit)",
    5014: "Mining helmet (unlit)",
}
MINING_BONUS_EQUIPMENT_FALLBACKS: Mapping[int, int] = {
    8283: 1704,
}
RANGED_BOW_EQUIPMENT: Mapping[str, Tuple[int, str]] = {
    "Shortbow": (1, "shortbow"),
    "Longbow": (1, "longbow"),
    "Oak shortbow": (5, "oak_shortbow"),
    "Oak longbow": (5, "oak_longbow"),
    "Willow shortbow": (20, "willow_shortbow"),
    "Willow longbow": (20, "willow_longbow"),
    "Maple shortbow": (30, "maple_shortbow"),
    "Maple longbow": (30, "maple_longbow"),
    "Yew shortbow": (40, "yew_shortbow"),
    "Yew longbow": (40, "yew_longbow"),
    "Magic shortbow": (50, "magic_shortbow"),
    "Magic longbow": (50, "magic_longbow"),
}
LEGACY_EQUIPMENT_ITEMS: Tuple[Tuple[str, int, Optional[str], int, bool, str, str], ...] = (
    ("Air tiara", 5527, None, 1, False, "runecrafting_access", "Altar.kt; AIR_TIARA"),
    ("Binding necklace", 5521, None, 1, False, "binding_necklace", "legacy equipment_data.py; BINDING_NECKLACE"),
    ("Blood tiara", 5549, None, 1, False, "runecrafting_access", "Altar.kt; BLOOD_TIARA"),
    ("Body tiara", 5533, None, 1, False, "runecrafting_access", "Altar.kt; BODY_TIARA"),
    ("Brass necklace", 1009, None, 1, False, "necklace", "BRASS_NECKLACE"),
    ("Bronze spear", 1237, "attack", 1, True, "spear", "BRONZE_SPEAR"),
    ("Cape", 1019, None, 1, False, "cape", "CAPE_1019"),
    ("Chaos tiara", 5543, None, 1, False, "runecrafting_access", "Altar.kt; CHAOS_TIARA"),
    ("Chef's hat", 1949, None, 1, False, "hat", "CHEFS_HAT"),
    ("Mining helmet (lit)", 5013, "defense", 1, False, "head", "LightSource.java; MINING_HELMET_LIT"),
    ("Cosmic tiara", 5539, None, 1, False, "runecrafting_access", "Altar.kt; COSMIC_TIARA"),
    ("Death tiara", 5547, None, 1, False, "runecrafting_access", "Altar.kt; DEATH_TIARA"),
    ("Earth tiara", 5535, None, 1, False, "runecrafting_access", "Altar.kt; EARTH_TIARA"),
    ("Fire battlestaff", 1393, "attack", 30, False, "battlestaff", "FIRE_BATTLESTAFF"),
    ("Fire tiara", 5537, None, 1, False, "runecrafting_access", "Altar.kt; FIRE_TIARA"),
    ("Iron spear", 1239, "attack", 1, True, "spear", "IRON_SPEAR"),
    ("Law tiara", 5545, None, 1, False, "runecrafting_access", "Altar.kt; LAW_TIARA"),
    ("Mind tiara", 5529, None, 1, False, "runecrafting_access", "Altar.kt; MIND_TIARA"),
    ("Nature tiara", 5541, None, 1, False, "runecrafting_access", "Altar.kt; NATURE_TIARA"),
    ("Obsidian cape", 6568, None, 1, False, "obsidian_cape", "OBSIDIAN_CAPE"),
    ("Staff", 1379, None, 1, False, "staff", "STAFF"),
    ("Staff of air", 1381, None, 1, False, "elemental_staff", "STAFF_OF_AIR"),
    ("Staff of earth", 1385, None, 1, False, "elemental_staff", "STAFF_OF_EARTH"),
    ("Staff of fire", 1387, None, 1, False, "elemental_staff", "STAFF_OF_FIRE"),
    ("Staff of water", 1383, None, 1, False, "elemental_staff", "STAFF_OF_WATER"),
    ("Steel spear", 1241, "attack", 5, True, "spear", "STEEL_SPEAR"),
    ("Toktz-ket-xil", 6524, "defense", 60, False, "obsidian_shield", "TOKTZKETXIL"),
    ("Tzhaar-ket-om", 6528, "strength", 60, True, "obsidian_maul", "TZHAARKETOM"),
    ("Water tiara", 5531, None, 1, False, "runecrafting_access", "Altar.kt; WATER_TIARA"),
    ("Wicked hood", 22332, None, 1, False, "wicked_hood", "legacy equipment_data.py; WICKED_HOOD"),
)
QUEST_EQUIPMENT_ITEMS: Tuple[Tuple[int, str], ...] = (
    (78, "Ice arrows"),
    (86, "Pendant of lucien"),
    (87, "Armadyl pendant"),
    (552, "Ghostspeak amulet"),
    (589, "Gnome amulet"),
    (4677, "Catspeak amulet"),
    (10282, "Yew comp bow"),
    (10284, "Magic comp bow"),
    (11235, "Dark bow"),
    (13277, "Masked earmuffs"),
)


@dataclass(frozen=True)
class SourceItem:
    item_id: int
    name: str
    tradeable: bool
    equipment: Optional[EquipmentBlock]


@dataclass(frozen=True)
class GeneratedEquipmentItem:
    item_name: str
    slot: SlotId
    combat_skill: Optional[str]
    required_level: int
    two_handed: bool
    equipment_type: str
    bonuses: Mapping[str, int]
    attack_speed: int
    source_item_id: int
    source: str
    source_status: str
    skill_requirements: Tuple[Tuple[str, int], ...] = ()
    weapon_type: int = -1


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _parse_scalar(raw_value: str) -> BonusValue:
    value = raw_value.strip().strip('"')
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def _parse_items_yml(path: Path) -> Dict[int, SourceItem]:
    items: Dict[int, SourceItem] = {}
    current_id: Optional[int] = None
    current_name: Optional[str] = None
    current_tradeable = True
    current_equipment: Optional[EquipmentBlock] = None
    in_equipment = False

    def flush() -> None:
        nonlocal current_id, current_name, current_tradeable, current_equipment
        if current_id is not None and current_name is not None:
            items[current_id] = SourceItem(
                current_id,
                current_name,
                current_tradeable,
                dict(current_equipment) if current_equipment is not None else None,
            )
        current_id = None
        current_name = None
        current_tradeable = True
        current_equipment = None

    for raw_line in _read(path).splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("- id:"):
            flush()
            current_id = int(stripped.split(":", 1)[1].strip())
            in_equipment = False
            continue
        if current_id is None:
            continue
        if in_equipment and raw_line.startswith("    ") and ":" in stripped:
            key, value = stripped.split(":", 1)
            if current_equipment is not None:
                current_equipment[key.strip()] = _parse_scalar(value)
            continue
        if stripped.startswith("name:"):
            current_name = str(_parse_scalar(stripped.split(":", 1)[1]))
            in_equipment = False
        elif stripped.startswith("tradeable:"):
            current_tradeable = bool(_parse_scalar(stripped.split(":", 1)[1]))
            in_equipment = False
        elif stripped.startswith("equipment:"):
            value = stripped.split(":", 1)[1].strip()
            if value == "null":
                current_equipment = None
                in_equipment = False
            else:
                current_equipment = {}
                in_equipment = True
        else:
            in_equipment = False
    flush()
    return items


def _int_from_block(block: Optional[Mapping[str, BonusValue]], key: str, default: int = 0) -> int:
    if block is None:
        return default
    value = block.get(key, default)
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return int(value)
    try:
        return int(str(value))
    except ValueError:
        return default


def _slot_from_source(block: Optional[Mapping[str, BonusValue]], fallback: SlotId) -> SlotId:
    source_slot = _int_from_block(block, "equip_slot", -1)
    return SOURCE_SLOT_IDS.get(source_slot, fallback)


def _combat_skill_for_type(smithing_type: str) -> Optional[str]:
    if smithing_type in DEFENCE_TYPES:
        return "defense"
    if smithing_type in ATTACK_TYPES:
        return "attack"
    if smithing_type in RANGED_TYPES:
        return "ranged"
    return None


def _equipment_type_for_smithing(smithing_type: str) -> str:
    return re.sub(r"^type_", "", smithing_type.lower())


def _bonuses_from_block(block: Optional[Mapping[str, BonusValue]]) -> Dict[str, int]:
    return {field: _int_from_block(block, field, 0) for field in BONUS_FIELDS}


def _mining_bonus_slot(raw_slot: object) -> SlotId:
    if isinstance(raw_slot, str):
        return NORMALIZED_MINING_BONUS_SLOTS.get(raw_slot, raw_slot)
    return "body"


def _has_mappable_equipment_slot(block: Optional[Mapping[str, BonusValue]]) -> bool:
    if block is None:
        return False
    return _int_from_block(block, "equip_slot", -1) in SOURCE_SLOT_IDS


def _combat_skill_for_recipe_equipment(slot: SlotId, bonuses: Mapping[str, int]) -> Optional[str]:
    if slot in {"head", "body", "shield", "legs", "hands", "feet"}:
        return "defense"
    if slot in {"ammunition", "weapon"} and (
        int(bonuses.get("attack_ranged", 0)) != 0 or int(bonuses.get("ranged_strength", 0)) != 0
    ):
        return "ranged"
    return None


def _combat_requirements(combat_skill: Optional[str], required_level: int) -> Tuple[Tuple[str, int], ...]:
    if combat_skill is None or required_level <= 1:
        return ()
    return ((combat_skill, required_level),)


def _source_skill_requirements(block: Optional[Mapping[str, BonusValue]]) -> Tuple[Tuple[str, int], ...]:
    raw_requirements = block.get("skill_reqs") if block is not None else None
    if not isinstance(raw_requirements, str):
        return ()
    try:
        parsed = ast.literal_eval(raw_requirements)
    except (SyntaxError, ValueError):
        return ()
    requirements = []
    if not isinstance(parsed, list):
        return ()
    for requirement in parsed:
        if not isinstance(requirement, dict):
            continue
        skill_id = requirement.get("skill")
        level = requirement.get("level")
        if not isinstance(skill_id, int) or not isinstance(level, int):
            continue
        skill = COMBAT_SKILL_IDS.get(skill_id)
        if skill is not None and level > 1:
            requirements.append((skill, level))
    return tuple(requirements)


def _source_required_level(
    combat_skill: Optional[str],
    skill_requirements: Tuple[Tuple[str, int], ...],
) -> int:
    if not skill_requirements:
        return 1
    if combat_skill is not None:
        for skill, level in skill_requirements:
            if skill == combat_skill:
                return level
    return max(level for _, level in skill_requirements)


def _equipment_type_for_recipe(item_name: str, slot: SlotId) -> str:
    if item_name in RANGED_BOW_EQUIPMENT:
        return RANGED_BOW_EQUIPMENT[item_name][1]
    return slot


def _required_level_for_recipe_equipment(item_name: str, combat_skill: Optional[str], recipe_level: object) -> int:
    if item_name in RANGED_BOW_EQUIPMENT:
        return RANGED_BOW_EQUIPMENT[item_name][0]
    if combat_skill is None:
        return 1
    return recipe_level if isinstance(recipe_level, int) else 1


def _canonical_equipment_item_name(source_item: SourceItem) -> str:
    override = EQUIPMENT_ITEM_NAME_OVERRIDES.get(source_item.item_id)
    if override:
        return override
    if _slot_from_source(source_item.equipment, "weapon") == "ammunition" and source_item.name.endswith(" arrow"):
        return f"{source_item.name}s"
    return source_item.name


def _equipment_item_from_source_item(source_item: SourceItem, source_note: str) -> Optional[GeneratedEquipmentItem]:
    block = source_item.equipment
    if not _has_mappable_equipment_slot(block):
        return None
    slot = _slot_from_source(block, "weapon")
    bonuses = _bonuses_from_block(block)
    combat_skill = _combat_skill_for_recipe_equipment(slot, bonuses)
    skill_requirements = _source_skill_requirements(block)
    required_level = _source_required_level(combat_skill, skill_requirements)
    return GeneratedEquipmentItem(
        item_name=_canonical_equipment_item_name(source_item),
        slot=slot,
        combat_skill=combat_skill,
        required_level=required_level,
        two_handed=_int_from_block(block, "equip_type", -1) == 5,
        equipment_type=_equipment_type_for_recipe(source_item.name, slot),
        bonuses=bonuses,
        attack_speed=_int_from_block(block, "attack_speed", 0),
        source_item_id=source_item.item_id,
        source=f"{ITEMS_YML_RELATIVE.as_posix()} item {source_item.item_id}; {source_note}",
        source_status="items.yml equipment block",
        skill_requirements=skill_requirements,
    )


def _recipe_equipment_item(
    recipe_key: str,
    recipe: Mapping[str, object],
    items: Mapping[int, SourceItem],
    items_by_name: Mapping[str, SourceItem],
) -> Optional[GeneratedEquipmentItem]:
    source_item_id = recipe.get("source_item_id")
    output_item = recipe.get("output_item")
    if not isinstance(output_item, str) or not output_item:
        return None
    source_item = items.get(source_item_id) if isinstance(source_item_id, int) and source_item_id > 0 else None
    if source_item is None:
        source_item = items_by_name.get(output_item)
    if source_item is None:
        return None
    block = source_item.equipment
    if not _has_mappable_equipment_slot(block):
        return None
    source_item_id = source_item.item_id
    slot = _slot_from_source(block, "weapon")
    bonuses = _bonuses_from_block(block)
    combat_skill = _combat_skill_for_recipe_equipment(slot, bonuses)
    required_level = _required_level_for_recipe_equipment(output_item, combat_skill, recipe.get("level", 1))
    source_enum = recipe.get("source_enum") or recipe_key
    return GeneratedEquipmentItem(
        item_name=output_item,
        slot=slot,
        combat_skill=combat_skill,
        required_level=required_level,
        two_handed=output_item in RANGED_BOW_EQUIPMENT,
        equipment_type=_equipment_type_for_recipe(output_item, slot),
        bonuses=bonuses,
        attack_speed=_int_from_block(block, "attack_speed", 0),
        source_item_id=source_item_id,
        source=f"{ITEMS_YML_RELATIVE.as_posix()} item {source_item_id}; {source_enum}",
        source_status="items.yml equipment block",
        skill_requirements=_combat_requirements(combat_skill, required_level),
    )


def _smithing_equipment_items(items: Mapping[int, SourceItem]) -> Tuple[GeneratedEquipmentItem, ...]:
    try:
        from smithing_data import SMITHING_RECIPES
    except ImportError as exc:
        raise RuntimeError("Run this script from the add-on root so smithing_data.py is importable.") from exc

    generated = []
    for recipe in SMITHING_RECIPES:
        if recipe.station != "anvil" or not isinstance(recipe.smithing_type, str):
            continue
        if recipe.smithing_type not in FALLBACK_SLOT_BY_SMITHING_TYPE:
            continue
        combat_skill = _combat_skill_for_type(recipe.smithing_type)
        if combat_skill is None:
            continue
        source_item = items.get(recipe.source_item_id)
        block = source_item.equipment if source_item is not None else None
        fallback_slot = FALLBACK_SLOT_BY_SMITHING_TYPE[recipe.smithing_type]
        required_level = BAR_TIER_REQUIREMENTS.get(str(recipe.bar_tier or ""), 1)
        source_status = "items.yml equipment block" if block is not None else "missing equipment block; bonuses zeroed"
        generated.append(
            GeneratedEquipmentItem(
                item_name=recipe.output_item,
                slot=_slot_from_source(block, fallback_slot),
                combat_skill=combat_skill,
                required_level=required_level,
                two_handed=recipe.smithing_type == "TYPE_TWO_HAND_SWORD",
                equipment_type=_equipment_type_for_smithing(recipe.smithing_type),
                bonuses=_bonuses_from_block(block),
                attack_speed=_int_from_block(block, "attack_speed", 0),
                source_item_id=recipe.source_item_id,
                source=f"{ITEMS_YML_RELATIVE.as_posix()} item {recipe.source_item_id}; {recipe.source_enum}",
                source_status=source_status,
                skill_requirements=_combat_requirements(combat_skill, required_level),
            )
        )
    return tuple(generated)


def _crafting_equipment_items(
    items: Mapping[int, SourceItem], items_by_name: Mapping[str, SourceItem]
) -> Tuple[GeneratedEquipmentItem, ...]:
    try:
        from constants import CRAFTING_DATA
    except ImportError as exc:
        raise RuntimeError("Run this script from the add-on root so constants.py is importable.") from exc

    generated = []
    for recipe_key, recipe in CRAFTING_DATA.items():
        equipment_item = _recipe_equipment_item(recipe_key, recipe, items, items_by_name)
        if equipment_item is not None:
            generated.append(equipment_item)
    return tuple(generated)


def _fletching_equipment_items(
    items: Mapping[int, SourceItem], items_by_name: Mapping[str, SourceItem]
) -> Tuple[GeneratedEquipmentItem, ...]:
    try:
        from constants import FLETCHING_DATA
    except ImportError as exc:
        raise RuntimeError("Run this script from the add-on root so constants.py is importable.") from exc

    generated = []
    for recipe_key, recipe in FLETCHING_DATA.items():
        equipment_item = _recipe_equipment_item(recipe_key, recipe, items, items_by_name)
        if equipment_item is not None:
            generated.append(equipment_item)
    return tuple(generated)


def _smithing_recipe_equipment_items(
    items: Mapping[int, SourceItem], items_by_name: Mapping[str, SourceItem]
) -> Tuple[GeneratedEquipmentItem, ...]:
    """Emit equipment for every smithable output with an equip block.

    The type-based ``_smithing_equipment_items`` selector maps armour and weapon
    families but skips smithable tools that are also wieldable (e.g. hatchets), so
    higher tiers that nothing drops fall through. Merged last, this only adds the
    net-new names that source-obtainable smithing recipes would otherwise miss.
    """
    try:
        from constants import SMITHING_DATA
    except ImportError as exc:
        raise RuntimeError("Run this script from the add-on root so constants.py is importable.") from exc

    generated = []
    for recipe_key, recipe in SMITHING_DATA.items():
        equipment_item = _recipe_equipment_item(recipe_key, recipe, items, items_by_name)
        if equipment_item is not None:
            generated.append(equipment_item)
    return tuple(generated)


def _resolve_source_item_by_name(
    item_name: object,
    items_by_name: Mapping[str, SourceItem],
) -> Optional[SourceItem]:
    if not isinstance(item_name, str) or not item_name:
        return None
    source_item = items_by_name.get(item_name)
    if source_item is not None:
        return source_item
    for candidate in (f"{item_name}s", f"{item_name}es"):
        source_item = items_by_name.get(candidate)
        if source_item is not None:
            return source_item
    if item_name.endswith(" arrows"):
        source_item = items_by_name.get(f"{item_name[:-7]} arrow")
        if source_item is not None:
            return source_item
    if item_name.endswith("y"):
        source_item = items_by_name.get(f"{item_name[:-1]}ies")
        if source_item is not None:
            return source_item
    return None


def _shop_equipment_items(
    items: Mapping[int, SourceItem], items_by_name: Mapping[str, SourceItem]
) -> Tuple[GeneratedEquipmentItem, ...]:
    try:
        from shop_data import SHOP_DATA
    except ImportError as exc:
        raise RuntimeError("Run this script from the add-on root so shop_data.py is importable.") from exc

    generated = []
    for shop in SHOP_DATA.values():
        shop_name = shop.get("display_name") or shop.get("source_name") or shop.get("id") or "shop stock"
        for stock_item in shop.get("stock", ()):
            if not isinstance(stock_item, Mapping):
                continue
            item_id = stock_item.get("item_id")
            source_item = items.get(item_id) if isinstance(item_id, int) else None
            if source_item is None:
                source_item = _resolve_source_item_by_name(stock_item.get("item_name"), items_by_name)
            if source_item is None:
                continue
            equipment_item = _equipment_item_from_source_item(source_item, f"SHOP_DATA stock; {shop_name}")
            if equipment_item is not None:
                generated.append(equipment_item)
    return tuple(generated)


def _drop_equipment_items(
    items: Mapping[int, SourceItem], items_by_name: Mapping[str, SourceItem]
) -> Tuple[GeneratedEquipmentItem, ...]:
    try:
        from combat_data import COMBAT_ENEMY_DATA
    except ImportError as exc:
        raise RuntimeError("Run this script from the add-on root so combat_data.py is importable.") from exc

    generated = []
    for enemy in COMBAT_ENEMY_DATA.values():
        enemy_name = enemy.get("display_name") or enemy.get("name") or enemy.get("id") or "combat drop"
        drops = enemy.get("drops") or {}
        if not isinstance(drops, Mapping):
            continue
        for guaranteed_drop in drops.get("guaranteed", ()):
            if not guaranteed_drop:
                continue
            source_item = _resolve_source_item_by_name(guaranteed_drop[0], items_by_name)
            if source_item is None:
                continue
            equipment_item = _equipment_item_from_source_item(source_item, f"COMBAT_ENEMY_DATA guaranteed drop; {enemy_name}")
            if equipment_item is not None:
                generated.append(equipment_item)
        for table in drops.get("tables", ()):
            if not isinstance(table, Mapping):
                continue
            table_name = table.get("name") or "drop table"
            for slot in table.get("slots", ()):
                if not isinstance(slot, Mapping):
                    continue
                source_item = _resolve_source_item_by_name(slot.get("item"), items_by_name)
                if source_item is None:
                    continue
                equipment_item = _equipment_item_from_source_item(
                    source_item,
                    f"COMBAT_ENEMY_DATA table drop; {enemy_name}; {table_name}",
                )
                if equipment_item is not None:
                    generated.append(equipment_item)
    return tuple(generated)


def _mining_bonus_equipment_items(items: Mapping[int, SourceItem]) -> Tuple[GeneratedEquipmentItem, ...]:
    try:
        from mining_data import MINING_BONUS_ITEMS
    except ImportError as exc:
        raise RuntimeError("Run this script from the add-on root so mining_data.py is importable.") from exc

    generated = []
    for bonus in MINING_BONUS_ITEMS:
        source_item = items.get(bonus.item_id)
        block = source_item.equipment if source_item is not None else None
        source_status = "items.yml equipment block" if block is not None else "missing equipment block; bonuses zeroed"
        fallback_item_id = MINING_BONUS_EQUIPMENT_FALLBACKS.get(bonus.item_id)
        if block is None and fallback_item_id is not None:
            fallback_item = items.get(fallback_item_id)
            if fallback_item is not None and fallback_item.equipment is not None:
                block = fallback_item.equipment
                source_status = f"items.yml item {fallback_item_id} equipment block; same-name cache alias for Mining.kt runtime binding {bonus.item_id}"
        generated.append(
            GeneratedEquipmentItem(
                item_name=bonus.display_name,
                slot=_mining_bonus_slot(bonus.slot),
                combat_skill=None,
                required_level=1,
                two_handed=False,
                equipment_type=bonus.bonus_type,
                bonuses=_bonuses_from_block(block),
                attack_speed=_int_from_block(block, "attack_speed", 0),
                source_item_id=bonus.item_id,
                source=f"{ITEMS_YML_RELATIVE.as_posix()} item {bonus.item_id}; {bonus.source}",
                source_status=source_status,
            )
        )
    return tuple(generated)


def _legacy_equipment_items(items: Mapping[int, SourceItem]) -> Tuple[GeneratedEquipmentItem, ...]:
    generated = []
    for item_name, item_id, combat_skill, required_level, two_handed, equipment_type, source_note in LEGACY_EQUIPMENT_ITEMS:
        source_item = items.get(item_id)
        block = source_item.equipment if source_item is not None else None
        if not _has_mappable_equipment_slot(block):
            continue
        generated.append(
            GeneratedEquipmentItem(
                item_name=item_name,
                slot=_slot_from_source(block, "weapon"),
                combat_skill=combat_skill,
                required_level=required_level,
                two_handed=two_handed,
                equipment_type=equipment_type,
                bonuses=_bonuses_from_block(block),
                attack_speed=_int_from_block(block, "attack_speed", 0),
                source_item_id=item_id,
                source=f"{ITEMS_YML_RELATIVE.as_posix()} item {item_id}; {source_note}",
                source_status="items.yml equipment block",
                skill_requirements=(
                    (("attack", 30), ("magic", 30))
                    if item_name == "Fire battlestaff"
                    else _combat_requirements(combat_skill, required_level)
                ),
            )
        )
    generated.append(
        GeneratedEquipmentItem(
            item_name="Wicked hood",
            slot="head",
            combat_skill=None,
            required_level=1,
            two_handed=False,
            equipment_type="wicked_hood",
            bonuses={field: 0 for field in BONUS_FIELDS},
            attack_speed=4,
            source_item_id=22332,
            source="external RuneScape wiki; not present in local 2011Scape rev-667 source",
            source_status="manual Runecrafting v1 equipment entry",
        )
    )
    generated.append(
        GeneratedEquipmentItem(
            item_name="Spiked gauntlets",
            slot="hands",
            combat_skill=None,
            required_level=1,
            two_handed=False,
            equipment_type="hands",
            bonuses={
                **{field: 0 for field in BONUS_FIELDS},
                "defence_slash": 1,
                "defence_crush": 2,
            },
            attack_speed=4,
            source_item_id=23035,
            source=(
                "RuneScape Wiki Spiked gauntlets oldid 5827717; "
                "Darkan item config 23035 and Slayer Equipment stock"
            ),
            source_status="period manual slot and bonuses",
        )
    )
    generated.extend(
        (
            GeneratedEquipmentItem(
                item_name="Coral bolts",
                slot="ammunition",
                combat_skill=None,
                required_level=1,
                two_handed=False,
                equipment_type="ammunition",
                bonuses={
                    **{field: 0 for field in BONUS_FIELDS},
                    "ranged_strength": 19,
                },
                attack_speed=4,
                source_item_id=24304,
                source=(
                    "RuneScape Wiki Coral bolts oldid 6146806; "
                    "Darkan item config 24304"
                ),
                source_status="period manual slot and ranged strength",
            ),
            GeneratedEquipmentItem(
                item_name="Royal cape",
                slot="cape",
                combat_skill=None,
                required_level=1,
                two_handed=False,
                equipment_type="cape",
                bonuses={field: 0 for field in BONUS_FIELDS},
                attack_speed=4,
                source_item_id=24315,
                source=(
                    "RuneScape Wiki Royal cape oldid 6308196; "
                    "Darkan item config 24315"
                ),
                source_status="period manual slot and zero bonuses",
            ),
        )
    )
    return tuple(generated)


def _quest_equipment_items(items: Mapping[int, SourceItem]) -> Tuple[GeneratedEquipmentItem, ...]:
    generated = []
    for item_id, item_name in QUEST_EQUIPMENT_ITEMS:
        source_item = items.get(item_id)
        if source_item is None:
            continue
        equipment_item = _equipment_item_from_source_item(source_item, "live quest item or reward")
        if equipment_item is not None:
            generated.append(replace(equipment_item, item_name=item_name))
    return tuple(generated)


def _agility_equipment_items(
    items: Mapping[int, SourceItem],
    items_by_name: Mapping[str, SourceItem],
) -> Tuple[GeneratedEquipmentItem, ...]:
    """Period Agility rewards and effect-bearing equipment.

    Agile uses the primary IDs explicitly because duplicate same-name config rows
    have the wrong weight sign. Weight itself remains in the Agility travel data;
    this generator owns equip slots, combat bonuses, and level gates only.
    """

    definitions = (
        ("Agile top", "body", 14936, (("defense", 35), ("constitution", 35))),
        ("Agile legs", "legs", 14938, (("defense", 35), ("constitution", 35))),
        ("Gorilla mask", "head", None, ()),
        ("Factory mask", "head", None, ()),
        ("Factory top", "body", None, ()),
        ("Factory trousers", "legs", None, ()),
        ("Factory gloves", "hands", None, ()),
        ("Factory boots", "feet", None, ()),
        ("Rogue mask", "head", None, ()),
        ("Rogue top", "body", None, ()),
        ("Rogue trousers", "legs", None, ()),
        ("Rogue gloves", "hands", None, ()),
        ("Rogue boots", "feet", None, ()),
        ("Pirate's hook", "hands", None, ()),
        ("Acrobat hood", "head", None, ()),
        ("Acrobat shirt", "body", None, ()),
        ("Acrobat pants", "legs", None, ()),
        ("Acrobat shoes", "feet", None, ()),
        ("Boots of lightness", "feet", None, ()),
        ("Spotted cape", "cape", None, ()),
        ("Spottier cape", "cape", None, ()),
        ("Karamja gloves 4", "hands", None, ()),
        ("Brawling gloves (Agility)", "hands", None, ()),
        ("Sköll boots", "feet", None, ()),
        ("Pendant of Agility", "neck", None, ()),
        ("Prized pendant of Agility", "neck", None, ()),
        ("Agility cape", "cape", None, (("agility", 99),)),
        ("Agility hood", "head", None, (("agility", 99),)),
    )
    generated = []
    for index, (name, fallback_slot, item_id, requirements) in enumerate(definitions):
        source_item = items.get(item_id) if item_id is not None else items_by_name.get(name)
        block = source_item.equipment if source_item is not None else None
        generated.append(GeneratedEquipmentItem(
            item_name=name,
            slot=_slot_from_source(block, fallback_slot),
            combat_skill=None,
            required_level=1,
            two_handed=False,
            equipment_type="agility_reward",
            bonuses=_bonuses_from_block(block),
            attack_speed=_int_from_block(block, "attack_speed", 4),
            source_item_id=source_item.item_id if source_item is not None else -1000 - index,
            source=(
                f"{ITEMS_YML_RELATIVE.as_posix()} item {source_item.item_id}; Agility reward/effect"
                if source_item is not None
                else "period RuneScape Wiki Agility reward; equipment block unavailable in rev-667 config"
            ),
            source_status="items.yml equipment block" if block is not None else "period manual slot; bonuses zeroed",
            skill_requirements=requirements,
        ))
    return tuple(generated)


def _stronghold_equipment_items(items: Mapping[int, SourceItem]) -> Tuple[GeneratedEquipmentItem, ...]:
    """Fancy boots (9005) and Fighting boots (9006), the Stronghold of Security
    completion reward. The player picks one; both are stat-identical, so the
    choice is purely cosmetic. Bonuses come straight from their items.yml blocks."""
    generated = []
    for item_id, item_name in ((9005, "Fancy boots"), (9006, "Fighting boots")):
        source_item = items.get(item_id)
        block = source_item.equipment if source_item is not None else None
        generated.append(
            GeneratedEquipmentItem(
                item_name=item_name,
                slot="feet",
                combat_skill="defense",
                required_level=1,
                two_handed=False,
                equipment_type="feet",
                bonuses=_bonuses_from_block(block),
                attack_speed=_int_from_block(block, "attack_speed", 4),
                source_item_id=item_id,
                source=f"{ITEMS_YML_RELATIVE.as_posix()} item {item_id}; Stronghold of Security reward",
                source_status="items.yml equipment block",
            )
        )
    return tuple(generated)


def _mage_arena_equipment_items(
    items: Mapping[int, SourceItem],
) -> Tuple[GeneratedEquipmentItem, ...]:
    generated = []
    for item_id in (2412, 2413, 2414):
        source_item = items.get(item_id)
        if source_item is None:
            continue
        equipment_item = _equipment_item_from_source_item(
            source_item,
            "Mage Arena reward; RuneScape Wiki oldid=6512911",
        )
        if equipment_item is not None:
            generated.append(
                replace(equipment_item, equipment_type="god_cape")
            )
    return tuple(generated)


def _dedupe_equipment_items(items: Sequence[GeneratedEquipmentItem]) -> Tuple[GeneratedEquipmentItem, ...]:
    by_name: Dict[str, GeneratedEquipmentItem] = {}
    for item in items:
        by_name.setdefault(item.item_name, item)
    return tuple(by_name.values())


def _source_items_by_name(items: Mapping[int, SourceItem]) -> Dict[str, SourceItem]:
    by_name: Dict[str, SourceItem] = {}
    for item in items.values():
        if _has_mappable_equipment_slot(item.equipment):
            by_name.setdefault(item.name, item)
    return by_name


def _bonus_repr(bonuses: Mapping[str, int]) -> str:
    args = ", ".join(f"{field}={int(bonuses.get(field, 0))}" for field in BONUS_FIELDS)
    return f"EquipmentBonuses({args})"


def _item_repr(item: GeneratedEquipmentItem) -> str:
    combat_skill = item.combat_skill if item.combat_skill is not None else None
    return (
        "EquipmentItem(\n"
        f"        item_name={item.item_name!r},\n"
        f"        slot={item.slot!r},\n"
        f"        combat_skill={combat_skill!r},\n"
        f"        required_level={item.required_level},\n"
        f"        two_handed={item.two_handed!r},\n"
        f"        equipment_type={item.equipment_type!r},\n"
        f"        bonuses={_bonus_repr(item.bonuses)},\n"
        f"        attack_speed={item.attack_speed},\n"
        f"        source_item_id={item.source_item_id},\n"
        f"        source={item.source!r},\n"
        f"        source_status={item.source_status!r},\n"
        f"        skill_requirements={item.skill_requirements!r},\n"
        f"        weapon_type={item.weapon_type},\n"
        "    )"
    )


def _render_module(items: Sequence[GeneratedEquipmentItem]) -> str:
    item_rows = ",\n".join(f"    {item.item_name!r}: {_item_repr(item)}" for item in items)
    slot_rows = ",\n".join(f"    EquipmentSlot({slot_id!r}, {label!r})" for slot_id, label in SLOT_LABELS)
    return f'''"""2011Scape-sourced equipment data for AnkiScape.

This module is generated by ``tools/generate_equipment_data.py``. Runtime imports
only this checked-in Python data; the emulator checkout is a development-time
source audit input.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Optional, Tuple


ITEMS_SOURCE_PATH = "/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml"
EQUIPMENT_BONUS_FIELDS: Tuple[str, ...] = {BONUS_FIELDS!r}


@dataclass(frozen=True)
class EquipmentSlot:
    id: str
    label: str


@dataclass(frozen=True)
class EquipmentBonuses:
    attack_stab: int = 0
    attack_slash: int = 0
    attack_crush: int = 0
    attack_magic: int = 0
    attack_ranged: int = 0
    defence_stab: int = 0
    defence_slash: int = 0
    defence_crush: int = 0
    defence_magic: int = 0
    defence_ranged: int = 0
    melee_strength: int = 0
    ranged_strength: int = 0
    magic_damage: int = 0
    prayer: int = 0


@dataclass(frozen=True)
class EquipmentItem:
    item_name: str
    slot: str
    combat_skill: Optional[str]
    required_level: int
    two_handed: bool
    equipment_type: str
    bonuses: EquipmentBonuses
    attack_speed: int
    source_item_id: int
    source: str
    source_status: str
    skill_requirements: Tuple[Tuple[str, int], ...] = ()
    weapon_type: int = -1


EQUIPMENT_SLOTS: Tuple[EquipmentSlot, ...] = (
{slot_rows}
)

EQUIPMENT_DATA: Dict[str, EquipmentItem] = {{
{item_rows}
}}


def equipment_items_as_dict() -> Dict[str, Dict[str, object]]:
    return {{
        item_name: {{
            "item_name": item.item_name,
            "slot": item.slot,
            "combat_skill": item.combat_skill,
            "required_level": item.required_level,
            "two_handed": item.two_handed,
            "equipment_type": item.equipment_type,
            "bonuses": asdict(item.bonuses),
            "attack_speed": item.attack_speed,
            "source_item_id": item.source_item_id,
            "source": item.source,
            "source_status": item.source_status,
            "skill_requirements": item.skill_requirements,
            "weapon_type": item.weapon_type,
        }}
        for item_name, item in EQUIPMENT_DATA.items()
    }}
'''


def _with_weapon_type(
    item: GeneratedEquipmentItem, items: Mapping[int, SourceItem]
) -> GeneratedEquipmentItem:
    """Attach the items.yml ``weapon_type`` id so combat can pick the right
    attack style (stab/slash/crush) per weapon. Only weapon-slot items carry a
    meaningful type; everything else keeps the -1 (unarmed/typeless) default."""
    if item.slot != "weapon":
        return item
    source = items.get(item.source_item_id)
    weapon_type = _int_from_block(source.equipment, "weapon_type", -1) if source else -1
    if weapon_type == item.weapon_type:
        return item
    return replace(item, weapon_type=weapon_type)


def generate(game_root: Path, output_path: Path) -> None:
    addon_root = output_path.resolve().parent
    if str(addon_root) not in sys.path:
        sys.path.insert(0, str(addon_root))
    items = _parse_items_yml(game_root / ITEMS_YML_RELATIVE)
    items_by_name = _source_items_by_name(items)
    equipment_items = _dedupe_equipment_items(
        tuple(_agility_equipment_items(items, items_by_name))
        + tuple(_smithing_equipment_items(items))
        + tuple(_mining_bonus_equipment_items(items))
        + tuple(_legacy_equipment_items(items))
        + tuple(_quest_equipment_items(items))
        + tuple(_stronghold_equipment_items(items))
        + tuple(_mage_arena_equipment_items(items))
        + tuple(_crafting_equipment_items(items, items_by_name))
        + tuple(_fletching_equipment_items(items, items_by_name))
        + tuple(_shop_equipment_items(items, items_by_name))
        + tuple(_drop_equipment_items(items, items_by_name))
        + tuple(_smithing_recipe_equipment_items(items, items_by_name))
    )
    equipment_items = tuple(_with_weapon_type(item, items) for item in equipment_items)
    output_path.write_text(_render_module(equipment_items), encoding="utf-8")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=DEFAULT_GAME_ROOT)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "equipment_data.py")
    args = parser.parse_args(argv)
    generate(args.game_root, args.output)
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
