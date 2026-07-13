#!/usr/bin/env python3
"""Audit unittest files for mechanically detectable low-signal tests."""

from __future__ import annotations

import argparse
import ast
import json
from collections import defaultdict
from dataclasses import asdict, dataclass
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
        or (isinstance(child, ast.Call) and _call_name(child).startswith("assert"))
        for child in ast.walk(node)
    )


def _reads_open_file(node: ast.AST) -> bool:
    return any(
        isinstance(child, ast.Call) and _call_name(child) in {"open", "read"}
        for child in ast.walk(node)
    )


def _has_literal_membership_assertion(node: ast.AST) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Assert) and isinstance(child.test, ast.Compare):
            if any(isinstance(op, (ast.In, ast.NotIn)) for op in child.test.ops):
                if isinstance(child.test.left, ast.Constant) and isinstance(child.test.left.value, str):
                    return True
        if isinstance(child, ast.Call) and _call_name(child) in {"assertIn", "assertNotIn"}:
            if child.args and isinstance(child.args[0], ast.Constant) and isinstance(child.args[0].value, str):
                return True
    return False


class _BlankConstants(ast.NodeTransformer):
    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        return ast.copy_location(ast.Constant(value=type(node.value).__name__), node)


def _body_dump(node: ast.FunctionDef | ast.AsyncFunctionDef, *, blank_constants: bool) -> str:
    module = ast.Module(body=node.body, type_ignores=[])
    if blank_constants:
        module = _BlankConstants().visit(module)  # type: ignore[assignment]
    return ast.dump(module, include_attributes=False)


def _test_files(tests_root: Path) -> Iterable[Path]:
    return sorted(tests_root.glob("test_*.py"))


def audit_test_suite(tests_root: Path) -> TestQualityReport:
    issues: list[TestIssue] = []
    methods: list[tuple[Path, str, ast.FunctionDef | ast.AsyncFunctionDef]] = []

    files = tuple(_test_files(tests_root))
    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
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
                methods.append((path, qualified, child))
                if _assertion_count(child) == 0:
                    issues.append(TestIssue(
                        "assertion_free_test",
                        str(path),
                        child.lineno,
                        qualified,
                        "test contains no assertion or assertion helper call",
                    ))
                if _reads_open_file(child) and _has_literal_membership_assertion(child):
                    issues.append(TestIssue(
                        "source_text_membership_check",
                        str(path),
                        child.lineno,
                        qualified,
                        "literal source/file text membership does not prove executable behavior",
                    ))

    exact: dict[str, list[tuple[Path, str, ast.FunctionDef | ast.AsyncFunctionDef]]] = defaultdict(list)
    structural: dict[str, list[str]] = defaultdict(list)
    for path, name, node in methods:
        exact[_body_dump(node, blank_constants=False)].append((path, name, node))
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
