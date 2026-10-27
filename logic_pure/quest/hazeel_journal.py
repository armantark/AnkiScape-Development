"""Read-only Hazeel opening history from earned deeds and current settings."""

from ...data.quest.hazeel_opening import (
    QUEST_ID, ACTIONS, PROOFS, SHARED, BRANCH_DEEDS, CORRECT_VALVE_ACTIONS,
    ENDPOINTS, ENDPOINT_SENTENCES, VALVE_CONTEXT, VALVE_KEY,
    POISON_OWNED, MARK_OWNED, OWNED_SENTENCES,
)
from ..logic_pure_state import quest_state_pure
from ..quest_action_proofs import quest_action_proof_completed_pure
from .hazeel import hazeel_opening_branch_pure, sanitize_hazeel_valve_states_pure


def hazeel_completed_sentence_pure(player_data, action_id):
    outcome = {"cult_acceptance": POISON_OWNED, "clivet_mark": MARK_OWNED}.get(action_id)
    if outcome and quest_action_proof_completed_pure(player_data, outcome):
        return OWNED_SENTENCES[action_id]
    return ACTIONS[action_id].completed


def _earned(player_data, key):
    return quest_action_proof_completed_pure(player_data, PROOFS[key])


def _deed_line(player_data, key):
    action = ACTIONS[key]
    earned = _earned(player_data, key)
    if action.direction:
        states = sanitize_hazeel_valve_states_pure(player_data.get(VALVE_KEY))
        earned = earned and states.get(str(action.target)) == action.direction
    if earned:
        return f"<s>Done: {hazeel_completed_sentence_pure(player_data, key)}</s>"
    return f"Pending: {action.pending}"


def _branch_lines(player_data, branch):
    lines = [_deed_line(player_data, key) for key in BRANCH_DEEDS[branch][2:]]
    if branch == "carnillean" and _earned(player_data, "carnillean_refusal"):
        lines.append("Clivet departs after refusal.")
    lines.extend(_deed_line(player_data, key) for key in CORRECT_VALVE_ACTIONS)
    return lines


def _opening_lines(player_data, branch):
    lines = [_deed_line(player_data, key) for key in SHARED]
    if branch in BRANCH_DEEDS:
        lines.extend(_branch_lines(player_data, branch))
    else:
        for route, label in (("carnillean", "Carnillean route, if chosen"), ("hazeel", "Hazeel's cult route, if chosen")):
            lines.append(label)
            lines.extend(_branch_lines(player_data, route))
    lines.extend(VALVE_CONTEXT)
    return lines


def hazeel_journal_row_pure(player_data, quest_id, row):
    if quest_id != QUEST_ID or row["stage"] != 1:
        return row
    state = quest_state_pure(player_data, QUEST_ID)
    branch = hazeel_opening_branch_pure(player_data)
    endpoint = branch in ENDPOINTS and _earned(player_data, ENDPOINTS[branch])
    if (state["progress"] > 1 or state["completed"]) and not endpoint:
        lines = ["I have already progressed beyond this opening."]
    else:
        lines = _opening_lines(player_data, branch)
        if endpoint and _valves_currently_correct(player_data):
            lines.append(ENDPOINT_SENTENCES[branch])
    return dict(row, lines=tuple(lines), completed=False,
                current=state["started"] and not state["completed"] and state["progress"] <= 1)


def _valves_currently_correct(player_data):
    return all(_deed_line(player_data, key).startswith("<s>") for key in CORRECT_VALVE_ACTIONS)


def hazeel_opening_announcement_pure(player_data, action):
    if not _earned(player_data, action.action_id):
        return ()
    lines = [hazeel_completed_sentence_pure(player_data, action.action_id)]
    branch = hazeel_opening_branch_pure(player_data)
    if action.direction and branch in ENDPOINTS and _earned(player_data, ENDPOINTS[branch]) and _valves_currently_correct(player_data):
        lines.append(ENDPOINT_SENTENCES[branch])
    return tuple(lines)
