"""Witch's House deeds, local recovery, observational journal and save repair."""

from ...data.quest.witchs_house import (
    QUEST_ID, DIARY, MAGNET, BACKROOM_KEY, BALL, LEATHER_GLOVES,
    TAKE_DIARY, READ_DIARY, TAKE_GLOVES, PASS_GATE, TAKE_MAGNET, TAKE_KEY,
    TAKE_BALL, INSULATING_GLOVES, EXPERIMENTS, RESUME_KEY,
    LEGACY_COMPLETED_KEY, RESUME_STAGES,
)
from ..logic_pure_state import _copy_player_data_with_nested, _positive_int, quest_state_pure
from ..quest_action_proofs import (
    quest_action_proof_completed_pure, record_quest_stage_action_proofs_pure,
)
from .progress_state import _quest_combat_completed_count


def witchs_house_worn_insulation_pure(player_data):
    return (player_data.get("equipment", {}) or {}).get("hands") in INSULATING_GLOVES


def _unfinished_experiments(player_data):
    return tuple(
        (encounter_id, name) for encounter_id, name in EXPERIMENTS
        if _quest_combat_completed_count(player_data, QUEST_ID, encounter_id, {"quantity": 1}) < 1
    )


def _suppress_acquisition(row, action):
    return dict(row, produced_inventory={}, auto_actions=tuple(
        deed for deed in row.get("auto_actions", ()) if deed != action
    ))


def _conditional_stage_row(player_data, row):
    stage = row.get("stage")
    inventory = player_data.get("inventory", {}) or {}
    acquisitions = {3: (DIARY, TAKE_DIARY), 5: (LEATHER_GLOVES, TAKE_GLOVES),
                    7: (MAGNET, TAKE_MAGNET), 10: (BACKROOM_KEY, TAKE_KEY),
                    13: (BALL, TAKE_BALL)}
    if stage not in acquisitions:
        return dict(row)
    item, action = acquisitions[stage]
    held = _positive_int(inventory.get(item, 0), 0) > 0
    worn_leather = stage == 5 and (player_data.get("equipment", {}) or {}).get("hands") == LEATHER_GLOVES
    return _suppress_acquisition(row, action) if held or worn_leather else dict(row)


def witchs_house_stage_rows_pure(player_data, quest_id, rows):
    if quest_id != QUEST_ID:
        return rows
    return tuple(_conditional_stage_row(player_data, row) for row in rows)


def witchs_house_extra_blockers_pure(player_data, quest_id, requirement):
    if quest_id != QUEST_ID:
        return ()
    stage = requirement.get("stage")
    source = requirement.get("source", "")
    if stage == 6 and not witchs_house_worn_insulation_pure(player_data):
        return ({"stage": stage, "kind": "missing_tool", "source": source,
                 "reason": "Wear insulating gloves to pass the electric gate"},)
    if stage != 13:
        return ()
    return tuple(
        {"stage": stage, "kind": "required_action", "source": source,
         "action_id": encounter_id, "display_name": name,
         "reason": "Defeat all four Witch's experiment forms before taking the Ball"}
        for encounter_id, name in _unfinished_experiments(player_data)
    )


def _only_missing_item(blockers, item):
    return bool(blockers) and all(
        (blocker.get("kind") == "missing_item" and blocker.get("item_name") == item)
        or (blocker.get("kind") == "missing_tool" and blocker.get("tool_name") == item)
        for blocker in blockers
    )


def witchs_house_service_phase_pure(player_data, quest_id, blockers):
    if quest_id != QUEST_ID:
        return None
    state = quest_state_pure(player_data, quest_id)
    if not state["started"] or state["completed"]:
        return None
    if (state["progress"] == 11 and quest_action_proof_completed_pure(player_data, READ_DIARY)
            and _only_missing_item(blockers, BACKROOM_KEY)):
        return "recover_key"
    if (state["progress"] == 14 and not _unfinished_experiments(player_data)
            and _only_missing_item(blockers, BALL)):
        return "recover_ball"
    return None


def witchs_house_service_ready_pure(player_data, quest_id, blockers):
    return witchs_house_service_phase_pure(player_data, quest_id, blockers) is not None


def apply_witchs_house_service_pure(player_data, quest_id, blockers):
    phase = witchs_house_service_phase_pure(player_data, quest_id, blockers)
    if phase is None:
        return player_data, "unchanged"
    item, action = (BACKROOM_KEY, TAKE_KEY) if phase == "recover_key" else (BALL, TAKE_BALL)
    data = _copy_player_data_with_nested(player_data)
    data["inventory"][item] = _positive_int(data["inventory"].get(item, 0), 0) + 1
    record_quest_stage_action_proofs_pure(data, quest_id, (action,))
    return data, "deed_only"


def _valid_resume_stage(data, state):
    resume = data.get(RESUME_KEY, 0)
    return (type(resume) is int and resume in range(8, 15) and state["started"]
            and not state["completed"] and state["progress"] in range(3, 7))


def witchs_house_next_progress_pure(data, quest_id, current_stage, total_stages):
    if quest_id == QUEST_ID and current_stage == 6 and _valid_resume_stage(data, quest_state_pure(data, quest_id)):
        resume = data[RESUME_KEY]
        data[RESUME_KEY] = 0
        return resume
    return min(total_stages, current_stage + 1)


def _map_old_progress(data, state):
    data[RESUME_KEY] = 0
    data[LEGACY_COMPLETED_KEY] = state["completed"]
    if state["started"] and not state["completed"] and state["progress"] in RESUME_STAGES:
        data[RESUME_KEY] = RESUME_STAGES[state["progress"]]
        data["quests"][QUEST_ID]["progress"] = 3


def _sanitize_witchs_house_scalars(data, state):
    if not _valid_resume_stage(data, state):
        data[RESUME_KEY] = 0
    data[LEGACY_COMPLETED_KEY] = state["completed"] and data.get(LEGACY_COMPLETED_KEY) is True


def migrate_witchs_house_state(data, loaded_config_version):
    state = quest_state_pure(data, QUEST_ID)
    if loaded_config_version < 126:
        _map_old_progress(data, state)
    else:
        _sanitize_witchs_house_scalars(data, state)


def witchs_house_journal_row_pure(player_data, quest_id, row):
    if quest_id != QUEST_ID:
        return row
    row = dict(row)
    corrections = {5: (READ_DIARY, "Read the Witch's diary before searching the fountain."),
                   7: (PASS_GATE, "Wear insulating gloves to pass the electric gate before searching the cupboard.")}
    proof, text = corrections.get(row["stage"], (None, None))
    if proof and not quest_action_proof_completed_pure(player_data, proof):
        row.update(lines=(text,), completed=False)
    if row["stage"] == 13 and _unfinished_experiments(player_data):
        row.update(lines=("Defeat all four forms of the Witch's experiment before taking the Ball.",), completed=False)
    if row["current"] and _valid_resume_stage(player_data, quest_state_pure(player_data, quest_id)):
        row["lines"] = tuple(row["lines"]) + (
            "Your earlier quest progress is preserved. Complete the diary and worn-glove steps, then resume it.",
        )
    return row


def witchs_house_journal_rows_pure(player_data, quest_id, rows):
    if quest_id != QUEST_ID:
        return rows
    if player_data.get(LEGACY_COMPLETED_KEY) and quest_state_pure(player_data, quest_id)["completed"]:
        return rows[-1:]
    return tuple(witchs_house_journal_row_pure(player_data, quest_id, row) for row in rows)
