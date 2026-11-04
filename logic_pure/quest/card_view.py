"""The Quests tab card's stage line and journal rows."""

from ..logic_pure_quest import quest_current_stage_blocker_reasons_pure, quest_current_stage_blockers_pure
from .journal import quest_journal_rows_pure
from .supply_steps import supply_step_pure


def quest_supply_step_text_pure(player_data, quest_id, quest_data):
    """The line for the supply step the quest's next review runs, or an empty string."""
    if not (quest_data.get(quest_id) or {}).get("supply_recipes"):
        return ""
    blockers = quest_current_stage_blockers_pure(player_data, quest_id, quest_data)
    recipe = supply_step_pure(player_data, quest_id, quest_data, blockers)
    return f"Next: {recipe['step'][:1].upper()}{recipe['step'][1:]}" if recipe else ""


def quest_card_blocker_text_pure(player_data, quest_id, quest_data):
    """The card's blocked line, empty when nothing blocks the stage or the quest supplies it."""
    if quest_supply_step_text_pure(player_data, quest_id, quest_data):
        return ""
    reasons = quest_current_stage_blocker_reasons_pure(player_data, quest_id, quest_data)
    shown = [str(reason) for reason in reasons[:3]]
    if len(reasons) > 3:
        shown.append(f"+{len(reasons) - 3} more")
    return "Blocked: " + ", ".join(shown) if shown else ""


def quest_journal_view_rows_pure(player_data, quest_id, quest_data):
    """The journal rows, with the next supply step under the current stage."""
    rows = quest_journal_rows_pure(player_data, quest_id, quest_data)
    text = quest_supply_step_text_pure(player_data, quest_id, quest_data)
    return tuple(dict(row, lines=(*row["lines"], text)) if text and row["current"] else row for row in rows)
