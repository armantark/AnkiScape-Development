"""Ancient Effigies reducers: inspect, investigate, rub and destroy.

Each returns ``(updated, ok, info)``. A refusal returns the caller's own input
object unchanged and draws nothing from the shared random module. Actions are
bound to a token describing the copy as it was shown, so a stale window or a
repeated click cannot act on a copy that has since changed.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ...core.constants import exp_table_for_skill
from ...core.skill_registry import get_skill
from ...data.ancient_effigies.catalog import (
    DRAGONKIN_LAMP_ID,
    ITEM_NAMES_BY_ID,
    LAMP_SKILL_IDS,
    SKILL_PAIRS,
    STAGES_BY_ITEM_ID,
    dragonkin_lamp_xp,
    lamp_level_cap,
)
from ...logic_pure.logic_pure_progression import calculate_new_level
from ...logic_pure.logic_pure_quest import _apply_skill_xp_reward
from ..skilling_boost_logic import skilling_effective_level_pure
from .custody import INSTANCES_KEY, bank_units_pure, custody_records_pure
from .requests import initial_pair_index_pure, next_pair_index_pure


STALE_MESSAGE = "This item changed since it was shown. Inspect it again before using it."
MISSING_MESSAGE = "You no longer have that item."


def _refuse(player_data: Mapping[str, Any], message: str, **extra: Any):
    return player_data, False, {"message": message, **extra}


def skill_name(skill_id: str) -> str:
    skill = get_skill(skill_id)
    return skill.display_name if skill is not None else skill_id.replace("_", " ").title()


def stage_token_pure(instance_id: str, record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "instance_id": instance_id,
        "item_id": record["item_id"],
        "request_step": record["request_step"],
        "pair_index": record["pair_index"],
    }


def lamp_token_pure(instance_id: str) -> dict[str, Any]:
    return {"instance_id": instance_id, "item_id": DRAGONKIN_LAMP_ID}


def _live_record(player_data: Mapping[str, Any], instance_id: Any) -> dict[str, Any] | None:
    return custody_records_pure(player_data).get(instance_id) if isinstance(instance_id, str) else None


def _bank_stage_record(player_data: Mapping[str, Any], instance_id: Any) -> tuple[dict[str, Any] | None, str]:
    """The live record of a Bank-owned stage copy, or the refusal message."""
    record = _live_record(player_data, instance_id)
    if record is None or record["item_id"] not in STAGES_BY_ITEM_ID:
        return None, MISSING_MESSAGE
    if record["location"] != "bank":
        return None, "Reclaim this effigy before using it."
    if bank_units_pure(player_data, record["item_id"]) < 1:
        return None, MISSING_MESSAGE
    return record, ""


def _with_record(player_data: Mapping[str, Any], instance_id: str, record: Mapping[str, Any] | None) -> dict[str, Any]:
    """A shallow save copy whose instance mapping is rebuilt with one change."""
    data = dict(player_data)
    instances = {key: dict(value) for key, value in dict(player_data.get(INSTANCES_KEY) or {}).items()}
    if record is None:
        instances.pop(instance_id, None)
    else:
        instances[instance_id] = dict(record)
    data[INSTANCES_KEY] = instances
    return data


def _award(data: dict[str, Any], skill_id: str, amount: int) -> None:
    """Pay one reward through the quest/claim XP path, never training bonuses."""
    pending = data.get("pending_skill_exp_rewards")
    if isinstance(pending, Mapping):
        data["pending_skill_exp_rewards"] = dict(pending)
    _apply_skill_xp_reward(data, skill_id, amount)


def inspect_effigy_pure(player_data: Mapping[str, Any], instance_id: str):
    """Reveal a copy's persistent request. A revealed copy is a read."""
    record, refusal = _bank_stage_record(player_data, instance_id)
    if record is None:
        return _refuse(player_data, refusal)
    if record["pair_index"] is not None:
        return player_data, True, {"changed": False, "pair_index": record["pair_index"]}
    revealed = dict(record, pair_index=initial_pair_index_pure(record["request_seed"]))
    updated = _with_record(player_data, instance_id, revealed)
    return updated, True, {"changed": True, "pair_index": revealed["pair_index"]}


def _token_matches(record: Mapping[str, Any], token: Mapping[str, Any]) -> bool:
    return all(
        type(token.get(field)) is type(record[field]) and token.get(field) == record[field]
        for field in ("item_id", "request_step", "pair_index")
    )


def _investigation_refusal(player_data: Mapping[str, Any], token: Any, skill_id: Any):
    """The live record when the investigation may proceed, else the refusal text."""
    if not isinstance(token, Mapping):
        return None, STALE_MESSAGE
    record, refusal = _bank_stage_record(player_data, token.get("instance_id"))
    if record is None:
        return None, refusal
    if not _token_matches(record, token):
        return None, STALE_MESSAGE
    if record["pair_index"] is None:
        return None, "Inspect this effigy to reveal the skills it wants."
    if skill_id not in SKILL_PAIRS[record["pair_index"]]:
        return None, "This effigy does not want that skill."
    stage = STAGES_BY_ITEM_ID[record["item_id"]]
    if skilling_effective_level_pure(player_data, skill_id) < stage.required_level:
        return None, (
            f"You need level {stage.required_level} {skill_name(skill_id)} "
            f"to investigate the {stage.name.lower()}."
        )
    return record, ""


def _replace_one_unit(player_data: Mapping[str, Any], item_id: int, output_id: int) -> dict[str, int]:
    inventory = dict(player_data.get("inventory") or {})
    name = ITEM_NAMES_BY_ID[item_id]
    remaining = int(inventory.get(name, 0)) - 1
    if remaining > 0:
        inventory[name] = remaining
    else:
        inventory.pop(name, None)
    if output_id != DRAGONKIN_LAMP_ID:
        output_name = ITEM_NAMES_BY_ID[output_id]
        inventory[output_name] = int(inventory.get(output_name, 0) or 0) + 1
    elif not inventory.get(ITEM_NAMES_BY_ID[DRAGONKIN_LAMP_ID]):
        # The lamp is its record alone; a seeded zero Bank entry goes too.
        inventory.pop(ITEM_NAMES_BY_ID[DRAGONKIN_LAMP_ID], None)
    return inventory


def investigate_effigy_pure(player_data: Mapping[str, Any], token: Any, skill_id: Any):
    """Feed one copy one of its two requested skills, using the player's own level."""
    record, refusal = _investigation_refusal(player_data, token, skill_id)
    if record is None:
        return _refuse(player_data, refusal)
    instance_id = token["instance_id"]
    stage = STAGES_BY_ITEM_ID[record["item_id"]]
    advanced = dict(record, item_id=stage.output_item_id)
    if stage.output_item_id == DRAGONKIN_LAMP_ID:
        advanced.update(location="held", pair_index=None)
    else:
        advanced["request_step"] = record["request_step"] + 1
        advanced["pair_index"] = next_pair_index_pure(
            record["request_seed"], advanced["request_step"], record["pair_index"]
        )
    data = _with_record(player_data, instance_id, advanced)
    data["inventory"] = _replace_one_unit(player_data, stage.item_id, stage.output_item_id)
    _award(data, skill_id, stage.reward_xp)
    return data, True, {
        "instance_id": instance_id,
        "skill_id": skill_id,
        "xp": stage.reward_xp,
        "from_name": stage.name,
        "to_name": stage.output_name,
        "message": (
            f"You gain {stage.reward_xp:,} {skill_name(skill_id)} XP. "
            f"The {stage.name.lower()} becomes "
            + ("a Dragonkin lamp." if stage.output_item_id == DRAGONKIN_LAMP_ID else f"a {stage.output_name.lower()}.")
        ),
    }


def lamp_preview_pure(player_data: Mapping[str, Any], skill_id: str) -> tuple[int, int]:
    """The permanent XP-derived level the lamp reads, and its exact reward."""
    skill = get_skill(skill_id)
    exp_key = skill.exp_key if skill is not None else f"{skill_id}_exp"
    try:
        experience = float(player_data.get(exp_key, 0) or 0)
    except (TypeError, ValueError):
        experience = 0.0
    level = calculate_new_level(experience, 1, exp_table_for_skill(skill_id))
    level = min(level, lamp_level_cap(skill_id))
    return level, dragonkin_lamp_xp(level)


def _held_lamp(player_data: Mapping[str, Any], token: Any) -> tuple[str | None, str]:
    if not isinstance(token, Mapping) or token.get("item_id") != DRAGONKIN_LAMP_ID:
        return None, STALE_MESSAGE
    instance_id = token.get("instance_id")
    record = _live_record(player_data, instance_id)
    if record is None or record["item_id"] != DRAGONKIN_LAMP_ID:
        return None, STALE_MESSAGE
    if record["location"] != "held":
        return None, "Reclaim this lamp before rubbing it."
    return instance_id, ""


def redeem_lamp_pure(player_data: Mapping[str, Any], token: Any, skill_id: Any):
    """Rub one held lamp for its exact reward, read at this moment, and use it up."""
    instance_id, refusal = _held_lamp(player_data, token)
    if instance_id is None:
        return _refuse(player_data, refusal)
    if skill_id not in LAMP_SKILL_IDS:
        return _refuse(player_data, "The lamp cannot grant experience in that skill.")
    level, xp = lamp_preview_pure(player_data, skill_id)
    data = _with_record(player_data, instance_id, None)
    _award(data, skill_id, xp)
    return data, True, {
        "instance_id": instance_id,
        "skill_id": skill_id,
        "level": level,
        "xp": xp,
        "message": f"You gain {xp:,} {skill_name(skill_id)} XP. The Dragonkin lamp is used up.",
    }


def destroy_lamp_pure(player_data: Mapping[str, Any], token: Any):
    """Destroy one held lamp. Nothing replaces it and nothing is awarded."""
    instance_id, refusal = _held_lamp(player_data, token)
    if instance_id is None:
        return _refuse(player_data, refusal)
    data = _with_record(player_data, instance_id, None)
    return data, True, {"instance_id": instance_id, "message": "The Dragonkin lamp is destroyed."}
