"""Read the reachability baseline pinned in the audit's own test.

The pins live as assertions in one test method so a content change updates the
suite and the promotion gate together. `audit_item_reachability.py --check`
and the promotion gate both read them here, from the tree being measured.
"""

from __future__ import annotations

import ast
from pathlib import Path


REACHABILITY_PIN_FIELDS = (
    "action_count",
    "reachable_item_count",
    "orphan_input_count",
    "root_orphan_count",
    "cascade_orphan_count",
    "unresolved_action_count",
    "seed_item_count",
)


REACHABILITY_PIN_METHOD = "test_report_matches_player_finishable_quest_baseline"


def _pin_assertion(node: ast.AST) -> tuple[str, int] | None:
    match node:
        case ast.Call(
            func=ast.Attribute(attr="assertEqual"),
            args=[
                ast.Subscript(value=ast.Name(id="report"), slice=ast.Constant(value=str() as field)),
                ast.Constant(value=int() as value),
                *_,
            ],
        ) if field in REACHABILITY_PIN_FIELDS and type(value) is int:
            return field, value
    return None


def read_reachability_pins(root: Path) -> dict[str, int]:
    path = root / "tests" / "test_item_reachability_audit.py"
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError) as exc:
        raise ValueError(f"Cannot read reachability pins from {path}: {exc}") from exc

    methods = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == REACHABILITY_PIN_METHOD
    ]
    if len(methods) != 1:
        raise ValueError(
            f"Expected one {REACHABILITY_PIN_METHOD} method in {path}; found {len(methods)}"
        )

    pins: dict[str, int] = {}
    for pin in filter(None, map(_pin_assertion, ast.walk(methods[0]))):
        field, value = pin
        if field in pins:
            raise ValueError(f"Reachability pin {field!r} appears more than once in {path}")
        pins[field] = value

    missing = [field for field in REACHABILITY_PIN_FIELDS if field not in pins]
    if missing:
        raise ValueError(f"Reachability pins missing from {path}: {', '.join(missing)}")
    return pins
