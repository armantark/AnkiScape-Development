"""Quest defaults and ordered save migration, including service custody."""

from typing import Any, Dict

from ..logic.cold_war_greeting_logic import ensure_cold_war_greeting_pure

from ..data.quest_data import DEFAULT_QUEST_TARGET, default_quest_states
from ..data.quest.oronwen_repair_data import PENDING_KEY
from ..logic_pure.logic_pure_quest import default_quest_combat_active_encounters_pure
from ..logic_pure.logic_pure_state import sanitize_quest_combat_active_encounters_pure
from ..logic_pure.quest_action_proofs import sanitize_quest_action_proofs_pure
from ..logic_pure.quest.oronwen import migrate_oronwen_repair_state


def default_quest_side_state():
    return {
        "quests": default_quest_states(),
        "quest_points": 0,
        "quest_combat_encounters": {},
        "quest_combat_encounter_counts": {},
        "quest_combat_active_encounters": default_quest_combat_active_encounters_pure(),
        "quest_action_proofs": [],
        PENDING_KEY: False,
        "quest_route_states": {},
    }


def migrate_quest_data(data, loaded_config_version, current_config_version, retired_proofs):
    _migrate_quest_state(data)
    data["cold_war_greeting"] = ensure_cold_war_greeting_pure(data)
    _migrate_quest_stage_side_state(data, loaded_config_version)
    _migrate_quest_action_proofs(data, loaded_config_version, current_config_version, retired_proofs)
    migrate_oronwen_repair_state(data, loaded_config_version)


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


def _migrate_quest_flag_collection(data: Dict[str, Any], key: str) -> None:
    raw_collection = data.get(key)
    clean: Dict[str, list[str]] = {}
    if isinstance(raw_collection, dict):
        for quest_id, raw_flags in raw_collection.items():
            if not isinstance(quest_id, str):
                continue
            if isinstance(raw_flags, str):
                flags = [raw_flags]
            elif isinstance(raw_flags, dict):
                flags = [flag for flag, enabled in raw_flags.items() if isinstance(flag, str) and bool(enabled)]
            elif isinstance(raw_flags, (list, tuple, set)):
                flags = [flag for flag in raw_flags if isinstance(flag, str)]
            else:
                flags = []
            if flags:
                clean[quest_id] = sorted(set(flags))
    data[key] = clean


def _migrate_quest_combat_encounter_counts(data: Dict[str, Any]) -> None:
    raw_collection = data.get("quest_combat_encounter_counts")
    clean: Dict[str, Dict[str, int]] = {}
    if isinstance(raw_collection, dict):
        for quest_id, raw_counts in raw_collection.items():
            if not isinstance(quest_id, str) or not isinstance(raw_counts, dict):
                continue
            quest_counts: Dict[str, int] = {}
            for encounter_id, raw_count in raw_counts.items():
                if not isinstance(encounter_id, str):
                    continue
                try:
                    count = int(raw_count)
                except (TypeError, ValueError):
                    continue
                if count > 0:
                    quest_counts[encounter_id] = count
            if quest_counts:
                clean[quest_id] = quest_counts
    data["quest_combat_encounter_counts"] = clean


def _migrate_quest_stage_side_state(data: Dict[str, Any], version: int) -> None:
    if version < 124:
        data.pop("quest_combat_config", None)
    _migrate_quest_flag_collection(data, "quest_combat_encounters")
    _migrate_quest_combat_encounter_counts(data)
    data["quest_combat_active_encounters"] = sanitize_quest_combat_active_encounters_pure(
        data.get("quest_combat_active_encounters")
    )
    data.pop("quest_stage_actions", None)
    _migrate_quest_flag_collection(data, "quest_route_states")


def _migrate_quest_action_proofs(data, loaded_config_version, current_config_version, retired_proofs):
    proofs = sanitize_quest_action_proofs_pure(data.get("quest_action_proofs")) if loaded_config_version >= 122 else []
    if loaded_config_version < current_config_version:
        proofs = [proof for proof in proofs if proof not in retired_proofs]
    data["quest_action_proofs"] = proofs
