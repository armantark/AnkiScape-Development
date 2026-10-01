#!/usr/bin/env python3
"""Run the cheap Pass 14 structural ratchets against the staged snapshot."""

from __future__ import annotations

import argparse
import importlib.util
import json
import tempfile
from pathlib import Path


IMPORT_PROBES = ("ui/ui.py", "ui/completion_dialogs.py")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Pass 14 structural preflight.")
    parser.add_argument("--hook", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    spec = importlib.util.spec_from_file_location("pass14_slop_gate", args.hook.resolve())
    if spec is None or spec.loader is None:
        parser.error(f"cannot load slop gate: {args.hook}")
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
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

    with tempfile.TemporaryDirectory(prefix="pass14-imports-") as temporary:
        temporary_root = Path(temporary)
        staged_root = temporary_root / "staged"
        head_root = temporary_root / "head"
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
    if dead:
        violations.append(
            {
                "check": "dead_code",
                "title": "new dead code was introduced:",
                "rows": [
                    {"path": path, "message": message} for path, message in dead
                ],
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

    report = {
        "staged_paths": paths,
        "import_probes": imports,
        "violations": violations,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
