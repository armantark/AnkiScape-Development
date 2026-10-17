#!/usr/bin/env python3
"""Measure named Python functions with slop-gate's instruments.

--output names one evidence file outside the worktrees (the common Git directory
is allowed). Exit 1 means a selected function exceeds a gate limit; invalid
inputs or missing instruments exit 2 without publishing a report. Name one
source file, then each function by its file-unique bare name; the gate's tables
key on bare names, so qualified names cannot disambiguate repeated methods and a
nested function is measurable only as its enclosing function.

Requires the fleet slop_gate.py and its uv-installed lizard, complexipy and radon.
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GATE = Path.home() / "fleet/config/git/hooks/slop_gate.py"


def validate_output(source: Path, output: Path) -> None:
    roots = {ROOT, source.parent}
    common = None
    if (ROOT / ".git").exists():
        listing = subprocess.check_output(
            ["git", "-C", str(ROOT), "worktree", "list", "--porcelain"], text=True,
        )
        roots.update(Path(line.removeprefix("worktree ")).resolve()
                     for line in listing.splitlines() if line.startswith("worktree "))
        common = Path(subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "--path-format=absolute", "--git-common-dir"], text=True,
        ).strip()).resolve()
    if output.is_dir() or not output.parent.is_dir():
        raise ValueError("--output must name a file in an existing evidence directory")
    if any(output.is_relative_to(root) for root in roots) and not (
        common is not None and output.is_relative_to(common)
    ):
        raise ValueError(
            "--output must be outside the worktrees and measured source directory; "
            "use separate sibling source and evidence directories"
        )


def collect_definitions(node: ast.AST, definitions: dict, scope: str = "", enclosing: str | None = None) -> dict:
    """Map bare function names to (qualified name, line, enclosing function or None)."""
    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.ClassDef):
            collect_definitions(child, definitions, f"{scope}{child.name}.", enclosing)
        elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            qualified = scope + child.name
            definitions.setdefault(child.name, []).append((qualified, child.lineno, enclosing))
            collect_definitions(child, definitions, f"{qualified}.", enclosing or child.name)
        else:
            collect_definitions(child, definitions, scope, enclosing)
    return definitions


def validate_selection(tree: ast.AST, names: list[str]) -> None:
    definitions = collect_definitions(tree, {})
    for name in names:
        matches = definitions.get(name.rsplit(".", 1)[-1], [])
        if len(matches) != 1 or "." in name:
            locations = ", ".join(f"{qualified} at line {line}" for qualified, line, _ in matches)
            raise ValueError(
                f"{name}: expected one file-unique bare function name; definitions: {locations or 'none'}; "
                "qualified names are unsupported because slop-gate tables key on bare names"
            )
        qualified, line, enclosing = matches[0]
        if enclosing is not None:
            raise ValueError(
                f"{name}: nested function {qualified} at line {line} has no separate slop-gate "
                f"result; measure enclosing function {enclosing!r} instead"
            )


def measure(source: Path, names: list[str], gate) -> dict:
    # Both the source snapshot and the instrument cwd are disposable: complexipy
    # puts its cache in cwd even when the report has an explicit destination.
    previous = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="ankiscape-function-metrics-") as temporary:
        root = Path(temporary).resolve()
        snapshot = root / "snapshot"
        snapshot.mkdir()
        (snapshot / source.name).write_bytes(source.read_bytes())
        try:
            os.chdir(root)
            tables = {
                "ccn": gate.ccn_by_function(snapshot),
                "cognitive": gate.cognitive_by_function(snapshot),
                "halstead_difficulty": gate.halstead_by_function(snapshot),
            }
        finally:
            os.chdir(previous)
    limits = {"ccn": gate.CCN_MAX, "cognitive": gate.COGNITIVE_MAX, "halstead_difficulty": gate.HALSTEAD_MAX}
    functions = {}
    for name in names:
        row = {}
        for metric, table in tables.items():
            matches = [value for (_, measured), value in table.items() if gate.simple_name(measured) == name]
            if len(matches) != 1:
                raise ValueError(f"{name}: expected one {metric} entry from slop-gate, found {len(matches)}")
            row[metric] = matches[0]
        row["violations"] = {metric: value for metric, value in row.items() if value > limits[metric]}
        functions[name] = row
    return {"file": str(source), "limits": limits, "functions": functions}


def load_gate(path: Path):
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("slop_gate", path)
    if spec is None or spec.loader is None:
        raise ValueError("--slop-gate must name a Python module")
    gate = importlib.util.module_from_spec(spec)
    previous_path = sys.path.copy()
    sys.path.insert(0, str(path.resolve().parent))
    try:
        spec.loader.exec_module(gate)
    finally:
        sys.path[:] = previous_path
    functions = ("ccn_by_function", "cognitive_by_function", "halstead_by_function", "simple_name")
    missing = [name for name in functions if not callable(getattr(gate, name, None))]
    missing.extend(name for name in ("CCN_MAX", "COGNITIVE_MAX", "HALSTEAD_MAX") if not hasattr(gate, name))
    if missing:
        raise ValueError(f"{path}: missing required slop-gate API: {', '.join(missing)}")
    return gate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("file", type=Path)
    parser.add_argument("functions", nargs="+")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--slop-gate", type=Path, default=DEFAULT_GATE)
    args = parser.parse_args()
    try:
        source, output = args.file.resolve(), args.output.resolve()
        if source.suffix != ".py" or not source.is_file():
            raise ValueError(f"file must be an existing Python source file: {args.file}")
        validate_selection(ast.parse(source.read_bytes()), args.functions)
        validate_output(source, output)
        gate = load_gate(args.slop_gate.resolve())
        # Match fleet's pre-commit hook, including uv tool executable discovery.
        os.environ["PATH"] = str(Path.home() / ".local/bin") + os.pathsep + os.environ["PATH"]
        report = measure(source, args.functions, gate)
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, SyntaxError, SystemExit) as error:
        parser.error(str(error))
    for name, row in report["functions"].items():
        for metric, value in row["violations"].items():
            print(f"{name}: {metric} {value:g} > {report['limits'][metric]}", file=sys.stderr)
    print(f"Wrote function metrics: {output}")
    return int(any(row["violations"] for row in report["functions"].values()))


if __name__ == "__main__":
    raise SystemExit(main())
