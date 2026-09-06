"""Pure matching for diary deeds that depend on one live action result."""

from __future__ import annotations

import base64
import functools
import json
from collections.abc import Mapping, Sequence
from typing import Any


DIARY_EVENT_COUNTER_PREFIX = "achievement_diaries.event_counts."
_ALLOWED_EVENT_TYPES = frozenset({
    "action",
    "agility_result",
    "bank_run",
    "castle_wars_review",
    "construction_command",
    "court_cases_command",
    "farming_result",
    "great_orb_project_teleport",
    "managing_miscellania_command",
    "shades_of_mortton_review",
    "slayer_command",
    "summoning_command",
    "temple_trekking_command",
})
_ALLOWED_MATCH_KEYS = frozenset({
    "any", "eq", "gte", "in", "state_contains", "state_eq",
})
_ALLOWED_EVENT_FIELDS = frozenset({
    "action_id",
    "active_prayer_selection",
    "altar_id",
    "combat_result.killed",
    "completed_lap",
    "deposited_non_coin",
    "duty",
    "familiar_id",
    "hammer",
    "kills",
    "kind",
    "patch_id",
    "crop_id",
    "reason",
    "skill_id",
    "success",
    "target_id",
    "type",
})
_MISSING = object()


def encode_diary_event_rule_pure(rule: Mapping[str, Any]) -> str:
    payload = json.dumps(rule, sort_keys=True, separators=(",", ":")).encode()
    token = base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")
    return DIARY_EVENT_COUNTER_PREFIX + token


def decode_diary_event_rule_pure(key: str) -> dict[str, Any] | None:
    if not key.startswith(DIARY_EVENT_COUNTER_PREFIX):
        return None
    token = key[len(DIARY_EVENT_COUNTER_PREFIX):]
    try:
        payload = base64.urlsafe_b64decode(token + "=" * (-len(token) % 4))
        rule = json.loads(payload.decode())
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return rule if token and isinstance(rule, dict) else None


def _valid_field_path(path: Any) -> bool:
    return isinstance(path, str) and bool(path) and (
        path in _ALLOWED_EVENT_FIELDS or path.startswith("outputs.")
    )


def _validate_event_clause(name: str, values: Any) -> str:
    if not isinstance(values, Mapping) or not values:
        return f"event matcher {name!r} clause is not a non-empty mapping"
    if any(not _valid_field_path(path) for path in values):
        return f"event matcher {name!r} carries an unsupported field path"
    if name == "gte" and any(not isinstance(value, int) for value in values.values()):
        return "event matcher threshold is not an integer"
    if name == "in" and any(
        not isinstance(value, Sequence)
        or isinstance(value, (str, bytes))
        or not value
        for value in values.values()
    ):
        return "event matcher 'in' clause has no allowed values"
    return ""


def _validate_state_clause(name: str, values: Any) -> str:
    if not isinstance(values, Mapping) or not values:
        return f"event matcher {name!r} clause is not a non-empty mapping"
    if any(not isinstance(path, str) or not path for path in values):
        return f"event matcher {name!r} carries an invalid state path"
    return ""


def _validate_alternatives(alternatives: Any) -> str:
    if (
        not isinstance(alternatives, Sequence)
        or isinstance(alternatives, (str, bytes))
        or not alternatives
    ):
        return "event matcher 'any' clause has no alternatives"
    for alternative in alternatives:
        error = _validate_matcher(alternative)
        if error:
            return error
    return ""


def _validate_matcher(matcher: Any) -> str:
    if not isinstance(matcher, Mapping) or not matcher:
        return "event matcher is not a non-empty mapping"
    unknown = sorted(set(matcher) - _ALLOWED_MATCH_KEYS)
    if unknown:
        return f"event matcher has unsupported clauses: {unknown}"
    validators = {
        "any": _validate_alternatives,
        "eq": lambda values: _validate_event_clause("eq", values),
        "gte": lambda values: _validate_event_clause("gte", values),
        "in": lambda values: _validate_event_clause("in", values),
        "state_contains": lambda values: _validate_state_clause("state_contains", values),
        "state_eq": lambda values: _validate_state_clause("state_eq", values),
    }
    for name, values in matcher.items():
        error = validators[name](values)
        if error:
            return error
    event_type = (matcher.get("eq") or {}).get("type")
    return "" if event_type in _ALLOWED_EVENT_TYPES else (
        f"event matcher names unsupported type {event_type!r}"
    )


def validate_diary_event_rule_pure(rule: Any) -> str:
    if not isinstance(rule, Mapping):
        return "event rule is not a mapping"
    if set(rule) == {"match"}:
        return _validate_matcher(rule["match"])
    if set(rule) != {"sequence"}:
        return "event rule must contain exactly one of 'match' or 'sequence'"
    steps = rule["sequence"]
    if not isinstance(steps, Sequence) or isinstance(steps, (str, bytes)) or len(steps) < 2:
        return "event sequence must contain at least two matchers"
    for matcher in steps:
        error = _validate_matcher(matcher)
        if error:
            return error
    return ""


def _positive_int_mapping(raw: Any, maximum: int) -> dict[str, int]:
    if not isinstance(raw, Mapping):
        return {}
    rows = {}
    for key, value in raw.items():
        try:
            amount = int(value)
        except (TypeError, ValueError, OverflowError):
            continue
        if isinstance(key, str) and key and amount > 0:
            rows[key] = min(amount, maximum)
    return rows


def sanitize_diary_event_maps_pure(diary_state: Any) -> tuple[dict[str, int], dict[str, int]]:
    source = diary_state if isinstance(diary_state, Mapping) else {}
    return (
        _positive_int_mapping(source.get("event_counts"), 1),
        _positive_int_mapping(source.get("event_stages"), 100),
    )


def _value_at(source: Mapping[str, Any], path: str) -> Any:
    node: Any = source
    for part in path.split("."):
        if not isinstance(node, Mapping) or part not in node:
            return _MISSING
        node = node[part]
    return node


def _mapping_clause_matches(source: Mapping[str, Any], values: Mapping, operator) -> bool:
    return all(operator(_value_at(source, path), expected) for path, expected in values.items())


def _contains(actual: Any, expected: Any) -> bool:
    return expected in actual if (
        isinstance(actual, Mapping)
        or isinstance(actual, Sequence) and not isinstance(actual, (str, bytes))
    ) else False


def _equals(actual: Any, expected: Any) -> bool:
    if actual == expected:
        return True
    return (
        isinstance(actual, Sequence)
        and not isinstance(actual, (str, bytes))
        and expected in actual
    )


def _at_least(actual: Any, expected: Any) -> bool:
    try:
        return int(actual) >= int(expected)
    except (TypeError, ValueError, OverflowError):
        return False


def _matches(matcher: Mapping[str, Any], event: Mapping[str, Any], player: Mapping[str, Any]) -> bool:
    checks = (
        _mapping_clause_matches(event, matcher.get("eq") or {}, _equals),
        _mapping_clause_matches(event, matcher.get("in") or {}, lambda a, b: a in b),
        _mapping_clause_matches(event, matcher.get("gte") or {}, _at_least),
        _mapping_clause_matches(player, matcher.get("state_eq") or {}, lambda a, b: a == b),
        _mapping_clause_matches(player, matcher.get("state_contains") or {}, _contains),
    )
    alternatives = matcher.get("any") or ()
    return all(checks) and (not alternatives or any(
        _matches(alternative, event, player) for alternative in alternatives
    ))


def _catalog_event_conditions():
    from ..data.achievement_diary_data import ACHIEVEMENT_DIARY_CATALOG

    rows = (
        (task, condition)
        for family in ACHIEVEMENT_DIARY_CATALOG for tier in family.tiers
        for task in tier.tasks for condition in task.conditions
    )
    for task, condition in rows:
        rule = decode_diary_event_rule_pure(condition.key)
        if condition.kind == "counter" and rule is not None:
            yield task.id, condition.key, condition.amount, rule


def _rule_event_types(rule: Mapping[str, Any]) -> set[str]:
    matchers = (rule["match"],) if "match" in rule else rule["sequence"]
    return {matcher["eq"]["type"] for matcher in matchers}


@functools.lru_cache(maxsize=1)
def _event_conditions_by_type() -> dict[str, tuple[tuple[str, str, int, dict], ...]]:
    indexed: dict[str, list[tuple[str, str, int, dict]]] = {}
    for task_id, key, amount, rule in _catalog_event_conditions():
        for event_type in _rule_event_types(rule):
            indexed.setdefault(event_type, []).append((task_id, key, amount, rule))
    return {event_type: tuple(entries) for event_type, entries in indexed.items()}


def _advance_rule(rule, token, event, player, counts, stages) -> bool:
    if "match" in rule:
        matched = _matches(rule["match"], event, player)
        if matched:
            counts[token] = 1
        return matched
    sequence = rule["sequence"]
    stage = min(max(0, int(stages.get(token, 0) or 0)), len(sequence) - 1)
    if not _matches(sequence[stage], event, player):
        if stage and _matches(sequence[0], event, player):
            stages[token] = 1
        return False
    if stage + 1 < len(sequence):
        stages[token] = stage + 1
        return False
    counts[token] = 1
    stages.pop(token, None)
    return True


def record_achievement_diary_event_pure(
    player_data: dict[str, Any], event: Mapping[str, Any]
) -> tuple[str, ...]:
    if not isinstance(event, Mapping):
        return ()
    diary = player_data.get("achievement_diaries")
    diary = dict(diary) if isinstance(diary, Mapping) else {}
    counts, stages = sanitize_diary_event_maps_pure(diary)
    completed = set(diary.get("completed_tasks", ()) or ())
    matched = []
    for task_id, key, amount, rule in _event_conditions_by_type().get(str(event.get("type", "")), ()):
        token = key[len(DIARY_EVENT_COUNTER_PREFIX):]
        if task_id in completed or counts.get(token, 0) >= max(1, int(amount or 1)):
            continue
        if _advance_rule(rule, token, event, player_data, counts, stages):
            matched.append(key)
    diary.update(event_counts=counts, event_stages=stages)
    player_data["achievement_diaries"] = diary
    return tuple(matched)


def record_action_diary_event_pure(
    player_data: dict[str, Any], skill_id: str, action_id: str,
    output_item: str | None, output_qty: int, output_items: Mapping | None,
    kills: int, event_fields: Mapping[str, Any] | None = None,
) -> None:
    outputs = dict(output_items) if output_items is not None else (
        {output_item: output_qty} if output_item and output_qty > 0 else {}
    )
    event = {
        "type": "action", "skill_id": str(skill_id), "action_id": str(action_id),
        "success": True, "outputs": outputs, "kills": max(0, int(kills or 0)),
    }
    if isinstance(event_fields, Mapping):
        event.update(event_fields)
    record_achievement_diary_event_pure(player_data, event)


def record_farming_diary_event_pure(
    player_data: dict[str, Any], info: Mapping[str, Any], replaced_outputs: Mapping | None
) -> None:
    if info.get("status") not in {"executed", "continuing"}:
        return
    outputs = dict(info.get("outputs") or {})
    for item_name, replaced in (replaced_outputs or {}).items():
        outputs[item_name] = max(0, int(outputs.get(item_name, 0) or 0) - int(replaced or 0))
    event = dict(info)
    event.update(type="farming_result", outputs=outputs)
    record_achievement_diary_event_pure(player_data, event)


def record_direct_diary_event_pure(
    player_data: dict[str, Any], ok: bool, event_type: str, **fields: Any
) -> None:
    if ok:
        record_achievement_diary_event_pure(player_data, {"type": event_type, **fields})


def record_bank_run_diary_event_pure(
    player_data: dict[str, Any], completed: bool, carried: Mapping[str, Any]
) -> None:
    if completed:
        record_achievement_diary_event_pure(player_data, {
            "type": "bank_run",
            "deposited_non_coin": any(
                item != "Coins" and int(amount or 0) > 0 for item, amount in carried.items()
            ),
        })


def run_bank_run_diary_callbacks_pure(
    completed: bool, player_data: dict[str, Any], refresh, check
) -> None:
    if not completed:
        return
    if refresh is not None:
        refresh()
    check(player_data)
