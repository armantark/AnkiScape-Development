"""Oronwen's single quest repair: hand in, then collect on the next review."""

from ...data.quest.oronwen_repair_data import (
    QUEST_ID, REPAIR_STAGE, DAMAGED_TROUSERS, REPAIRED_TROUSERS,
    REPAIR_INPUTS, PENDING_KEY, REPAIR_EVENT, MOURNER_ENCOUNTER,
)
from ...data.quest_action_proof_data import ORONWEN_REPAIR_PROOF
from ..logic_pure_state import _copy_player_data_with_nested, quest_state_pure, _positive_int
from ..quest_action_proofs import (
    quest_action_proof_completed_pure, record_runtime_quest_action_proofs_pure,
)


def oronwen_phase_pure(player_data, quest_id):
    if quest_id != QUEST_ID:
        return None
    state = quest_state_pure(player_data, quest_id)
    if not state["started"] or state["completed"] or state["progress"] != REPAIR_STAGE:
        return None
    if quest_action_proof_completed_pure(player_data, ORONWEN_REPAIR_PROOF):
        return "complete"
    return "collect" if player_data.get(PENDING_KEY) is True else "hand_in"


def oronwen_requirement_pure(player_data, quest_id, requirement):
    if requirement.get("stage") != REPAIR_STAGE or oronwen_phase_pure(player_data, quest_id) not in ("collect", "complete"):
        return requirement
    inputs = {name for name, _ in REPAIR_INPUTS}
    return dict(requirement, required_inventory={
        name: quantity for name, quantity in requirement.get("required_inventory", {}).items()
        if name not in inputs
    })


def oronwen_review_ready_pure(player_data, quest_id, blockers):
    phase = oronwen_phase_pure(player_data, quest_id)
    if phase not in ("hand_in", "collect"):
        return False
    if any(blocker.get("kind") != "required_action" or blocker.get("action_id") != ORONWEN_REPAIR_PROOF for blocker in blockers):
        return False
    inventory = player_data.get("inventory", {}) or {}
    return phase == "collect" or all(
        _positive_int(inventory.get(name, 0), 0) >= quantity for name, quantity in REPAIR_INPUTS
    )


def apply_oronwen_review_pure(player_data, quest_id, blockers):
    if not oronwen_review_ready_pure(player_data, quest_id, blockers):
        return player_data, "unchanged"
    data = _copy_player_data_with_nested(player_data)
    inventory = data["inventory"]
    if oronwen_phase_pure(player_data, quest_id) == "hand_in":
        for name, quantity in REPAIR_INPUTS:
            inventory[name] -= quantity
        data[PENDING_KEY] = True
        return data, "handed_in"
    inventory[REPAIRED_TROUSERS] = inventory.get(REPAIRED_TROUSERS, 0) + 1
    data[PENDING_KEY] = False
    record_runtime_quest_action_proofs_pure(data, *REPAIR_EVENT)
    return data, "collected"


def migrate_oronwen_repair_state(data, loaded_config_version):
    phase = oronwen_phase_pure(data, QUEST_ID)
    pending = data.get(PENDING_KEY) is True
    data[PENDING_KEY] = loaded_config_version >= 125 and phase in ("hand_in", "collect") and pending
    if loaded_config_version >= 125 or phase not in ("hand_in", "collect"):
        return
    inventory = data.get("inventory", {}) or {}
    flags = data.get("quest_combat_encounters", {}).get(QUEST_ID, ())
    counts = data.get("quest_combat_encounter_counts", {}).get(QUEST_ID, {})
    if (_positive_int(inventory.get(DAMAGED_TROUSERS, 0), 0) == 0
            and MOURNER_ENCOUNTER not in flags
            and _positive_int(counts.get(MOURNER_ENCOUNTER, 0), 0) == 0):
        data["quests"][QUEST_ID]["progress"] = 2
