#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Replace Old School-sourced assets with their last pre-EOC RuneScape revision.

The manifest comes from the two Old School URLs in ``assets_provenance.json``.
Each RuneScape Wiki file title is tried exactly as recorded; a same-name miss is
reported instead of being replaced with guessed art. Progress is checkpointed
under ``tmp/`` so an interrupted run resumes without repeating finished assets.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import sys
import time
import urllib.parse
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.fetch_assets import (  # noqa: E402
    AssetFetchError,
    HttpWikiClient,
    _source_image_url,
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
API_ATTEMPTS = 4


@dataclass(frozen=True)
class HistoricalRevision:
    file_title: str
    image_url: str
    timestamp: str
    sha1: str
    archivename: str


@dataclass(frozen=True)
class HistoryQueryPage:
    canonical_title: str
    revisions: Tuple[Mapping[str, object], ...]
    continuation: Mapping[str, str]


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
        "fetch_date": datetime.now().astimezone().date().isoformat(),
        "assets": assets,
        "results": {},
    }


def _load_checkpoint(
    checkpoint_path: Path, provenance: Mapping[str, object]
) -> Dict[str, object]:
    if checkpoint_path.exists():
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
    checkpoint = _new_checkpoint(provenance)
    _write_json(checkpoint_path, checkpoint)
    return checkpoint


def _request_json_with_retry(client: HttpWikiClient, url: str) -> Mapping[str, object]:
    last_error = "unknown MediaWiki API error"
    for attempt in range(API_ATTEMPTS):
        try:
            payload = client._request_json(url)
        except (AssetFetchError, json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
            last_error = str(exc)
        else:
            error = payload.get("error")
            if not isinstance(error, dict):
                return payload
            code = str(error.get("code") or "unknown")
            info = str(error.get("info") or "no details")
            last_error = f"MediaWiki API error {code}: {info}"
        if attempt + 1 < API_ATTEMPTS:
            time.sleep(min(8.0, 0.75 * (2**attempt)))
    raise AssetFetchError(f"Wiki history query failed after retries: {last_error}")


def _history_page(
    payload: Mapping[str, object], wiki_title: str
) -> Tuple[Optional[Mapping[str, object]], str]:
    query = payload.get("query")
    if not isinstance(query, dict):
        raise AssetFetchError(f"Wiki response omitted query data for File:{wiki_title}.")
    pages = query.get("pages")
    if not isinstance(pages, dict) or not pages:
        raise AssetFetchError(f"Wiki response omitted page data for File:{wiki_title}.")
    page = next(iter(pages.values()))
    if not isinstance(page, dict):
        raise AssetFetchError(f"Wiki returned malformed page data for File:{wiki_title}.")
    if "missing" in page:
        return None, "No file exists at that RuneScape Wiki title."
    return page, ""


def _query_history_page(
    client: HttpWikiClient,
    wiki_title: str,
    continuation: Mapping[str, str],
) -> Tuple[Optional[HistoryQueryPage], str]:
    params = {
        "action": "query",
        "prop": "imageinfo",
        "titles": f"File:{wiki_title}",
        "iilimit": "50",
        "iiprop": "url|timestamp|archivename|sha1",
        "format": "json",
    }
    params.update(continuation)
    url = f"{RS_WIKI_API}?{urllib.parse.urlencode(params)}"
    payload = _request_json_with_retry(client, url)
    page, reason = _history_page(payload, wiki_title)
    if page is None:
        return None, reason

    imageinfo = page.get("imageinfo", [])
    if not isinstance(imageinfo, list):
        raise AssetFetchError(
            f"Wiki returned malformed image history for File:{wiki_title}."
        )
    raw_continue = payload.get("continue")
    next_continuation = (
        {str(key): str(value) for key, value in raw_continue.items()}
        if isinstance(raw_continue, dict) and raw_continue.get("iicontinue")
        else {}
    )
    return (
        HistoryQueryPage(
            canonical_title=str(page.get("title") or f"File:{wiki_title}"),
            revisions=tuple(
                revision for revision in imageinfo if isinstance(revision, dict)
            ),
            continuation=next_continuation,
        ),
        "",
    )


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
    while True:
        history_page, reason = _query_history_page(
            client, wiki_title, continuation
        )
        if history_page is None:
            return None, reason
        revisions.extend(history_page.revisions)
        selected = select_newest_revision(revisions)
        if selected is not None:
            return _historical_revision(history_page.canonical_title, selected), ""
        if not history_page.continuation:
            break
        continuation = history_page.continuation

    reason = (
        "Every file revision is at or after the pre-EOC cutoff."
        if revisions
        else "The RuneScape Wiki file has no revisions."
    )
    return None, reason


def _download_revision(
    client: HttpWikiClient, revision: HistoricalRevision
) -> Tuple[bytes, str]:
    image_bytes = b""
    downloaded_sha1 = ""
    for attempt in range(API_ATTEMPTS):
        image_bytes = client.download_bytes(
            _source_image_url(
                revision.image_url,
                cache_bust=f"{time.time_ns()}-{attempt}",
            )
        )
        downloaded_sha1 = hashlib.sha1(image_bytes).hexdigest()
        if downloaded_sha1 == revision.sha1:
            return image_bytes, downloaded_sha1
    return image_bytes, downloaded_sha1


def _png_dimensions(image_bytes: bytes) -> Tuple[int, int]:
    if len(image_bytes) < 24 or not image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        raise AssetFetchError("An existing sweep asset is not a valid PNG.")
    width, height = struct.unpack(">II", image_bytes[16:24])
    if width <= 0 or height <= 0:
        raise AssetFetchError("An existing sweep asset has invalid PNG dimensions.")
    return width, height


def _replace_asset(
    output_path: Path,
    source_bytes: bytes,
    recorded_source_sha1: str,
) -> bool:
    if not output_path.is_file():
        raise AssetFetchError(f"Sweep asset does not exist: {output_path}")
    existing_bytes = output_path.read_bytes()
    transformed = hashlib.sha1(existing_bytes).hexdigest() != recorded_source_sha1
    with NamedTemporaryFile(
        "wb", delete=False, dir=str(output_path.parent), suffix=".png"
    ) as temp_file:
        candidate_path = Path(temp_file.name)
    candidate_path.unlink()
    try:
        if transformed:
            width, height = _png_dimensions(existing_bytes)
            write_png(source_bytes, candidate_path, size=max(width, height))
        else:
            write_source_png(source_bytes, candidate_path)
        candidate_bytes = candidate_path.read_bytes()
        changed = candidate_bytes != existing_bytes
        if changed:
            os.replace(candidate_path, output_path)
        return changed
    finally:
        candidate_path.unlink(missing_ok=True)


def _file_page_url(file_title: str) -> str:
    quoted_title = urllib.parse.quote(
        f"File:{file_title}".replace(" ", "_"), safe=":/"
    )
    return f"{RS_WIKI_PAGE_BASE}{quoted_title}"


def _provenance_entry(
    revision: HistoricalRevision,
    source_bytes: bytes,
    downloaded_sha1: str,
    fetch_date: str,
) -> Dict[str, object]:
    entry: Dict[str, object] = {
        "fetch_date": fetch_date,
        "file_page_url": _file_page_url(revision.file_title),
        "file_title": revision.file_title,
        "image_url": revision.image_url,
        "license_string": "unknown",
        "mediatype": "BITMAP",
        "mime": "image/png",
        "sha1": revision.sha1,
        "size": len(source_bytes),
        "source_wiki": "rs3",
        "timestamp": revision.timestamp,
    }
    if downloaded_sha1 != revision.sha1:
        entry["download_sha1"] = downloaded_sha1
        entry["source_note"] = (
            "The archive URL bytes did not match the MediaWiki revision SHA-1; "
            "both hashes are retained."
        )
    return entry


def _classify_audit_result(
    asset_path: str, raw_result: object
) -> Tuple[
    str,
    Optional[Tuple[str, str, str]],
    Optional[Tuple[str, str, str, str]],
]:
    if not isinstance(raw_result, dict):
        raise AssetFetchError(f"Checkpoint has no result for {asset_path}.")
    status = str(raw_result.get("status") or "")
    if status not in {"fetched", "unchanged", "missing"}:
        raise AssetFetchError(f"Checkpoint has an invalid status for {asset_path}.")
    if status == "missing":
        return (
            status,
            (
                asset_path,
                str(raw_result.get("wiki_title") or ""),
                str(raw_result.get("reason") or "No reason recorded."),
            ),
            None,
        )

    revision = raw_result.get("revision")
    if not isinstance(revision, dict):
        raise AssetFetchError(f"Checkpoint has no revision for {asset_path}.")
    api_sha1 = str(revision.get("sha1") or "")
    download_sha1 = str(raw_result.get("download_sha1") or api_sha1)
    mismatch = (
        (
            asset_path,
            str(revision.get("file_title") or ""),
            api_sha1,
            download_sha1,
        )
        if download_sha1 != api_sha1
        else None
    )
    return status, None, mismatch


def _summarize_audit(
    assets: Mapping[str, object],
    results: Mapping[str, object],
) -> Tuple[
    Dict[str, int],
    List[Tuple[str, str, str]],
    List[Tuple[str, str, str, str]],
]:
    counts = {"fetched": 0, "unchanged": 0, "missing": 0}
    missing_rows: List[Tuple[str, str, str]] = []
    mismatch_rows: List[Tuple[str, str, str, str]] = []
    for asset_path in sorted(assets):
        status, missing, mismatch = _classify_audit_result(
            asset_path, results.get(asset_path)
        )
        counts[status] += 1
        if missing is not None:
            missing_rows.append(missing)
        if mismatch is not None:
            mismatch_rows.append(mismatch)
    return counts, missing_rows, mismatch_rows


def _write_audit(
    audit_path: Path,
    checkpoint: Mapping[str, object],
) -> Dict[str, int]:
    assets = checkpoint["assets"]
    results = checkpoint["results"]
    assert isinstance(assets, dict)
    assert isinstance(results, dict)
    counts, missing_rows, mismatch_rows = _summarize_audit(assets, results)

    lines = [
        "# 2012 icon sweep source audit",
        "",
        f"- Cutoff: `{CUTOFF_TIMESTAMP}`; revisions at the cutoff are excluded.",
        f"- Fetch date: `{checkpoint['fetch_date']}`.",
        (
            f"- Scope: `{len(assets)}` assets whose provenance carried two "
            "`oldschool.runescape.wiki` URLs."
        ),
        (
            f"- Result: `{counts['fetched']}` fetched with changed PNG bytes, "
            f"`{counts['unchanged']}` fetched with unchanged PNG bytes, and "
            f"`{counts['missing']}` missing a pre-cutoff revision."
        ),
        (
            "- Method: each recorded file title was queried exactly on "
            "`runescape.wiki`; no alternate title or substitute icon was guessed."
        ),
        "",
        "## Assets without a pre-cutoff revision",
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
        lines.append("No assets were missing a pre-cutoff revision.")
    lines.extend(["", "## Archive-byte SHA-1 mismatches", ""])
    if mismatch_rows:
        lines.extend(
            [
                (
                    "The exact archive URL returned PNG bytes whose SHA-1 differed "
                    "from the MediaWiki revision metadata. No alternate asset was "
                    "substituted; both hashes are retained in provenance."
                ),
                "",
                "| Asset path | RuneScape Wiki file | API SHA-1 | Download SHA-1 |",
                "| --- | --- | --- | --- |",
            ]
        )
        lines.extend(
            f"| `{path}` | `File:{title}` | `{api_sha1}` | `{download_sha1}` |"
            for path, title, api_sha1, download_sha1 in mismatch_rows
        )
    else:
        lines.append("All downloaded source bytes matched the MediaWiki revision SHA-1.")
    lines.append("")
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text("\n".join(lines), encoding="utf-8")
    return counts


def _record_missing_results(
    checkpoint_path: Path,
    checkpoint: Mapping[str, object],
    results: Dict[str, object],
    asset_paths: Sequence[str],
    wiki_title: str,
    reason: str,
    finished: int,
    total: int,
) -> int:
    for asset_path in asset_paths:
        results[asset_path] = {
            "reason": reason,
            "status": "missing",
            "wiki_title": wiki_title,
        }
        finished += 1
        _write_json(checkpoint_path, checkpoint)
        print(f"[{finished}/{total}] missing {asset_path}: {reason}", flush=True)
    return finished


def _replace_title_assets(
    provenance_path: Path,
    checkpoint_path: Path,
    provenance: Dict[str, object],
    checkpoint: Mapping[str, object],
    results: Dict[str, object],
    asset_paths: Sequence[str],
    wiki_title: str,
    revision: HistoricalRevision,
    source_bytes: bytes,
    downloaded_sha1: str,
    finished: int,
    total: int,
) -> int:
    for asset_path in asset_paths:
        raw_entry = provenance.get(asset_path)
        if not isinstance(raw_entry, dict):
            raise AssetFetchError(f"Provenance entry is missing for {asset_path}.")
        changed = _replace_asset(
            REPO_ROOT / asset_path,
            source_bytes,
            str(raw_entry.get("sha1") or ""),
        )
        provenance[asset_path] = _provenance_entry(
            revision,
            source_bytes,
            downloaded_sha1,
            str(checkpoint["fetch_date"]),
        )
        _write_json(provenance_path, provenance)
        status = "fetched" if changed else "unchanged"
        results[asset_path] = {
            "download_sha1": downloaded_sha1,
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

    pending_by_title: Dict[str, List[str]] = defaultdict(list)
    for asset_path, manifest_row in assets.items():
        if asset_path in results:
            continue
        if not isinstance(manifest_row, dict):
            raise AssetFetchError(f"Checkpoint manifest is malformed for {asset_path}.")
        pending_by_title[str(manifest_row["wiki_title"])].append(str(asset_path))

    finished = len(results)
    total = len(assets)
    for wiki_title in sorted(pending_by_title):
        asset_paths = pending_by_title[wiki_title]
        revision, missing_reason = query_pre_cutoff_revision(client, wiki_title)
        if revision is None:
            finished = _record_missing_results(
                checkpoint_path,
                checkpoint,
                results,
                asset_paths,
                wiki_title,
                missing_reason,
                finished,
                total,
            )
            continue

        source_bytes, downloaded_sha1 = _download_revision(client, revision)
        if downloaded_sha1 != revision.sha1:
            print(
                f"warning: File:{revision.file_title} API SHA-1 {revision.sha1} "
                f"!= downloaded SHA-1 {downloaded_sha1}",
                flush=True,
            )
        finished = _replace_title_assets(
            provenance_path,
            checkpoint_path,
            provenance,
            checkpoint,
            results,
            asset_paths,
            wiki_title,
            revision,
            source_bytes,
            downloaded_sha1,
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
