"""Reachability adapters for quest-action proof sources."""

from collections.abc import Iterable, Mapping
from typing import Any

from ankiscape.data.quest_action_proof_data import QUEST_ACTION_PROOF_AUDIT_SOURCES
from ankiscape.logic_pure.quest_action_proofs import quest_action_proofs_for_reachable_events_pure


def reachable_quest_action_proof_events(
    actions: Iterable[Mapping[str, Any]],
    unresolved_actions: Iterable[Mapping[str, Any]],
    seed_sources: Mapping[str, set[str]],
) -> set[tuple[str, str]]:
    unresolved_ids = {str(action["id"]) for action in unresolved_actions}
    resolved_action_ids = {
        str(action["id"])
        for action in actions
        if str(action["id"]) not in unresolved_ids
    }
    return {
        event
        for event, (source_id, item_name) in QUEST_ACTION_PROOF_AUDIT_SOURCES.items()
        if source_id in resolved_action_ids
        or (item_name and source_id in seed_sources.get(item_name, ()))
    }


def advance_reachable_quest_action_proofs(
    raw_proofs: Iterable[str],
    actions: Iterable[Mapping[str, Any]],
    unresolved_actions: Iterable[Mapping[str, Any]],
    seed_sources: Mapping[str, set[str]],
) -> set[str]:
    events = reachable_quest_action_proof_events(
        actions,
        unresolved_actions,
        seed_sources,
    )
    return set(quest_action_proofs_for_reachable_events_pure(raw_proofs, events))


def close_actions_with_quest_proofs(
    close_actions,
    actions: Iterable[Mapping[str, Any]],
    seed_sources: Mapping[str, set[str]],
    active_action_ids: set[str],
    raw_proofs: Iterable[str],
):
    reachable_items, route, unresolved = close_actions(
        actions,
        seed_sources,
        active_action_ids=active_action_ids,
    )
    proofs = advance_reachable_quest_action_proofs(
        raw_proofs,
        actions,
        unresolved,
        seed_sources,
    )
    return reachable_items, route, proofs


def merged_scenario_action_proofs(scenario_results) -> set[str]:
    return set().union(*(result[5] for result in scenario_results))
