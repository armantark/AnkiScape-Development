"""Pure projection for the registry-backed Stats skill guide."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional


@dataclass(frozen=True)
class SkillGuideRow:
    row_id: str
    name: str
    level: int
    icon_key: Optional[str] = None


@dataclass(frozen=True)
class SkillGuideSection:
    section_id: str
    title: str
    rows: tuple[SkillGuideRow, ...]


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


def skill_guide_sections_pure(
    skill: str,
    target_table: object,
    equipment_data: Mapping[str, Mapping[str, object]],
) -> tuple[SkillGuideSection, ...]:
    """Project the two settled guide families without copying source metadata."""

    sections = []
    action_rows = _action_rows(target_table)
    if action_rows:
        sections.append(SkillGuideSection("actions", "Actions", action_rows))

    equipment_rows = _equipment_rows(_skill_id(skill), equipment_data)
    if equipment_rows:
        sections.append(
            SkillGuideSection("equipment", "Equipment", equipment_rows)
        )
    return tuple(sections)
