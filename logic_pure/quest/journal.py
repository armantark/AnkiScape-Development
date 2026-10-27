"""Read-only quest journal projections, independent of progression controllers."""

from ..logic_pure_state import quest_state_pure, _positive_int
from .review_services import quest_review_journal_row_pure
from .elemental_workshop import opening_journal_rows_pure
from .hazeel_journal import hazeel_journal_row_pure
from .enakhra import enakhra_opening_journal_row_pure
from .toktz_opening import toktz_opening_journal_row_pure
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
        row = quest_review_journal_row_pure(player_data, quest_id, row)
        row = hazeel_journal_row_pure(player_data, quest_id, row)
        row = toktz_opening_journal_row_pure(player_data, quest_id, row)
        rows.append(enakhra_opening_journal_row_pure(player_data, quest_id, row))
    rows = opening_journal_rows_pure(player_data, quest_id, tuple(rows))
    return witchs_house_journal_rows_pure(player_data, quest_id, rows)
