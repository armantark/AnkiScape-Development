#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Replace Old School-sourced assets with their last pre-EOC revision.

Each recorded file title is queried exactly on the RuneScape Wiki. Historical
archive bytes must match the API SHA-1 before an existing asset is replaced.
Progress is checkpointed under ``tmp/`` so interrupted runs resume safely.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.parse
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.fetch_assets import (  # noqa: E402
    AssetFetchError,
    HttpWikiClient,
    write_png,
    write_source_png,
)

CUTOFF_TIMESTAMP = "2012-11-20T00:00:00Z"
RS_WIKI_API = "https://runescape.wiki/api.php"
RS_WIKI_PAGE_BASE = "https://runescape.wiki/wiki/"
DEFAULT_PROVENANCE_PATH = REPO_ROOT / "assets_provenance.json"
DEFAULT_AUDIT_PATH = (
    REPO_ROOT
    / "memory-bank"
    / "source-audits"
    / "icon-2012-sweep-2026-09-03.md"
)
DEFAULT_CHECKPOINT_PATH = REPO_ROOT / "tmp" / "icon-2012-sweep-checkpoint.json"
DEFAULT_USER_AGENT = (
    "AnkiScape icon-2012-sweep/1.0 "
    "(personal add-on historical asset audit; sequential requests)"
)
CHECKPOINT_SCHEMA_VERSION = 1
DOWNLOAD_ATTEMPTS = 4


@dataclass(frozen=True)
class HistoricalRevision:
    file_title: str
    image_url: str
    timestamp: str
    sha1: str
    archivename: str


def _parse_timestamp(value: object) -> datetime:
    text = str(value or "")
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def select_newest_revision(
    imageinfo: Sequence[Mapping[str, object]],
    cutoff_timestamp: str = CUTOFF_TIMESTAMP,
) -> Optional[Mapping[str, object]]:
    """Return the newest revision strictly before the cutoff, if one exists."""
    cutoff = _parse_timestamp(cutoff_timestamp)
    eligible = [
        revision
        for revision in imageinfo
        if revision.get("timestamp")
        and "filemissing" not in revision
        and _parse_timestamp(revision["timestamp"]) < cutoff
    ]
    if not eligible:
        return None
    return max(eligible, key=lambda revision: _parse_timestamp(revision["timestamp"]))


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(
        "w", delete=False, dir=str(path.parent), encoding="utf-8"
    ) as temp_file:
        temp_name = temp_file.name
        json.dump(value, temp_file, indent=2, sort_keys=True)
        temp_file.write("\n")
    os.replace(temp_name, path)


def _load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as file_obj:
        return json.load(file_obj)


def _is_old_school_entry(entry: Mapping[str, object]) -> bool:
    return all(
        urllib.parse.urlsplit(str(entry.get(field) or "")).hostname
        == "oldschool.runescape.wiki"
        for field in ("file_page_url", "image_url")
    )


def _new_checkpoint(provenance: Mapping[str, object]) -> Dict[str, object]:
    assets: Dict[str, Dict[str, str]] = {}
    for asset_path, raw_entry in sorted(provenance.items()):
        if not isinstance(raw_entry, dict) or not _is_old_school_entry(raw_entry):
            continue
        wiki_title = str(raw_entry.get("file_title") or "").strip()
        if not wiki_title:
            raise AssetFetchError(f"Old School provenance has no file_title: {asset_path}")
        assets[str(asset_path)] = {"wiki_title": wiki_title}
    if not assets:
        raise AssetFetchError("No provenance entries contain two Old School wiki URLs.")
    return {
        "schema_version": CHECKPOINT_SCHEMA_VERSION,
        "cutoff_timestamp": CUTOFF_TIMESTAMP,
        "assets": assets,
        "results": {},
    }


def _load_checkpoint(
    checkpoint_path: Path, provenance: Mapping[str, object]
) -> Dict[str, object]:
    if not checkpoint_path.exists():
        checkpoint = _new_checkpoint(provenance)
        _write_json(checkpoint_path, checkpoint)
        return checkpoint

    checkpoint = _load_json(checkpoint_path)
    if not isinstance(checkpoint, dict):
        raise AssetFetchError("The icon sweep checkpoint must be a JSON object.")
    if checkpoint.get("schema_version") != CHECKPOINT_SCHEMA_VERSION:
        raise AssetFetchError("The icon sweep checkpoint has an unsupported schema version.")
    if checkpoint.get("cutoff_timestamp") != CUTOFF_TIMESTAMP:
        raise AssetFetchError("The icon sweep checkpoint uses a different cutoff.")
    if not isinstance(checkpoint.get("assets"), dict) or not isinstance(
        checkpoint.get("results"), dict
    ):
        raise AssetFetchError("The icon sweep checkpoint is malformed.")
    return checkpoint


def _request_json(
    client: HttpWikiClient, url: str
) -> Mapping[str, object]:
    try:
        payload = client._request_json(url)
    except (AssetFetchError, json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
        raise AssetFetchError(f"Wiki history query failed after retries: {exc}") from exc
    error = payload.get("error")
    if isinstance(error, dict):
        code = str(error.get("code") or "unknown")
        info = str(error.get("info") or "no details")
        raise AssetFetchError(f"MediaWiki API error {code}: {info}")
    return payload


def _query_history_batch(
    client: HttpWikiClient,
    wiki_title: str,
    continuation: Mapping[str, str],
) -> Tuple[str, List[Mapping[str, object]], Dict[str, str], str]:
    params = {
        "action": "query",
        "prop": "imageinfo",
        "titles": f"File:{wiki_title}",
        "iilimit": "50",
        "iiprop": "url|timestamp|archivename|sha1",
        "redirects": "1",
        "format": "json",
    }
    params.update(continuation)
    url = f"{RS_WIKI_API}?{urllib.parse.urlencode(params)}"
    payload = _request_json(client, url)
    query = payload.get("query")
    if not isinstance(query, dict):
        raise AssetFetchError(f"Wiki response omitted query data for File:{wiki_title}.")
    pages = query.get("pages")
    if not isinstance(pages, dict) or not pages:
        raise AssetFetchError(f"Wiki response omitted page data for File:{wiki_title}.")
    page = next(iter(pages.values()))
    if not isinstance(page, dict):
        raise AssetFetchError(f"Wiki returned malformed page data for File:{wiki_title}.")

    canonical_title = str(page.get("title") or f"File:{wiki_title}")
    if "missing" in page:
        return canonical_title, [], {}, "No file exists at that RuneScape Wiki title."
    imageinfo = page.get("imageinfo", [])
    if not isinstance(imageinfo, list):
        raise AssetFetchError(
            f"Wiki returned malformed image history for File:{wiki_title}."
        )
    raw_continue = payload.get("continue")
    next_page = (
        {str(key): str(value) for key, value in raw_continue.items()}
        if isinstance(raw_continue, dict) and raw_continue.get("iicontinue")
        else {}
    )
    revisions = [row for row in imageinfo if isinstance(row, dict)]
    return canonical_title, revisions, next_page, ""


def _historical_revision(
    canonical_title: str, selected: Mapping[str, object]
) -> HistoricalRevision:
    image_url = str(selected.get("url") or "")
    sha1 = str(selected.get("sha1") or "")
    if not image_url or not sha1:
        raise AssetFetchError(
            f"Pre-cutoff revision lacks a URL or SHA-1 for {canonical_title}."
        )
    return HistoricalRevision(
        file_title=canonical_title.removeprefix("File:"),
        image_url=image_url,
        timestamp=str(selected.get("timestamp") or ""),
        sha1=sha1,
        archivename=str(selected.get("archivename") or ""),
    )


def query_pre_cutoff_revision(
    client: HttpWikiClient, wiki_title: str
) -> Tuple[Optional[HistoricalRevision], str]:
    revisions: List[Mapping[str, object]] = []
    continuation: Mapping[str, str] = {}
    canonical_title = f"File:{wiki_title}"
    while True:
        canonical_title, batch, next_page, reason = _query_history_batch(
            client, wiki_title, continuation
        )
        if reason:
            return None, reason
        revisions.extend(batch)
        selected = select_newest_revision(revisions)
        if selected is not None:
            return _historical_revision(canonical_title, selected), ""
        if not next_page:
            break
        continuation = next_page
    if revisions:
        return None, "Every file revision is at or after the pre-EOC cutoff."
    return None, "The RuneScape Wiki file has no revisions."


def _download_revision(
    client: HttpWikiClient, revision: HistoricalRevision
) -> Tuple[Optional[bytes], str]:
    download_url = revision.image_url.replace("%21", "!")
    separator = "&" if "?" in download_url else "?"
    actual_sha1 = ""
    for attempt in range(DOWNLOAD_ATTEMPTS):
        attempt_url = (
            f"{download_url}{separator}ankiscape_sha1={revision.sha1}"
            f"&ankiscape_attempt={attempt}"
        )
        candidate = client.download_bytes(attempt_url)
        actual_sha1 = hashlib.sha1(candidate).hexdigest()
        if actual_sha1 == revision.sha1:
            return candidate, actual_sha1
    return None, actual_sha1


def _png_dimensions(image_bytes: bytes) -> Tuple[int, int]:
    try:
        from PIL import Image, UnidentifiedImageError
    except ImportError as exc:
        raise AssetFetchError("Pillow is required for PNG validation. Run with `uv run`.") from exc
    try:
        with Image.open(BytesIO(image_bytes)) as image:
            image.load()
            width, height = image.size
    except (OSError, UnidentifiedImageError) as exc:
        raise AssetFetchError("An existing sweep asset is not a valid PNG.") from exc
    if width <= 0 or height <= 0:
        raise AssetFetchError("An existing sweep asset has invalid PNG dimensions.")
    return width, height


def _replace_asset(
    output_path: Path,
    source_bytes: bytes,
    recorded_sha1: str,
    already_current: bool,
) -> Tuple[bool, bytes]:
    if not output_path.is_file():
        raise AssetFetchError(f"Sweep asset does not exist: {output_path}")
    existing_bytes = output_path.read_bytes()
    existing_sha1 = hashlib.sha1(existing_bytes).hexdigest()
    if already_current and existing_sha1 == recorded_sha1:
        return False, existing_bytes

    with NamedTemporaryFile(
        "wb", delete=False, dir=str(output_path.parent), suffix=".png"
    ) as temp_file:
        candidate_path = Path(temp_file.name)
    candidate_path.unlink()
    try:
        if existing_sha1 != recorded_sha1:
            width, height = _png_dimensions(existing_bytes)
            write_png(source_bytes, candidate_path, size=max(width, height))
        else:
            write_source_png(source_bytes, candidate_path)
        candidate_bytes = candidate_path.read_bytes()
        changed = candidate_bytes != existing_bytes
        if changed:
            os.replace(candidate_path, output_path)
        return changed, candidate_bytes
    finally:
        candidate_path.unlink(missing_ok=True)


def _file_page_url(file_title: str) -> str:
    quoted_title = urllib.parse.quote(
        f"File:{file_title}".replace(" ", "_"), safe=":/"
    )
    return f"{RS_WIKI_PAGE_BASE}{quoted_title}"


def _provenance_entry(
    revision: HistoricalRevision, written_bytes: bytes
) -> Dict[str, object]:
    return {
        "file_page_url": _file_page_url(revision.file_title),
        "file_title": revision.file_title,
        "image_url": revision.image_url,
        "license_string": "unknown",
        "mediatype": "BITMAP",
        "mime": "image/png",
        "sha1": hashlib.sha1(written_bytes).hexdigest(),
        "size": len(written_bytes),
        "source_wiki": "rs3",
        "timestamp": revision.timestamp,
    }


def _write_audit(
    audit_path: Path, checkpoint: Mapping[str, object]
) -> Dict[str, int]:
    assets = checkpoint["assets"]
    results = checkpoint["results"]
    assert isinstance(assets, dict)
    assert isinstance(results, dict)
    counts = {"fetched": 0, "unchanged": 0, "missing": 0}
    missing_rows: List[Tuple[str, str, str]] = []
    for asset_path in sorted(assets):
        result = results.get(asset_path)
        if not isinstance(result, dict):
            raise AssetFetchError(f"Checkpoint has no result for {asset_path}.")
        status = str(result.get("status") or "")
        if status not in counts:
            raise AssetFetchError(f"Checkpoint has an invalid status for {asset_path}.")
        counts[status] += 1
        if status == "missing":
            missing_rows.append(
                (
                    asset_path,
                    str(result.get("wiki_title") or ""),
                    str(result.get("reason") or "No reason recorded."),
                )
            )

    lines = [
        "# 2012 icon sweep source audit",
        "",
        f"- Cutoff: `{CUTOFF_TIMESTAMP}`; revisions at the cutoff are excluded.",
        (
            f"- Scope: `{len(assets)}` assets whose original provenance carried "
            "two `oldschool.runescape.wiki` URLs."
        ),
        (
            f"- Result: `{counts['fetched']}` fetched with changed PNG bytes, "
            f"`{counts['unchanged']}` fetched with unchanged PNG bytes, and "
            f"`{counts['missing']}` missing a verified pre-cutoff revision."
        ),
        (
            "- Method: exact recorded titles were queried with redirect resolution; "
            "no alternate title or substitute icon was guessed."
        ),
        "- Download verification: every installed archive matched the API SHA-1.",
        "",
        "## Assets without a verified pre-cutoff revision",
        "",
    ]
    if missing_rows:
        lines.extend(
            [
                "| Asset path | RuneScape Wiki title tried | Reason |",
                "| --- | --- | --- |",
            ]
        )
        lines.extend(
            f"| `{path}` | `File:{title}` | {reason} |"
            for path, title, reason in missing_rows
        )
    else:
        lines.append("No assets were missing a verified pre-cutoff revision.")
    lines.append("")
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text("\n".join(lines), encoding="utf-8")
    return counts


def _pending_by_title(
    assets: Mapping[str, object], results: Mapping[str, object]
) -> Dict[str, List[str]]:
    pending: Dict[str, List[str]] = defaultdict(list)
    for asset_path, manifest_row in assets.items():
        if asset_path in results:
            continue
        if not isinstance(manifest_row, dict):
            raise AssetFetchError(f"Checkpoint manifest is malformed for {asset_path}.")
        pending[str(manifest_row["wiki_title"])].append(str(asset_path))
    return pending


def _process_title(
    provenance_path: Path,
    checkpoint_path: Path,
    provenance: Dict[str, object],
    checkpoint: Mapping[str, object],
    results: Dict[str, object],
    client: HttpWikiClient,
    wiki_title: str,
    asset_paths: Sequence[str],
    finished: int,
    total: int,
) -> int:
    revision, missing_reason = query_pre_cutoff_revision(client, wiki_title)
    source_bytes: Optional[bytes] = None
    actual_sha1 = ""
    if revision is not None:
        source_bytes, actual_sha1 = _download_revision(client, revision)
        if source_bytes is None:
            missing_reason = (
                f"Archive SHA-1 mismatch after {DOWNLOAD_ATTEMPTS} attempts: "
                f"expected {revision.sha1}, last got {actual_sha1}."
            )

    if source_bytes is None:
        for asset_path in asset_paths:
            results[asset_path] = {
                "reason": missing_reason,
                "status": "missing",
                "wiki_title": wiki_title,
            }
            finished += 1
            _write_json(checkpoint_path, checkpoint)
            print(
                f"[{finished}/{total}] missing {asset_path}: {missing_reason}",
                flush=True,
            )
        return finished

    assert revision is not None
    for asset_path in asset_paths:
        raw_entry = provenance.get(asset_path)
        if not isinstance(raw_entry, dict):
            raise AssetFetchError(f"Provenance entry is missing for {asset_path}.")
        already_current = (
            raw_entry.get("source_wiki") == "rs3"
            and raw_entry.get("file_title") == revision.file_title
            and raw_entry.get("timestamp") == revision.timestamp
        )
        changed, written_bytes = _replace_asset(
            REPO_ROOT / asset_path,
            source_bytes,
            str(raw_entry.get("sha1") or ""),
            already_current,
        )
        provenance[asset_path] = _provenance_entry(revision, written_bytes)
        _write_json(provenance_path, provenance)
        status = "fetched" if changed else "unchanged"
        results[asset_path] = {
            "revision": asdict(revision),
            "status": status,
            "wiki_title": wiki_title,
        }
        finished += 1
        _write_json(checkpoint_path, checkpoint)
        print(
            f"[{finished}/{total}] {status} {asset_path} <- "
            f"File:{revision.file_title} ({revision.timestamp})",
            flush=True,
        )
    return finished


def run_sweep(
    provenance_path: Path,
    audit_path: Path,
    checkpoint_path: Path,
    client: HttpWikiClient,
) -> Dict[str, int]:
    provenance = _load_json(provenance_path)
    if not isinstance(provenance, dict):
        raise AssetFetchError("assets_provenance.json must contain a JSON object.")
    checkpoint = _load_checkpoint(checkpoint_path, provenance)
    assets = checkpoint["assets"]
    results = checkpoint["results"]
    assert isinstance(assets, dict)
    assert isinstance(results, dict)

    finished = len(results)
    total = len(assets)
    for wiki_title, asset_paths in sorted(
        _pending_by_title(assets, results).items()
    ):
        finished = _process_title(
            provenance_path,
            checkpoint_path,
            provenance,
            checkpoint,
            results,
            client,
            wiki_title,
            asset_paths,
            finished,
            total,
        )

    counts = _write_audit(audit_path, checkpoint)
    if len(results) == len(assets):
        checkpoint_path.unlink(missing_ok=True)
    return counts


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provenance", type=Path, default=DEFAULT_PROVENANCE_PATH)
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT_PATH)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT_PATH)
    parser.add_argument("--min-interval", type=float, default=1.1)
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.min_interval < 0:
        parser.error("--min-interval must not be negative")
    try:
        counts = run_sweep(
            provenance_path=args.provenance.resolve(),
            audit_path=args.audit.resolve(),
            checkpoint_path=args.checkpoint.resolve(),
            client=HttpWikiClient(
                user_agent=args.user_agent,
                retries=3,
                min_interval_seconds=args.min_interval,
            ),
        )
    except (AssetFetchError, OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, f"error: {exc}\n")
    print(json.dumps(counts, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
