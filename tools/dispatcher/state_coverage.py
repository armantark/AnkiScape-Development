#!/usr/bin/env python3
"""Run unittest modules and map executed dispatcher state accesses to test cases."""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
DISPATCHER = ROOT / "__init__.py"


class StateAccesses(ast.NodeVisitor):
    def __init__(self):
        self.scope = []
        self.functions = {}
        self.code_names = {}
        self.line_names = {}

    def visit_FunctionDef(self, node):
        self.scope.append(f"{node.name}@{node.lineno}")
        first_line = min([node.lineno, *(item.lineno for item in node.decorator_list)])
        self.code_names[node.name, first_line] = ".".join(self.scope)
        self.generic_visit(node)
        self.scope.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Lambda(self, node):
        self.scope.append(f"<lambda>@{node.lineno}")
        self.code_names["<lambda>", node.lineno] = ".".join(self.scope)
        self.generic_visit(node)
        self.scope.pop()

    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name) and node.value.id == "_state":
            name = ".".join(self.scope)
            function = self.functions.setdefault(name, {"fields": set(), "lines": set()})
            function["fields"].add(node.attr)
            function["lines"].add(node.lineno)
            self.line_names[node.lineno] = name
        self.generic_visit(node)

    def frame_name(self, frame):
        if frame.f_code.co_name in {"<listcomp>", "<dictcomp>", "<setcomp>", "<genexpr>"}:
            return self.line_names.get(frame.f_lineno)
        return self.code_names.get((frame.f_code.co_name, frame.f_code.co_firstlineno))

    def summarize_functions(self, observed):
        functions = {}
        for name, definition in self.functions.items():
            tests = observed[name]
            covered = {line for lines in tests.values() for line in lines}
            functions[name] = {
                "fields": sorted(definition["fields"]),
                "state_lines": sorted(definition["lines"]),
                "executed_state_lines": sorted(covered),
                "unexecuted_state_lines": sorted(definition["lines"] - covered),
                "tests": {test: sorted(lines) for test, lines in sorted(tests.items())},
            }
        return functions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("modules", nargs="+", help="Exact unittest module names")
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT))
    survey = StateAccesses()
    survey.visit(ast.parse(DISPATCHER.read_text()))
    observed = {name: {} for name in survey.functions}
    current_test = None

    class Result(unittest.TextTestResult):
        def startTest(self, test):
            nonlocal current_test
            current_test = test.id()
            super().startTest(test)

        def stopTest(self, test):
            nonlocal current_test
            super().stopTest(test)
            current_test = None

    def trace(frame, event, _arg):
        if frame.f_code.co_filename != str(DISPATCHER):
            return None
        if event == "line" and current_test:
            name = survey.frame_name(frame)
            if name in survey.functions and frame.f_lineno in survey.functions[name]["lines"]:
                observed[name].setdefault(current_test, set()).add(frame.f_lineno)
        return trace

    suite = unittest.defaultTestLoader.loadTestsFromNames(args.modules)
    previous_trace = sys.gettrace()
    try:
        sys.settrace(trace)
        result = unittest.TextTestRunner(verbosity=1, resultclass=Result).run(suite)
    finally:
        sys.settrace(previous_trace)
    functions = survey.summarize_functions(observed)
    report = {
        "modules": args.modules,
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "skipped_tests": {test.id(): reason for test, reason in result.skipped},
        "functions": functions,
        "unexecuted_functions": sorted(name for name in functions if not observed[name]),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"State access evidence: {args.output}")
    print(f"Unexecuted functions: {len(report['unexecuted_functions'])}/{len(functions)}")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
