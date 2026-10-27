"""Genuine Hazeel opening transactions and current valve-state validation."""

from collections.abc import Mapping

from ...data.quest.hazeel_opening import (
    ACTIONS, PROOFS, SHARED, BRANCH_ROUTES, BRANCH_DEEDS, ENDPOINTS,
    REQUIRED_PROOFS, VALVES, CORRECT_VALVE_ACTIONS, QUEST_ID, SOURCE,
    VALVE_KEY, POISON, MARK, POISON_RECEIPT, POISON_OWNED, MARK_RECEIPT, MARK_OWNED,
)
from ..logic_pure_state import _copy_player_data_with_nested, _positive_int, quest_state_pure
from ..quest_action_proofs import quest_action_proof_completed_pure, record_quest_stage_action_proofs_pure
from .progress_state import _quest_flag_completed, _quest_combat_remaining_count
from .stage_items import (
    _quest_stage_item_pairs, _quest_stage_item_option_groups, _quest_stage_strings, _has_quest_tool,
)


def sanitize_hazeel_valve_states_pure(raw):
    if not isinstance(raw, Mapping):
        return {}
    targets = {str(valve.object_id) for valve in VALVES}
    return {key: value for key, value in raw.items()
            if isinstance(key, str) and key in targets and value in ("left", "right")}


def _active(player_data):
    state = quest_state_pure(player_data, QUEST_ID)
    return state["started"] and not state["completed"] and state["progress"] in (0, 1)


def hazeel_opening_branch_pure(player_data):
    branches = [branch for branch, route in BRANCH_ROUTES.items()
                if _quest_flag_completed(player_data, "quest_route_states", QUEST_ID, route)]
    if len(branches) > 1:
        return "inconsistent"
    return branches[0] if branches else None


def _earned(player_data, action_id):
    return quest_action_proof_completed_pure(player_data, PROOFS[action_id])


def _all_earned(player_data, action_ids):
    return all(_earned(player_data, key) for key in action_ids)


def hazeel_opening_choice_ready_pure(player_data):
    return (_active(player_data) and hazeel_opening_branch_pure(player_data) != "inconsistent"
            and _all_earned(player_data, SHARED))


def _correct_valve(player_data, valve):
    action_id = f"valve_{valve.object_id}_{valve.correct}"
    states = sanitize_hazeel_valve_states_pure(player_data.get(VALVE_KEY))
    return states.get(str(valve.object_id)) == valve.correct and _earned(player_data, action_id)


def hazeel_opening_next_action_pure(player_data, quest_id=QUEST_ID):
    if quest_id != QUEST_ID or not _active(player_data):
        return None
    branch = hazeel_opening_branch_pure(player_data)
    if branch == "inconsistent":
        return None
    for action_id in SHARED:
        if not _earned(player_data, action_id):
            return ACTIONS[action_id]
    if branch is None:
        return None
    for action_id in BRANCH_DEEDS[branch][2:]:
        if not _earned(player_data, action_id):
            return ACTIONS[action_id]
    for valve, action_id in zip(VALVES, CORRECT_VALVE_ACTIONS):
        if not _correct_valve(player_data, valve):
            return ACTIONS[action_id]
    return None


def _count(player_data, name):
    inventory = player_data.get("inventory", {})
    if not isinstance(inventory, Mapping):
        return None
    value = inventory.get(name, 0)
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def _mark_owned(player_data, count):
    equipment = player_data.get("equipment", {}) or {}
    return count > 0 or (isinstance(equipment, Mapping) and MARK in equipment.values())


def _item_transaction(player_data, action_id):
    """Validate custody first; return an inventory delta and optional outcome."""
    if action_id == "cult_acceptance":
        count = _count(player_data, POISON)
        if count is None:
            return None
        return (POISON, 1, POISON_RECEIPT) if count == 0 else (None, 0, POISON_OWNED)
    if action_id == "poison_range":
        count = _count(player_data, POISON)
        return (POISON, -1, None) if count is not None and count >= 1 else None
    if action_id == "clivet_mark":
        count = _count(player_data, MARK)
        if count is None:
            return None
        return (None, 0, MARK_OWNED) if _mark_owned(player_data, count) else (MARK, 1, MARK_RECEIPT)
    return (None, 0, None)


def _prerequisites_met(player_data, action, branch):
    if action.action_id in SHARED:
        preceding = SHARED[:SHARED.index(action.action_id)]
    else:
        if branch not in BRANCH_DEEDS:
            return False
        deeds = BRANCH_DEEDS[branch]
        if action.direction:
            preceding = deeds
        elif action.action_id in deeds:
            preceding = deeds[:deeds.index(action.action_id)]
        else:
            return False
    return _all_earned(player_data, preceding)


def _target_valid(player_data, action, target, option):
    if type(target) is not type(action.target) or target != action.target or option != action.option:
        return False
    if not action.direction:
        return not _earned(player_data, action.action_id)
    states = sanitize_hazeel_valve_states_pure(player_data.get(VALVE_KEY))
    return states.get(str(action.target)) != action.direction


def apply_hazeel_opening_action_pure(player_data, action_id, target=None, option=None, *, quest_data=None, eligibility_reasons=None):
    """Sole opening proof writer. Failed requests retain the original object."""
    result = {"action_id": action_id, "status": "unchanged"}
    action = ACTIONS.get(action_id) if isinstance(action_id, str) else None
    branch = hazeel_opening_branch_pure(player_data)
    if not _active(player_data) or action is None or branch == "inconsistent":
        return player_data, False, result
    if (_eligibility_blocked(player_data, QUEST_ID, quest_data, eligibility_reasons)
            or not _catalog_ready(player_data, quest_data, branch, eligibility_reasons)):
        return player_data, False, result
    if not _prerequisites_met(player_data, action, branch) or not _target_valid(player_data, action, target, option):
        return player_data, False, result
    transaction = _item_transaction(player_data, action_id)
    if transaction is None:
        return player_data, False, result
    data = _copy_player_data_with_nested(player_data)
    data[VALVE_KEY] = sanitize_hazeel_valve_states_pure(player_data.get(VALVE_KEY))
    item, delta, outcome = transaction
    if item:
        data["inventory"][item] = _count(player_data, item) + delta
    if action.direction:
        data[VALVE_KEY][str(action.target)] = action.direction
    proofs = [action.proof]
    if outcome:
        proofs.append(outcome)
    # Evaluate against the proposed turn without publishing a proof early.
    if action.direction and _endpoint_after_turn(player_data, data, action, branch):
        proofs.append(PROOFS[ENDPOINTS[branch]])
        result["status"] = "ready"
    else:
        result["status"] = "pending"
    record_quest_stage_action_proofs_pure(data, QUEST_ID, proofs)
    return data, True, result


def _endpoint_after_turn(before, after, action, branch):
    if not _all_earned(before, BRANCH_DEEDS[branch]):
        return False
    for valve in VALVES:
        key = f"valve_{valve.object_id}_{valve.correct}"
        if after[VALVE_KEY].get(str(valve.object_id)) != valve.correct:
            return False
        if key != action.action_id and not _earned(before, key):
            return False
    return True


def _blocker(kind, reason, **extra):
    return dict(stage=1, kind=kind, reason=reason, source=SOURCE, **extra)


def hazeel_opening_state_blockers_pure(player_data, quest_id=QUEST_ID, quest_data=None, eligibility_reasons=None):
    if quest_id != QUEST_ID or not _active(player_data):
        return ()
    branch = hazeel_opening_branch_pure(player_data)
    if branch == "inconsistent":
        return (_blocker("hazeel_branch", "Conflicting Hazeel Cult faction routes"),)
    blockers = [_blocker("hazeel_valve_state", f"Set valve {valve.number} {valve.correct}",
                         target=valve.object_id)
                for valve in VALVES if not _correct_valve(player_data, valve)]
    if eligibility_reasons is not None:
        blockers.extend(_blocker("hazeel_eligibility", reason)
                        for reason in eligibility_reasons(player_data, quest_id, quest_data))
    action = hazeel_opening_next_action_pure(player_data)
    if action and action.action_id == "poison_range" and _item_transaction(player_data, action.action_id) is None:
        blockers.append(_blocker("missing_item", "Needs Poison x1", item_name=POISON, quantity=1, owned=0))
    return tuple(blockers)


def _ignorable_blocker(blocker, branch):
    if blocker.get("kind") == "hazeel_valve_state":
        return True
    if blocker.get("kind") == "required_action":
        allowed = REQUIRED_PROOFS[branch] if branch in BRANCH_DEEDS else tuple(PROOFS[key] for key in SHARED)
        return blocker.get("action_id") in allowed
    return branch is None and blocker.get("kind") == "unmet_route" and blocker.get("route_id") in BRANCH_ROUTES.values()


def _external_items_ready(player_data, row):
    inventory = player_data.get("inventory", {}) or {}
    for key in ("required_inventory", "consumed_inventory"):
        if any(_positive_int(inventory.get(name, 0), 0) < amount
               for name, amount in _quest_stage_item_pairs(row, key)):
            return False
    for key in ("required_inventory_options", "consumed_inventory_options"):
        for options in _quest_stage_item_option_groups(row, key):
            if not any(_external_option_owned(player_data, inventory, key, name, amount)
                       for name, amount in options):
                return False
    return all(_has_quest_tool(player_data, name, amount)
               for name, amount in _quest_stage_item_pairs(row, "required_tools"))


def _external_option_owned(player_data, inventory, key, name, amount):
    if key == "required_inventory_options":
        return _has_quest_tool(player_data, name, amount)
    return _positive_int(inventory.get(name, 0), 0) >= amount


def _external_skills_ready(player_data, row, quest_data, eligibility_reasons):
    requirements = row.get("required_skills", ())
    if not requirements:
        return True
    # Reuse the supplied evaluator without importing the combat/orchestration graph.
    quest = dict(quest_data[QUEST_ID], required_skills=requirements)
    catalog = {**quest_data, QUEST_ID: quest}
    return not _eligibility_blocked(player_data, QUEST_ID, catalog, eligibility_reasons)


def _external_row_ready(player_data, row, branch, quest_data, eligibility_reasons):
    if not _external_items_ready(player_data, row):
        return False
    if not _external_skills_ready(player_data, row, quest_data, eligibility_reasons):
        return False
    if any(_quest_combat_remaining_count(player_data, QUEST_ID, encounter.get("encounter_id"), encounter) > 0
           for encounter in row.get("combat_encounters", ())):
        return False
    allowed = REQUIRED_PROOFS[branch] if branch in BRANCH_DEEDS else {
        proof for proofs in REQUIRED_PROOFS.values() for proof in proofs
    }
    if any(proof not in allowed and not quest_action_proof_completed_pure(player_data, proof)
           for proof in _quest_stage_strings(row, "required_actions")):
        return False
    return all(_external_route_ready(player_data, route, branch)
               for route in _quest_stage_strings(row, "required_routes"))


def _external_route_ready(player_data, route, branch):
    return ((branch is None and route in BRANCH_ROUTES.values())
            or _quest_flag_completed(player_data, "quest_route_states", QUEST_ID, route))


def _catalog_ready(player_data, quest_data, branch, eligibility_reasons):
    """Check mandatory and selected rows; before selection check both routes."""
    if quest_data is None:
        return True
    quest = quest_data.get(QUEST_ID)
    if not quest:
        return False
    rows = (row for row in quest.get("stage_requirements", ())
            if row.get("stage") == 1 and (not row.get("variant") or branch is None or row.get("variant") == branch))
    return all(_external_row_ready(player_data, row, branch, quest_data, eligibility_reasons) for row in rows)


def _eligibility_blocked(player_data, quest_id, quest_data, eligibility_reasons):
    if eligibility_reasons is not None:
        return bool(eligibility_reasons(player_data, quest_id, quest_data))
    if quest_data is None:
        return False
    quest = quest_data.get(quest_id)
    # Direct callers without the shared evaluator may run this ungated opening,
    # but cannot waive catalog obligations they have not evaluated.
    return not quest or any(quest.get(key) for key in (
        "required_quests", "required_skills", "required_items", "required_quest_points",
    ))


def hazeel_opening_review_ready_pure(player_data, quest_id, quest_data, blockers, eligibility_reasons=None):
    action = hazeel_opening_next_action_pure(player_data, quest_id)
    if action is None or _eligibility_blocked(player_data, quest_id, quest_data, eligibility_reasons):
        return False
    branch = hazeel_opening_branch_pure(player_data)
    if not _catalog_ready(player_data, quest_data, branch, eligibility_reasons):
        return False
    if any(not _ignorable_blocker(blocker, branch) for blocker in blockers):
        return False
    return (_prerequisites_met(player_data, action, branch)
            and _target_valid(player_data, action, action.target, action.option)
            and _item_transaction(player_data, action.action_id) is not None)


def apply_hazeel_opening_review_pure(player_data, quest_id, quest_data, blockers, eligibility_reasons=None):
    if not hazeel_opening_review_ready_pure(player_data, quest_id, quest_data, blockers, eligibility_reasons):
        return player_data, "unchanged"
    action = hazeel_opening_next_action_pure(player_data, quest_id)
    data, ok, result = apply_hazeel_opening_action_pure(
        player_data, action.action_id, action.target, action.option, quest_data=quest_data, eligibility_reasons=eligibility_reasons,
    )
    return data, result["status"] if ok else "unchanged"
