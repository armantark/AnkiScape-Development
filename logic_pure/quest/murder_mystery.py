"""The first evidence deed commits only after both ordinary inventory grants."""

from ...data.quest.murder_mystery import (
    QUEST_ID, OPENING_ACTION, OPENING_OUTPUTS, LEGACY_OPENING_JOURNAL,
)
from ..logic_pure_state import _copy_player_data_with_nested, quest_state_pure
from ..quest_action_proofs import (
    quest_action_proof_completed_pure, record_quest_stage_action_proofs_pure,
)


def _grant_opening_item_pure(inventory, item_name, quantity):
    count = inventory.get(item_name, 0)
    if not isinstance(count, int) or isinstance(count, bool) or count < 0:
        return False
    inventory[item_name] = count + quantity
    return True


def apply_murder_mystery_opening_items_pure(data):
    state = quest_state_pure(data, QUEST_ID)
    if not state["started"] or state["completed"] or state["progress"] not in (0, 1):
        return False
    candidate = _copy_player_data_with_nested(data)
    for item_name, quantity in OPENING_OUTPUTS:
        if not _grant_opening_item_pure(candidate["inventory"], item_name, quantity):
            return False
    record_quest_stage_action_proofs_pure(candidate, QUEST_ID, (OPENING_ACTION,))
    data.update(candidate)
    return True


def murder_mystery_journal_row_pure(player_data, quest_id, row):
    if quest_id != QUEST_ID or row["stage"] != 1:
        return row
    if row["current"] or quest_action_proof_completed_pure(player_data, OPENING_ACTION):
        return row
    if row["completed"]:
        return dict(row, completed=False, current=False, lines=LEGACY_OPENING_JOURNAL)
    return row
