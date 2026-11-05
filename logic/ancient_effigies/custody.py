"""Per-copy custody for Ancient Effigies and Dragonkin lamps.

Effigy stages live in the Bank as ordinary name counts, and the gravestone and
Death's Office hold them as name lists. Those counts cannot tell two Starved
effigies apart, but each copy carries its own hidden request, so every copy
also has an instance record:

    ancient_effigy_instances["ancient-effigy-<n>"] = {
        "item_id": 18778..18782,
        "location": "bank" | "held" | "grave" | "death_office",
        "request_seed": 32 lowercase hex characters,
        "request_step": stage advancements so far,
        "pair_index": None until inspected, then 0..7,
    }

Synchronization reconciles the records with the name holders. It keeps valid
assignments, moves leftover records to holders that are short (in numeric ID
order), and creates records only for units no record covers. A Dragonkin lamp
is different: its record is the ownership, it has no Bank or carried count, and
a lamp unit that appears in the Bank (a grave reclaim, or a legacy save) is
folded back into a held record.
"""

from __future__ import annotations

import math
import random
import re
from collections.abc import Mapping
from typing import Any, Callable

from ...data.ancient_effigies.catalog import (
    DRAGONKIN_LAMP_ID,
    DRAGONKIN_LAMP_NAME,
    ITEM_NAMES_BY_ID,
    STAGE_ITEM_IDS,
)


INSTANCES_KEY = "ancient_effigy_instances"
NEXT_ID_KEY = "ancient_effigy_next_id"
INSTANCE_PREFIX = "ancient-effigy-"
LOCATIONS = ("bank", "held", "grave", "death_office")
RECOVERY_LOCATIONS = ("grave", "death_office")
STAGE_LOCATIONS = ("bank", "grave", "death_office")

_INSTANCE_ID = re.compile(r"ancient-effigy-([1-9][0-9]*)")
_SEED = re.compile(r"[0-9a-f]{32}")


def default_effigy_custody_state_pure() -> dict[str, Any]:
    return {INSTANCES_KEY: {}, NEXT_ID_KEY: 1}


def instance_number(instance_id: Any) -> int | None:
    """The positive numeric suffix of a syntactically valid instance ID."""
    if not isinstance(instance_id, str):
        return None
    match = _INSTANCE_ID.fullmatch(instance_id)
    return int(match.group(1)) if match else None


def instance_id_for(number: int) -> str:
    return f"{INSTANCE_PREFIX}{number}"


def new_request_seed(getrandbits: Callable[[int], int] | None = None) -> str:
    """A hidden per-copy replay seed from the shared random module."""
    draw = getrandbits or random.getrandbits
    return f"{draw(128):032x}"


def _whole_number(value: Any) -> int | None:
    """An integer, or an integral finite float; never a bool or a fraction."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and math.isfinite(value) and value.is_integer():
        return int(value)
    return None


def _count(value: Any) -> int:
    number = _whole_number(value)
    return number if number is not None and number > 0 else 0


def _clean_seed(value: Any) -> str | None:
    return value if isinstance(value, str) and _SEED.fullmatch(value) else None


def _clean_step(value: Any) -> int | None:
    number = _whole_number(value)
    return number if number is not None and number >= 0 else None


def _clean_pair(value: Any) -> int | None:
    number = _whole_number(value)
    return number if number is not None and 0 <= number <= 7 else None


def _clean_location(item_id: int, value: Any) -> str | None:
    if value not in LOCATIONS:
        return None
    if item_id == DRAGONKIN_LAMP_ID and value == "bank":
        return None
    return value


def clean_record_pure(raw: Any) -> dict[str, Any] | None:
    """Repair one record field by field, keeping every field that is valid.

    Only an unknown item makes the record unusable. A missing seed, step or
    location is left as ``None`` for synchronization to fill; a valid pair is
    never discarded because a neighbouring field was damaged.
    """
    if not isinstance(raw, Mapping):
        return None
    item_id = _whole_number(raw.get("item_id"))
    if item_id not in ITEM_NAMES_BY_ID:
        return None
    pair_index = None if item_id == DRAGONKIN_LAMP_ID else _clean_pair(raw.get("pair_index"))
    return {
        "item_id": item_id,
        "location": _clean_location(item_id, raw.get("location")),
        "request_seed": _clean_seed(raw.get("request_seed")),
        "request_step": _clean_step(raw.get("request_step")),
        "pair_index": pair_index,
    }


def is_valid_record_pure(raw: Any) -> bool:
    """Whether a stored record is already fully normalized."""
    cleaned = clean_record_pure(raw)
    return (
        cleaned is not None
        and None not in (cleaned["location"], cleaned["request_seed"], cleaned["request_step"])
        and dict(raw) == cleaned
    )


def sorted_instance_ids(instances: Mapping[str, Any]) -> list[str]:
    return sorted(
        (instance_id for instance_id in instances if instance_number(instance_id) is not None),
        key=lambda instance_id: instance_number(instance_id) or 0,
    )


def _name_list_counts(raw_holder: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    items = raw_holder.get("items") if isinstance(raw_holder, Mapping) else None
    if not isinstance(items, (list, tuple)):
        return counts
    for item_name in items:
        if isinstance(item_name, str):
            counts[item_name] = counts.get(item_name, 0) + 1
    return counts


def holder_counts_pure(player_data: Mapping[str, Any]) -> dict[tuple[int, str], int]:
    """How many units of each effigy item each name holder owns."""
    inventory = player_data.get("inventory")
    inventory = inventory if isinstance(inventory, Mapping) else {}
    grave = _name_list_counts(player_data.get("combat_grave"))
    office = _name_list_counts(player_data.get("death_office"))
    counts: dict[tuple[int, str], int] = {}
    for item_id, name in ITEM_NAMES_BY_ID.items():
        counts[(item_id, "bank")] = _count(inventory.get(name))
        counts[(item_id, "grave")] = grave.get(name, 0)
        counts[(item_id, "death_office")] = office.get(name, 0)
    return counts


class _Allocator:
    """Hands out new instance IDs and seeds in a fixed order."""

    def __init__(self, next_id: int, getrandbits: Callable[[int], int] | None) -> None:
        self.next_id = next_id
        self.getrandbits = getrandbits

    def new_record(self, item_id: int, location: str) -> tuple[str, dict[str, Any]]:
        instance_id = instance_id_for(self.next_id)
        self.next_id += 1
        return instance_id, {
            "item_id": item_id,
            "location": location,
            "request_seed": new_request_seed(self.getrandbits),
            "request_step": 0,
            "pair_index": None,
        }

    def complete(self, record: dict[str, Any], location: str) -> dict[str, Any]:
        """Place a kept record and fill any field a repair left empty."""
        record = dict(record)
        record["location"] = location
        if record["request_seed"] is None:
            record["request_seed"] = new_request_seed(self.getrandbits)
        if record["request_step"] is None:
            record["request_step"] = 0
        return record


def _place_in_holders(
    item_id: int,
    candidates: list[str],
    records: Mapping[str, dict[str, Any]],
    holders: Mapping[tuple[int, str], int],
    locations: tuple[str, ...],
    allocator: _Allocator,
    placed: dict[str, dict[str, Any]],
) -> list[str]:
    """Fill each name holder's count with records; return the unplaced records.

    Records already at a holder keep their place first. Leftover records then
    fill the remaining shortfalls in numeric ID order, and only a shortfall no
    record can cover gets a new record.
    """
    deficits: dict[str, int] = {}
    for location in locations:
        wanted = holders[(item_id, location)]
        kept = [
            instance_id
            for instance_id in candidates
            if instance_id not in placed and records[instance_id]["location"] == location
        ][:wanted]
        for instance_id in kept:
            placed[instance_id] = allocator.complete(records[instance_id], location)
        deficits[location] = wanted - len(kept)
    pool = [instance_id for instance_id in candidates if instance_id not in placed]
    for location in locations:
        moved, pool = pool[: deficits[location]], pool[deficits[location]:]
        for instance_id in moved:
            placed[instance_id] = allocator.complete(records[instance_id], location)
        for _ in range(deficits[location] - len(moved)):
            instance_id, record = allocator.new_record(item_id, location)
            placed[instance_id] = record
    return pool


def _reconcile_stage(
    item_id: int,
    records: Mapping[str, dict[str, Any]],
    holders: Mapping[tuple[int, str], int],
    allocator: _Allocator,
) -> dict[str, dict[str, Any]]:
    """Bank, gravestone and Death's Office counts each own that many copies."""
    candidates = [instance_id for instance_id in records if records[instance_id]["item_id"] == item_id]
    placed: dict[str, dict[str, Any]] = {}
    # Records left over own no unit any more; they are dropped, never reused.
    _place_in_holders(item_id, candidates, records, holders, STAGE_LOCATIONS, allocator, placed)
    return placed


def _reconcile_lamps(
    records: Mapping[str, dict[str, Any]],
    holders: Mapping[tuple[int, str], int],
    allocator: _Allocator,
) -> dict[str, dict[str, Any]]:
    """Held lamps stand alone; recovery lamps follow the grave and office lists.

    A lamp record that left its recovery holder either filled another holder's
    shortfall or came back through the reclaim path as a Bank unit, which it
    absorbs. With neither, it expired with its gravestone.
    """
    candidates = [instance_id for instance_id in records if records[instance_id]["item_id"] == DRAGONKIN_LAMP_ID]
    placed = {
        instance_id: allocator.complete(records[instance_id], "held")
        for instance_id in candidates
        if records[instance_id]["location"] == "held"
    }
    pool = _place_in_holders(DRAGONKIN_LAMP_ID, candidates, records, holders, RECOVERY_LOCATIONS, allocator, placed)
    bank_units = holders[(DRAGONKIN_LAMP_ID, "bank")]
    for instance_id in pool[:bank_units]:
        placed[instance_id] = allocator.complete(records[instance_id], "held")
    # Count-backed lamps from before custody existed are adopted exactly once:
    # the same pass removes their Bank units.
    for _ in range(bank_units - len(pool[:bank_units])):
        instance_id, record = allocator.new_record(DRAGONKIN_LAMP_ID, "held")
        placed[instance_id] = record
    return placed


def _clean_records(raw_instances: Any) -> tuple[dict[str, dict[str, Any]], int]:
    """Records in numeric ID order, and the highest valid numeric suffix seen."""
    records: dict[str, dict[str, Any]] = {}
    highest = 0
    if not isinstance(raw_instances, Mapping):
        return records, highest
    for instance_id in sorted_instance_ids(raw_instances):
        highest = max(highest, instance_number(instance_id) or 0)
        record = clean_record_pure(raw_instances[instance_id])
        if record is not None:
            records[instance_id] = record
    return records, highest


def _without_lamp_entry(view: Any) -> Any:
    if not isinstance(view, Mapping):
        return view
    return {name: amount for name, amount in view.items() if name != DRAGONKIN_LAMP_NAME}


def _without_lamp_units(player_data: Mapping[str, Any]) -> dict[str, Any]:
    """Rebuilt Bank and carried views with no Dragonkin lamp entry.

    A lamp exists only as a record. Adoption, reclaim and an older save's
    stored zero all leave the Bank with no lamp entry at all.
    """
    patch: dict[str, Any] = {}
    inventory = player_data.get("inventory")
    if isinstance(inventory, Mapping) and DRAGONKIN_LAMP_NAME in inventory:
        patch["inventory"] = _without_lamp_entry(inventory)
    carried = player_data.get("carried_inventory")
    if isinstance(carried, Mapping) and any(_without_lamp_entry(view) != view for view in carried.values()):
        patch["carried_inventory"] = {target_id: _without_lamp_entry(view) for target_id, view in carried.items()}
    return patch


def synchronize_effigy_custody_pure(
    player_data: Mapping[str, Any],
    *,
    getrandbits: Callable[[int], int] | None = None,
) -> dict[str, Any]:
    """Reconcile instance records with every holder; return a new save.

    Touched mappings are rebuilt rather than edited, so the caller's nested
    objects are never mutated. An already normalized save gets equal values
    back and allocates nothing.
    """
    data = dict(player_data)
    records, highest = _clean_records(data.get(INSTANCES_KEY))
    stored_next = _whole_number(data.get(NEXT_ID_KEY))
    allocator = _Allocator(max(highest + 1, stored_next if stored_next and stored_next > 0 else 1), getrandbits)
    holders = holder_counts_pure(data)
    placed: dict[str, dict[str, Any]] = {}
    for item_id in STAGE_ITEM_IDS:
        placed.update(_reconcile_stage(item_id, records, holders, allocator))
    placed.update(_reconcile_lamps(records, holders, allocator))
    data[INSTANCES_KEY] = {instance_id: placed[instance_id] for instance_id in sorted_instance_ids(placed)}
    data[NEXT_ID_KEY] = allocator.next_id
    data.update(_without_lamp_units(data))
    return data


def custody_records_pure(player_data: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    """The fully valid stored records, in numeric order, without repairing any."""
    raw = player_data.get(INSTANCES_KEY)
    if not isinstance(raw, Mapping):
        return {}
    return {
        instance_id: dict(raw[instance_id])
        for instance_id in sorted_instance_ids(raw)
        if is_valid_record_pure(raw[instance_id])
    }


def bank_units_pure(player_data: Mapping[str, Any], item_id: int) -> int:
    inventory = player_data.get("inventory")
    if not isinstance(inventory, Mapping):
        return 0
    return _count(inventory.get(ITEM_NAMES_BY_ID[item_id]))


def held_lamp_ids_pure(player_data: Mapping[str, Any]) -> list[str]:
    return [
        instance_id
        for instance_id, record in custody_records_pure(player_data).items()
        if record["item_id"] == DRAGONKIN_LAMP_ID and record["location"] == "held"
    ]
