"""Chronological Farming deadlines, independent of how cards divide play time."""

from typing import Any, Callable

from ...data.farming_data import FARMING_COMPOST_BINS_BY_ID, FARMING_CROPS_BY_ID, FARMING_PATCHES_BY_ID
from .materials import _int


def _patch_deadline(record):
    crop = FARMING_CROPS_BY_ID.get(record.get("crop_id"))
    if crop is None or record.get("dead"):
        return 0
    if crop.stages and record["stage"] < crop.stages:
        return record["planted_at"] + (record["stage"] + 1) * crop.stage_minutes
    if record.get("next_regrowth_at"):
        return record["next_regrowth_at"]
    if crop.regrowth_minutes and record["produce_count"] < crop.fixed_yield:
        return record["last_regrowth_at"] + crop.regrowth_minutes
    return 0


def farm_clock_steps_pure(state, minutes):
    """Yield each deadline before the endpoint; the caller settles it before resuming.

    Ordering deadlines across patches keeps disease rolls and event timestamps
    identical for a large logout jump and for the same time in smaller pieces.
    """
    end = round(state["farm_clock_minutes"] + minutes, 2)
    while state["farm_clock_minutes"] < end:
        deadlines = [job["ready_at"] for job in state["farm_sapling_jobs"]]
        deadlines.extend(record["ready_at"] for record in state["farm_compost_bins"].values() if record["status"] == "filling")
        deadlines.extend(_patch_deadline(record) for record in state["farm_patches"].values())
        yield min((point for point in deadlines if state["farm_clock_minutes"] < point < end), default=end)


def _advance_farm_to(updated: dict[str, Any], minute: float, random_random: Callable[[], float], process_patch: Callable, log: Callable) -> None:
    updated["farm_clock_minutes"] = minute
    ready_jobs = []
    pending_jobs = []
    for job in updated["farm_sapling_jobs"]:
        (ready_jobs if job["ready_at"] <= updated["farm_clock_minutes"] else pending_jobs).append(job)
    updated["farm_sapling_jobs"] = pending_jobs
    for job in ready_jobs:
        inventory = updated["inventory"]
        amount = min(job["amount"], _int(inventory.get(job["seedling_item"])))
        if amount:
            inventory[job["seedling_item"]] -= amount
            inventory[job["sapling_item"]] = _int(inventory.get(job["sapling_item"])) + amount
        log(updated, "saplings_ready", f"{amount} {job['sapling_item']} matured.", amount=amount)
    for bin_id in FARMING_COMPOST_BINS_BY_ID:
        record = updated["farm_compost_bins"][bin_id]
        if record["status"] == "filling" and record["ready_at"] <= updated["farm_clock_minutes"]:
            record["status"] = "ready"
            log(updated, "compost_ready", f"{FARMING_COMPOST_BINS_BY_ID[bin_id].display_name} is ready.", bin_id=bin_id)
    for patch_id in FARMING_PATCHES_BY_ID:
        process_patch(updated, patch_id, random_random)


def advance_farm_calendar(state, minutes, random_random, process_patch, log):
    events = []
    for minute in farm_clock_steps_pure(state, minutes):
        _advance_farm_to(state, minute, random_random, process_patch, log)
        events.extend(dict(row) for row in state["farm_event_log"] if row.get("clock") == minute)
    return {"minutes": minutes, "events": events}
