#!/usr/bin/env python3
"""Generate source-backed AnkiScape equipment data from local 2011Scape files."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
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
            )
        )
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
        }}
        for item_name, item in EQUIPMENT_DATA.items()
    }}
'''


def generate(game_root: Path, output_path: Path) -> None:
    addon_root = output_path.resolve().parent
    if str(addon_root) not in sys.path:
        sys.path.insert(0, str(addon_root))
    items = _parse_items_yml(game_root / ITEMS_YML_RELATIVE)
    equipment_items = tuple(_smithing_equipment_items(items)) + tuple(_mining_bonus_equipment_items(items))
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
