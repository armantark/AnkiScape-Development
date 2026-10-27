"""Atomic, proof-driven Watchtower opening deeds and observational journal rows."""

from collections.abc import Mapping

from ...data.quest.watchtower_opening import (
    QUEST_ID, COMMISSION_PROOF, SEARCH_PROOF, PRESENTATION_PROOF,
    OPENING_PROOFS, PHASE_EVENTS, PHASE_PROOFS, CLUE_QUANTITY,
    PENDING_JOURNAL, COMMISSION_JOURNAL, SEARCH_JOURNAL,
    COMPLETED_JOURNAL, LEGACY_JOURNAL,
)
from ..logic_pure_state import _copy_player_data_with_nested, quest_state_pure
from ..quest_action_proofs import (
    quest_action_proof_completed_pure, record_runtime_quest_action_proofs_pure,
)


def _unfinished_opening(player_data, quest_id):
    state = quest_state_pure(player_data, quest_id)
    return quest_id == QUEST_ID and not state["completed"] and state["progress"] in (0, 1)


def watchtower_phase_pure(player_data, quest_id):
    if not _unfinished_opening(player_data, quest_id):
        return None
    for phase, proof in PHASE_PROOFS.items():
        if not quest_action_proof_completed_pure(player_data, proof):
            return phase
    return None


def watchtower_requirement_pure(player_data, quest_id, requirement):
    if requirement.get("stage") != 1 or not _unfinished_opening(player_data, quest_id):
        return requirement
    adjusted = dict(requirement)
    if quest_action_proof_completed_pure(player_data, COMMISSION_PROOF):
        adjusted["required_skills"] = tuple(
            skill for skill in requirement.get("required_skills", ())
            if not (skill.get("skill_id") == "agility" and skill.get("level") == 18)
        )
    inventory = dict(requirement.get("required_inventory", {}))
    if quest_action_proof_completed_pure(player_data, PRESENTATION_PROOF):
        inventory.pop("Fingernails", None)
    elif watchtower_phase_pure(player_data, quest_id) == "present":
        inventory["Fingernails"] = CLUE_QUANTITY
    adjusted["required_inventory"] = inventory
    return adjusted


def _valid_count(count):
    return isinstance(count, int) and not isinstance(count, bool) and count >= 0


def _clue_count(player_data):
    inventory = player_data.get("inventory", {})
    return inventory.get("Fingernails", 0) if isinstance(inventory, Mapping) else None


def _phase_access_valid(player_data, phase):
    if phase == "commission":
        agility = player_data.get("agility_level", 1)
        return _valid_count(agility) and agility >= 18
    count = _clue_count(player_data)
    return _valid_count(count) and (phase != "present" or count >= CLUE_QUANTITY)


def watchtower_review_ready_pure(player_data, quest_id, blockers):
    phase = watchtower_phase_pure(player_data, quest_id)
    if phase is None or not _phase_access_valid(player_data, phase):
        return False
    return all(
        blocker.get("kind") == "required_action" and blocker.get("action_id") in OPENING_PROOFS
        for blocker in blockers
    )


def _apply_phase_mutations(data, phase):
    if phase != "commission":
        count = _clue_count(data)
        if not _valid_count(count):
            return False
        delta = -CLUE_QUANTITY if phase == "present" else CLUE_QUANTITY
        if count + delta < 0:
            return False
        data["inventory"]["Fingernails"] = count + delta
    state = quest_state_pure(data, QUEST_ID)
    state.update(started=True, progress=1, completed=False)
    data["quests"][QUEST_ID] = state
    return True


def apply_watchtower_review_pure(player_data, quest_id, blockers, *, requested_phase=None):
    phase = watchtower_phase_pure(player_data, quest_id)
    if requested_phase is not None and requested_phase != phase:
        return player_data, "unchanged"
    if not watchtower_review_ready_pure(player_data, quest_id, blockers):
        return player_data, "unchanged"
    candidate = _copy_player_data_with_nested(player_data)
    if not _apply_phase_mutations(candidate, phase):
        return player_data, "unchanged"
    emitted = record_runtime_quest_action_proofs_pure(candidate, *PHASE_EVENTS[phase])
    if not emitted or not quest_action_proof_completed_pure(candidate, PHASE_PROOFS[phase]):
        return player_data, "unchanged"
    return candidate, "completed" if phase == "present" else "pending"


def _opening_journal_lines(player_data):
    if not quest_action_proof_completed_pure(player_data, COMMISSION_PROOF):
        return PENDING_JOURNAL
    if not quest_action_proof_completed_pure(player_data, SEARCH_PROOF):
        return COMMISSION_JOURNAL + PENDING_JOURNAL[1:]
    return COMMISSION_JOURNAL + (SEARCH_JOURNAL, PENDING_JOURNAL[2])


def watchtower_journal_row_pure(player_data, quest_id, row):
    if quest_id != QUEST_ID or row["stage"] != 1:
        return row
    performed = all(quest_action_proof_completed_pure(player_data, proof) for proof in OPENING_PROOFS)
    if performed:
        return dict(row, lines=COMPLETED_JOURNAL)
    state = quest_state_pure(player_data, quest_id)
    if state["completed"] or state["progress"] > 1:
        return dict(row, lines=LEGACY_JOURNAL, completed=False, current=False)
    return dict(row, lines=_opening_journal_lines(player_data), completed=False)
