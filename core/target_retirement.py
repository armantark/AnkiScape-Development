"""Repair retired or invalid skilling targets in saved state."""

from ..data.cooking_data import DEFAULT_COOKING_TARGET, COOKING_TARGETS_BY_ID
from ..data.runecrafting_data import DEFAULT_RUNECRAFTING_TARGET, RUNECRAFTING_TARGETS_BY_ID


def _retired_hood_feed(target_id) -> bool:
    return isinstance(target_id, str) and target_id.startswith("feed_") and target_id.endswith("_to_hood")


def migrate_runecrafting_target(data: dict) -> None:
    current = data.get("current_runecrafting")
    if not isinstance(current, str) or current not in RUNECRAFTING_TARGETS_BY_ID:
        data["current_runecrafting"] = DEFAULT_RUNECRAFTING_TARGET
    for key in (
        "carried_inventory", "carried_layout", "carried_churn", "carried_keep_drop",
        "carried_advanced_targets", "carried_primed_targets",
    ):
        collection = data.get(key)
        if isinstance(collection, dict):
            data[key] = {target: value for target, value in collection.items() if not _retired_hood_feed(target)}
    run = data.get("skilling_bank_run")
    if isinstance(run, dict) and _retired_hood_feed(run.get("target_id")):
        data["skilling_bank_run"] = {}
    if _retired_hood_feed(data.get("skilling_bank_run_requested")):
        data.pop("skilling_bank_run_requested")


def migrate_cooking_target(data: dict) -> None:
    current_cooking = data.get("current_cooking")
    if not isinstance(current_cooking, str) or current_cooking not in COOKING_TARGETS_BY_ID:
        current_cooking = DEFAULT_COOKING_TARGET
    data["current_cooking"] = current_cooking
