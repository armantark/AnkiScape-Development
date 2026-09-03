"""Compile and validate the canonical Achievement Diary curation ledger."""

from __future__ import annotations

import ast
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
_ITEM_NAMES = frozenset(row.storage_key for row in ITEM_DEFINITIONS)
_LIVE_DISPOSITIONS = frozenset({"active", "translated", "swapped", "invented"})
_ALLOWED_DISPOSITIONS = _LIVE_DISPOSITIONS | {"dormant"}


def _dynamic_direct_event_domain(event_type: str, field: str) -> frozenset | None:
    """Resolve dynamic emitter fields against their production registries."""
    if event_type == "agility_result" and field == "target_id":
        from ankiscape.data.agility_data import AGILITY_TARGETS_BY_ID

        return frozenset(AGILITY_TARGETS_BY_ID)
    if event_type == "shades_of_mortton_review" and field == "hammer":
        return frozenset({"Flamtaer hammer", "Hammer"})
    if event_type == "great_orb_project_teleport" and field == "altar_id":
        from ankiscape.data.great_orb_project_data import (
            GREAT_ORB_PROJECT_TELEPORT_TABLETS,
        )

        return frozenset(row[4] for row in GREAT_ORB_PROJECT_TELEPORT_TABLETS)
    return None


def _literal_domain(node: ast.AST, scope: ast.AST | None = None) -> frozenset | None:
    if isinstance(node, ast.Constant):
        return frozenset({node.value}) if isinstance(node.value, (str, bool, int)) else None
    if isinstance(node, ast.Call):
        return _call_literal_domain(node, scope)
    if isinstance(node, ast.IfExp):
        return _union_literal_domains(node.body, node.orelse, scope)
    if isinstance(node, ast.Name):
        return _name_literal_domain(node, scope)
    if isinstance(node, (ast.Set, ast.Tuple, ast.List)):
        return _collection_literal_domain(node)
    return None


def _call_literal_domain(node: ast.Call, scope: ast.AST | None) -> frozenset | None:
    if not isinstance(node.func, ast.Name):
        return None
    if node.func.id in {"all", "any", "bool"}:
        return frozenset({False, True})
    if node.func.id == "str" and len(node.args) == 1:
        return _literal_domain(node.args[0], scope)
    return None


def _union_literal_domains(
    left_node: ast.AST, right_node: ast.AST, scope: ast.AST | None
) -> frozenset | None:
    left, right = _literal_domain(left_node, scope), _literal_domain(right_node, scope)
    return left | right if left is not None and right is not None else None


def _name_literal_domain(node: ast.Name, scope: ast.AST | None) -> frozenset | None:
    if scope is None:
        return None
    values = set()
    for comparison in ast.walk(scope):
        domain = _comparison_literal_domain(comparison, node.id)
        if domain is not None:
            values.update(domain)
    return frozenset(values) if values else None


def _comparison_literal_domain(node: ast.AST, name: str) -> frozenset | None:
    if not isinstance(node, ast.Compare) or len(node.ops) != 1:
        return None
    if not isinstance(node.ops[0], (ast.Eq, ast.In, ast.NotIn)):
        return None
    left, right = node.left, node.comparators[0]
    if isinstance(left, ast.Name) and left.id == name:
        return _literal_domain(right)
    if isinstance(right, ast.Name) and right.id == name:
        return _literal_domain(left)
    return None


def _collection_literal_domain(node: ast.Set | ast.Tuple | ast.List) -> frozenset | None:
    domains = [_literal_domain(value) for value in node.elts]
    if not all(domain is not None and len(domain) == 1 for domain in domains):
        return None
    return frozenset(next(iter(domain)) for domain in domains)


def _production_emitter_paths() -> tuple[Path, ...]:
    return (ROOT / "__init__.py",) + tuple(
        path
        for directory in (ROOT / "logic", ROOT / "logic_pure", ROOT / "runtime")
        for path in directory.rglob("*.py")
    )


def _call_scopes(call: ast.Call, parents: Mapping[ast.AST, ast.AST]) -> tuple[ast.AST, ...]:
    scopes = []
    cursor = call
    while cursor in parents:
        cursor = parents[cursor]
        if isinstance(cursor, (ast.FunctionDef, ast.AsyncFunctionDef)):
            scopes.append(cursor)
    return tuple(scopes)


def _direct_event_call_shape(
    call: ast.Call, scope: ast.AST
) -> tuple[frozenset, dict[str, ast.AST]] | None:
    name = call.func.id if isinstance(call.func, ast.Name) else ""
    if name == "record_direct_diary_event_pure" and len(call.args) >= 3:
        fields = {keyword.arg: keyword.value for keyword in call.keywords if keyword.arg}
        return _literal_domain(call.args[2], scope), fields
    if name != "record_achievement_diary_event_pure" or len(call.args) < 2:
        return None
    payload = call.args[1]
    if not isinstance(payload, ast.Dict):
        return None
    fields = {
        key.value: value for key, value in zip(payload.keys, payload.values)
        if isinstance(key, ast.Constant) and isinstance(key.value, str)
    }
    event_types = _literal_domain(fields.pop("type", ast.Constant(None)))
    return (event_types, fields) if event_types is not None else None


def _expression_domain(
    expression: ast.AST, scope: ast.AST, scopes: tuple[ast.AST, ...]
) -> frozenset | None:
    inner = expression.args[0] if (
        isinstance(expression, ast.Call)
        and isinstance(expression.func, ast.Name)
        and expression.func.id == "str"
        and len(expression.args) == 1
    ) else expression
    if not isinstance(inner, ast.Name):
        return _literal_domain(expression, scope)
    parameter_scope = next(
        (
            candidate for candidate in scopes
            if inner.id in {
                argument.arg
                for argument in (
                    candidate.args.posonlyargs
                    + candidate.args.args
                    + candidate.args.kwonlyargs
                )
            }
        ),
        scope,
    )
    return _literal_domain(expression, parameter_scope)


def _merge_direct_event_fields(
    emitted: dict[str, frozenset | None],
    event_type: str,
    fields: Mapping[str, ast.AST],
    scope: ast.AST,
    scopes: tuple[ast.AST, ...],
) -> None:
    for field, expression in fields.items():
        domain = _expression_domain(expression, scope, scopes)
        dynamic_domain = _dynamic_direct_event_domain(event_type, field)
        if dynamic_domain is not None:
            domain = dynamic_domain if domain is None else domain | dynamic_domain
        if field not in emitted or emitted[field] is None or domain is None:
            emitted[field] = domain
        else:
            emitted[field] |= domain


def _support_from_tree(tree: ast.AST) -> dict[str, dict[str, frozenset | None]]:
    support: dict[str, dict[str, frozenset | None]] = {}
    parents = {
        child: parent
        for parent in ast.walk(tree)
        for child in ast.iter_child_nodes(parent)
    }
    for call in (node for node in ast.walk(tree) if isinstance(node, ast.Call)):
        scopes = _call_scopes(call, parents)
        scope = scopes[0] if scopes else call
        shape = _direct_event_call_shape(call, scope)
        if shape is None:
            continue
        event_types, fields = shape
        for event_type in (str(value) for value in event_types if value not in {"action", "farming_result"}):
            _merge_direct_event_fields(
                support.setdefault(event_type, {}), event_type, fields, scope, scopes
            )
    return support


def _merge_event_support(
    target: dict[str, dict[str, frozenset | None]],
    source: Mapping[str, Mapping[str, frozenset | None]],
) -> None:
    for event_type, fields in source.items():
        emitted = target.setdefault(event_type, {})
        for field, domain in fields.items():
            if field not in emitted or emitted[field] is None or domain is None:
                emitted[field] = domain
            else:
                emitted[field] |= domain


def _direct_event_emitters() -> dict[str, dict[str, frozenset | None]]:
    """Read direct-event shapes from the production calls that emit them."""
    support: dict[str, dict[str, frozenset | None]] = {}
    for path in _production_emitter_paths():
        _merge_event_support(
            support,
            _support_from_tree(ast.parse(path.read_text(encoding="utf-8"), filename=str(path))),
        )
    return support


_DIRECT_EVENT_EMITTERS = _direct_event_emitters()


def _validate_row_metadata(task_id: str, row: Mapping) -> None:
    disposition = row.get("disposition")
    if disposition not in _ALLOWED_DISPOSITIONS:
        raise SystemExit(
            f"diary ledger task {task_id} has unsupported disposition {disposition!r}"
        )
    designed_text = (row.get("designed_name"), row.get("designed_description"))
    if disposition == "invented" and not all(
        isinstance(value, str) and value for value in designed_text
    ):
        raise SystemExit(
            f"invented diary ledger task {task_id} has no designed task text"
        )
    if disposition != "invented" and any(value is not None for value in designed_text):
        raise SystemExit(
            f"non-invented diary ledger task {task_id} carries designed task text"
        )


def _load_rows(path: Path) -> dict[str, dict]:
    rows = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise SystemExit(f"invalid diary ledger JSON on line {line_number}: {error}")
        task_id = str(row.get("task_id", ""))
        if not task_id or task_id in rows:
            raise SystemExit(f"invalid or duplicate diary ledger task_id {task_id!r}")
        _validate_row_metadata(task_id, row)
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


def _normalize_event_rule(value, ordered: bool = False):
    if isinstance(value, Mapping):
        return tuple(
            (key, _normalize_event_rule(item, ordered=key == "sequence"))
            for key, item in sorted(value.items())
        )
    if isinstance(value, list):
        items = tuple(_normalize_event_rule(item) for item in value)
        return items if ordered else tuple(sorted(items, key=repr))
    return value


def _condition_seam(condition: tuple) -> tuple:
    kind, key, amount = condition[:3]
    if kind == "any_of":
        alternatives = tuple(
            sorted((_condition_seam(item) for item in condition[4]), key=repr)
        )
        return kind, key, amount, alternatives
    if kind == "state_equals":
        expected = json.dumps(condition[4], sort_keys=True, separators=(",", ":"))
        return kind, key, amount, expected
    event_rule = decode_diary_event_rule_pure(key) if kind == "counter" else None
    if event_rule is not None:
        matcher = event_rule.get("match")
        if matcher == {
            "eq": {
                "type": "action",
                "skill_id": matcher.get("eq", {}).get("skill_id") if matcher else None,
                "action_id": matcher.get("eq", {}).get("action_id") if matcher else None,
                "success": True,
            }
        }:
            eq = matcher["eq"]
            return "ledger_action", f"{eq['skill_id']}:{eq['action_id']}", amount
        return "event", amount, _normalize_event_rule(event_rule)
    return kind, key, amount


def _completion_seam(conditions: list[tuple]) -> tuple:
    return tuple(sorted((_condition_seam(item) for item in conditions), key=repr))


def _validate_completion_seams(rows: Mapping[str, dict]) -> None:
    owners = {}
    duplicates = []
    for task_id, row in rows.items():
        conditions = _conditions_from_row(row)
        if not conditions:
            continue
        seam = _completion_seam(conditions)
        previous = owners.get(seam)
        if previous is not None:
            duplicates.append((previous, task_id))
        else:
            owners[seam] = task_id
    if duplicates:
        pairs = "; ".join(f"{first!r} and {second!r}" for first, second in duplicates)
        raise SystemExit(f"diary ledger tasks {pairs} share completion seams")


class CurationLedger:
    def __init__(self, path: Path = CURATION_LEDGER_PATH):
        self.rows = _load_rows(path)
        _validate_completion_seams(self.rows)
        self.seen: set[str] = set()
        self.seam_owners = {}
        self.duplicate_seams = []

    def begin(self) -> None:
        self.seen.clear()
        self.seam_owners.clear()
        self.duplicate_seams.clear()

    def conditions_for(self, task_id: str, base_conditions: list[tuple]) -> list[tuple]:
        row = self.rows.get(task_id)
        if row is None:
            conditions = base_conditions
        else:
            if base_conditions:
                raise SystemExit(
                    f"diary ledger task {task_id} already has a non-ledger condition"
                )
            self.seen.add(task_id)
            conditions = _conditions_from_row(row)
        if conditions:
            seam = _completion_seam(conditions)
            previous = self.seam_owners.get(seam)
            if previous is not None:
                self.duplicate_seams.append((previous, task_id))
            else:
                self.seam_owners[seam] = task_id
        return conditions

    def text_for(
        self, task_id: str, base_name: str, base_description: str
    ) -> tuple[str, str]:
        row = self.rows.get(task_id)
        if row is None or row["disposition"] != "invented":
            return base_name, base_description
        return row["designed_name"], row["designed_description"]

    def assert_complete(self) -> None:
        missing = sorted(set(self.rows) - self.seen)
        if missing:
            raise SystemExit(f"diary ledger rows do not resolve to generated tasks: {missing}")
        if self.duplicate_seams:
            pairs = "; ".join(
                f"{first!r} and {second!r}"
                for first, second in self.duplicate_seams
            )
            raise SystemExit(f"diary tasks {pairs} share completion seams")


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
    allowed = _DIRECT_EVENT_EMITTERS.get(str(event_type))
    if allowed is None:
        return f"counter key {key!r} names unsupported direct-event type {event_type!r}"
    constrained_fields = {
        field for clause in ("eq", "in", "gte")
        for field in matcher.get(clause, {})
        if field != "type" and not field.startswith("outputs.")
    }
    unsupported_fields = sorted(constrained_fields - set(allowed))
    if unsupported_fields:
        return f"counter key {key!r} names unsupported {event_type} field: {unsupported_fields}"
    for field, values in allowed.items():
        candidates = _values(matcher, field)
        if values is not None and not candidates:
            return f"counter key {key!r} has no exact {event_type} {field}"
        invalid = sorted(set(candidates) - values) if values is not None else []
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
    from ankiscape.logic_pure.shop_diary_transactions import (
        SHOP_DIARY_TRANSACTION_KEYS,
    )
    return "" if len(parts) == 2 and parts[1] in SHOP_DIARY_TRANSACTION_KEYS else (
        f"counter key {key!r} names no diary shop transaction"
    )
