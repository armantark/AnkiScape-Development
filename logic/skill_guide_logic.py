"""Pure projection for the registry-backed Stats skill guide."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional, Sequence

from ..logic_pure.logic_pure_state import quest_completed_pure


_FARMING_CROP_ALIASES = {
    3473: "scarecrow",
    3504: "redblossom",
}
_EVIL_TREE_TIER_IDS = ("oak", "willow", "maple", "yew", "magic", "elder")


@dataclass(frozen=True)
class SkillGuideRow:
    row_id: str
    name: str
    level: int
    icon_key: Optional[str] = None
    icon_item_id: Optional[int] = None
    lock_reasons: tuple[str, ...] = ()
    guide_struct_id: Optional[int] = None
    resolution_status: str = "resolved"


@dataclass(frozen=True)
class SkillGuideSection:
    section_id: str
    title: str
    rows: tuple[SkillGuideRow, ...]


@dataclass(frozen=True)
class _FarmingResolution:
    status: str
    target: object = None


def _skill_id(value: object) -> str:
    skill_id = str(value or "").strip().lower()
    return "defense" if skill_id == "defence" else skill_id


def _field(spec: object, name: str, default: object = None) -> object:
    if isinstance(spec, Mapping):
        return spec.get(name, default)
    return getattr(spec, name, default)


def _positive_level(value: object) -> Optional[int]:
    if isinstance(value, bool):
        return None
    try:
        level = int(value)
    except (TypeError, ValueError):
        return None
    return max(1, level)


def _target_icon_key(spec: object, name: str) -> str:
    for key in ("output_item", "primary_output", "input_item", "asset_name"):
        value = _field(spec, key)
        if isinstance(value, str) and value.strip():
            return value

    outputs = _field(spec, "outputs", {})
    if isinstance(outputs, Mapping):
        first = next((key for key in outputs if isinstance(key, str)), None)
        if first:
            return first

    fish = _field(spec, "fish", ())
    if isinstance(fish, (tuple, list)):
        for fish_row in fish:
            output = _field(fish_row, "output_item")
            if isinstance(output, str) and output.strip():
                return output
    return name


def _action_rows(target_table: object) -> tuple[SkillGuideRow, ...]:
    if not isinstance(target_table, Mapping):
        return ()

    rows = []
    for target_key, spec in target_table.items():
        if _field(spec, "source_enum") == "MILESTONE_CAPES":
            continue
        level = _positive_level(_field(spec, "level"))
        if level is None:
            continue
        target_id = str(_field(spec, "id", target_key) or target_key)
        name = str(
            _field(
                spec,
                "display_name",
                _field(spec, "name", target_id),
            )
            or target_id
        )
        rows.append(
            SkillGuideRow(
                row_id=f"action:{target_id}",
                name=name,
                level=level,
                icon_key=_target_icon_key(spec, name),
            )
        )
    return tuple(sorted(rows, key=lambda row: (row.level, row.name.casefold(), row.row_id)))


def _requirement_levels(spec: Mapping[str, object], skill_id: str) -> tuple[int, ...]:
    levels = []
    if _skill_id(spec.get("combat_skill")) == skill_id:
        level = _positive_level(spec.get("required_level", 1))
        if level is not None:
            levels.append(level)

    requirements = spec.get("skill_requirements", ()) or ()
    pairs = requirements.items() if isinstance(requirements, Mapping) else requirements
    for requirement in pairs:
        if not isinstance(requirement, (tuple, list)) or len(requirement) < 2:
            continue
        if _skill_id(requirement[0]) != skill_id:
            continue
        level = _positive_level(requirement[1])
        if level is not None:
            levels.append(level)
    return tuple(levels)


def _equipment_rows(
    skill_id: str,
    equipment_data: Mapping[str, Mapping[str, object]],
) -> tuple[SkillGuideRow, ...]:
    rows = []
    for item_name, spec in equipment_data.items():
        if spec.get("equipment_type") == "milestone_cape":
            continue
        levels = _requirement_levels(spec, skill_id)
        if not levels:
            continue
        name = str(spec.get("item_name", item_name) or item_name)
        rows.append(
            SkillGuideRow(
                row_id=f"equipment:{item_name}",
                name=name,
                level=max(levels),
                icon_key=name,
            )
        )
    return tuple(sorted(rows, key=lambda row: (row.level, row.name.casefold(), row.row_id)))


def _slayer_monster_rows(slayer_families: object) -> tuple[SkillGuideRow, ...]:
    if not isinstance(slayer_families, Mapping):
        return ()

    rows = []
    for family_key, family in slayer_families.items():
        family_id = str(_field(family, "id", family_key) or family_key)
        name = str(_field(family, "display_name", family_id) or family_id)
        level = _positive_level(_field(family, "required_slayer_level", 1))
        target_ids = _field(family, "target_ids", ())
        icon_key = None
        if isinstance(target_ids, (tuple, list)) and target_ids:
            icon_key = str(target_ids[0])
        rows.append(
            SkillGuideRow(
                row_id=f"monster:{family_id}",
                name=name,
                level=level or 1,
                icon_key=icon_key,
            )
        )
    return tuple(sorted(rows, key=lambda row: (row.level, row.name.casefold(), row.row_id)))


def _normalized_name(value: object) -> str:
    text = str(value or "").casefold()
    for suffix in (" tree", " plant", " bush", " hops", " hop"):
        if text.endswith(suffix):
            text = text[: -len(suffix)]
    return "".join(character for character in text if character.isalnum())


def _player_level(player_data: Mapping[str, object], skill_id: str) -> int:
    return _positive_level(player_data.get(f"{skill_id}_level", 1)) or 1


def _farming_crop_lookup(farming_crops: object) -> dict[str, object]:
    lookup: dict[str, object] = {}
    if not isinstance(farming_crops, Sequence):
        return lookup
    for crop in farming_crops:
        for value in (_field(crop, "id"), _field(crop, "display_name")):
            key = _normalized_name(value)
            if key:
                lookup[key] = crop
    return lookup


def _farming_resolution(
    source_row: object,
    *,
    crop_lookup: Mapping[str, object],
    evil_tree_tiers: object,
    farming_patches_by_id: object,
    livid_farm_entry_levels: object,
    dungeoneering_rewards: object,
    bork_effigy_item: object,
    skillcapes: object,
) -> _FarmingResolution:
    struct_id = _positive_level(_field(source_row, "struct_id")) or 0
    name = str(_field(source_row, "name", ""))
    crop = crop_lookup.get(_FARMING_CROP_ALIASES.get(struct_id, _normalized_name(name)))
    if crop is not None:
        return _FarmingResolution("crop", crop)

    if struct_id == 3512 and isinstance(farming_patches_by_id, Mapping):
        patch = farming_patches_by_id.get("spirit_tree_secondary")
        if patch is not None:
            return _FarmingResolution("patch_unlock", patch)

    if struct_id == 3514 and isinstance(livid_farm_entry_levels, Mapping):
        return _FarmingResolution("livid_farm", livid_farm_entry_levels)

    if 3520 <= struct_id <= 3525 and isinstance(evil_tree_tiers, Sequence):
        tier_id = _EVIL_TREE_TIER_IDS[struct_id - 3520]
        tier = next(
            (tier for tier in evil_tree_tiers if str(_field(tier, "id", "")) == tier_id),
            None,
        )
        if tier is not None:
            return _FarmingResolution("evil_tree", tier)

    if struct_id == 3513 and isinstance(dungeoneering_rewards, Sequence):
        reward = next(
            (
                reward
                for reward in dungeoneering_rewards
                if str(_field(reward, "id", "")) == "scroll_of_life"
            ),
            None,
        )
        if reward is not None:
            return _FarmingResolution("dungeoneering_reward", reward)

    if struct_id == 3516 and str(bork_effigy_item or "") == name:
        return _FarmingResolution("bork_reward", bork_effigy_item)

    if struct_id == 3548 and isinstance(skillcapes, Sequence):
        cape = next(
            (
                cape
                for cape in skillcapes
                if str(_field(cape, "skill_id", "")) == "farming"
            ),
            None,
        )
        if cape is not None:
            return _FarmingResolution("skillcape", cape)

    return _FarmingResolution("unresolved")


def _farming_target_available(resolution: _FarmingResolution) -> bool:
    if resolution.status == "unresolved":
        return False
    if resolution.status == "crop":
        return bool(_field(resolution.target, "runnable", False))
    if resolution.status == "dungeoneering_reward":
        return bool(_field(resolution.target, "fully_functional", False))
    return resolution.target is not None


def _farming_gate_reasons(
    source_row: object,
    player_data: Mapping[str, object],
    resolution: _FarmingResolution,
) -> tuple[str, ...]:
    reasons: list[str] = []
    requirements = _field(source_row, "requirements", ()) or ()
    if isinstance(requirements, Sequence):
        for requirement in requirements:
            kind = str(_field(requirement, "kind", ""))
            key = str(_field(requirement, "key", ""))
            minimum = int(_field(requirement, "minimum", 0) or 0)
            if kind == "quest" and not quest_completed_pure(player_data, key):
                reasons.append(str(_field(requirement, "label", key) or key))
            elif kind == "skill" and _player_level(player_data, key) < minimum:
                reasons.append(f"{key.title()} {minimum}")

    if not _farming_target_available(resolution):
        reasons.append("Not implemented in AnkiScape")
    return tuple(dict.fromkeys(reasons))


def farming_skill_guide_sections_pure(
    player_data: Mapping[str, object],
    source_rows: object,
    source_sections: object,
    *,
    guide_key: int = 21,
    icon_storage_keys: object = None,
    item_definitions: object = (),
    farming_crops: object = (),
    farming_patches_by_id: object = None,
    evil_tree_tiers: object = (),
    livid_farm_entry_levels: object = None,
    dungeoneering_rewards: object = (),
    bork_effigy_item: object = None,
    skillcapes: object = (),
) -> tuple[SkillGuideSection, ...]:
    """Project the source-enumerated Farming guide without trusting crop shape."""

    if not isinstance(source_sections, Sequence):
        return ()
    section_category_ids = {
        int(section[2])
        for section in source_sections
        if isinstance(section, (tuple, list)) and len(section) >= 3
    }
    crop_lookup = _farming_crop_lookup(farming_crops)
    rows_by_category: dict[int, list[SkillGuideRow]] = {}
    definitions_by_key: dict[str, object] = {}
    if isinstance(item_definitions, Sequence):
        for definition in item_definitions:
            asset_path = _field(definition, "asset_path")
            storage_key = _field(definition, "storage_key")
            if asset_path and storage_key:
                definitions_by_key[str(storage_key)] = definition
    guide_icon_keys = icon_storage_keys if isinstance(icon_storage_keys, Mapping) else {}

    if isinstance(source_rows, Sequence):
        for source_row in source_rows:
            try:
                struct_id = int(_field(source_row, "struct_id"))
                category_id = int(_field(source_row, "category_id"))
                row_guide_key = int(_field(source_row, "guide_key"))
            except (TypeError, ValueError, AttributeError):
                continue
            if row_guide_key != guide_key or category_id not in section_category_ids:
                continue

            try:
                name = str(_field(source_row, "name"))
                level = int(_field(source_row, "level"))
                icon_item_id = int(_field(source_row, "icon_item_id"))
                requirements = _field(source_row, "requirements", ()) or ()
                if not isinstance(requirements, Sequence):
                    raise TypeError("requirements must be a sequence")
                for requirement in requirements:
                    kind = str(_field(requirement, "kind", ""))
                    key = str(_field(requirement, "key", ""))
                    minimum = int(_field(requirement, "minimum", 0) or 0)
                    if kind not in {"quest", "skill"} or not key:
                        raise ValueError("invalid requirement")
                    if kind == "skill" and minimum < 1:
                        raise ValueError("invalid skill minimum")
            except (TypeError, ValueError, AttributeError):
                row = SkillGuideRow(
                    row_id=f"farming-struct:{struct_id}",
                    name=str(_field(source_row, "name", f"Struct {struct_id}") or f"Struct {struct_id}"),
                    level=_positive_level(_field(source_row, "level")) or 1,
                    lock_reasons=("Guide metadata unavailable",),
                    guide_struct_id=struct_id,
                    resolution_status="malformed",
                )
                rows_by_category.setdefault(category_id, []).append(row)
                continue
            resolution = _farming_resolution(
                source_row,
                crop_lookup=crop_lookup,
                evil_tree_tiers=evil_tree_tiers,
                farming_patches_by_id=farming_patches_by_id,
                livid_farm_entry_levels=livid_farm_entry_levels,
                dungeoneering_rewards=dungeoneering_rewards,
                bork_effigy_item=bork_effigy_item,
                skillcapes=skillcapes,
            )
            lock_reasons = _farming_gate_reasons(
                source_row,
                player_data,
                resolution,
            )
            icon_key = guide_icon_keys.get(icon_item_id)
            if icon_key not in definitions_by_key:
                icon_key = None
            rows_by_category.setdefault(category_id, []).append(
                SkillGuideRow(
                    row_id=f"farming-struct:{struct_id}",
                    name=name,
                    level=max(1, level),
                    icon_key=icon_key,
                    icon_item_id=icon_item_id,
                    lock_reasons=lock_reasons,
                    guide_struct_id=struct_id,
                    resolution_status=resolution.status,
                )
            )

    sections = []
    for section in source_sections:
        try:
            section_id, title, category_id = section
            rows = tuple(
                sorted(
                    rows_by_category.get(int(category_id), ()),
                    key=lambda row: (row.level, row.guide_struct_id or 0),
                )
            )
        except (TypeError, ValueError):
            continue
        if rows:
            sections.append(SkillGuideSection(str(section_id), str(title), rows))
    return tuple(sections)


def skill_guide_sections_pure(
    skill: str,
    target_table: object,
    equipment_data: Mapping[str, Mapping[str, object]],
    *,
    slayer_families: object = None,
) -> tuple[SkillGuideSection, ...]:
    """Project settled guide families without copying source metadata."""

    sections = []
    action_rows = _action_rows(target_table)
    if action_rows:
        sections.append(SkillGuideSection("actions", "Actions", action_rows))

    if _skill_id(skill) == "slayer":
        monster_rows = _slayer_monster_rows(slayer_families)
        if monster_rows:
            sections.append(
                SkillGuideSection("monsters", "Monsters", monster_rows)
            )

    equipment_rows = _equipment_rows(_skill_id(skill), equipment_data)
    if equipment_rows:
        sections.append(
            SkillGuideSection("equipment", "Equipment", equipment_rows)
        )
    return tuple(sections)
