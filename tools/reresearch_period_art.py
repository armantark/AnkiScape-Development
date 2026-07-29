"""Re-research period art for post-cutoff assets against the RuneScape wiki.

Tranche 1 of the art-provenance sweep lost ~200 assets to agents improvising
API calls against the wrong endpoint and recording the failures as "no period
art". This tool owns the whole per-asset protocol so research agents drive it
instead of re-deriving it:

    python3 tools/reresearch_period_art.py \
        --batch-file <batches.json> --index 3 --out <rows.json>

    python3 tools/reresearch_period_art.py \
        --single shopitems/foo.png --title "Foo (historical).png" --out <rows.json>

Per asset it queries the FULL upload history at https://runescape.wiki/api.php
(never /w/api.php), picks the latest revision strictly before the EOC cutoff
2012-11-20T00:00:00Z, downloads that exact revision, verifies the API's sha1,
normalizes through the shared write_png pipeline, and replaces the repo PNG.
The provenance ledger is deliberately NOT written here — the workflow's single
apply step owns it to avoid concurrent-writer corruption.

Statuses emitted per row: replaced | no_period_art | unreachable |
sha_mismatch | non_wiki | error. A no_period_art row always carries evidence:
the earliest surviving upload timestamp and every title variant tried. Output
is JSONL-appended per asset (crash-resumable); rows for paths already in the
output file are skipped on rerun.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from io import BytesIO
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
from fetch_assets import write_png  # noqa: E402

API_URL = "https://runescape.wiki/api.php"
CUTOFF = "2012-11-20T00:00:00Z"
USER_AGENT = "AnkiScapePeriodArtResearch/2.0 (single-user preservation project)"
BASE_DELAY_SECONDS = 0.5


def _request(url: str, *, binary: bool = False, attempts: int = 4) -> bytes:
    last_error: Exception | None = None
    for attempt in range(attempts):
        time.sleep(BASE_DELAY_SECONDS * (1 + attempt * 2))
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                payload = response.read()
            if binary:
                return payload
            decoded = json.loads(payload.decode("utf-8"))
            if isinstance(decoded, dict) and decoded.get("error", {}).get("code") == "maxlag":
                last_error = RuntimeError("maxlag")
                continue
            return payload
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            continue
    raise RuntimeError(f"request failed after {attempts} attempts: {last_error}")


def _query_history(file_title: str) -> tuple[str, list[dict]] | None:
    """Return (resolved_title, revisions newest-first) or None when missing."""
    params = urllib.parse.urlencode(
        {
            "action": "query",
            "titles": f"File:{file_title}",
            "prop": "imageinfo",
            "iiprop": "timestamp|sha1|url|size|mime|archivename",
            "iilimit": "max",
            "redirects": 1,
            "maxlag": 5,
            "format": "json",
        }
    )
    decoded = json.loads(_request(f"{API_URL}?{params}").decode("utf-8"))
    pages = decoded.get("query", {}).get("pages", {})
    for page_id, page in pages.items():
        if page_id == "-1" or "missing" in page:
            return None
        info = page.get("imageinfo")
        if not info:
            return None
        return page.get("title", f"File:{file_title}"), info
    return None


def _title_variants(title: str) -> list[str]:
    base, dot, extension = title.rpartition(".")
    if not dot:
        base, extension = title, "png"
    return [
        title,
        f"{base} (historical).{extension}",
        f"{base} (historic).{extension}",
        f"{base} detail.{extension}",
    ]


def research_asset(path: str, title: str, *, explicit_title: str | None = None) -> dict:
    tried: list[str] = []
    variants = [explicit_title] if explicit_title else _title_variants(title)
    resolved = None
    for variant in variants:
        tried.append(variant)
        try:
            resolved = _query_history(variant)
        except RuntimeError as exc:
            return {"path": path, "status": "unreachable", "evidence": f"history query failed for {variant}: {exc}", "titles_tried": tried}
        if resolved is not None:
            break
    if resolved is None:
        return {"path": path, "status": "no_period_art", "evidence": "no File page under any tried title", "titles_tried": tried}

    resolved_title, revisions = resolved
    period = [r for r in revisions if str(r.get("timestamp", "")) < CUTOFF]
    if not period:
        earliest = min(str(r.get("timestamp", "")) for r in revisions)
        return {
            "path": path,
            "status": "no_period_art",
            "evidence": f"upload history of {resolved_title} starts {earliest}, after cutoff {CUTOFF}",
            "titles_tried": tried,
        }

    chosen = max(period, key=lambda r: str(r.get("timestamp", "")))
    expected_sha1 = str(chosen.get("sha1", ""))
    # The 2018 wiki migration scrambled some archivename->bytes mappings, so a
    # revision's own URL can serve different bytes than its claimed sha1. Any
    # revision URL whose claimed sha1 matches the chosen period revision is an
    # equally valid source for the identical bytes, so try them all and accept
    # whichever download actually hashes to the period sha1.
    candidate_urls = [
        r.get("url", "")
        for r in revisions
        if r.get("url") and str(r.get("sha1", "")) == expected_sha1
    ] or [chosen.get("url", "")]
    if not any(candidate_urls):
        return {"path": path, "status": "unreachable", "evidence": f"{resolved_title} period revision {chosen.get('timestamp')} has no url", "titles_tried": tried}

    payload = None
    attempts_log: list[str] = []
    for image_url in candidate_urls:
        try:
            downloaded = _request(image_url, binary=True)
        except RuntimeError as exc:
            attempts_log.append(f"{image_url}: {exc}")
            continue
        actual_sha1 = hashlib.sha1(downloaded).hexdigest()
        if not expected_sha1 or actual_sha1 == expected_sha1:
            payload, matched_url = downloaded, image_url
            break
        attempts_log.append(f"{image_url}: served {actual_sha1}, want {expected_sha1}")
    if payload is None:
        status = "unreachable" if not any("served" in line for line in attempts_log) else "sha_mismatch"
        return {"path": path, "status": status, "evidence": "; ".join(attempts_log), "titles_tried": tried}
    image_url = matched_url

    output_path = REPO_ROOT / path
    size_limit = None
    if output_path.exists():
        from PIL import Image

        with Image.open(output_path) as current:
            size_limit = max(current.size)
    write_png(payload, output_path, size_limit)
    return {
        "path": path,
        "status": "replaced",
        "file_title": resolved_title.removeprefix("File:"),
        "file_page_url": f"https://runescape.wiki/wiki/{urllib.parse.quote(resolved_title.replace(' ', '_'), safe=':')}",
        "image_url": image_url,
        "timestamp": chosen.get("timestamp"),
        "sha1": expected_sha1 or actual_sha1,
        "size": chosen.get("size"),
        "mime": chosen.get("mime", "image/png"),
        "source_wiki": "rs3",
        "titles_tried": tried,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-file")
    parser.add_argument("--index", type=int)
    parser.add_argument("--single", help="repo-relative asset path for a one-off rerun")
    parser.add_argument("--title", help="explicit File title override (with --single)")
    parser.add_argument("--out", required=True, help="JSONL output; existing rows are skipped")
    args = parser.parse_args()

    if args.single:
        jobs = [{"path": args.single, "title": args.title or Path(args.single).stem.replace("_", " ").capitalize() + ".png"}]
    else:
        if args.batch_file is None or args.index is None:
            parser.error("--batch-file with --index, or --single, is required")
        batches = json.loads(Path(args.batch_file).read_text())
        jobs = batches[args.index]

    out_path = Path(args.out)
    done: set[str] = set()
    if out_path.exists():
        for line in out_path.read_text().splitlines():
            if line.strip():
                done.add(json.loads(line)["path"])

    with out_path.open("a", encoding="utf-8") as sink:
        for job in jobs:
            if job["path"] in done:
                continue
            try:
                row = research_asset(job["path"], job["title"], explicit_title=args.title if args.single else None)
            except Exception as exc:  # noqa: BLE001 - a row must record, never abort the batch
                row = {"path": job["path"], "status": "error", "evidence": repr(exc)}
            sink.write(json.dumps(row) + "\n")
            sink.flush()
            print(f"{row['status']}: {job['path']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
