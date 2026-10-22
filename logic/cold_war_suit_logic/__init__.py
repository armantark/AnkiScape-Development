"""One-time Bank suit repair for saves already past Cold War's suit stage."""

from ...data.quest.cold_war import (
    COLD_WAR_SUIT_ACTION,
    COLD_WAR_SUIT_BACKFILL_KEY,
    COLD_WAR_SUIT_NAME,
)
from ...logic_pure.logic_pure_quest import (
    _positive_int,
    quest_action_proof_completed_pure,
    quest_state_pure,
)


def migrate_cold_war_suit_pure(data):
    checked = data.get(COLD_WAR_SUIT_BACKFILL_KEY) is True
    data[COLD_WAR_SUIT_BACKFILL_KEY] = checked
    state = quest_state_pure(data, "cold_war")
    past_stage = state["completed"] or (state["started"] and state["progress"] >= 3)
    if checked or not past_stage:
        return
    data[COLD_WAR_SUIT_BACKFILL_KEY] = True
    if quest_action_proof_completed_pure(data, COLD_WAR_SUIT_ACTION):
        return
    inventory = data.get("inventory")
    inventory = inventory if isinstance(inventory, dict) else {}
    if _positive_int(inventory.get(COLD_WAR_SUIT_NAME), 0) > 0:
        return
    data["inventory"] = dict(inventory)
    data["inventory"][COLD_WAR_SUIT_NAME] = 1
