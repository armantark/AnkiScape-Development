#!/usr/bin/env python3
"""Audit unittest files for mechanically detectable low-signal tests."""

from __future__ import annotations

import argparse
import ast
import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from functools import cached_property
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class TestIssue:
    kind: str
    path: str
    line: int
    name: str
    detail: str


@dataclass(frozen=True)
class CloneGroup:
    tests: tuple[str, ...]


@dataclass(frozen=True)
class TestQualityReport:
    test_files: int
    test_methods: int
    hard_issues: tuple[TestIssue, ...]
    structural_clones: tuple[CloneGroup, ...]

    @property
    def ok(self) -> bool:
        return not self.hard_issues


def _call_name(call: ast.Call) -> str:
    if isinstance(call.func, ast.Attribute):
        return call.func.attr
    if isinstance(call.func, ast.Name):
        return call.func.id
    return ""


def _assertion_count(node: ast.AST) -> int:
    return sum(
        isinstance(child, ast.Assert)
        or (
            isinstance(child, ast.Call)
            and _call_name(child).startswith(("assert", "_assert_"))
        )
        for child in ast.walk(node)
    )


def _is_read_call(node: ast.AST) -> bool:
    return isinstance(node, ast.Call) and _call_name(node) in {"read", "read_bytes", "read_text"}


def _target_names(target: ast.AST) -> set[str]:
    if isinstance(target, ast.Name):
        return {target.id}
    if isinstance(target, (ast.Tuple, ast.List)):
        return {name for item in target.elts for name in _target_names(item)}
    return set()


def _assigned_read_names(node: ast.AST) -> set[str]:
    names: set[str] = set()
    for child in ast.walk(node):
        if not isinstance(child, (ast.Assign, ast.AnnAssign)) or not _is_read_call(child.value):
            continue
        targets = child.targets if isinstance(child, ast.Assign) else [child.target]
        for target in targets:
            names.update(_target_names(target))
    return names


def _is_read_value(node: ast.AST, read_names: set[str]) -> bool:
    return _is_read_call(node) or (isinstance(node, ast.Name) and node.id in read_names)


def _has_source_text_membership_assertion(node: ast.AST) -> bool:
    read_names = _assigned_read_names(node)
    for child in ast.walk(node):
        if isinstance(child, ast.Assert) and isinstance(child.test, ast.Compare):
            for op, comparator in zip(child.test.ops, child.test.comparators):
                if isinstance(op, (ast.In, ast.NotIn)):
                    literal = isinstance(child.test.left, ast.Constant) and isinstance(
                        child.test.left.value, (str, bytes)
                    )
                    if literal and _is_read_value(comparator, read_names):
                        return True
        if isinstance(child, ast.Call) and _call_name(child) in {"assertIn", "assertNotIn"}:
            if len(child.args) >= 2:
                literal = isinstance(child.args[0], ast.Constant) and isinstance(
                    child.args[0].value, (str, bytes)
                )
                if literal and _is_read_value(child.args[1], read_names):
                    return True
    return False


def _imported_names(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            names.update(alias.asname or alias.name.partition(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.update(alias.asname or alias.name for alias in node.names)
    return names


def _is_literal_source_path(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and node.value.endswith(".py")
    )


def _is_module_source_path(node: ast.AST, imported_names: set[str]) -> bool:
    return (
        isinstance(node, ast.Attribute)
        and node.attr == "__file__"
        and isinstance(node.value, ast.Name)
        and node.value.id in imported_names
    )


def _is_source_path(node: ast.AST, imported_names: set[str]) -> bool:
    if _is_literal_source_path(node) or _is_module_source_path(node, imported_names):
        return True
    return (
        isinstance(node, ast.Call)
        and _call_name(node) == "Path"
        and bool(node.args)
        and _is_source_path(node.args[0], imported_names)
    )


def _is_source_open(node: ast.AST, imported_names: set[str]) -> bool:
    if not isinstance(node, ast.Call):
        return False
    if isinstance(node.func, ast.Name) and node.func.id == "open":
        return bool(node.args) and _is_source_path(node.args[0], imported_names)
    return (
        isinstance(node.func, ast.Attribute)
        and node.func.attr == "open"
        and _is_source_path(node.func.value, imported_names)
    )


def _source_handles(node: ast.AST, imported_names: set[str]) -> set[str]:
    return {
        name
        for child in ast.walk(node)
        if isinstance(child, ast.With)
        for item in child.items
        if _is_source_open(item.context_expr, imported_names)
        and item.optional_vars is not None
        for name in _target_names(item.optional_vars)
    }


def _is_source_read(node: ast.AST, imported_names: set[str], handles: set[str]) -> bool:
    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
        return False
    if node.func.attr in {"read_bytes", "read_text"}:
        return _is_source_path(node.func.value, imported_names)
    return node.func.attr in {"read", "readline", "readlines"} and (
        (isinstance(node.func.value, ast.Name) and node.func.value.id in handles)
        or _is_source_open(node.func.value, imported_names)
    )


def _source_reads(
    node: ast.AST,
    imported_names: set[str],
    handles: set[str],
) -> tuple[ast.Call, ...]:
    return tuple(
        child
        for child in ast.walk(node)
        if _is_source_read(child, imported_names, handles)
    )


def _assignments(node: ast.AST) -> tuple[ast.Assign | ast.AnnAssign, ...]:
    return tuple(
        child
        for child in ast.walk(node)
        if isinstance(child, (ast.Assign, ast.AnnAssign)) and child.value is not None
    )


def _assignment_targets(node: ast.Assign | ast.AnnAssign) -> set[str]:
    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
    return {name for target in targets for name in _target_names(target)}


def _materialized_collection(node: ast.AST, materialized_names: set[str]) -> bool:
    materialized_nodes = (
        ast.List,
        ast.Tuple,
        ast.Set,
        ast.Dict,
        ast.ListComp,
        ast.SetComp,
        ast.DictComp,
    )
    if isinstance(node, materialized_nodes):
        return True
    if isinstance(node, ast.Name):
        return node.id in materialized_names
    return isinstance(node, ast.Call) and _call_name(node) in {"list", "set", "sorted", "tuple"}


def _assignment_depends_on_scan(
    assignment: ast.Assign | ast.AnnAssign,
    names: set[str],
    imported_names: set[str],
    handles: set[str],
) -> bool:
    return any(
        _is_source_read(part, imported_names, handles)
        or (isinstance(part, ast.Name) and part.id in names)
        for part in ast.walk(assignment.value)
    )


def _propagate_scan_names_once(
    assignments: tuple[ast.Assign | ast.AnnAssign, ...],
    names: set[str],
    materialized_names: set[str],
    imported_names: set[str],
    handles: set[str],
) -> bool:
    changed = False
    for assignment in assignments:
        if not _assignment_depends_on_scan(assignment, names, imported_names, handles):
            continue
        found = _assignment_targets(assignment)
        if _materialized_collection(assignment.value, materialized_names):
            materialized_names.update(found)
        missing = found - names
        names.update(missing)
        changed = bool(missing) or changed
    return changed


def _propagate_scan_names(
    assignments: tuple[ast.Assign | ast.AnnAssign, ...],
    imported_names: set[str],
    handles: set[str],
) -> tuple[set[str], set[str]]:
    names: set[str] = set()
    materialized_names: set[str] = set()
    while _propagate_scan_names_once(
        assignments, names, materialized_names, imported_names, handles
    ):
        pass
    return names, materialized_names


def _source_scan_names(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    imported_names: set[str],
) -> tuple[int | None, set[str], set[str]]:
    handles = _source_handles(node, imported_names)
    reads = _source_reads(node, imported_names, handles)
    if not reads:
        return None, set(), set()
    names, materialized_names = _propagate_scan_names(
        _assignments(node), imported_names, handles
    )
    return min(read.lineno for read in reads), names, materialized_names


@dataclass(frozen=True)
class _ScanGuardContext:
    names: frozenset[str]
    materialized_names: frozenset[str]
    expected_names: frozenset[str]
    imported_names: frozenset[str]


def _is_scan_result(node: ast.AST, context: _ScanGuardContext) -> bool:
    if isinstance(node, ast.Name):
        return node.id in context.materialized_names
    return (
        isinstance(node, ast.Call)
        and _call_name(node) in {"list", "set", "sorted", "tuple"}
        and any(
            isinstance(part, ast.Name) and part.id in context.names
            for part in ast.walk(node)
        )
    )


def _collection_size(node: ast.AST) -> int | None:
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return len(node.elts)
    if isinstance(node, ast.Dict):
        return len(node.keys)
    return None


def _integer_literal(node: ast.AST) -> int | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return node.value
    return None


def _expected_key_names(node: ast.AST, imported_names: set[str]) -> set[str]:
    names = {name for name in imported_names if name.isupper()}
    for assignment in _assignments(node):
        if (_collection_size(assignment.value) or 0) > 0:
            names.update(_assignment_targets(assignment))
    return names


def _is_expected_keys(node: ast.AST, context: _ScanGuardContext) -> bool:
    size = _collection_size(node)
    if size is not None:
        return size > 0
    if isinstance(node, ast.Name):
        return node.id in context.expected_names
    if isinstance(node, ast.Attribute):
        return (
            node.attr.isupper()
            and isinstance(node.value, ast.Name)
            and node.value.id in context.imported_names
        )
    return (
        isinstance(node, ast.Call)
        and _call_name(node) in {"list", "set", "tuple"}
        and bool(node.args)
        and _is_expected_keys(node.args[0], context)
    )


def _len_of_scan(node: ast.AST, context: _ScanGuardContext) -> bool:
    return (
        isinstance(node, ast.Call)
        and _call_name(node) == "len"
        and bool(node.args)
        and _is_scan_result(node.args[0], context)
    )


def _guards_membership(
    left: ast.AST,
    op: ast.cmpop,
    right: ast.AST,
    context: _ScanGuardContext,
) -> bool:
    return isinstance(op, ast.In) and _is_scan_result(right, context)


def _guards_exact_keys(
    left: ast.AST,
    op: ast.cmpop,
    right: ast.AST,
    context: _ScanGuardContext,
) -> bool:
    if not isinstance(op, ast.Eq):
        return False
    return (
        _is_scan_result(left, context) and _is_expected_keys(right, context)
    ) or (
        _is_scan_result(right, context) and _is_expected_keys(left, context)
    )


def _guards_nonempty_inequality(
    left: ast.AST,
    op: ast.cmpop,
    right: ast.AST,
    context: _ScanGuardContext,
) -> bool:
    if not isinstance(op, ast.NotEq):
        return False
    return (
        _is_scan_result(left, context) and _collection_size(right) == 0
    ) or (
        _is_scan_result(right, context) and _collection_size(left) == 0
    )


def _guards_known_count(
    left: ast.AST,
    op: ast.cmpop,
    right: ast.AST,
    context: _ScanGuardContext,
) -> bool:
    left_count = _len_of_scan(left, context)
    right_count = _len_of_scan(right, context)
    left_value = _integer_literal(left)
    right_value = _integer_literal(right)
    if isinstance(op, ast.Eq):
        return (left_count and (right_value or 0) > 0) or (
            right_count and (left_value or 0) > 0
        )
    if isinstance(op, ast.Gt):
        return left_count and right_value is not None and right_value >= 0
    return (
        isinstance(op, ast.GtE)
        and left_count
        and right_value is not None
        and right_value > 0
    )


_GUARD_PREDICATES = (
    _guards_membership,
    _guards_exact_keys,
    _guards_nonempty_inequality,
    _guards_known_count,
)


def _comparison_guards_scan(
    left: ast.AST,
    op: ast.cmpop,
    right: ast.AST,
    context: _ScanGuardContext,
) -> bool:
    return any(predicate(left, op, right, context) for predicate in _GUARD_PREDICATES)


_ASSERTION_OPERATORS = {
    "assertEqual": ast.Eq,
    "assertNotEqual": ast.NotEq,
    "assertIn": ast.In,
    "assertGreater": ast.Gt,
    "assertGreaterEqual": ast.GtE,
}


def _truthy_assertion_target(node: ast.AST) -> ast.AST | None:
    if isinstance(node, ast.Assert) and not isinstance(node.test, ast.Compare):
        return node.test
    if isinstance(node, ast.Call) and _call_name(node) == "assertTrue" and node.args:
        return node.args[0]
    return None


def _assertion_comparison(node: ast.AST) -> tuple[ast.AST, ast.cmpop, ast.AST] | None:
    if (
        isinstance(node, ast.Assert)
        and isinstance(node.test, ast.Compare)
        and len(node.test.ops) == len(node.test.comparators) == 1
    ):
        return node.test.left, node.test.ops[0], node.test.comparators[0]
    if not isinstance(node, ast.Call) or len(node.args) < 2:
        return None
    operator = _ASSERTION_OPERATORS.get(_call_name(node))
    if operator is None:
        return None
    return node.args[0], operator(), node.args[1]


def _is_conditional_guard(
    node: ast.AST,
    parents: dict[ast.AST, ast.AST],
    names: frozenset[str],
) -> bool:
    parent = parents.get(node)
    while parent is not None:
        condition = None
        if isinstance(parent, (ast.For, ast.AsyncFor)):
            condition = parent.iter
        elif isinstance(parent, (ast.If, ast.While)):
            condition = parent.test
        if condition is not None and any(
            isinstance(part, ast.Name) and part.id in names
            for part in ast.walk(condition)
        ):
            return True
        parent = parents.get(parent)
    return False


def _node_guards_scan(node: ast.AST, context: _ScanGuardContext) -> bool:
    truthy_target = _truthy_assertion_target(node)
    if truthy_target is not None and _is_scan_result(truthy_target, context):
        return True
    comparison = _assertion_comparison(node)
    return comparison is not None and _comparison_guards_scan(*comparison, context)


def _has_scan_guard(
    node: ast.AST,
    names: set[str],
    materialized_names: set[str],
    imported_names: set[str],
) -> bool:
    context = _ScanGuardContext(
        frozenset(names),
        frozenset(materialized_names),
        frozenset(_expected_key_names(node, imported_names)),
        frozenset(imported_names),
    )
    parents = {
        child: parent
        for parent in ast.walk(node)
        for child in ast.iter_child_nodes(parent)
    }
    return any(
        _node_guards_scan(child, context)
        for child in ast.walk(node)
        if not _is_conditional_guard(child, parents, context.names)
    )


def _vacuous_source_scan_line(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    imported_names: set[str],
) -> int | None:
    line, scan_names, materialized_names = _source_scan_names(node, imported_names)
    if line is None or _has_scan_guard(
        node, scan_names, materialized_names, imported_names
    ):
        return None
    return line


def _vacuous_source_scan_issues(
    path: Path,
    qualified: str,
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    imported_names: set[str],
) -> tuple[TestIssue, ...]:
    line = _vacuous_source_scan_line(node, imported_names)
    if line is None:
        return ()
    return (TestIssue(
        "vacuous_source_scan",
        str(path),
        line,
        qualified,
        "source scan has no non-empty or exact-key-set assertion",
    ),)


def _module_names(path: Path, tests_root: Path) -> tuple[str, ...]:
    relative = path.relative_to(tests_root).with_suffix("")
    parts = relative.parts[:-1] if relative.name == "__init__" else relative.parts
    dotted = ".".join(parts)
    return tuple(name for name in (dotted, f"tests.{dotted}" if dotted else "tests") if name)


@dataclass(frozen=True)
class _TestModule:
    path: Path

    @cached_property
    def tree(self) -> ast.Module:
        return ast.parse(self.path.read_text(encoding="utf-8"), filename=str(self.path))


def _test_module_index(tests_root: Path) -> dict[str, _TestModule]:
    modules: dict[str, _TestModule] = {}
    for path in tests_root.rglob("*.py"):
        module = _TestModule(path)
        for name in _module_names(path, tests_root):
            modules[name] = module
    return modules


def _module_binds_name(node: ast.AST, name: str) -> bool:
    if isinstance(node, (
        ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef,
        ast.ExceptHandler, ast.MatchAs, ast.MatchStar,
    )):
        return node.name == name
    if isinstance(node, ast.MatchMapping):
        return node.rest == name
    if isinstance(node, ast.Name):
        return node.id == name and isinstance(node.ctx, (ast.Store, ast.Del))
    if isinstance(node, ast.Import):
        return any((alias.asname or alias.name.partition(".")[0]) == name for alias in node.names)
    if isinstance(node, ast.ImportFrom):
        return any(alias.name == "*" or (alias.asname or alias.name) == name for alias in node.names)
    return False


def _module_binding_nodes(node: ast.AST, name: str) -> list[ast.AST]:
    if _module_binds_name(node, name):
        return [node]
    if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
        return []
    return [
        binding for child in ast.iter_child_nodes(node)
        for binding in _module_binding_nodes(child, name)
    ]


def _import_module_name(
    node: ast.ImportFrom,
    current_module: str,
    modules: dict[str, _TestModule],
) -> str | None:
    if not node.level:
        return node.module
    package = current_module.split(".")
    if modules[current_module].path.name != "__init__.py":
        package.pop()
    if node.level > len(package):
        return None
    parts = package[: len(package) - node.level + 1]
    if node.module:
        parts.extend(node.module.split("."))
    return ".".join(parts)


_STDLIB_UNITTEST = "<stdlib unittest>"


def _import_binding(
    node: ast.Import | ast.ImportFrom,
    name: str,
    current_module: str,
    modules: dict[str, _TestModule],
) -> tuple[str, str] | None:
    from_import = isinstance(node, ast.ImportFrom)
    alias = next((
        alias for alias in node.names
        if (alias.asname or (alias.name if from_import else alias.name.partition(".")[0])) == name
    ), None)
    if alias is None:
        return None
    imported = _import_module_name(node, current_module, modules) if from_import else alias.name
    bound_module = alias.name if alias.asname else alias.name.partition(".")[0]
    if imported in {"unittest", "unittest.case"} and not {"unittest", imported}.intersection(modules):
        member = alias.name if from_import else bound_module.partition(".")[2]
        return (_STDLIB_UNITTEST, member)
    if imported not in modules:
        return None
    if not from_import:
        return (bound_module, "")
    child = f"{imported}.{alias.name}"
    return (child, "") if child in modules else (imported, alias.name)


class _TestCaseResolver:
    def __init__(self, modules: dict[str, _TestModule]) -> None:
        self.modules = modules
        self.resolved: dict[tuple[str, str], bool] = {}
        self.resolving: set[tuple[str, str]] = set()

    def binding_node(self, module: str, name: str) -> ast.AST | None:
        if module not in self.modules:
            return None
        bindings = _module_binding_nodes(self.modules[module].tree, name)
        return bindings[0] if len(bindings) == 1 else None

    def imported_binding(self, module: str, name: str) -> tuple[str, str] | None:
        node = self.binding_node(module, name)
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            return _import_binding(node, name, module, self.modules)
        return None

    def base_binding(self, module: str, base: ast.expr) -> tuple[str, str] | None:
        if isinstance(base, ast.Name):
            return self.imported_binding(module, base.id) or (module, base.id)
        if not isinstance(base, ast.Attribute):
            return None
        binding = self.base_binding(module, base.value)
        if binding is None:
            return None
        owner, member = binding
        if owner == _STDLIB_UNITTEST:
            return (owner, f"{member}.{base.attr}" if member else base.attr)
        if member:
            return None
        child = f"{owner}.{base.attr}"
        return (child, "") if child in self.modules else (owner, base.attr)

    def is_test_case(self, module: str, name: str) -> bool:
        key = (module, name)
        if module == _STDLIB_UNITTEST:
            return name in {"TestCase", "case.TestCase"}
        if key in self.resolved:
            return self.resolved[key]
        if key in self.resolving:
            return False
        self.resolving.add(key)
        node = self.binding_node(module, name)
        if isinstance(node, ast.ClassDef):
            bindings = (self.base_binding(module, base) for base in node.bases)
            result = any(self.is_test_case(*binding) for binding in bindings if binding is not None)
        else:
            binding = self.imported_binding(module, name)
            result = binding is not None and self.is_test_case(*binding)
        self.resolving.remove(key)
        self.resolved[key] = result
        return result

    def class_names(self, current_module: str) -> set[str]:
        return {
            node.name for node in self.modules[current_module].tree.body
            if isinstance(node, ast.ClassDef) and self.is_test_case(current_module, node.name)
        }


class _BlankConstants(ast.NodeTransformer):
    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        return ast.copy_location(ast.Constant(value=type(node.value).__name__), node)


def _body_dump(node: ast.FunctionDef | ast.AsyncFunctionDef, *, blank_constants: bool) -> str:
    module = ast.Module(body=node.body, type_ignores=[])
    if blank_constants:
        module = _BlankConstants().visit(module)  # type: ignore[assignment]
    return ast.dump(module, include_attributes=False)


def _test_files(tests_root: Path) -> Iterable[Path]:
    return sorted(tests_root.rglob("test_*.py"))


def audit_test_suite(tests_root: Path) -> TestQualityReport:
    issues: list[TestIssue] = []
    methods: list[tuple[Path, str, ast.FunctionDef | ast.AsyncFunctionDef]] = []

    files = tuple(_test_files(tests_root))
    modules = _test_module_index(tests_root)
    resolver = _TestCaseResolver(modules)
    for path in files:
        module_name = _module_names(path, tests_root)[-1]
        tree = modules[module_name].tree
        test_case_classes = resolver.class_names(module_name)
        imported_names = _imported_names(tree)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
                issues.append(TestIssue(
                    "undiscovered_test_function",
                    str(path),
                    node.lineno,
                    node.name,
                    "unittest discovery ignores module-level test functions",
                ))

            if not isinstance(node, ast.ClassDef):
                continue
            for child in node.body:
                if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if not child.name.startswith("test_"):
                    continue
                qualified = f"{node.name}.{child.name}"
                if node.name not in test_case_classes:
                    issues.append(TestIssue(
                        "undiscovered_test_method",
                        str(path),
                        child.lineno,
                        qualified,
                        "unittest discovery ignores test methods outside TestCase classes",
                    ))
                    continue
                methods.append((path, qualified, child))
                if _assertion_count(child) == 0:
                    issues.append(TestIssue(
                        "assertion_free_test",
                        str(path),
                        child.lineno,
                        qualified,
                        "test contains no assertion or assertion helper call",
                    ))
                if _has_source_text_membership_assertion(child):
                    issues.append(TestIssue(
                        "source_text_membership_check",
                        str(path),
                        child.lineno,
                        qualified,
                        "literal source/file text membership does not prove executable behavior",
                    ))
                issues.extend(
                    _vacuous_source_scan_issues(path, qualified, child, imported_names)
                )

    exact: dict[tuple[Path, str, str], list[tuple[Path, str, ast.FunctionDef | ast.AsyncFunctionDef]]] = defaultdict(list)
    structural: dict[str, list[str]] = defaultdict(list)
    for path, name, node in methods:
        class_name = name.partition(".")[0]
        exact[(path, class_name, _body_dump(node, blank_constants=False))].append((path, name, node))
        structural[_body_dump(node, blank_constants=True)].append(f"{path}:{node.lineno}:{name}")

    for group in exact.values():
        if len(group) < 2:
            continue
        identities = ", ".join(f"{path}:{node.lineno}:{name}" for path, name, node in group)
        for path, name, node in group:
            issues.append(TestIssue(
                "exact_duplicate_test",
                str(path),
                node.lineno,
                name,
                identities,
            ))

    clone_groups = tuple(
        CloneGroup(tuple(group))
        for group in sorted(structural.values(), key=lambda rows: (-len(rows), rows))
        if len(group) > 1
    )
    return TestQualityReport(
        test_files=len(files),
        test_methods=len(methods),
        hard_issues=tuple(sorted(issues, key=lambda issue: (issue.path, issue.line, issue.kind))),
        structural_clones=clone_groups,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tests-root", type=Path, default=Path("tests"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = audit_test_suite(args.tests_root)
    if args.json:
        print(json.dumps({
            "test_files": report.test_files,
            "test_methods": report.test_methods,
            "hard_issues": [asdict(issue) for issue in report.hard_issues],
            "structural_clones": [asdict(group) for group in report.structural_clones],
        }, indent=2))
    else:
        print(f"{report.test_methods} tests across {report.test_files} files")
        print(f"hard issues: {len(report.hard_issues)}")
        for issue in report.hard_issues:
            print(f"- {issue.kind}: {issue.path}:{issue.line} {issue.name} — {issue.detail}")
        print(f"structural clone candidates: {len(report.structural_clones)} groups")
        for group in report.structural_clones:
            print("- " + " | ".join(group.tests))
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
