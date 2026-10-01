from collections.abc import Mapping
from typing import Any


def _quest_action_proofs_for_key(
    player_data: Mapping[str, Any],
    quest_id: str,
    quest_data: Mapping[str, Any],
    requirement_key: str,
) -> tuple[str, ...]:
    proofs = set(player_data.get("quest_action_proofs", ()))
    return tuple(
        dict.fromkeys(
            action_id
            for requirement in quest_data[quest_id].get("stage_requirements", ())
            for action_id in requirement.get(requirement_key, ())
            if action_id in proofs
        )
    )


def quest_action_proofs_for_quest(
    player_data: Mapping[str, Any],
    quest_id: str,
    quest_data: Mapping[str, Any],
) -> tuple[str, ...]:
    return _quest_action_proofs_for_key(player_data, quest_id, quest_data, "auto_actions")


def quest_required_action_proofs_for_quest(
    player_data: Mapping[str, Any],
    quest_id: str,
    quest_data: Mapping[str, Any],
) -> tuple[str, ...]:
    return _quest_action_proofs_for_key(player_data, quest_id, quest_data, "required_actions")
