#!/usr/bin/env python3
"""Preflight recurring Codex Workflows manifest mistakes before launch."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence


DEFAULT_CLI = Path("/Users/ArmanTarkhanian1/.local/bin/codex-workflows")
BUDGET_FIELDS = (
    "max_output_tokens",
    "max_processed_tokens",
    "max_tool_calls",
    "max_tool_output_bytes",
)


def _validate_object_schema(schema: Any, location: str, errors: list[str]) -> None:
    if isinstance(schema, list):
        for index, child in enumerate(schema):
            _validate_object_schema(child, f"{location}[{index}]", errors)
        return
    if not isinstance(schema, dict):
        return
    if schema.get("type") == "object" and schema.get("additionalProperties") is not False:
        errors.append(f"{location}: object schemas must set additionalProperties to false")
    for key, child in schema.items():
        _validate_object_schema(child, f"{location}.{key}", errors)


def validate_manifest(manifest: Any) -> list[str]:
    if not isinstance(manifest, dict):
        return ["manifest must be a JSON object"]
    errors: list[str] = []
    cwd = manifest.get("cwd")
    if not isinstance(cwd, str) or not Path(cwd).is_absolute():
        errors.append("cwd must be an absolute path")
    elif not Path(cwd).is_dir():
        errors.append(f"cwd does not exist: {cwd}")

    jobs = manifest.get("jobs")
    if not isinstance(jobs, list) or not jobs:
        errors.append("jobs must be a non-empty array")
        return errors
    for index, job in enumerate(jobs):
        location = f"jobs[{index}]"
        if not isinstance(job, dict):
            errors.append(f"{location} must be an object")
            continue
        mode = job.get("mode")
        if mode not in (None, "read", "write"):
            errors.append(f"{location}.mode must be 'read' or 'write', not {mode!r}")
        budget = job.get("budget")
        if budget is not None and not isinstance(budget, dict):
            errors.append(f"{location}.budget must be an object")
        elif isinstance(budget, dict):
            for field in BUDGET_FIELDS:
                value = budget.get(field)
                if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value < 1):
                    errors.append(f"{location}.budget.{field} must be an integer of at least 1")
        _validate_object_schema(job.get("output_schema"), f"{location}.output_schema", errors)
    return errors


def _read_manifest(path: str) -> Any:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    return json.loads(text)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", help="manifest JSON path, or - for standard input")
    parser.add_argument("--start", action="store_true", help="launch through codex-workflows after preflight")
    parser.add_argument(
        "--cli",
        type=Path,
        default=Path(os.environ.get("CODEX_WORKFLOWS_CLI", DEFAULT_CLI)),
    )
    args = parser.parse_args(argv)

    try:
        manifest = _read_manifest(args.manifest)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Invalid manifest input: {exc}", file=sys.stderr)
        return 2
    errors = validate_manifest(manifest)
    if errors:
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 2
    print("Workflow manifest preflight passed.")
    if not args.start:
        return 0
    if not args.cli.is_file():
        print(f"Codex Workflows CLI not found: {args.cli}", file=sys.stderr)
        return 2
    completed = subprocess.run(
        [str(args.cli), "start", "-"],
        input=json.dumps(manifest),
        text=True,
        check=False,
    )
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
