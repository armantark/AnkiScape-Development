"""Restore literal historical-wiki audit caches from archived API receipts."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools import audit_quest_historical_wiki_combat_stats as wiki
from tools import build_pre_eoc_quest_catalog as builder


def _period_pages(path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("query"), dict):
        return
    pages = payload["query"].get("pages", [])
    if not isinstance(pages, list):
        return
    for page in pages:
        revisions = page.get("revisions", [])
        if len(revisions) > 1:
            continue
        timestamp = revisions[0]["timestamp"] if revisions else ""
        if timestamp >= wiki.EOC_CUTOFF_TIMESTAMP:
            continue
        yield timestamp, page


def _receipt_rank(entry):
    title, (timestamp, page) = entry
    revision = wiki._revision_from_payload(title, {"query": {"pages": [page]}})
    content = revision.content if revision else ""
    return next(wiki.monster_infoboxes(content), None) is not None, timestamp, title


def _restore_receipts(pages_by_title):
    groups = {}
    for title, receipt in pages_by_title.items():
        groups.setdefault(builder.slug_key(title), {})[title] = receipt
    wiki.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    for key, receipts in sorted(groups.items()):
        primary = max(receipts.items(), key=_receipt_rank)[0]
        if len(receipts) > 1:
            print(f"Audit cache key collision {key}: {sorted(receipts)}; audit receipt: {primary}")
        for title, (_, page) in sorted(receipts.items()):
            # The fixed audit reads the bare slug; hex preserves every other exact title.
            name = key if title == primary else f"{key}--{title.encode('utf-8').hex()}"
            path = wiki.CACHE_DIR / f"{name}.json"
            path.write_text(json.dumps({"query": {"pages": [page]}}, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archives", nargs="+", type=Path)
    args = parser.parse_args()
    pages_by_title = {}
    for archive in args.archives:
        if not archive.is_dir():
            parser.error(f"Archive directory does not exist: {archive}")
        for path in sorted(archive.rglob("*.json")):
            for timestamp, page in _period_pages(path):
                title = page["title"]
                previous = pages_by_title.get(title)
                if previous is None or timestamp > previous[0]:
                    pages_by_title[title] = (timestamp, page)
    _restore_receipts(pages_by_title)
    print(f"Restored {len(pages_by_title)} literal historical-wiki audit receipts.")


if __name__ == "__main__":
    main()
