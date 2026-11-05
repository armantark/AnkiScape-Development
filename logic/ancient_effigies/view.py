"""Read-only projection of Ancient Effigies ownership for the window.

Rows and details come from the current records only. Projecting never
allocates an ID, a seed or a pair, and never exposes a seed.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ...data.ancient_effigies.catalog import (
    DRAGONKIN_LAMP_ID,
    DRAGONKIN_LAMP_NAME,
    EFFIGY_ASSET_PATH,
    LAMP_ASSET_PATH,
    LAMP_DESTROY_WARNING,
    LAMP_SKILL_IDS,
    SKILL_PAIRS,
    STAGES_BY_ITEM_ID,
)
from ..skilling_boost_logic import skilling_effective_level_pure
from .actions import (
    lamp_preview_pure,
    lamp_token_pure,
    skill_name,
    stage_token_pure,
)
from .custody import bank_units_pure, custody_records_pure, instance_number


EMPTY_TEXT = "You do not own an Ancient Effigy or Dragonkin lamp."
UNREVEALED_TEXT = "Inspect to reveal skills"
LOCATION_LABELS = {
    "bank": "In your bank",
    "held": "Carried",
    "grave": "At your gravestone",
    "death_office": "In Death's Office",
}
RECOVERY_TEXT = {
    "grave": "This item is at your gravestone. Walk back and reclaim it before using it.",
    "death_office": "This item is in Death's Office. Reclaim it there before using it.",
}


def _usable(player_data: Mapping[str, Any], record: Mapping[str, Any]) -> bool:
    if record["item_id"] == DRAGONKIN_LAMP_ID:
        return record["location"] == "held"
    return record["location"] == "bank" and bank_units_pure(player_data, record["item_id"]) > 0


def _item_name(record: Mapping[str, Any]) -> str:
    stage = STAGES_BY_ITEM_ID.get(record["item_id"])
    return stage.name if stage is not None else DRAGONKIN_LAMP_NAME


def _pair_text(record: Mapping[str, Any]) -> str:
    if record["item_id"] == DRAGONKIN_LAMP_ID:
        return "Any skill"
    if record["pair_index"] is None:
        return UNREVEALED_TEXT
    first, second = SKILL_PAIRS[record["pair_index"]]
    return f"{skill_name(first)} or {skill_name(second)}"


def effigy_rows_pure(player_data: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    """One row per owned copy, in numeric copy order."""
    rows = []
    for instance_id, record in custody_records_pure(player_data).items():
        is_lamp = record["item_id"] == DRAGONKIN_LAMP_ID
        rows.append(
            {
                "instance_id": instance_id,
                "copy_number": instance_number(instance_id),
                "kind": "lamp" if is_lamp else "stage",
                "name": _item_name(record),
                "icon": LAMP_ASSET_PATH if is_lamp else EFFIGY_ASSET_PATH,
                "location": record["location"],
                "location_label": LOCATION_LABELS[record["location"]],
                "pair_text": _pair_text(record),
                "usable": _usable(player_data, record),
            }
        )
    return tuple(rows)


def _skill_choice(player_data: Mapping[str, Any], skill_id: str, required_level: int, usable: bool) -> dict[str, Any]:
    level = skilling_effective_level_pure(player_data, skill_id)
    try:
        base_level = max(1, int(player_data.get(f"{skill_id}_level", 1) or 1))
    except (TypeError, ValueError):
        base_level = 1
    eligible = usable and level >= required_level
    shown = f"{level} (boosted from {base_level})" if level != base_level else str(level)
    if eligible:
        reason = f"Your {skill_name(skill_id)} level is {shown}."
    else:
        reason = f"Needs level {required_level} {skill_name(skill_id)}; yours is {shown}."
    return {
        "skill_id": skill_id,
        "skill_name": skill_name(skill_id),
        "level": level,
        "base_level": base_level,
        "boosted": level != base_level,
        "eligible": eligible,
        "reason": reason,
    }


def _stage_detail(player_data: Mapping[str, Any], instance_id: str, record: Mapping[str, Any], detail: dict[str, Any]):
    stage = STAGES_BY_ITEM_ID[record["item_id"]]
    detail.update(
        required_level=stage.required_level,
        reward_xp=stage.reward_xp,
        output_name=stage.output_name,
        revealed=record["pair_index"] is not None,
        token=stage_token_pure(instance_id, record),
        choices=(),
    )
    if detail["revealed"]:
        detail["choices"] = tuple(
            _skill_choice(player_data, skill_id, stage.required_level, detail["usable"])
            for skill_id in SKILL_PAIRS[record["pair_index"]]
        )
    return detail


def effigy_detail_pure(player_data: Mapping[str, Any], instance_id: str) -> dict[str, Any] | None:
    """Everything the detail area shows for one copy, or None if it is gone."""
    record = custody_records_pure(player_data).get(instance_id)
    if record is None:
        return None
    row = next(row for row in effigy_rows_pure(player_data) if row["instance_id"] == instance_id)
    detail = dict(row, recovery_text=RECOVERY_TEXT.get(record["location"], ""))
    if record["item_id"] != DRAGONKIN_LAMP_ID:
        return _stage_detail(player_data, instance_id, record, detail)
    detail.update(
        token=lamp_token_pure(instance_id),
        skill_ids=LAMP_SKILL_IDS,
        destroy_warning=LAMP_DESTROY_WARNING,
    )
    return detail


def lamp_confirmation_pure(player_data: Mapping[str, Any], skill_id: str) -> dict[str, Any]:
    level, xp = lamp_preview_pure(player_data, skill_id)
    return {"skill_id": skill_id, "skill_name": skill_name(skill_id), "level": level, "xp": xp}
