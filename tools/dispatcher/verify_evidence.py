#!/usr/bin/env python3
"""Verify plaintext and gzip artifacts declared by an evidence manifest."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
import zlib
from collections.abc import Mapping, Sequence
from pathlib import Path


PLAIN_FIELDS = frozenset(("bytes", "sha256"))
GZIP_FIELDS = frozenset(
    ("gzip_bytes", "gzip_sha256", "plaintext_bytes", "plaintext_sha256")
)


class EvidenceVerificationError(RuntimeError):
    pass


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _artifact_path(root: Path, name: str) -> Path:
    path = (root / name).resolve()
    if not path.is_relative_to(root):
        raise EvidenceVerificationError(f"{name}: path is outside artifact directory")
    return path


def _verify_value(name: str, field: str, actual: object, expected: object) -> None:
    if actual != expected:
        raise EvidenceVerificationError(
            f"{name}: {field} mismatch: expected {expected}, got {actual}"
        )


def _verify_payload(
    name: str,
    declaration: Mapping[str, object],
    data: bytes,
    prefix: str = "",
) -> None:
    bytes_field = f"{prefix}bytes"
    hash_field = f"{prefix}sha256"
    _verify_value(name, bytes_field, len(data), declaration[bytes_field])
    _verify_value(name, hash_field, _sha256(data), declaration[hash_field])


def _verify_gzip(name: str, declaration: Mapping[str, object], data: bytes) -> None:
    _verify_payload(name, declaration, data, "gzip_")
    try:
        plaintext = gzip.decompress(data)
    except (EOFError, OSError, zlib.error) as exc:
        raise EvidenceVerificationError(f"{name}: invalid gzip data: {exc}") from exc
    _verify_payload(name, declaration, plaintext, "plaintext_")


def _verify_artifact(
    root: Path,
    name: str,
    declaration: object,
) -> None:
    if not isinstance(declaration, Mapping):
        raise EvidenceVerificationError(f"{name}: declaration must be an object")
    fields = frozenset(declaration)
    if fields not in (PLAIN_FIELDS, GZIP_FIELDS):
        raise EvidenceVerificationError(
            f"{name}: unsupported hash declaration; expected {sorted(PLAIN_FIELDS)} "
            f"or {sorted(GZIP_FIELDS)}"
        )
    path = _artifact_path(root, name)
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise EvidenceVerificationError(f"{name}: cannot read artifact: {exc}") from exc
    if fields == PLAIN_FIELDS:
        _verify_payload(name, declaration, data)
    else:
        _verify_gzip(name, declaration, data)


def verify_manifest(manifest_path: Path, artifact_dir: Path) -> int:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise EvidenceVerificationError(f"cannot read manifest: {exc}") from exc
    if not isinstance(manifest, Mapping) or not isinstance(manifest.get("artifacts"), Mapping):
        raise EvidenceVerificationError("manifest must contain an artifacts object")
    artifacts = manifest["artifacts"]
    root = artifact_dir.resolve()
    for name, declaration in artifacts.items():
        _verify_artifact(root, name, declaration)
    return len(artifacts)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument(
        "artifact_dir",
        type=Path,
        help="directory containing every artifact named by the manifest",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        count = verify_manifest(args.manifest, args.artifact_dir)
    except (EvidenceVerificationError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Verified {count} artifacts from {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
