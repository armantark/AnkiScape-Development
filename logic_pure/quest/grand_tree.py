"""Atomic Grand Tree review bundles and read-only opening projections."""

from ...data.quest.grand_tree import (
    QUEST_ID, BARK_SAMPLE, TRANSLATION_BOOK, HAZELMERES_SCROLL,
    PROOFS, EVENTS, REVIEW_BUNDLES, STAGE_SOURCES,
)
from ..logic_pure_state import _copy_player_data_with_nested, quest_state_pure
from ..quest_action_proofs import (
    quest_action_proof_completed_pure, record_runtime_quest_action_proofs_pure,
)

_PHASE_BY_STATE = {
    (0, 0): "commission", (1, 0): "commission", (1, 1): "examination",
    (2, 2): "translation", (2, 3): "report_warning",
}
_MATERIALS = {
    "examination": ((BARK_SAMPLE, 1),),
    "translation": ((TRANSLATION_BOOK, 1), (HAZELMERES_SCROLL, 1)),
}
_DELTAS = {
    "commission": ((BARK_SAMPLE, 1), (TRANSLATION_BOOK, 1)),
    "examination": ((BARK_SAMPLE, -1), (HAZELMERES_SCROLL, 1)),
}
_NEXT_PROGRESS = {"commission": 1, "examination": 2, "translation": 2, "report_warning": 3}
_STAGE_PROOFS = {1: PROOFS[:2], 2: PROOFS[2:]}


def _performed(player_data):
    return tuple(proof for proof in PROOFS if quest_action_proof_completed_pure(player_data, proof))


def grand_tree_phase_pure(player_data, quest_id=QUEST_ID):
    """Project the upcoming bundle without inferring any deed from custody."""
    if quest_id != QUEST_ID:
        return None
    state = quest_state_pure(player_data, quest_id)
    if state["completed"] or state["progress"] >= 3:
        return None
    if not state["started"]:
        return "commission"
    performed = _performed(player_data)
    if performed != PROOFS[:len(performed)]:
        return "inconsistent"
    return _PHASE_BY_STATE.get((state["progress"], len(performed)), "inconsistent")


def _started_opening(player_data, quest_id, quest_data):
    return (
        quest_id in quest_data and quest_state_pure(player_data, quest_id)["started"]
        and grand_tree_phase_pure(player_data, quest_id) is not None
    )


def _blocker(player_data, kind, reason, **fields):
    stage = max(1, quest_state_pure(player_data, QUEST_ID)["progress"])
    return dict(kind=kind, stage=stage, source=STAGE_SOURCES.get(stage, STAGE_SOURCES[1]),
                reason=reason, **fields)


def _valid_count(inventory, name):
    count = inventory.get(name, 0)
    return type(count) is int and count >= 0


def _inventory_blockers(player_data, phase):
    inventory = player_data.get("inventory", {}) or {}
    touched = dict((*_DELTAS.get(phase, ()), *_MATERIALS.get(phase, ())))
    invalid = tuple(
        _blocker(player_data, "opening_inventory", f"Invalid {name} quantity", item_name=name)
        for name in touched if not _valid_count(inventory, name)
    )
    if invalid:
        return invalid
    return tuple(
        _blocker(player_data, "missing_item", f"Missing {name} x{amount - inventory.get(name, 0)}",
                 item_name=name, shortfall=amount - inventory.get(name, 0))
        for name, amount in _MATERIALS.get(phase, ()) if inventory.get(name, 0) < amount
    )


def grand_tree_opening_blockers_pure(player_data, quest_id, quest_data, eligibility_reasons):
    if not _started_opening(player_data, quest_id, quest_data):
        return ()
    phase = grand_tree_phase_pure(player_data, quest_id)
    if phase == "inconsistent":
        return (_blocker(player_data, "opening_state", "The Grand Tree opening has inconsistent progress."),)
    eligibility = tuple(
        _blocker(player_data, "opening_requirement", f"Requires {reason}")
        for reason in eligibility_reasons(player_data, quest_id, quest_data)
    )
    return (*eligibility, *_inventory_blockers(player_data, phase))


def grand_tree_review_ready_pure(player_data, quest_id, quest_data, blockers, eligibility_reasons):
    if not _started_opening(player_data, quest_id, quest_data):
        return False
    if grand_tree_opening_blockers_pure(player_data, quest_id, quest_data, eligibility_reasons):
        return False
    stage = max(1, quest_state_pure(player_data, quest_id)["progress"])
    return all(
        row.get("kind") == "required_action" and row.get("stage") == stage
        and row.get("action_id") in _STAGE_PROOFS[stage]
        for row in blockers
    )


def _change_item(inventory, name, delta):
    if not _valid_count(inventory, name) or inventory.get(name, 0) + delta < 0:
        return False
    inventory[name] = inventory.get(name, 0) + delta
    return True


def _apply_inventory(data, phase):
    return all(_change_item(data["inventory"], name, delta) for name, delta in _DELTAS.get(phase, ()))


def apply_grand_tree_review_pure(player_data, quest_id, quest_data, blockers, eligibility_reasons):
    """Publish one whole bundle only after every expected new proof succeeds."""
    if not _started_opening(player_data, quest_id, quest_data):
        return None
    if not grand_tree_review_ready_pure(player_data, quest_id, quest_data, blockers, eligibility_reasons):
        return player_data, False
    phase = grand_tree_phase_pure(player_data, quest_id)
    data = _copy_player_data_with_nested(player_data)
    # Re-evaluate eligibility immediately before the first provisional mutation.
    if eligibility_reasons(player_data, quest_id, quest_data):
        return player_data, False
    if not _apply_inventory(data, phase):
        return player_data, False
    for event in REVIEW_BUNDLES[phase]:
        proof = PROOFS[EVENTS.index(event)]
        if quest_action_proof_completed_pure(data, proof):
            return player_data, False
        if not record_runtime_quest_action_proofs_pure(data, *event):
            return player_data, False
        if not quest_action_proof_completed_pure(data, proof):
            return player_data, False
    state = quest_state_pure(data, quest_id)
    state.update(progress=_NEXT_PROGRESS[phase], completed=False)
    data["quests"][quest_id] = state
    return data, True


def grand_tree_journal_rows_pure(player_data, quest_id, rows):
    """Only proof prefixes mark opening rows performed; text belongs to the catalog."""
    if quest_id != QUEST_ID:
        return rows
    performed = _performed(player_data)
    return tuple(
        dict(row, completed=all(proof in performed for proof in PROOFS[:2 if row["stage"] == 1 else 5]))
        if row["stage"] in (1, 2) else row
        for row in rows
    )
