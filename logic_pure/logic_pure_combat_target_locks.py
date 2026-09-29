"""Quest access requirements for combat targets."""

from typing import Mapping


def _combat_quest_locked_reasons(player_data, enemy):
    quest_gate = str(enemy.get("quest_gate", enemy.get("required_quest", "")) or "")
    if not quest_gate:
        return tuple()
    quests = player_data.get("quests", {}) or {}
    quest_state = quests.get(quest_gate, {}) if isinstance(quests, Mapping) else {}
    gate_state = str(enemy.get("quest_gate_state", "completed") or "completed")
    if isinstance(quest_state, Mapping):
        quest_accessible = bool(quest_state.get("completed"))
        if gate_state == "started":
            quest_accessible = quest_accessible or bool(quest_state.get("started"))
    else:
        quest_accessible = bool(quest_state)
    if not quest_accessible:
        verb = "Start" if gate_state == "started" else "Complete"
        return (
            str(
                enemy.get(
                    "quest_gate_label",
                    f"{verb} {quest_gate.replace('_', ' ').title()}",
                )
            ),
        )
    return tuple()
