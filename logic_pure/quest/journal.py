"""Read-only quest journal projections, independent of progression controllers."""

from ...logic.cold_war_greeting_logic import cold_war_journal_lines_pure
from ..logic_pure_state import quest_state_pure, _positive_int
from .murder_mystery import murder_mystery_journal_row_pure
from .elemental_workshop import opening_journal_rows_pure
from .enakhra import enakhra_opening_journal_row_pure


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
            "lines": cold_war_journal_lines_pure(player_data, quest_id, stage, journal_stages.get(stage, ())),
            "completed": state["completed"] or stage < progress,
            "current": (not state["completed"] and stage == progress),
        }
        row = murder_mystery_journal_row_pure(player_data, quest_id, row)
        rows.append(enakhra_opening_journal_row_pure(player_data, quest_id, row))
    return opening_journal_rows_pure(player_data, quest_id, tuple(rows))
