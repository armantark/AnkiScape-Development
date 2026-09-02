"""Compile and validate the canonical Achievement Diary curation ledger."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Callable

from ankiscape.core.constants import COMBAT_ENEMY_DATA, ITEM_DEFINITIONS
from ankiscape.data.farming_data import FARMING_CROPS_BY_ID, FARMING_PATCHES_BY_ID
from ankiscape.logic_pure.achievement_diary_events import (
    DIARY_EVENT_COUNTER_PREFIX,
    decode_diary_event_rule_pure,
    encode_diary_event_rule_pure,
    validate_diary_event_rule_pure,
)


ROOT = Path(__file__).resolve().parents[1]
CURATION_LEDGER_PATH = (
    ROOT / "memory-bank" / "diary-curation-ledger" / "dormant-task-ledger.jsonl"
)
_SPEC_KINDS = frozenset({
    "any_of", "combat_kill", "counter", "equipped_item", "event", "hold_item",
    "ledger_action", "ledger_action_family", "ledger_output", "shop_transaction",
    "state_equals",
})
_DIRECT_EVENT_VALUES = {
    "agility_result": {"action_id": {"barbarian_advanced"}},
    "bank_run": {"deposited_non_coin": {True}},
    "castle_wars_review": {"duty": {"catapult"}},
    "construction_command": {"action_id": {"purchase_house", "purchase_room"}},
    "court_cases_command": {"action_id": {"enter"}},
    "managing_miscellania_command": {"action_id": {"collect"}},
    "shades_of_mortton_review": {"hammer": {"Flamtaer hammer"}},
    "slayer_command": {
        "action_id": {"get_assignment"}, "reason": {"assignment_started"},
    },
    "summoning_command": {
        "action_id": {"restore_points", "summon"}, "familiar_id": {"ibis"},
    },
    "temple_trekking_command": {"action_id": {"prepare_pouch"}},
}
_REQUIRED_DIRECT_FIELDS = {
    event_type: frozenset(values) for event_type, values in _DIRECT_EVENT_VALUES.items()
}
_REQUIRED_DIRECT_FIELDS["summoning_command"] = frozenset({"action_id"})
_ITEM_NAMES = frozenset(row.storage_key for row in ITEM_DEFINITIONS)


def _load_rows(path: Path) -> dict[str, dict]:
    rows = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise SystemExit(f"invalid diary ledger JSON on line {line_number}: {error}")
        task_id = str(row.get("task_id", ""))
        disposition = row.get("disposition")
        if not task_id or task_id in rows:
            raise SystemExit(f"invalid or duplicate diary ledger task_id {task_id!r}")
        if disposition not in {"active", "translated", "dormant"}:
            raise SystemExit(
                f"diary ledger task {task_id} has unsupported disposition {disposition!r}"
            )
        rows[task_id] = row
    if len(rows) != 320:
        raise SystemExit(f"diary ledger has {len(rows)} rows, expected 320")
    return rows


def _condition_from_spec(spec: dict, task_id: str) -> tuple:
    if not isinstance(spec, dict):
        raise SystemExit(f"diary ledger task {task_id} has a non-mapping condition")
    kind, label = str(spec.get("kind", "")), str(spec.get("label", ""))
    if kind not in _SPEC_KINDS:
        raise SystemExit(
            f"diary ledger task {task_id} has unsupported condition kind {kind!r}"
        )
    if not label:
        raise SystemExit(f"diary ledger task {task_id} has an unlabelled condition")
    if kind == "event":
        rule = spec.get("rule")
        error = validate_diary_event_rule_pure(rule)
        if error:
            raise SystemExit(f"diary ledger task {task_id} has invalid event rule: {error}")
        return "counter", encode_diary_event_rule_pure(rule), 1, label
    if kind == "any_of":
        alternatives = tuple(
            _condition_from_spec(alternative, task_id)
            for alternative in spec.get("alternatives", ())
        )
        return "any_of", "", 1, label, alternatives
    key, amount = str(spec.get("key", "")), int(spec.get("amount", 1))
    if amount < 1:
        raise SystemExit(f"diary ledger task {task_id} condition amount must be positive")
    if kind == "state_equals":
        if "expected" not in spec:
            raise SystemExit(
                f"diary ledger task {task_id} state_equals condition has no expected value"
            )
        return kind, key, amount, label, spec["expected"]
    return kind, key, amount, label


def _conditions_from_row(row: dict) -> list[tuple]:
    task_id, specs = str(row["task_id"]), row.get("wiring")
    if row["disposition"] == "dormant":
        if specs is not None:
            raise SystemExit(f"dormant diary ledger task {task_id} carries wiring")
        return []
    if not isinstance(specs, list) or not specs:
        raise SystemExit(f"live diary ledger task {task_id} has no valid wiring clause")
    return [_condition_from_spec(spec, task_id) for spec in specs]


class CurationLedger:
    def __init__(self, path: Path = CURATION_LEDGER_PATH):
        self.rows = _load_rows(path)
        self.seen: set[str] = set()

    def begin(self) -> None:
        self.seen.clear()

    def conditions_for(self, task_id: str, base_conditions: list[tuple]) -> list[tuple]:
        row = self.rows.get(task_id)
        if row is None:
            return base_conditions
        if base_conditions:
            raise SystemExit(f"diary ledger task {task_id} already has a non-ledger condition")
        self.seen.add(task_id)
        return _conditions_from_row(row)

    def assert_complete(self) -> None:
        missing = sorted(set(self.rows) - self.seen)
        if missing:
            raise SystemExit(f"diary ledger rows do not resolve to generated tasks: {missing}")


CURATION_LEDGER = CurationLedger()


def _walk_matchers(matcher):
    yield matcher
    for alternative in matcher.get("any", ()):
        yield from _walk_matchers(alternative)


def _event_matchers(rule):
    roots = (rule["match"],) if "match" in rule else tuple(rule["sequence"])
    for matcher in roots:
        yield from _walk_matchers(matcher)


def _values(matcher: Mapping, field: str) -> list:
    values = []
    if field in matcher.get("eq", {}):
        values.append(matcher["eq"][field])
    values.extend(matcher.get("in", {}).get(field, ()))
    return values


def _output_error(matcher, skill_id, resolve_ledger_key) -> str:
    for clause in ("eq", "gte"):
        for path in matcher.get(clause, {}):
            if path.startswith("outputs."):
                error = resolve_ledger_key(
                    "ledger_output", f"{skill_id}:{path.split('.', 1)[1]}"
                )
                if error:
                    return error
    return ""


def _action_id_error(skill_id, action_id, resolve_ledger_key, quest_data) -> str:
    if skill_id == "combat":
        return "" if action_id in COMBAT_ENEMY_DATA else f"names no combat target {action_id!r}"
    if skill_id == "quest":
        return "" if action_id in quest_data else f"names no quest action {action_id!r}"
    return resolve_ledger_key("ledger_action", f"{skill_id}:{action_id}")


def _resolve_action_match(matcher, key, resolve_ledger_key, quest_data) -> str:
    skill_id, action_ids = matcher.get("eq", {}).get("skill_id"), _values(matcher, "action_id")
    if not isinstance(skill_id, str) or not skill_id:
        return f"counter key {key!r} action event has no exact skill_id"
    if not action_ids:
        return f"counter key {key!r} action event has no action_id"
    for action_id in action_ids:
        if error := _action_id_error(skill_id, action_id, resolve_ledger_key, quest_data):
            return f"counter key {key!r}: {error}"
    output_error = _output_error(matcher, skill_id, resolve_ledger_key)
    return f"counter key {key!r}: {output_error}" if output_error else ""


def _resolve_farming_match(matcher, key) -> str:
    equal = matcher.get("eq", {})
    if equal.get("kind") not in {"check_health", "chop", "harvest", "plant"}:
        return f"counter key {key!r} names no exact Farming result kind"
    missing_patches = sorted(set(_values(matcher, "patch_id")) - set(FARMING_PATCHES_BY_ID))
    missing_crops = sorted(set(_values(matcher, "crop_id")) - set(FARMING_CROPS_BY_ID))
    if missing_patches:
        return f"counter key {key!r} names no farming patches {missing_patches}"
    if missing_crops:
        return f"counter key {key!r} names no farming crops {missing_crops}"
    return _unknown_output_item_error(matcher, key)


def _unknown_output_item_error(matcher, key) -> str:
    paths = {
        path for clause in ("eq", "gte") for path in matcher.get(clause, {})
        if path.startswith("outputs.")
    }
    missing = sorted(path.split(".", 1)[1] for path in paths if path.split(".", 1)[1] not in _ITEM_NAMES)
    return f"counter key {key!r} names no output item {missing[0]!r}" if missing else ""


def _resolve_direct_match(matcher, key, event_type) -> str:
    allowed = _DIRECT_EVENT_VALUES.get(str(event_type), {})
    for field, values in allowed.items():
        candidates = _values(matcher, field)
        if field in _REQUIRED_DIRECT_FIELDS.get(str(event_type), ()) and not candidates:
            return f"counter key {key!r} has no exact {event_type} {field}"
        invalid = sorted(set(candidates) - values)
        if invalid:
            return f"counter key {key!r} names unsupported {event_type} {field}: {invalid}"
    return _unknown_output_item_error(matcher, key)


def _resolve_match(matcher, key, resolve_ledger_key, resolve_state_path, quest_data) -> str:
    event_type = matcher.get("eq", {}).get("type")
    error = (
        _resolve_action_match(matcher, key, resolve_ledger_key, quest_data)
        if event_type == "action" else _resolve_farming_match(matcher, key)
        if event_type == "farming_result" else _resolve_direct_match(matcher, key, event_type)
    )
    if error:
        return error
    for path in (path for clause in ("state_eq", "state_contains") for path in matcher.get(clause, {})):
        if state_error := resolve_state_path(path):
            return f"counter key {key!r}: {state_error}"
    return ""


def resolve_diary_event_key(
    key: str, resolve_ledger_key: Callable[[str, str], str],
    resolve_state_path: Callable[[str], str], quest_data: Mapping,
) -> str | None:
    if not key.startswith(DIARY_EVENT_COUNTER_PREFIX):
        return None
    rule = decode_diary_event_rule_pure(key)
    if rule is None:
        return f"counter key {key!r} has invalid diary-event encoding"
    if error := validate_diary_event_rule_pure(rule):
        return f"counter key {key!r} has invalid diary-event rule: {error}"
    for matcher in _event_matchers(rule):
        if error := _resolve_match(matcher, key, resolve_ledger_key, resolve_state_path, quest_data):
            return error
    return ""


def _encounter_ids(value):
    if isinstance(value, Mapping):
        if isinstance(value.get("encounter_id"), str):
            yield value["encounter_id"]
        for nested in value.values():
            yield from _encounter_ids(nested)
    elif isinstance(value, (list, tuple)):
        for nested in value:
            yield from _encounter_ids(nested)


def resolve_special_counter(
    key: str, resolve_ledger_key: Callable[[str, str], str],
    resolve_state_path: Callable[[str], str], quest_data: Mapping,
) -> str | None:
    event_error = resolve_diary_event_key(key, resolve_ledger_key, resolve_state_path, quest_data)
    if event_error is not None:
        return event_error
    parts = key.split(".")
    if parts[:2] == ["action_telemetry", "actions"]:
        if len(parts) != 4 or parts[3] not in {"attempts", "successes", "failures"}:
            return f"counter key {key!r} names no action telemetry counter"
        error = resolve_ledger_key("ledger_action", parts[2])
        return f"counter key {key!r}: {error}" if error else ""
    if not parts or parts[0] != "quest_combat_encounter_counts":
        return None
    if len(parts) != 3 or parts[1] not in quest_data:
        return f"counter key {key!r} names no shipped quest encounter"
    if parts[2] not in set(_encounter_ids(quest_data[parts[1]])):
        return f"counter key {key!r} names no encounter in quest {parts[1]!r}"
    return ""


def resolve_named_counter(key: str) -> str | None:
    parts = key.split(".")
    if parts[0] == "combat_kill_counts":
        return "" if len(parts) == 2 and parts[1] in COMBAT_ENEMY_DATA else (
            f"counter key {key!r} names no enemy in COMBAT_ENEMY_DATA"
        )
    if parts[0] != "shop_transaction_counts":
        return None
    from ankiscape.logic.shop_logic import SHOP_DIARY_TRANSACTION_KEYS
    return "" if len(parts) == 2 and parts[1] in SHOP_DIARY_TRANSACTION_KEYS else (
        f"counter key {key!r} names no diary shop transaction"
    )
