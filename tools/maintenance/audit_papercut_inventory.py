#!/usr/bin/env python3
"""Check that a source-bound papercut inventory accounts for every incident."""

from __future__ import annotations

import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess


INCIDENT = re.compile(r"^(?:-\s+)?\d{4}-\d{2}-\d{2}(?:\b|T)")
DISPOSITIONS = {
    "fixed-before", "fixed-this-pass", "operator-error", "external-blocker",
    "design-decision", "paused-feature", "repair-now",
}


def source_coverage(repo: Path, baseline: str, source: str, groups: list) -> tuple[bytes, dict]:
    payload = subprocess.check_output(
        ["git", "-C", str(repo), "show", f"{baseline}:{source}"],
    )
    text = gzip.decompress(payload) if source.endswith(".gz") else payload
    expected = {
        line for line, value in enumerate(text.decode("utf-8").splitlines(), 1)
        if INCIDENT.match(value)
    }
    assigned = Counter(line for group in groups for line in group["incident_lines"])
    return payload, {
        "source": source,
        "incidents": len(expected),
        "missing": sorted(expected - assigned.keys()),
        "extra": sorted(assigned.keys() - expected),
        "repeated": sorted(line for line, count in assigned.items() if count != 1),
    }


def audit(repo: Path, inventory: dict) -> dict:
    baseline = inventory["baseline"]
    groups = inventory["groups"]
    identifiers = Counter(group["id"] for group in groups)
    errors = [f"duplicate group: {key}" for key, count in identifiers.items() if count != 1]
    by_source: dict[str, list] = {}
    for group in groups:
        by_source.setdefault(group["source"], []).append(group)
        if group["disposition"] not in DISPOSITIONS or not group["evidence"]:
            errors.append(f"invalid disposition or missing evidence: {group['id']}")
    coverage = []
    for source, expected_hash in inventory["sources"].items():
        payload, result = source_coverage(repo, baseline, source, by_source.get(source, []))
        if hashlib.sha256(payload).hexdigest() != expected_hash:
            errors.append(f"source hash mismatch: {source}")
        if any(result[key] for key in ("missing", "extra", "repeated")):
            errors.append(f"coverage mismatch: {source}")
        coverage.append(result)
    unknown = sorted(by_source.keys() - inventory["sources"].keys())
    errors.extend(f"unknown source: {source}" for source in unknown)
    return {"baseline": baseline, "coverage": coverage, "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory", type=Path)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    report = audit(args.repo, json.loads(args.inventory.read_text(encoding="utf-8")))
    print(json.dumps(report, indent=2))
    return int(bool(report["errors"]))


if __name__ == "__main__":
    raise SystemExit(main())
