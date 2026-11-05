"""Read-only quest journal projections, independent of progression controllers."""

from ...data.quest.stage_overrides.members.later.animal_magnetism import (
    COMPLETED_OPENING, OPENING_ACTIONS, PENDING_OPENING,
)
from ..logic_pure_state import quest_state_pure, _positive_int
from ..quest_action_proofs import quest_action_proof_completed_pure
from .the_slug_menace import slug_menace_journal_row_pure
from .another_cook import another_cook_journal_row_pure
from .review_services import quest_review_journal_row_pure
from .grand_tree import grand_tree_journal_rows_pure
from .elemental_workshop import opening_journal_rows_pure
from .hazeel_journal import hazeel_journal_row_pure
from .enakhra import enakhra_opening_journal_row_pure
from .toktz_opening import toktz_opening_journal_row_pure
from .elder_kiln_journal import elder_kiln_journal_row_pure
from .witchs_house import witchs_house_journal_rows_pure


def quest_current_stage_pure(player_data, quest_id, quest_data):
    quest = quest_data.get(quest_id)
    if not quest:
        return 0
    state = quest_state_pure(player_data, quest_id)
    if not state["started"]:
        return 0
    total_stages = _positive_int(quest.get("stages", 1), 1)
    if state["completed"]:
        return total_stages
    return min(total_stages, max(1, state["progress"]))


def _animal_magnetism_opening_rows(player_data, progress, rows):
    if not rows or rows[0]["stage"] != 1:
        return tuple(rows)
    if progress <= 1:
        opening = dict(stage=1, lines=(PENDING_OPENING,), completed=False, current=True)
    elif all(quest_action_proof_completed_pure(player_data, action) for action in OPENING_ACTIONS):
        opening = dict(stage=1, lines=(COMPLETED_OPENING,), completed=True, current=False)
    else:
        return tuple(rows[1:])
    return (opening, *rows[1:])


def quest_journal_rows_pure(player_data, quest_id, quest_data):
    quest = quest_data.get(quest_id)
    if not quest:
        return tuple()
    state = quest_state_pure(player_data, quest_id)
    progress = state["progress"]
    if state["started"] and progress <= 0:
        progress = 1
    if state["completed"]:
        progress = _positive_int(quest.get("stages", progress), progress)
    journal_stages = quest.get("journal_stages", {}) or {}
    rows = []
    for stage in sorted(journal_stages):
        if stage > progress:
            continue
        row = {
            "stage": stage,
            "lines": journal_stages.get(stage, ()),
            "completed": state["completed"] or stage < progress,
            "current": (not state["completed"] and stage == progress),
        }
        row = another_cook_journal_row_pure(player_data, quest_id, row)
        row = quest_review_journal_row_pure(player_data, quest_id, row)
        row = slug_menace_journal_row_pure(player_data, quest_id, row)
        row = hazeel_journal_row_pure(player_data, quest_id, row)
        row = toktz_opening_journal_row_pure(player_data, quest_id, row)
        row = elder_kiln_journal_row_pure(player_data, quest_id, row)
        rows.append(enakhra_opening_journal_row_pure(player_data, quest_id, row))
    if quest_id == "animal_magnetism":
        return _animal_magnetism_opening_rows(player_data, progress, rows)
    rows = opening_journal_rows_pure(player_data, quest_id, tuple(rows))
    rows = grand_tree_journal_rows_pure(player_data, quest_id, rows)
    return witchs_house_journal_rows_pure(player_data, quest_id, rows)
