"""Pure item manifest helpers for backend economy data."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Dict, Iterable, Literal, Mapping, Optional, Tuple, cast


ItemCategory = Literal["ore", "log", "fish", "gem", "bar", "crafted", "fletched", "material", "tool", "equipment", "smithed"]


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
    tradeable: bool = True
    equipment_slot: Optional[str] = None
    equipment_type: Optional[str] = None
    equipment_tier: int = 0


def slugify_item_id(category: ItemCategory, display_name: str) -> str:
    parts = re.findall(r"[a-z0-9]+", display_name.lower())
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


def _bool_value(spec: Mapping[str, object], key: str, default: bool) -> bool:
    value = spec.get(key, default)
    if isinstance(value, bool):
        return value
    return default


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
        tradeable=_bool_value(spec, "tradeable", True),
        equipment_slot=str(spec["equipment_slot"]) if isinstance(spec.get("equipment_slot"), str) else None,
        equipment_type=str(spec["equipment_type"]) if isinstance(spec.get("equipment_type"), str) else None,
        equipment_tier=_level_value({"level": spec.get("tier", 0)}),
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
    fletching_data: Optional[Mapping[str, Mapping[str, object]]] = None,
    fletched_item_images: Optional[Mapping[str, str]] = None,
    fishing_data: Optional[Mapping[str, Mapping[str, object]]] = None,
    fishing_item_images: Optional[Mapping[str, str]] = None,
    utility_activity_data: Optional[Mapping[str, Mapping[str, object]]] = None,
    utility_item_images: Optional[Mapping[str, str]] = None,
    extra_item_data: Optional[Mapping[str, Mapping[str, object]]] = None,
    extra_item_images: Optional[Mapping[str, str]] = None,
) -> Tuple[ItemDefinition, ...]:
    definitions = []
    seen_storage_keys = set()

    def add_definition(item: ItemDefinition) -> None:
        if item.storage_key in seen_storage_keys:
            return
        seen_storage_keys.add(item.storage_key)
        definitions.append(item)

    def add_material_definition(name: str, source: str, images: Mapping[str, str]) -> None:
        add_definition(
            ItemDefinition(
                id=slugify_item_id("material", name),
                display_name=name,
                storage_key=name,
                category="material",
                asset_path=images.get(name),
                source=source,
                license_note="private-fork asset; provenance not audited",
            )
        )

    def extra_item_category(spec: Mapping[str, object]) -> ItemCategory:
        category = spec.get("category", "material")
        if category in ("ore", "log", "fish", "gem", "bar", "crafted", "fletched", "material", "tool", "equipment", "smithed"):
            return cast(ItemCategory, category)
        return "material"

    crafting_material_images = dict(utility_item_images or {})
    crafting_material_images.update(crafted_item_images)

    for target_name, spec in ore_data.items():
        output_name = spec.get("output_item", target_name)
        if isinstance(output_name, str):
            output_spec = dict(spec)
            output_spec["tradeable"] = spec.get("output_tradeable", spec.get("tradeable", True))
            add_definition(_definition(output_name, "ore", "Mining", {output_name: output_spec}, ore_images))
        alternate_output = spec.get("alternate_output_item")
        if isinstance(alternate_output, str):
            alternate_spec = dict(spec)
            alternate_spec["level"] = spec.get("alternate_output_level", spec.get("level", 1))
            alternate_spec["tradeable"] = spec.get("alternate_output_tradeable", True)
            add_definition(_definition(alternate_output, "ore", "Mining", {alternate_output: alternate_spec}, ore_images))
        for weighted_output in spec.get("weighted_outputs", ()):
            if not isinstance(weighted_output, Mapping):
                continue
            weighted_name = weighted_output.get("item")
            if not isinstance(weighted_name, str):
                continue
            weighted_spec = dict(spec)
            weighted_spec["exp"] = weighted_output.get("exp", spec.get("exp", 0.0))
            weighted_spec["tradeable"] = weighted_output.get("tradeable", True)
            category = "gem" if weighted_name.startswith("Uncut ") else "ore"
            add_definition(_definition(weighted_name, cast(ItemCategory, category), "Mining", {weighted_name: weighted_spec}, ore_images))
    for target_name, spec in tree_data.items():
        output_name = spec.get("output_item", target_name)
        if isinstance(output_name, str):
            image_map = dict(tree_images)
            if target_name in tree_images and output_name not in image_map:
                image_map[output_name] = tree_images[target_name]
            add_definition(_definition(output_name, "log", "Woodcutting", {output_name: spec}, image_map))
    for name in gem_data:
        add_definition(_definition(name, "gem", "Mining gem drop", gem_data, gem_images))
    for name in bar_data:
        add_definition(_definition(name, "bar", "Smithing", bar_data, bar_images))
    for target_name, spec in crafting_data.items():
        output_name = spec.get("output_item", target_name)
        if isinstance(output_name, str):
            add_definition(_definition(output_name, "crafted", "Crafting", {output_name: spec}, crafted_item_images))
    for spec in crafting_data.values():
        for requirement_name in spec.get("requirements", {}):
            if requirement_name not in seen_storage_keys and (extra_item_data is None or requirement_name not in extra_item_data):
                add_material_definition(requirement_name, "Crafting material", crafting_material_images)
    if fletching_data is not None:
        image_map = fletched_item_images or {}
        for target_key, spec in fletching_data.items():
            output_name = spec.get("output_item", target_key)
            if isinstance(output_name, str):
                add_definition(_definition(output_name, "fletched", "Fletching", {output_name: spec}, image_map))
            for requirement_name in spec.get("requirements", {}):
                if requirement_name not in seen_storage_keys and (extra_item_data is None or requirement_name not in extra_item_data):
                    add_material_definition(requirement_name, "Fletching material", image_map)
    if fishing_data is not None:
        image_map = fishing_item_images or {}
        for target_key, spec in fishing_data.items():
            for fish in spec.get("fish", ()):
                if not isinstance(fish, Mapping):
                    continue
                output_name = fish.get("output_item")
                if not isinstance(output_name, str):
                    continue
                fish_spec = dict(fish)
                fish_spec.setdefault("level", fish.get("level", spec.get("level", 1)))
                fish_spec.setdefault("exp", fish.get("exp", 0.0))
                add_definition(_definition(output_name, "fish", "Fishing", {output_name: fish_spec}, image_map))
            for bait_name in spec.get("bait_options", ()):
                if isinstance(bait_name, str) and bait_name not in seen_storage_keys and (
                    extra_item_data is None or bait_name not in extra_item_data
                ):
                    add_material_definition(bait_name, "Fishing material", image_map)
    if utility_activity_data is not None:
        image_map = utility_item_images or {}
        for spec in utility_activity_data.values():
            output_name = spec.get("output_item")
            if isinstance(output_name, str):
                add_material_definition(output_name, "Utility / Activities", image_map)
            for requirement_name in spec.get("requirements", {}):
                if requirement_name not in seen_storage_keys and (extra_item_data is None or requirement_name not in extra_item_data):
                    add_material_definition(requirement_name, "Utility / Activities", image_map)
    if extra_item_data is not None:
        image_map = extra_item_images or {}
        for item_name, spec in extra_item_data.items():
            source = str(spec.get("source", "AnkiScape extra item"))
            add_definition(_definition(item_name, extra_item_category(spec), source, {item_name: spec}, image_map))
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
