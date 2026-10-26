"""Atomic complete review transactions, derived only from the ordered proofs."""

from collections.abc import Mapping

from ...data.quest.toktz_opening import (
    QUEST_ID, TABLET, GUIDE, SERVICES, PROOFS, INTERACTIONS, COMPLETED_LINES,
    PENDING_LINES, RECOVERY, INVALID, RECOVERY_INSTRUCTION, RECOVERY_MESSAGE, LEGACY_LINE,
)
from ..logic_pure_state import _copy_player_data_with_nested, quest_state_pure
from ..quest_action_proofs import (
    quest_action_proof_completed_pure, record_runtime_quest_action_proofs_pure,
)


def _opening_prefix_pure(player_data):
    flags = tuple(quest_action_proof_completed_pure(player_data, proof) for proof in PROOFS)
    count = sum(flags)
    return count if flags == (True,) * count + (False,) * (len(PROOFS) - count) else None


def _valid_quantity_pure(quantity):
    return isinstance(quantity, int) and not isinstance(quantity, bool) and quantity >= 0


def toktz_opening_phase_pure(player_data, quest_id):
    if quest_id != QUEST_ID:
        return None
    state = quest_state_pure(player_data, quest_id)
    if not state["started"] or state["completed"] or state["progress"] not in (0, 1):
        return None
    prefix = _opening_prefix_pure(player_data)
    if prefix is None or prefix == len(PROOFS):
        return INVALID
    tablet = player_data.get("inventory", {}).get(TABLET, 0)
    if prefix == 2 and _valid_quantity_pure(tablet) and tablet == 0:
        return RECOVERY
    return SERVICES[prefix]


def toktz_opening_review_ready_pure(player_data, quest_id, blockers):
    phase = toktz_opening_phase_pure(player_data, quest_id)
    return phase in (*SERVICES, RECOVERY) and all(
        blocker.get("kind") == "required_action" and blocker.get("action_id") == PROOFS[-1]
        for blocker in blockers
    )


def toktz_opening_next_event_pure(player_data, quest_id):
    phase = toktz_opening_phase_pure(player_data, quest_id)
    if phase == RECOVERY:
        return dict(INTERACTIONS[1], recovery=True, completed=True)
    if phase not in SERVICES:
        return None
    event = dict(INTERACTIONS[SERVICES.index(phase)], completed=True)
    if phase == SERVICES[0]:
        event["npc_id"] = event.pop("npc_ids")[0]
    return event


def _opening_event_valid_pure(player_data, quest_id, event):
    expected = toktz_opening_next_event_pure(player_data, quest_id)
    if not expected or not isinstance(event, Mapping) or event.get("completed") is not True:
        return False
    if expected["service_id"] == SERVICES[0]:
        if event.get("npc_id") not in INTERACTIONS[0]["npc_ids"]:
            return False
        expected = dict(expected, npc_id=event["npc_id"])
    return all(event.get(key) == value for key, value in expected.items())


def _grant_unique_opening_item_pure(inventory, item_name):
    quantity = inventory.get(item_name, 0)
    if not _valid_quantity_pure(quantity):
        return False
    if quantity == 0:
        inventory[item_name] = 1
    return True


def _opening_inventory_postconditions_pure(candidate, before, phase):
    item = {SERVICES[1]: TABLET, RECOVERY: TABLET, SERVICES[4]: GUIDE}.get(phase)
    inventory = candidate["inventory"]
    if phase == SERVICES[2]:
        quantity = inventory.get(TABLET, 0)
        return _valid_quantity_pure(quantity) and quantity > 0
    if item is None:
        return True
    quantity = before.get(item, 0)
    if not _valid_quantity_pure(quantity):
        return False
    if not _grant_unique_opening_item_pure(inventory, item):
        return False
    expected = dict(before)
    expected[item] = quantity if quantity > 0 else 1
    return inventory == expected and type(inventory.get(item)) is int


def apply_toktz_opening_review_pure(player_data, quest_id, blockers, event):
    if not toktz_opening_review_ready_pure(player_data, quest_id, blockers):
        return player_data, False
    if not _opening_event_valid_pure(player_data, quest_id, event):
        return player_data, False
    phase = toktz_opening_phase_pure(player_data, quest_id)
    candidate = _copy_player_data_with_nested(player_data)
    if not _opening_inventory_postconditions_pure(candidate, player_data.get("inventory", {}), phase):
        return player_data, False
    if phase == RECOVERY:
        return candidate, True
    index = SERVICES.index(phase)
    if not record_runtime_quest_action_proofs_pure(candidate, "quest_service", phase):
        return player_data, False
    if _opening_prefix_pure(candidate) != index + 1:
        return player_data, False
    candidate["quests"][quest_id] = dict(
        quest_state_pure(candidate, quest_id), started=True, completed=False,
        progress=2 if index == 4 else 1,
    )
    return candidate, True


def toktz_opening_journal_row_pure(player_data, quest_id, row):
    if quest_id != QUEST_ID or row["stage"] != 1:
        return row
    prefix = _opening_prefix_pure(player_data)
    phase = toktz_opening_phase_pure(player_data, quest_id)
    if prefix is None or phase == INVALID or (not row["current"] and prefix != len(PROOFS)):
        return dict(row, completed=False, current=False, lines=(LEGACY_LINE,))
    lines = COMPLETED_LINES[:prefix]
    if prefix < len(PROOFS):
        pending = RECOVERY_INSTRUCTION if phase == RECOVERY else PENDING_LINES[prefix]
        lines += (pending,)
    return dict(row, lines=lines)


def toktz_opening_message_pure(player_before, quest_id):
    phase = toktz_opening_phase_pure(player_before, quest_id)
    if phase == RECOVERY:
        return RECOVERY_MESSAGE
    return COMPLETED_LINES[SERVICES.index(phase)] if phase in SERVICES else ""
