"""The first evidence deed commits only after both ordinary inventory grants."""

from copy import deepcopy

from ...data.quest.murder_mystery_silver import SILVER_SEARCHES
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
    if quest_id == QUEST_ID and row["stage"] == 2:
        return _silver_journal_row_pure(player_data, row)
    if quest_id != QUEST_ID or row["stage"] != 1:
        return row
    if row["current"] or quest_action_proof_completed_pure(player_data, OPENING_ACTION):
        return row
    if row["completed"]:
        return dict(row, completed=False, current=False, lines=LEGACY_OPENING_JOURNAL)
    return row


# PLACEHOLDER(quests.murder_mystery.silver_search_yield): Replace with original
# server transaction or independently dated transaction quantity/cost evidence.
SILVER_SEARCH_YIELD = 1
INVALID_CUSTODY = 'The bedroom evidence inventory is invalid. No items or quest progress changed.'
NO_SEARCH = 'No bedroom search is pending.'
INVALID_BARREL = 'That barrel is not a Murder Mystery bedroom search.'
INACTIVE = 'Murder Mystery must be active to search this barrel.'
COMPLETED = 'Murder Mystery is complete; this barrel cannot supply more evidence.'


def _silver_family(row):
    return row['name'], row['dusted_name'], row['print_name']


def _silver_custody_pure(player_data, row):
    # PLACEHOLDER(quests.murder_mystery.silver_search_custody_recovery): Replace
    # with original predicates or independent dated custody/repeat/timer/loss evidence.
    # Inventory is also the Bank store; carried_inventory is only its view.
    inventory = player_data.get('inventory', {})
    equipment = player_data.get('equipment', {})
    if not isinstance(inventory, dict) or not isinstance(equipment, dict):
        return False, INVALID_CUSTODY
    counts = [inventory.get(name, 0) for name in _silver_family(row)]
    if any(type(count) is not int or count < 0 for count in counts):
        return False, INVALID_CUSTODY
    held = any(counts) or any(name in equipment.values() for name in _silver_family(row))
    return held, ''


def _silver_barrel_row(barrel_id):
    if type(barrel_id) is not int:
        return None
    return next((row for row in SILVER_SEARCHES if row['barrel_id'] == barrel_id), None)


def _silver_search_refusal_pure(player_data, row):
    if row is None:
        return INVALID_BARREL
    state = quest_state_pure(player_data, QUEST_ID)
    if state['completed']:
        return COMPLETED
    if not state['started']:
        return INACTIVE
    held, reason = _silver_custody_pure(player_data, row)
    if reason:
        return reason
    if held and quest_action_proof_completed_pure(player_data, row['proof_id']):
        return NO_SEARCH
    return ''


def search_murder_mystery_barrel_pure(player_data, barrel_id):
    row = _silver_barrel_row(barrel_id)
    reason = _silver_search_refusal_pure(player_data, row)
    if reason:
        return player_data, False, reason
    candidate = deepcopy(player_data)
    held, _ = _silver_custody_pure(candidate, row)
    if not held:
        inventory = candidate.setdefault('inventory', {})
        if not _grant_opening_item_pure(inventory, row['name'], SILVER_SEARCH_YIELD):
            return player_data, False, INVALID_CUSTODY
    if not quest_action_proof_completed_pure(candidate, row['proof_id']):
        record_quest_stage_action_proofs_pure(candidate, QUEST_ID, (row['proof_id'],))
    return candidate, True, ''


def murder_mystery_silver_review_phase_pure(player_data, quest_id, quest_data):
    if quest_id != QUEST_ID or quest_id not in quest_data:
        return False
    state = quest_state_pure(player_data, QUEST_ID)
    return state['started'] and not state['completed'] and state['progress'] >= 2


def next_murder_mystery_silver_search_pure(player_data):
    for row in SILVER_SEARCHES:
        if not quest_action_proof_completed_pure(player_data, row['proof_id']):
            return row
    for row in SILVER_SEARCHES:
        held, reason = _silver_custody_pure(player_data, row)
        if reason or not held:
            return row
    return None


def murder_mystery_silver_refusal_reason_pure(
    player_data, quest_id, quest_data, eligibility_reasons,
):
    state = quest_state_pure(player_data, QUEST_ID)
    if state['completed']:
        return COMPLETED
    if not murder_mystery_silver_review_phase_pure(player_data, quest_id, quest_data):
        return INACTIVE
    row = next_murder_mystery_silver_search_pure(player_data)
    if row is None:
        return NO_SEARCH
    reason = _silver_search_refusal_pure(player_data, row)
    if reason:
        return reason
    reasons = eligibility_reasons(player_data, quest_id, quest_data)
    return str(reasons[0]) if reasons else ''


def murder_mystery_silver_review_ready_pure(
    player_data, quest_id, quest_data, eligibility_reasons,
):
    return not murder_mystery_silver_refusal_reason_pure(
        player_data, quest_id, quest_data, eligibility_reasons,
    )


def apply_murder_mystery_silver_review_pure(
    player_data, quest_id, quest_data, eligibility_reasons,
):
    if not murder_mystery_silver_review_ready_pure(player_data, quest_id, quest_data, eligibility_reasons):
        return player_data, False
    row = next_murder_mystery_silver_search_pure(player_data)
    candidate, ok, _ = search_murder_mystery_barrel_pure(player_data, row['barrel_id'])
    return candidate, ok


def murder_mystery_silver_action_pure(player_data):
    """Capture the authored summary before the transaction changes custody/proof."""
    row = next_murder_mystery_silver_search_pure(player_data)
    if row is None:
        return ''
    held, _ = _silver_custody_pure(player_data, row)
    prefix = f"Searched {row['owner']}'s barrel"
    if held:
        return prefix + '; your existing evidence was kept.'
    verb = 'recovered' if quest_action_proof_completed_pure(player_data, row['proof_id']) else 'collected'
    return f"{prefix} and {verb} one {row['name']}."


def _silver_journal_line_pure(player_data, row, completed):
    base = f"Search {row['owner']}'s bedroom barrel for the {row['name']}."
    if not quest_action_proof_completed_pure(player_data, row['proof_id']):
        return base + (' (No recorded search)' if completed else ' (Pending)')
    line = f'<s>{base}</s> (Searched)'
    held, reason = _silver_custody_pure(player_data, row)
    if not completed and not held and not reason:
        line += ' Replacement pending: search the barrel again.'
    return line


def _silver_journal_row_pure(player_data, row):
    completed = quest_state_pure(player_data, QUEST_ID)['completed']
    lines = tuple(row['lines'][:2]) + tuple(
        _silver_journal_line_pure(player_data, search, completed) for search in SILVER_SEARCHES
    )
    return dict(row, completed=False, lines=lines)
