"""Quest wear declarations and the observational view used by admission checks."""

from collections.abc import Mapping

from ..logic_pure_state import _positive_int


def quest_wear_requirement_pure(player_data, quest_id, quest_data):
    state = (player_data.get('quests', {}) or {}).get(quest_id, {})
    if not state.get('started') or state.get('completed'):
        return {}
    stage = max(1, _positive_int(state.get('progress', 0), 0))
    return next((row for row in quest_data[quest_id].get('stage_requirements', ())
                 if row['stage'] == stage and row.get('wear_slot')), {})


def quest_wear_item_pure(player_data, requirement):
    accepted = requirement.get('wear_items', ())
    worn = (player_data.get('equipment', {}) or {}).get(requirement.get('wear_slot'))
    if worn in accepted:
        return worn
    inventory = player_data.get('inventory', {}) or {}
    return next((name for name in accepted if inventory.get(name, 0) > 0), '')


def quest_wear_view_pure(player_data, requirement):
    item = quest_wear_item_pure(player_data, requirement)
    if not item:
        return player_data
    return {**player_data, 'equipment': {
        **(player_data.get('equipment', {}) or {}), requirement['wear_slot']: item,
    }}


def _quest_current_stage_rows(quest, current_stage):
    rows = []
    for requirement in quest.get("stage_requirements", ()) or ():
        if not isinstance(requirement, Mapping):
            continue
        if _positive_int(requirement.get("stage", 0), 0) == current_stage:
            rows.append(requirement)
    return tuple(rows)
