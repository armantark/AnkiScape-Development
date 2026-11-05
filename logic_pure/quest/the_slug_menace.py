"""Atomic, invocation-local Witchaven investigation ending at the mayor scan."""

from ...data.quest.stage_overrides.members.later.the_slug_menace import (
    QUEST_ID, OPENING_ACTIONS, LEGACY_OPENING_JOURNAL,
)
from ...logic.inventory_pure import clamp_carried_view_to_bank
from ..logic_pure_state import _copy_player_data_with_nested, quest_state_pure
from ..quest_action_proofs import (
    record_quest_stage_action_proofs_pure, quest_action_proof_completed_pure,
)


def _clamp_opening_overlays_pure(candidate):
    candidate['carried_inventory'] = {
        target: clamped for target, view in candidate.get('carried_inventory', {}).items()
        if (clamped := clamp_carried_view_to_bank(view, candidate['inventory']))
    }


def _apply_commorb_custody_pure(candidate):
    inventory = candidate['inventory']
    original, upgraded = (inventory.get(name, 0) for name in ('Commorb', 'Commorb v2'))
    if any(type(count) is not int or count < 0 for count in (original, upgraded)):
        return False
    if not upgraded:
        if original:
            inventory['Commorb'] = original - 1
        inventory['Commorb v2'] = 1
    _clamp_opening_overlays_pure(candidate)
    return True


def _perform_commission_pure(candidate, performed):
    """Receive Tiffy's mission/password and perform the conditional orb exchange."""
    if performed or not _apply_commorb_custody_pure(candidate):
        return False
    record_quest_stage_action_proofs_pure(candidate, QUEST_ID, (OPENING_ACTIONS[0],))
    performed.append(OPENING_ACTIONS[0])
    return True


def _perform_referral_pure(candidate, performed):
    """Finish O'Niall's referral naming Hobb, Maledict and Holgart."""
    if tuple(performed) != OPENING_ACTIONS[:1]:
        return False
    record_quest_stage_action_proofs_pure(candidate, QUEST_ID, (OPENING_ACTIONS[1],))
    performed.append(OPENING_ACTIONS[1])
    return True


def _perform_mayor_conversation_pure(candidate, performed):
    """Discuss the Saradomin shrine and receive Savant's mayor-scan request."""
    if tuple(performed) != OPENING_ACTIONS[:2]:
        return False
    record_quest_stage_action_proofs_pure(candidate, QUEST_ID, (OPENING_ACTIONS[2],))
    performed.append(OPENING_ACTIONS[2])
    return True


def _perform_mayor_scan_pure(candidate, performed):
    """Perform Commorb v2's Scan on Mayor Hobb; return Savant's reading."""
    upgraded = candidate['inventory'].get('Commorb v2', 0)
    if tuple(performed) != OPENING_ACTIONS[:3] or type(upgraded) is not int or upgraded <= 0:
        return False
    reading = 'two life forms'
    record_quest_stage_action_proofs_pure(candidate, QUEST_ID, (OPENING_ACTIONS[3],))
    performed.append(OPENING_ACTIONS[3])
    return reading


def apply_slug_menace_opening_pure(data):
    state = quest_state_pure(data, QUEST_ID)
    if not state['started'] or state['completed'] or state['progress'] not in (0, 1):
        return False
    candidate = _copy_player_data_with_nested(data)
    performed = []
    for deed in (_perform_commission_pure, _perform_referral_pure,
                 _perform_mayor_conversation_pure, _perform_mayor_scan_pure):
        if not deed(candidate, performed):
            return False
    if tuple(performed) != OPENING_ACTIONS:
        return False
    data.update(candidate)
    return True


def slug_menace_journal_row_pure(player_data, quest_id, row):
    if quest_id != QUEST_ID or row['stage'] != 1:
        return row
    if row['current'] or quest_action_proof_completed_pure(player_data, OPENING_ACTIONS[3]):
        return row
    if row['completed']:
        return dict(row, completed=False, current=False, lines=LEGACY_OPENING_JOURNAL)
    return row
