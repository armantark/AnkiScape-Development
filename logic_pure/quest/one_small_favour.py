"""Ordered first-journal reviews and exact, recoverable hatchet custody."""

from collections.abc import Mapping

from ...data.quest.one_small_favour import (
    QUEST_ID, BLUNT_HATCHET, FORESTER_GRANT_QUANTITY, BRIAN_TAKE_QUANTITY,
    OPENING_DEEDS, OPENING_PROOFS, OPENING_SOURCE, REPLACEMENT_EVENT_ID,
)
from ...logic.summoning_logic import sanitize_summoning_state_pure
from ...logic.pace.summoning_clock import sanitize_cargo_events
from ..logic_pure_state import (
    quest_state_pure, _copy_player_data_with_nested, _positive_int,
    _sanitize_combat_grave_state, _sanitize_death_office_state,
)
from ..quest_action_proofs import (
    quest_action_proof_completed_pure, record_runtime_quest_action_proofs_pure,
)

ORDER_REASON = 'Complete the One Small Favour opening contacts in order.'
FORESTER_REASON = 'The Jungle Forester cannot give you another Blunt hatchet while you already have one.'
EXCESS_REASON = 'Keep exactly one Blunt hatchet before giving it to Brian.'
RECOVER_REASON = 'Recover your Blunt hatchet before giving it to Brian.'
BRIAN_REASON = 'Brian needs the Jungle Forester’s Blunt hatchet.'


def opening_applies_pure(player_data, quest_id):
    if quest_id != QUEST_ID:
        return False
    state = quest_state_pure(player_data, quest_id)
    return state['started'] and not state['completed'] and state['progress'] in (0, 1)


def _opening_prefix(player_data):
    completed = tuple(quest_action_proof_completed_pure(player_data, proof) for proof in OPENING_PROOFS)
    first_missing = next((index for index, done in enumerate(completed) if not done), len(completed))
    return first_missing, not any(completed[first_missing:])


def _hatchets(items):
    return _positive_int(items.get(BLUNT_HATCHET, 0), 0) if isinstance(items, Mapping) else 0


def opening_hatchet_custody_pure(player_data):
    """Return canonical and total custody; carried/loadout projections are excluded."""
    canonical = _hatchets(player_data.get('inventory'))
    equipment = player_data.get('equipment', {})
    worn = sum(name == BLUNT_HATCHET for name in equipment.values()) if isinstance(equipment, Mapping) else 0
    grave = _sanitize_combat_grave_state(player_data.get('combat_grave'))
    office = _sanitize_death_office_state(player_data.get('death_office'))
    stored = grave.get('items', []).count(BLUNT_HATCHET) + office.get('items', []).count(BLUNT_HATCHET)
    summoning = sanitize_summoning_state_pure(player_data.get('summoning_state'))
    follower = summoning['active_follower']
    familiar = _hatchets(follower.get('storage')) if follower.get('kind') == 'familiar' else 0
    cargo = sum(_hatchets(event['items']) for event in sanitize_cargo_events(summoning['cargo_events']))
    return canonical, canonical + worn + stored + familiar + cargo


def opening_phase_pure(player_data, quest_id=QUEST_ID):
    if not opening_applies_pure(player_data, quest_id):
        return None
    index, contiguous = _opening_prefix(player_data)
    if not contiguous or index == len(OPENING_DEEDS):
        return None
    if index == 3 and opening_hatchet_custody_pure(player_data)[1] == 0:
        return REPLACEMENT_EVENT_ID
    return OPENING_DEEDS[index]['event_id']


def _custody_refusal(player_data, index, event_id):
    canonical, total = opening_hatchet_custody_pure(player_data)
    if index == 1 and total:
        return FORESTER_REASON
    if index != 3:
        return ''
    if event_id == REPLACEMENT_EVENT_ID:
        return RECOVER_REASON if total else ''
    if total > 1:
        return EXCESS_REASON
    if total and canonical != 1:
        return RECOVER_REASON
    return '' if canonical == 1 else BRIAN_REASON


def opening_blockers_pure(player_data, quest_id=QUEST_ID, event_id=None):
    if not opening_applies_pure(player_data, quest_id):
        return ()
    index, contiguous = _opening_prefix(player_data)
    if index == len(OPENING_PROOFS):
        return ()
    phase = opening_phase_pure(player_data, quest_id)
    selected = phase if event_id is None else event_id
    # Explicit Brian without input must refuse that handoff, not perform recovery.
    brian_without_input = index == 3 and selected == OPENING_DEEDS[3]['event_id'] and not opening_hatchet_custody_pure(player_data)[1]
    reason = _custody_refusal(player_data, index, selected)
    if not contiguous or (selected != phase and not brian_without_input):
        reason = ORDER_REASON
    if not reason:
        return ()
    return ({'stage': 1, 'kind': 'required_action', 'action_id': OPENING_PROOFS[index],
             'reason': reason, 'source': OPENING_SOURCE},)


def opening_review_ready_pure(player_data, quest_id=QUEST_ID, blockers=(), event_id=None):
    if opening_phase_pure(player_data, quest_id) is None:
        return False
    if opening_blockers_pure(player_data, quest_id, event_id):
        return False
    return all(blocker.get('kind') == 'required_action' and blocker.get('action_id') in OPENING_PROOFS
               for blocker in blockers)


def _apply_opening_deed_pure(player_data, event_id):
    """Commit a copied transaction only when its exact proof was newly recorded."""
    data = _copy_player_data_with_nested(player_data)
    inventory = data['inventory']
    if event_id in (OPENING_DEEDS[1]['event_id'], REPLACEMENT_EVENT_ID):
        inventory[BLUNT_HATCHET] = FORESTER_GRANT_QUANTITY
    elif event_id == OPENING_DEEDS[3]['event_id']:
        inventory[BLUNT_HATCHET] -= BRIAN_TAKE_QUANTITY
    if event_id != REPLACEMENT_EVENT_ID:
        if not record_runtime_quest_action_proofs_pure(data, 'quest_service', event_id):
            return player_data, 'unchanged'
    data['quests'][QUEST_ID]['progress'] = 1
    return data, 'ready' if event_id == OPENING_DEEDS[-1]['event_id'] else 'partial'


def apply_opening_review_pure(player_data, quest_id=QUEST_ID, blockers=(), event_id=None):
    if not opening_review_ready_pure(player_data, quest_id, blockers, event_id):
        return player_data, 'unchanged'
    return _apply_opening_deed_pure(player_data, event_id or opening_phase_pure(player_data, quest_id))
