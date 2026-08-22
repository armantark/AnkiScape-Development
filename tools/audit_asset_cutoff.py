#!/usr/bin/env python3
"""Audit post-cutoff asset provenance against each wiki file's history.

The report is a checkpoint as well as the final result: after every batched API
query it is atomically rewritten, and later runs reuse rows whose provenance
input and cutoff still match. Unresolved rows are retried; resolved rows never
cause another network request unless their provenance changes.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.fetch_assets import (  # noqa: E402
    AssetFetchError,
    HttpWikiClient,
    WIKI_SOURCES_BY_NAME,
    WikiSource,
)

DEFAULT_CUTOFF_DATE = "2012-11-30"
DEFAULT_PROVENANCE_PATH = REPO_ROOT / "assets_provenance.json"
DEFAULT_REPORT_PATH = (
    REPO_ROOT
    / "memory-bank"
    / "source-audits"
    / "post-cutoff-asset-revisions-2026-08-21.json"
)
DEFAULT_BATCH_SIZE = 40
MAX_BATCH_SIZE = 50
API_ATTEMPTS = 4
SCHEMA_VERSION = 1

NO_EARLIER_REVISION = "no_earlier_revision"
BYTE_IDENTICAL = "byte_identical"
DIFFERENT = "different"
UNRESOLVED = "unresolved"
RESOLVED_STATUSES = frozenset({NO_EARLIER_REVISION, BYTE_IDENTICAL, DIFFERENT})
ALL_STATUSES = RESOLVED_STATUSES | {UNRESOLVED}


def classify_revision(recorded_sha1: str, earlier_revision: Optional[Mapping[str, object]]) -> str:
    """Classify an earlier revision without performing I/O."""
    if earlier_revision is None:
        return NO_EARLIER_REVISION
    earlier_sha1 = str(earlier_revision.get("sha1") or "")
    if not recorded_sha1 or not earlier_sha1:
        raise ValueError("Both recorded and earlier revisions require a SHA-1.")
    return BYTE_IDENTICAL if recorded_sha1 == earlier_sha1 else DIFFERENT


def _parse_timestamp(value: object) -> datetime:
    text = str(value or "")
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _cutoff_timestamp(cutoff_date: str) -> str:
    parsed = date.fromisoformat(cutoff_date)
    return f"{parsed.isoformat()}T23:59:59Z"


def _wiki_source(source_name: object) -> Optional[WikiSource]:
    prefix = str(source_name or "").partition("-")[0]
    return WIKI_SOURCES_BY_NAME.get(prefix)


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file_obj:
        return json.load(file_obj)


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(
        "w", delete=False, dir=str(path.parent), encoding="utf-8"
    ) as temp_file:
        temp_name = temp_file.name
        json.dump(value, temp_file, indent=2, sort_keys=True)
        temp_file.write("\n")
    os.replace(temp_name, path)


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path.resolve())


def _recorded_revision(entry: Mapping[str, object]) -> Dict[str, object]:
    return {
        "image_url": str(entry.get("image_url") or ""),
        "sha1": str(entry.get("sha1") or ""),
        "size": int(entry.get("size") or 0),
        "timestamp": str(entry.get("timestamp") or ""),
    }


def _row_input(
    entry: Mapping[str, object], source: Optional[WikiSource]
) -> Dict[str, object]:
    return {
        "file_title": str(entry.get("file_title") or ""),
        "provenance_source_wiki": str(entry.get("source_wiki") or ""),
        "wiki": source.name if source else None,
        "recorded_revision": _recorded_revision(entry),
    }


def _cache_matches(
    row: object,
    entry: Mapping[str, object],
    source: Optional[WikiSource],
) -> bool:
    if not isinstance(row, dict) or row.get("status") not in RESOLVED_STATUSES:
        return False
    expected = _row_input(entry, source)
    return all(row.get(key) == value for key, value in expected.items())


def _aliases(query: Mapping[str, object]) -> Dict[str, str]:
    aliases: Dict[str, str] = {}
    for section in ("normalized", "redirects"):
        rows = query.get(section, [])
        if not isinstance(rows, list):
            continue
        for row in rows:
            if isinstance(row, dict) and row.get("from") and row.get("to"):
                aliases[str(row["from"])] = str(row["to"])
    return aliases


def _canonical_title(title: str, aliases: Mapping[str, str]) -> str:
    seen = set()
    while title in aliases and title not in seen:
        seen.add(title)
        title = aliases[title]
    return title


def _request_batch(
    client: HttpWikiClient,
    source: WikiSource,
    titles: Sequence[str],
    cutoff_timestamp: str,
) -> Mapping[str, object]:
    params = {
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "redirects": "1",
        "prop": "imageinfo",
        "iiprop": "timestamp|sha1|url|size",
        "iistart": cutoff_timestamp,
        "iidir": "older",
        "iilimit": "1",
        "maxlag": "5",
        "titles": "|".join(f"File:{title}" for title in titles),
    }
    url = f"{source.api_url}?{urllib.parse.urlencode(params)}"
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
    raise AssetFetchError(
        f"Batch query failed after {API_ATTEMPTS} attempts: {last_error}"
    )


def _batch_results(
    payload: Mapping[str, object],
    titles: Sequence[str],
    cutoff_timestamp: str,
) -> Dict[str, Dict[str, object]]:
    query = payload.get("query")
    if not isinstance(query, dict):
        reason = "MediaWiki response omitted the query object."
        return {title: {"status": UNRESOLVED, "reason": reason} for title in titles}

    aliases = _aliases(query)
    raw_pages = query.get("pages", [])
    pages = {
        str(page.get("title")): page
        for page in raw_pages
        if isinstance(page, dict) and page.get("title")
    } if isinstance(raw_pages, list) else {}

    cutoff = _parse_timestamp(cutoff_timestamp)
    results: Dict[str, Dict[str, object]] = {}
    for title in titles:
        api_title = f"File:{title}"
        page = pages.get(_canonical_title(api_title, aliases))
        if page is None:
            results[title] = {
                "status": UNRESOLVED,
                "reason": "MediaWiki response omitted the requested file page.",
            }
            continue
        if "missing" in page:
            results[title] = {
                "status": UNRESOLVED,
                "reason": "The recorded file page is now missing from its source wiki.",
            }
            continue
        imageinfo = page.get("imageinfo", [])
        if not isinstance(imageinfo, list):
            results[title] = {
                "status": UNRESOLVED,
                "reason": "MediaWiki returned malformed imageinfo data.",
            }
            continue
        if not imageinfo:
            results[title] = {
                "status": NO_EARLIER_REVISION,
                "reason": "No file revision exists at or before the cutoff.",
            }
            continue
        revision = imageinfo[0]
        if not isinstance(revision, dict):
            results[title] = {
                "status": UNRESOLVED,
                "reason": "MediaWiki returned a malformed revision row.",
            }
            continue
        timestamp = str(revision.get("timestamp") or "")
        sha1 = str(revision.get("sha1") or "")
        archive_url = str(revision.get("url") or "")
        try:
            size = int(revision.get("size") or 0)
            timestamp_is_eligible = _parse_timestamp(timestamp) <= cutoff
        except (TypeError, ValueError):
            timestamp_is_eligible = False
            size = 0
        if not timestamp_is_eligible or not sha1 or size <= 0 or not archive_url:
            results[title] = {
                "status": UNRESOLVED,
                "reason": "The pre-cutoff revision lacks a valid timestamp, SHA-1, size, or URL.",
            }
            continue
        results[title] = {
            "status": "revision",
            "earlier_revision": {
                "archive_url": archive_url,
                "sha1": sha1,
                "size": size,
                "timestamp": timestamp,
            },
        }
    return results


def _make_row(
    entry: Mapping[str, object],
    source: Optional[WikiSource],
    result: Mapping[str, object],
) -> Dict[str, object]:
    row = _row_input(entry, source)
    result_status = str(result.get("status") or UNRESOLVED)
    if result_status == "revision":
        revision = result.get("earlier_revision")
        if not isinstance(revision, dict):
            row.update(
                {
                    "status": UNRESOLVED,
                    "reason": "The query result omitted its earlier revision.",
                    "earlier_revision": None,
                }
            )
            return row
        try:
            status = classify_revision(
                str(row["recorded_revision"].get("sha1") or ""),
                revision,
            )
        except ValueError as exc:
            row.update(
                {
                    "status": UNRESOLVED,
                    "reason": str(exc),
                    "earlier_revision": revision,
                }
            )
            return row
        row.update({"status": status, "earlier_revision": revision})
        return row

    row.update(
        {
            "status": result_status if result_status in ALL_STATUSES else UNRESOLVED,
            "reason": str(result.get("reason") or "No reason recorded."),
            "earlier_revision": None,
        }
    )
    return row


def _summary(late_paths: Iterable[str], rows: Mapping[str, object]) -> Dict[str, object]:
    late_paths = tuple(late_paths)
    counts = Counter()
    unresolved_reasons = Counter()
    for path in late_paths:
        row = rows.get(path)
        if not isinstance(row, dict) or row.get("status") not in ALL_STATUSES:
            counts["pending"] += 1
            continue
        status = str(row["status"])
        counts[status] += 1
        if status == UNRESOLVED:
            unresolved_reasons[str(row.get("reason") or "No reason recorded.")] += 1
    return {
        "post_cutoff_assets": len(late_paths),
        NO_EARLIER_REVISION: counts[NO_EARLIER_REVISION],
        BYTE_IDENTICAL: counts[BYTE_IDENTICAL],
        DIFFERENT: counts[DIFFERENT],
        UNRESOLVED: counts[UNRESOLVED],
        "pending": counts["pending"],
        "unresolved_reasons": dict(sorted(unresolved_reasons.items())),
    }


def _report_document(
    provenance_path: Path,
    report_path: Path,
    cutoff_date: str,
    cutoff_timestamp: str,
    late_paths: Sequence[str],
    rows: Mapping[str, object],
) -> Dict[str, object]:
    current_rows = {path: rows[path] for path in sorted(late_paths) if path in rows}
    return {
        "schema_version": SCHEMA_VERSION,
        "cutoff_date": cutoff_date,
        "cutoff_timestamp": cutoff_timestamp,
        "provenance_path": _display_path(provenance_path),
        "report_path": _display_path(report_path),
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "summary": _summary(late_paths, current_rows),
        "assets": current_rows,
    }


def audit_assets(
    provenance_path: Path,
    report_path: Path,
    cutoff_date: str,
    batch_size: int,
    client: HttpWikiClient,
) -> Dict[str, object]:
    cutoff_timestamp = _cutoff_timestamp(cutoff_date)
    cutoff = _parse_timestamp(cutoff_timestamp)
    provenance = _load_json(provenance_path)
    if not isinstance(provenance, dict):
        raise AssetFetchError("assets_provenance.json must contain a JSON object.")

    late: Dict[str, Mapping[str, object]] = {}
    for path, entry in provenance.items():
        if not isinstance(entry, dict):
            continue
        try:
            is_late = _parse_timestamp(entry.get("timestamp")) > cutoff
        except ValueError as exc:
            raise AssetFetchError(
                f"Invalid provenance timestamp for {path}: {entry.get('timestamp')!r}"
            ) from exc
        if is_late:
            late[str(path)] = entry

    existing_rows: Dict[str, object] = {}
    if report_path.exists():
        existing = _load_json(report_path)
        if (
            isinstance(existing, dict)
            and existing.get("schema_version") == SCHEMA_VERSION
            and existing.get("cutoff_timestamp") == cutoff_timestamp
            and existing.get("provenance_path") == _display_path(provenance_path)
            and isinstance(existing.get("assets"), dict)
        ):
            existing_rows = dict(existing["assets"])

    rows: Dict[str, object] = {}
    jobs: Dict[str, Dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    sources = WIKI_SOURCES_BY_NAME
    cached = 0
    for path, entry in late.items():
        source = _wiki_source(entry.get("source_wiki"))
        cached_row = existing_rows.get(path)
        if _cache_matches(cached_row, entry, source):
            rows[path] = cached_row
            cached += 1
            continue
        title = str(entry.get("file_title") or "")
        if source is None:
            rows[path] = _make_row(
                entry,
                source,
                {
                    "status": UNRESOLVED,
                    "reason": (
                        "Unsupported provenance source_wiki: "
                        f"{entry.get('source_wiki')!r}."
                    ),
                },
            )
        elif not title:
            rows[path] = _make_row(
                entry,
                source,
                {"status": UNRESOLVED, "reason": "Provenance has no file_title."},
            )
        else:
            jobs[source.name][title].append(path)

    document = _report_document(
        provenance_path,
        report_path,
        cutoff_date,
        cutoff_timestamp,
        tuple(late),
        rows,
    )
    _write_json(report_path, document)

    queried_titles = 0
    for source_name in sorted(jobs):
        source = sources[source_name]
        titles = sorted(jobs[source_name])
        for start in range(0, len(titles), batch_size):
            batch = titles[start : start + batch_size]
            try:
                payload = _request_batch(client, source, batch, cutoff_timestamp)
                results = _batch_results(payload, batch, cutoff_timestamp)
            except AssetFetchError as exc:
                results = {
                    title: {"status": UNRESOLVED, "reason": str(exc)}
                    for title in batch
                }
            for title in batch:
                result = results[title]
                for path in jobs[source_name][title]:
                    rows[path] = _make_row(late[path], source, result)
            queried_titles += len(batch)
            document = _report_document(
                provenance_path,
                report_path,
                cutoff_date,
                cutoff_timestamp,
                tuple(late),
                rows,
            )
            _write_json(report_path, document)
            print(
                f"{source_name}: resolved {min(start + len(batch), len(titles))}/"
                f"{len(titles)} titles",
                file=sys.stderr,
                flush=True,
            )

    print(
        f"Reused {cached} resolved asset rows; queried {queried_titles} unique titles.",
        file=sys.stderr,
    )
    return document


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provenance", type=Path, default=DEFAULT_PROVENANCE_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--cutoff-date", default=DEFAULT_CUTOFF_DATE)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--min-interval", type=float, default=1.1)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if not 1 <= args.batch_size <= MAX_BATCH_SIZE:
        parser.error(f"--batch-size must be between 1 and {MAX_BATCH_SIZE}")
    if args.min_interval < 0:
        parser.error("--min-interval must not be negative")
    try:
        document = audit_assets(
            provenance_path=args.provenance.resolve(),
            report_path=args.report.resolve(),
            cutoff_date=args.cutoff_date,
            batch_size=args.batch_size,
            client=HttpWikiClient(
                retries=3,
                min_interval_seconds=args.min_interval,
            ),
        )
    except (AssetFetchError, OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, f"error: {exc}\n")
    print(json.dumps(document["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
