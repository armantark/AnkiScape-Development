"""Quest flag and encounter quantities shared by progress and combat admission."""

from typing import Iterable, Mapping

from ..logic_pure_state import _positive_int


def _quest_flag_completed(player_data, collection_key, quest_id, flag_id):
    raw_collection = player_data.get(collection_key, {})
    if isinstance(raw_collection, Mapping):
        quest_flags = raw_collection.get(quest_id, ())
        if isinstance(quest_flags, Mapping):
            return bool(quest_flags.get(flag_id, False))
        if isinstance(quest_flags, str):
            return quest_flags == flag_id
        if isinstance(quest_flags, Iterable):
            return flag_id in {flag for flag in quest_flags if isinstance(flag, str)}
    elif isinstance(raw_collection, Iterable) and not isinstance(raw_collection, str):
        return flag_id in {flag for flag in raw_collection if isinstance(flag, str)}
    return False


def _quest_combat_total_quantity(encounter):
    return _positive_int(encounter.get("quantity", 1), 1)


def _quest_combat_completed_count(player_data, quest_id, encounter_id, encounter):
    quantity = _quest_combat_total_quantity(encounter)
    if _quest_flag_completed(player_data, "quest_combat_encounters", quest_id, encounter_id):
        return quantity
    raw_counts = player_data.get("quest_combat_encounter_counts", {})
    if not isinstance(raw_counts, Mapping):
        return 0
    quest_counts = raw_counts.get(quest_id, {})
    if not isinstance(quest_counts, Mapping):
        return 0
    return min(quantity, _positive_int(quest_counts.get(encounter_id, 0), 0))


def _quest_combat_remaining_count(player_data, quest_id, encounter_id, encounter):
    quantity = _quest_combat_total_quantity(encounter)
    return max(0, quantity - _quest_combat_completed_count(player_data, quest_id, encounter_id, encounter))


def quest_combat_prerequisites_completed_pure(player_data, quest_id, quest_data, encounter):
    required_ids = encounter.get("required_encounters", ())
    if not required_ids:
        return True
    encounters = {
        row.get("encounter_id"): row
        for requirement in quest_data[quest_id].get("stage_requirements", ())
        for row in requirement.get("combat_encounters", ())
        if isinstance(row, Mapping)
    }
    for encounter_id in required_ids:
        prerequisite = encounters.get(encounter_id)
        if prerequisite is None or _quest_combat_remaining_count(
            player_data, quest_id, encounter_id, prerequisite,
        ) > 0:
            return False
    return True
