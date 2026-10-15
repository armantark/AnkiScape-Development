"""Check external inputs recorded for generated data."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Mapping


def check_source_digests(
    manifest_path: Path,
    output_name: str,
    source_bytes: Mapping[Path, bytes],
    *,
    source_root: Path,
    accept_source_change: bool = False,
) -> dict[str, str]:
    root = source_root.resolve()
    current = {
        path.resolve().relative_to(root).as_posix(): hashlib.sha256(content).hexdigest()
        for path, content in source_bytes.items()
    }
    return check_source_digest_values(manifest_path, output_name, current, accept_source_change=accept_source_change)


def check_source_digest_values(
    manifest_path: Path,
    output_name: str,
    current: Mapping[str, str],
    *,
    accept_source_change: bool = False,
) -> dict[str, str]:
    current = dict(current)
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


def save_source_digests(manifest_path: Path, output_name: str, digests: dict[str, str]) -> None:
    # Imported here so --check, which never publishes, still loads where fcntl does not exist.
    import fcntl

    manifest_path = manifest_path.resolve()
    # The lock inode must survive replacement of the manifest.
    with manifest_path.with_suffix(manifest_path.suffix + ".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        content = source_digest_manifest(manifest_path, output_name, digests).encode("utf-8")
        if manifest_path.exists() and manifest_path.read_bytes() == content:
            return
        with NamedTemporaryFile(dir=manifest_path.parent, prefix=f".{manifest_path.name}.", delete=False) as temporary:
            try:
                temporary.write(content)
                temporary.flush()
                os.replace(temporary.name, manifest_path)
            finally:
                Path(temporary.name).unlink(missing_ok=True)
