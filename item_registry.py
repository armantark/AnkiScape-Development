"""Pure item manifest helpers for backend economy data."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, Iterable, Literal, Mapping, Optional, Tuple


ItemCategory = Literal["ore", "log", "gem", "bar", "crafted"]


@dataclass(frozen=True)
class ItemDefinition:
    id: str
    display_name: str
    storage_key: str
    category: ItemCategory
    asset_path: Optional[str]
    source: str
    license_note: str
    stackable: bool = True
    required_level: int = 1
    base_exp: float = 0.0


def slugify_item_id(category: ItemCategory, display_name: str) -> str:
    normalized = display_name.strip().lower().replace("/", " ")
    parts = [part for part in normalized.replace("-", " ").split() if part]
    return f"{category}_{'_'.join(parts)}"


def _number_value(spec: Mapping[str, object], key: str, default: float) -> float:
    value = spec.get(key, default)
    if isinstance(value, (int, float)):
        return float(value)
    return default


def _level_value(spec: Mapping[str, object]) -> int:
    value = spec.get("level", 1)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return 1


def _definition(
    name: str,
    category: ItemCategory,
    source: str,
    data: Mapping[str, Mapping[str, object]],
    images: Mapping[str, str],
) -> ItemDefinition:
    spec = data.get(name, {})
    return ItemDefinition(
        id=slugify_item_id(category, name),
        display_name=name,
        storage_key=name,
        category=category,
        asset_path=images.get(name),
        source=source,
        license_note="private-fork asset; provenance not audited",
        required_level=_level_value(spec),
        base_exp=_number_value(spec, "exp", 0.0),
    )


def build_item_definitions(
    ore_data: Mapping[str, Mapping[str, object]],
    ore_images: Mapping[str, str],
    tree_data: Mapping[str, Mapping[str, object]],
    tree_images: Mapping[str, str],
    gem_data: Mapping[str, Mapping[str, object]],
    gem_images: Mapping[str, str],
    bar_data: Mapping[str, Mapping[str, object]],
    bar_images: Mapping[str, str],
    crafting_data: Mapping[str, Mapping[str, object]],
    crafted_item_images: Mapping[str, str],
) -> Tuple[ItemDefinition, ...]:
    definitions = []
    for name in ore_data:
        definitions.append(_definition(name, "ore", "Mining", ore_data, ore_images))
    for name in tree_data:
        definitions.append(_definition(name, "log", "Woodcutting", tree_data, tree_images))
    for name in gem_data:
        definitions.append(_definition(name, "gem", "Mining gem drop", gem_data, gem_images))
    for name in bar_data:
        definitions.append(_definition(name, "bar", "Smithing", bar_data, bar_images))
    for name in crafting_data:
        definitions.append(_definition(name, "crafted", "Crafting", crafting_data, crafted_item_images))
    return tuple(definitions)


def item_definitions_by_storage_key(items: Iterable[ItemDefinition]) -> Dict[str, ItemDefinition]:
    return {item.storage_key: item for item in items}


def item_definitions_by_id(items: Iterable[ItemDefinition]) -> Dict[str, ItemDefinition]:
    return {item.id: item for item in items}


def item_storage_keys_by_category(items: Iterable[ItemDefinition], category: ItemCategory) -> Tuple[str, ...]:
    return tuple(item.storage_key for item in items if item.category == category)


def missing_required_asset_paths(items: Iterable[ItemDefinition]) -> Tuple[str, ...]:
    missing = []
    for item in items:
        if item.asset_path is not None and not os.path.exists(item.asset_path):
            missing.append(item.asset_path)
    return tuple(missing)
