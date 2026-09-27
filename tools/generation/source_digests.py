"""Check external inputs recorded for generated data."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Sequence


def check_source_digests(
    manifest_path: Path,
    output_name: str,
    source_paths: Sequence[Path],
    *,
    source_root: Path,
    accept_source_change: bool = False,
) -> dict[str, str]:
    root = source_root.resolve()
    current = {
        path.resolve().relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in source_paths
    }
    if not manifest_path.exists():
        return current
    previous = json.loads(manifest_path.read_text(encoding="utf-8")).get(output_name)
    if previous is not None and previous != current and not accept_source_change:
        changed = sorted(name for name in previous.keys() | current.keys() if previous.get(name) != current.get(name))
        raise ValueError(f"Source changed for {output_name}: {', '.join(changed)}; pass --accept-source-change")
    return current


def source_digest_manifest(manifest_path: Path, output_name: str, digests: dict[str, str]) -> str:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    manifest[output_name] = digests
    return json.dumps(manifest, indent=2, sort_keys=True) + "\n"
