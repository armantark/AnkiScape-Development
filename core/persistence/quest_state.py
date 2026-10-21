"""Normalize quest progress and supply its personal greeting assignment."""

from typing import Any, Dict

from ...data.quest_data import DEFAULT_QUEST_TARGET, default_quest_states
from ...logic.cold_war_greeting_logic import ensure_cold_war_greeting_pure  # noqa: F401 (re-export)


def _migrate_quest_state(data: Dict[str, Any]) -> None:
    quests = data.get("quests")
    clean_quests = default_quest_states()
    if isinstance(quests, dict):
        for quest_id, default_state in clean_quests.items():
            raw_state = quests.get(quest_id)
            if not isinstance(raw_state, dict):
                continue
            state = dict(default_state)
            state["started"] = bool(raw_state.get("started", state["started"]))
            state["completed"] = bool(raw_state.get("completed", state["completed"]))
            try:
                progress = int(raw_state.get("progress", state["progress"]))
            except (TypeError, ValueError):
                progress = int(state["progress"])
            state["progress"] = max(0, progress)
            if state["completed"] and state["progress"] < 1:
                state["progress"] = 1
            clean_quests[quest_id] = state
    data["quests"] = clean_quests
    try:
        data["quest_points"] = max(0, int(data.get("quest_points", 0)))
    except (TypeError, ValueError):
        data["quest_points"] = 0
    current_quest = data.get("current_quest")
    if not isinstance(current_quest, str) or current_quest not in clean_quests:
        current_quest = DEFAULT_QUEST_TARGET
    data["current_quest"] = current_quest
