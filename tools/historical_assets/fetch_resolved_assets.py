#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Install exact wiki revisions from a resolved asset manifest.

The manifest supplies already-resolved archive URLs and source SHA-1 values.
Downloaded bytes are verified before the existing asset normalization rules are
applied: combat enemy art is capped at 48 pixels, while item sprites retain
their source dimensions after transparent padding is trimmed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.fetch_assets import AssetFetchError, HttpWikiClient, write_png  # noqa: E402

NO_REVISION = "NO PRE-CUTOFF REVISION"
COMBAT_SIZE = 48
MAX_ITEM_DIMENSION = 128
MAX_NORMALIZED_BYTES = 128 * 1024
SHA1_ATTEMPTS = 4


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file_obj:
        return json.load(file_obj)


def _write_json(path: Path, value: Any) -> None:
    with NamedTemporaryFile(
        "w", delete=False, dir=str(path.parent), encoding="utf-8"
    ) as temp_file:
        temp_name = temp_file.name
        json.dump(value, temp_file, indent=2, sort_keys=True)
        temp_file.write("\n")
    os.replace(temp_name, path)


def _image_details(path: Path) -> tuple[tuple[int, int], int]:
    from PIL import Image

    with Image.open(path) as image:
        image.load()
        dimensions = image.size
    return dimensions, path.stat().st_size


def _suspicious_reason(
    asset: str,
    old_dimensions: tuple[int, int] | None,
    old_size: int | None,
    new_dimensions: tuple[int, int],
    new_size: int,
) -> str | None:
    if asset.startswith("combatenemies/"):
        if max(new_dimensions) > COMBAT_SIZE:
            return f"combat sprite dimensions {new_dimensions} exceed {COMBAT_SIZE}px"
        return None

    if max(new_dimensions) > MAX_ITEM_DIMENSION:
        return f"item sprite dimensions {new_dimensions} exceed {MAX_ITEM_DIMENSION}px"
    if new_size > MAX_NORMALIZED_BYTES:
        return f"normalized file size {new_size} exceeds {MAX_NORMALIZED_BYTES} bytes"
    if old_dimensions and max(old_dimensions) <= 64 and max(new_dimensions) > max(old_dimensions) * 4:
        return f"dimensions jumped from {old_dimensions} to {new_dimensions}"
    if old_size and new_size > max(MAX_NORMALIZED_BYTES, old_size * 20):
        return f"file size jumped from {old_size} to {new_size} bytes"
    return None


def install_assets(
    manifest_path: Path,
    prefix: str | None,
    dry_run: bool,
    report_path: Path | None,
) -> int:
    manifest = _load_json(manifest_path)
    if not isinstance(manifest, list):
        raise AssetFetchError("Resolved asset manifest must be a JSON list.")

    provenance_path = REPO_ROOT / "assets_provenance.json"
    provenance = _load_json(provenance_path)
    if not isinstance(provenance, dict):
        raise AssetFetchError("assets_provenance.json must be a JSON object.")

    client = HttpWikiClient()
    replaced: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []

    for entry in manifest:
        if not isinstance(entry, dict):
            skipped.append({"asset": "<invalid entry>", "reason": "manifest row is not an object"})
            continue
        asset = str(entry.get("asset", ""))
        if prefix and not asset.startswith(prefix.rstrip("/") + "/"):
            continue
        if not asset:
            skipped.append({"asset": "<missing asset>", "reason": "manifest row has no asset path"})
            continue
        if entry.get("revision_timestamp") == NO_REVISION:
            skipped.append({"asset": asset, "reason": "no pre-cutoff revision"})
            print(f"SKIP {asset}: no pre-cutoff revision")
            continue

        output_path = (REPO_ROOT / asset).resolve()
        try:
            output_path.relative_to(REPO_ROOT)
        except ValueError:
            skipped.append({"asset": asset, "reason": "asset path escapes repository root"})
            print(f"SKIP {asset}: asset path escapes repository root")
            continue

        expected_sha1 = str(entry.get("sha1", ""))
        image_url = str(entry.get("image_url", ""))
        timestamp = str(entry.get("revision_timestamp", ""))
        # MediaWiki emits archive URLs with an encoded exclamation mark, but
        # the wiki CDN can incorrectly cache those paths as a different file
        # revision. The literal delimiter addresses the same archive object
        # and consistently returns the imageinfo SHA-1 advertised by the API.
        download_url = image_url.replace("%21", "!")
        separator = "&" if "?" in download_url else "?"
        source_bytes: bytes | None = None
        actual_sha1 = ""
        try:
            for verify_attempt in range(SHA1_ATTEMPTS):
                attempt_url = (
                    f"{download_url}{separator}ankiscape_sha1={expected_sha1}"
                    f"&ankiscape_attempt={verify_attempt}"
                )
                candidate_bytes = client.download_bytes(attempt_url)
                actual_sha1 = hashlib.sha1(candidate_bytes).hexdigest()
                if actual_sha1 == expected_sha1:
                    source_bytes = candidate_bytes
                    break
        except AssetFetchError as exc:
            skipped.append({"asset": asset, "reason": str(exc)})
            print(f"SKIP {asset}: {exc}")
            continue

        if source_bytes is None:
            reason = (
                f"SHA-1 mismatch after {SHA1_ATTEMPTS} attempts: "
                f"expected {expected_sha1}, last got {actual_sha1}"
            )
            skipped.append({"asset": asset, "reason": reason})
            print(f"SKIP {asset}: {reason}")
            continue

        old_dimensions: tuple[int, int] | None = None
        old_size: int | None = None
        if output_path.exists():
            try:
                old_dimensions, old_size = _image_details(output_path)
            except Exception as exc:
                skipped.append({"asset": asset, "reason": f"existing image is unreadable: {exc}"})
                print(f"SKIP {asset}: existing image is unreadable: {exc}")
                continue

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(
            "wb", delete=False, dir=str(output_path.parent), suffix=".png"
        ) as temp_file:
            normalized_path: Path | None = Path(temp_file.name)
        try:
            size = COMBAT_SIZE if asset.startswith("combatenemies/") else None
            write_png(source_bytes, normalized_path, size=size)
            new_dimensions, new_size = _image_details(normalized_path)
            suspicious = _suspicious_reason(
                asset,
                old_dimensions,
                old_size,
                new_dimensions,
                new_size,
            )
            if suspicious:
                skipped.append({"asset": asset, "reason": suspicious})
                print(f"SKIP {asset}: {suspicious}")
                continue
            if not dry_run:
                os.replace(normalized_path, output_path)
                normalized_path = None
                row = provenance.get(asset)
                if not isinstance(row, dict):
                    row = {}
                    provenance[asset] = row
                row.update(
                    {
                        "image_url": image_url,
                        "timestamp": timestamp,
                        "sha1": expected_sha1,
                        "size": len(source_bytes),
                    }
                )
            replaced.append(
                {
                    "asset": asset,
                    "source_size": len(source_bytes),
                    "normalized_size": new_size,
                    "dimensions": list(new_dimensions),
                }
            )
            print(
                f"{'CHECK' if dry_run else 'OK'} {asset}: "
                f"sha1={actual_sha1} source={len(source_bytes)} bytes "
                f"normalized={new_size} bytes {new_dimensions[0]}x{new_dimensions[1]}"
            )
        except Exception as exc:
            skipped.append({"asset": asset, "reason": f"normalization failed: {exc}"})
            print(f"SKIP {asset}: normalization failed: {exc}")
        finally:
            if normalized_path is not None and normalized_path.exists():
                normalized_path.unlink()

    if not dry_run:
        _write_json(provenance_path, provenance)

    report = {
        "manifest": str(manifest_path),
        "prefix": prefix,
        "dry_run": dry_run,
        "replaced": replaced,
        "skipped": skipped,
        "replaced_count": len(replaced),
        "skipped_count": len(skipped),
    }
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        _write_json(report_path, report)
    print(json.dumps({"replaced_count": len(replaced), "skipped_count": len(skipped)}))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="Resolved asset JSON manifest.")
    parser.add_argument("--prefix", help="Only process assets under this repository-relative directory.")
    parser.add_argument("--dry-run", action="store_true", help="Verify and normalize without replacing files.")
    parser.add_argument("--report", type=Path, help="Write a machine-readable result report.")
    args = parser.parse_args(argv)
    try:
        return install_assets(args.manifest, args.prefix, args.dry_run, args.report)
    except (AssetFetchError, OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
