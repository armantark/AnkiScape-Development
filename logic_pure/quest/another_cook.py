"""Two real transactions inside Another Cook's unfinished first stage."""

from ...data.quest.another_cook import (
    QUEST_ID, OPENING_STAGE, ADVANCE, COOKING_REQUIREMENT, ELIGIBLE_COCKTAILS,
    DIRTY_BLAST_BASE_XP, STATIC_JOURNAL, COMMISSION_JOURNAL, PREPARED_LINE,
)
from ...data.quest_action_proof_data import ANOTHER_COOK_COMMISSION_PROOF, ANOTHER_COOK_DIRTY_BLAST_PROOF
from ..logic_pure_state import _copy_player_data_with_nested, quest_state_pure
from ..quest_action_proofs import quest_action_proof_completed_pure, record_runtime_quest_action_proofs_pure


def another_cook_phase_pure(player_data, quest_id):
    if quest_id != QUEST_ID:
        return None
    state = quest_state_pure(player_data, quest_id)
    if state['completed'] or state['progress'] not in (0, 1):
        return None
    if quest_action_proof_completed_pure(player_data, ANOTHER_COOK_DIRTY_BLAST_PROOF):
        return 'prepared'
    if quest_action_proof_completed_pure(player_data, ANOTHER_COOK_COMMISSION_PROOF):
        return 'prepare'
    return 'commission'


def another_cook_requirement_pure(player_data, quest_id, requirement):
    if quest_id != QUEST_ID or requirement.get('stage') != OPENING_STAGE:
        return requirement
    if another_cook_phase_pure(player_data, quest_id) == 'prepare':
        return dict(requirement, required_inventory={'Ashes': 1},
                    required_inventory_options=(tuple((name, 1) for name in ELIGIBLE_COCKTAILS),))
    return requirement


def _available_quantity(inventory, name):
    value = inventory.get(name, 0)
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _selected_cocktail(player_data):
    inventory = player_data.get('inventory', {}) or {}
    for name in ELIGIBLE_COCKTAILS:
        quantity = inventory.get(name, 0)
        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 0:
            return None
    return next((name for name in ELIGIBLE_COCKTAILS if _available_quantity(inventory, name)), None)


def another_cook_review_ready_pure(player_data, quest_id, blockers):
    phase = another_cook_phase_pure(player_data, quest_id)
    if phase not in ('commission', 'prepare'):
        return False
    if player_data.get('cooking_level', 1) < COOKING_REQUIREMENT:
        return False
    if not quest_state_pure(player_data, 'cooks_assistant')['completed']:
        return False
    if any(b.get('kind') != 'required_action' or b.get('action_id') != ANOTHER_COOK_DIRTY_BLAST_PROOF for b in blockers):
        return False
    if phase == 'commission':
        return True
    return _available_quantity(player_data.get('inventory', {}), 'Ashes') and _selected_cocktail(player_data) is not None


def _commit_commission_pure(data, quest_id):
    inventory = data['inventory']
    inventory['Coins'] = inventory.get('Coins', 0) + ADVANCE
    data.setdefault('quests', {})[quest_id] = dict(started=True, progress=1, completed=False)
    record_runtime_quest_action_proofs_pure(data, 'quest_service', 'another_cook_commission')
    return data, 'commissioned'


def _prepare_dirty_blast_pure(data):
    inventory = data['inventory']
    cocktail = _selected_cocktail(data)
    inventory['Ashes'] -= 1
    inventory[cocktail] -= 1
    inventory['Dirty blast'] = inventory.get('Dirty blast', 0) + 1
    data['cooking_exp'] = data.get('cooking_exp', 0) + DIRTY_BLAST_BASE_XP
    record_runtime_quest_action_proofs_pure(data, 'quest_service', 'another_cook_dirty_blast')
    return data, 'prepared'


def apply_another_cook_review_pure(player_data, quest_id, blockers):
    if not another_cook_review_ready_pure(player_data, quest_id, blockers):
        return player_data, 'unchanged'
    data = _copy_player_data_with_nested(player_data)
    if another_cook_phase_pure(player_data, quest_id) == 'commission':
        return _commit_commission_pure(data, quest_id)
    return _prepare_dirty_blast_pure(data)


def another_cook_journal_row_pure(player_data, quest_id, row):
    if quest_id != QUEST_ID or row['stage'] != OPENING_STAGE:
        return row
    prepared = quest_action_proof_completed_pure(player_data, ANOTHER_COOK_DIRTY_BLAST_PROOF)
    commissioned = quest_action_proof_completed_pure(player_data, ANOTHER_COOK_COMMISSION_PROOF)
    lines = STATIC_JOURNAL
    state = quest_state_pure(player_data, quest_id)
    if commissioned:
        lines = COMMISSION_JOURNAL[:2] + ((PREPARED_LINE,) if prepared else COMMISSION_JOURNAL[2:])
    elif state['completed'] or state['progress'] >= 2:
        lines = ('These opening deeds have not been recorded.',)
    return dict(row, lines=lines, completed=prepared)


def another_cook_progress_message_pure(phase):
    if phase == 'commission':
        return ("The Cook asked for 1 Eye of newt, 1 Greenman's ale, 1 Rotten tomato and 1 Dirty blast. "
                "+100 Coins for ingredients; keep the change. Add Ashes to a Fruit blast; Blurberry's premade drink will not work.")
    if phase == 'prepare':
        return '+1 Dirty blast: added Ashes to a Fruit blast.'
    return ''
