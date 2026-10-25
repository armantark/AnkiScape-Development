"""Atomic chapel search/read and honest projections of the performed opening.

The owners supply their shared eligibility evaluator to avoid a dependency back
into the quest/combat orchestration graph.
"""

from ...data.quest.elemental_workshop_iii import (
    QUEST_ID, RAGGED_BOOK, ACQUIRE_PROOF, READ_PROOF,
    ACQUIRE_EVENT, READ_EVENT, ELIGIBILITY_SOURCE,
)
from ..logic_pure_state import _copy_player_data_with_nested, quest_state_pure
from ..quest_action_proofs import (
    quest_action_proof_completed_pure, record_runtime_quest_action_proofs_pure,
)


def opening_applies_pure(player_data, quest_id, quest_data):
    if quest_id != QUEST_ID or quest_id not in quest_data:
        return False
    state = quest_state_pure(player_data, quest_id)
    return (
        state["started"] and not state["completed"]
        and max(1, state["progress"]) == 1
    )


def opening_blockers_pure(player_data, quest_id, quest_data, eligibility_reasons):
    if not opening_applies_pure(player_data, quest_id, quest_data):
        return ()
    return tuple(
        {"kind": "opening_requirement", "stage": 1,
         "source": ELIGIBILITY_SOURCE, "reason": f"Requires {reason}"}
        for reason in eligibility_reasons(player_data, quest_id, quest_data)
    )


def opening_review_ready_pure(player_data, quest_id, quest_data, blockers, eligibility_reasons):
    if not opening_applies_pure(player_data, quest_id, quest_data):
        return False
    if quest_action_proof_completed_pure(player_data, READ_PROOF):
        return False
    if opening_blockers_pure(player_data, quest_id, quest_data, eligibility_reasons):
        return False
    return all(
        blocker.get("kind") == "required_action" and blocker.get("action_id") == READ_PROOF
        for blocker in blockers
    )


def search_chapel_bookcase_pure(player_data):
    """Unified inventory is custody; an existing copy is retained at any quantity."""
    data = _copy_player_data_with_nested(player_data)
    if data["inventory"].get(RAGGED_BOOK, 0) <= 0:
        data["inventory"][RAGGED_BOOK] = 1
        record_runtime_quest_action_proofs_pure(data, *ACQUIRE_EVENT)
    return data, True


def read_ragged_book_pure(player_data, item_name):
    """An exact-item operation; possession alone never records the read deed."""
    inventory = player_data.get("inventory", {}) or {}
    if item_name != RAGGED_BOOK or inventory.get(RAGGED_BOOK, 0) <= 0:
        return player_data, False
    data = _copy_player_data_with_nested(player_data)
    record_runtime_quest_action_proofs_pure(data, *READ_EVENT)
    return data, True


def apply_opening_review_pure(player_data, quest_id, quest_data, blockers, eligibility_reasons):
    if not opening_applies_pure(player_data, quest_id, quest_data):
        return player_data, True
    if quest_action_proof_completed_pure(player_data, READ_PROOF):
        return player_data, not opening_blockers_pure(player_data, quest_id, quest_data, eligibility_reasons)
    if not opening_review_ready_pure(player_data, quest_id, quest_data, blockers, eligibility_reasons):
        return player_data, False
    data, ok = search_chapel_bookcase_pure(player_data)
    if not ok:
        return player_data, False
    data, ok = read_ragged_book_pure(data, RAGGED_BOOK)
    return (data, True) if ok else (player_data, False)


def _opening_journal_row(player_data, row):
    read = quest_action_proof_completed_pure(player_data, READ_PROOF)
    if read:
        acquired = quest_action_proof_completed_pure(player_data, ACQUIRE_PROOF)
        line = (
            "I searched the chapel bookcase, obtained the Ragged book and read it."
            if acquired else "I read my Ragged book."
        )
        return dict(row, lines=(line,), completed=True, current=False)
    state = quest_state_pure(player_data, QUEST_ID)
    if state["progress"] > 1 or state["completed"]:
        return dict(row, lines=("The chapel search and Ragged book reading have no recorded deed.",),
                    completed=False, current=False)
    return dict(row, completed=False)


def opening_journal_rows_pure(player_data, quest_id, rows):
    if quest_id != QUEST_ID:
        return rows
    result = []
    for row in rows:
        if row["stage"] == 1:
            row = _opening_journal_row(player_data, row)
        elif row["stage"] == 2:
            row = dict(row, completed=False)
        result.append(row)
    return tuple(result)
