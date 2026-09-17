"""Pure helpers for the global, forward-only quest action proof store."""

from collections.abc import Iterable, Mapping
from typing import Any

from ..data.quest_action_proof_data import QUEST_ACTION_PROOF_RULES


def sanitize_quest_action_proofs_pure(raw_proofs: Any) -> list[str]:
    if isinstance(raw_proofs, str):
        raw_proofs = (raw_proofs,)
    if isinstance(raw_proofs, Mapping) or not isinstance(raw_proofs, Iterable):
        return []
    return sorted(
        {
            proof
            for proof in raw_proofs
            if isinstance(proof, str) and proof
        }
    )


def quest_action_proof_completed_pure(player_data: Mapping[str, Any], proof_id: str) -> bool:
    return bool(proof_id) and proof_id in sanitize_quest_action_proofs_pure(
        player_data.get("quest_action_proofs", ())
    )


def quest_action_proofs_after_event_pure(
    raw_proofs: Any,
    event_type: str,
    event_id: str,
) -> list[str]:
    proofs = set(sanitize_quest_action_proofs_pure(raw_proofs))
    rule = QUEST_ACTION_PROOF_RULES.get((str(event_type), str(event_id)))
    if rule is None:
        return sorted(proofs)
    required_proofs, emitted_proofs = rule
    if set(required_proofs) <= proofs:
        proofs.update(emitted_proofs)
    return sorted(proofs)


def quest_action_proofs_for_reachable_events_pure(
    raw_proofs: Any,
    reachable_events: Iterable[tuple[str, str]],
) -> list[str]:
    proofs = sanitize_quest_action_proofs_pure(raw_proofs)
    events = tuple(reachable_events)
    while True:
        updated = proofs
        for event in events:
            updated = quest_action_proofs_after_event_pure(updated, *event)
        if updated == proofs:
            return proofs
        proofs = updated


def record_runtime_quest_action_proofs_pure(
    player_data: dict[str, Any],
    event_type: str,
    event_id: str,
) -> bool:
    current = sanitize_quest_action_proofs_pure(player_data.get("quest_action_proofs", ()))
    updated = quest_action_proofs_after_event_pure(current, event_type, event_id)
    if updated == current:
        return False
    player_data["quest_action_proofs"] = updated
    return True


def retract_shop_event_quest_action_proofs_pure(
    player_data: dict[str, Any],
    event: Mapping[str, Any],
) -> bool:
    current = sanitize_quest_action_proofs_pure(player_data.get("quest_action_proofs", ()))
    event_type = f"shop_{event.get('type', '')}"
    event_id = str(event.get("row_id") or event.get("service_id") or "")
    _required_proofs, emitted_proofs = QUEST_ACTION_PROOF_RULES.get(
        (event_type, event_id),
        ((), ()),
    )
    events = player_data.get("shop_events", ())
    rolled_back = {str(event.get("event_id", ""))}
    rolled_back.update(
        str(retained.get("rolled_back_event_id", ""))
        for retained in events
        if retained.get("type") == "rollback"
    )
    retained_events = (
        (
            f"shop_{retained.get('type', '')}",
            str(retained.get("row_id") or retained.get("service_id") or ""),
        )
        for retained in events
        if str(retained.get("event_id", "")) not in rolled_back
    )
    supported = quest_action_proofs_for_reachable_events_pure(
        set(current) - set(emitted_proofs), retained_events
    )
    # Rollback must not backfill proofs from older retained shop events.
    updated = sorted(set(current) & set(supported))
    if updated == current:
        return False
    player_data["quest_action_proofs"] = updated
    return True


def quest_action_proofs_after_stage_actions_pure(
    raw_proofs: Any,
    quest_id: str,
    action_ids: Iterable[str],
) -> list[str]:
    proofs = sanitize_quest_action_proofs_pure(raw_proofs)
    for action_id in action_ids:
        if not isinstance(action_id, str) or not action_id:
            continue
        proofs = sorted(set(proofs) | {action_id})
        proofs = quest_action_proofs_after_event_pure(
            proofs,
            "quest_stage",
            f"{quest_id}:{action_id}",
        )
    return proofs


def record_quest_stage_action_proofs_pure(
    player_data: dict[str, Any],
    quest_id: str,
    action_ids: Iterable[str],
) -> bool:
    current = sanitize_quest_action_proofs_pure(player_data.get("quest_action_proofs", ()))
    updated = quest_action_proofs_after_stage_actions_pure(current, quest_id, action_ids)
    if updated == current:
        return False
    player_data["quest_action_proofs"] = updated
    return True
