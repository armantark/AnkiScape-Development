#!/usr/bin/env python3
"""Run Pass 14 structural checks or plan a module's structural placement."""

from __future__ import annotations

import argparse
import importlib.util
import json
import posixpath
import tempfile
from pathlib import Path, PurePosixPath
from types import ModuleType


IMPORT_PROBES = ("ui/ui.py", "ui/completion_dialogs.py")


def load_gate(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("pass14_slop_gate", path.resolve())
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load slop gate: {path}")
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    return gate


def repo_path(value: str, label: str) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or str(path) in {"", "."}:
        raise ValueError(f"{label} must be a repository-relative file path: {value}")
    return str(path)


def blob_lines(blob: bytes | None) -> int:
    return 0 if blob is None else blob.count(b"\n")


def placement_advice(
    destination: str,
    exists: bool,
    directory: dict,
    line_budget: dict,
    origin_inference: dict,
    fan_out: dict,
) -> str:
    advice = []
    if directory["blocked"]:
        advice.append(
            f"{directory['path']} cannot gain another code file under its current "
            "ratchet; use a cohesive subpackage or offset the addition by relocating "
            "a file."
        )
    if exists and not line_budget["remaining_growth"]:
        advice.append(
            f"{destination} has no line-growth headroom; place the helper in a "
            "cohesive neighboring module or subpackage."
        )
    if origin_inference["blocked"]:
        advice.append(
            "The destination imports dependencies outside the origin's eligible "
            "dependency family."
        )
    if fan_out["blocked"]:
        advice.append(
            f"The destination's effective fan-out exceeds its "
            f"{fan_out['growth_ceiling']}-edge growth ceiling."
        )
    if not exists:
        advice.append(
            "Import eligibility and line size remain conditional until the file is "
            "staged; rerun the structural preflight after creating it."
        )
    return " ".join(advice)


def placement_report(gate: ModuleType, destination: str, origin: str) -> dict:
    staged, head, _tracked_count = gate.repository_snapshots()
    if origin not in head:
        raise ValueError(f"origin must be a code file tracked at HEAD: {origin}")
    if PurePosixPath(destination).suffix not in gate.CODE_SUFFIXES:
        raise ValueError(f"destination must use a code-file suffix: {destination}")

    directory = posixpath.dirname(destination) or "."
    head_directories = gate.directory_counts(head)
    current_directories = gate.directory_counts(staged)
    head_count = head_directories.get(directory, 0)
    current_count = current_directories.get(directory, 0)
    proposed_count = current_count + (destination not in staged)
    directory_blocked = (
        head_count >= gate.DIR_FILES_MAX and proposed_count > head_count
    )

    head_lines = blob_lines(head.get(destination))
    current_lines = blob_lines(staged.get(destination))
    line_ceiling = max(gate.FILE_LINES_MAX, head_lines)
    line_blocked = current_lines > line_ceiling

    staged_graph = gate.imports_by_file(staged)
    head_graph = gate.imports_by_file(head)
    _moved, origins, _spans = gate.moved_definitions(staged, head)
    origins = gate.infer_origins_by_edges(staged_graph, head_graph, origins)
    family = {rel for rel, inferred in origins.items() if inferred == origin}
    eligible_dependencies = head_graph.get(origin, set()) | family | {origin}
    current_dependencies = staged_graph.get(destination, set())
    origin_blocked = bool(
        destination in staged
        and current_dependencies - {destination} - eligible_dependencies
    )
    origin_status = "conditional"
    if destination in staged:
        origin_status = "blocked" if origin_blocked else "eligible"

    planned_origins = {**origins, destination: origin}
    fan_out = gate.moved_aware_fan_out(
        destination, current_dependencies, planned_origins
    )
    fan_out_baseline = len(head_graph.get(origin, set()))
    fan_out_ceiling = max(gate.FAN_OUT_MAX, fan_out_baseline)
    fan_out_blocked = fan_out > fan_out_ceiling

    directory_report = {
        "path": directory,
        "head_code_files": head_count,
        "current_code_files": current_count,
        "proposed_code_files": proposed_count,
        "limit": gate.DIR_FILES_MAX,
        "blocked": directory_blocked,
    }
    line_budget = {
        "head_lines": head_lines,
        "current_lines": current_lines,
        "growth_ceiling": line_ceiling,
        "remaining_growth": max(0, line_ceiling - current_lines),
        "blocked": line_blocked,
    }
    origin_inference = {
        "status": origin_status,
        "eligible_dependencies": sorted(eligible_dependencies),
        "current_dependencies": sorted(current_dependencies),
        "blocked": origin_blocked,
    }
    fan_out_report = {
        "current": fan_out,
        "head_baseline": fan_out_baseline,
        "growth_ceiling": fan_out_ceiling,
        "remaining_growth": max(0, fan_out_ceiling - fan_out),
        "blocked": fan_out_blocked,
    }
    blocked = any(
        (directory_blocked, line_blocked, origin_blocked, fan_out_blocked)
    )
    return {
        "destination": destination,
        "origin": origin,
        "directory": directory_report,
        "line_budget": line_budget,
        "origin_inference": origin_inference,
        "fan_out": fan_out_report,
        "blocked": blocked,
        "advice": placement_advice(
            destination,
            destination in staged,
            directory_report,
            line_budget,
            origin_inference,
            fan_out_report,
        ),
    }


def structural_report(gate: ModuleType) -> dict:
    paths = gate.staged_paths()
    snapshots = gate.repository_snapshots()
    staged, head, _tracked_count = snapshots
    _moved, origin_of, moved_spans = gate.moved_definitions(staged, head)

    staged_graph = gate.imports_by_file(staged)
    head_graph = gate.imports_by_file(head)
    inferred_origins = gate.infer_origins_by_edges(staged_graph, head_graph, origin_of)
    imports = {
        rel: {
            "current": sorted(staged_graph.get(rel, set())),
            "head": sorted(head_graph.get(rel, set())),
            "inferred_origin": inferred_origins.get(rel),
        }
        for rel in IMPORT_PROBES
    }
    violations = [
        {"check": "modularity", "title": title, "rows": rows, "advice": advice}
        for title, rows, advice in gate.modularity_reports(paths, snapshots, origin_of)
        if rows
    ]
    violations.extend(static_analysis_violations(gate, paths, staged, head, moved_spans))
    return {
        "staged_paths": paths,
        "import_probes": imports,
        "violations": violations,
    }


def static_analysis_violations(
    gate: ModuleType,
    paths: list[str],
    staged: dict[str, bytes],
    head: dict[str, bytes],
    moved_spans: dict[str, list[tuple[int, int]]],
) -> list[dict]:
    with tempfile.TemporaryDirectory(prefix="pass14-imports-") as temporary:
        staged_root = Path(temporary) / "staged"
        head_root = Path(temporary) / "head"
        for snapshot_root, blobs in ((staged_root, staged), (head_root, head)):
            snapshot_root.mkdir()
            for rel in sorted(set(paths).intersection(blobs)):
                destination = snapshot_root / rel
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(blobs[rel])
        dead = sorted(
            gate.dead_code_findings(staged_root, moved_spans)
            - gate.dead_code_findings(head_root)
        )
        layout = gate.layout_ratchet(
            gate.pep8_layout_findings(staged_root, moved_spans),
            gate.pep8_layout_findings(head_root),
        )

    violations = []
    if dead:
        violations.append(
            {
                "check": "dead_code",
                "title": "new dead code was introduced:",
                "rows": [{"path": path, "message": message} for path, message in dead],
            }
        )
    if layout:
        violations.append(
            {
                "check": "pep8_layout",
                "title": "PEP 8 layout violations were introduced:",
                "rows": layout,
            }
        )
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hook", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--placement",
        metavar="DESTINATION",
        help="report structural capacity for a proposed repository-relative module",
    )
    parser.add_argument(
        "--origin",
        help="HEAD-tracked module whose code would move to --placement",
    )
    args = parser.parse_args()
    if bool(args.placement) != bool(args.origin):
        parser.error("--placement and --origin must be provided together")

    try:
        gate = load_gate(args.hook)
        if args.placement:
            report = placement_report(
                gate,
                repo_path(args.placement, "destination"),
                repo_path(args.origin, "origin"),
            )
            failed = report["blocked"]
        else:
            report = structural_report(gate)
            failed = bool(report["violations"])
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
