"""Fetch literal period monster pages and expose all infobox fields for source review."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools import audit_quest_historical_wiki_combat_stats as wiki
from tools import build_pre_eoc_quest_catalog as builder


def inspect_title(title):
    revision = wiki.fetch_historical_revision(title)
    if revision is None:
        return {"title": title, "status": "no_period_revision"}
    if revision.timestamp >= wiki.EOC_CUTOFF_TIMESTAMP:
        raise ValueError(f"Revision outside requested period: {title} {revision.timestamp}")
    templates = list(wiki.monster_infoboxes(revision.content))
    stats, configs = wiki.parse_monster_infobox_metadata(revision.content)
    result = {
        "title": title, "resolved_title": revision.resolved_title,
        "oldid": revision.oldid, "timestamp": revision.timestamp,
        "templates": templates, "stats": stats, "configs": configs,
        "resolver_ready": wiki.metadata_has_resolver_stats(stats, configs),
    }
    (wiki.CACHE_DIR / f"{builder.slug_key(title)}.txt").write_text(revision.content, encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--before", default="2012-11-19T23:59:59Z")
    parser.add_argument("titles", nargs="+")
    args = parser.parse_args()
    if args.before >= "2012-11-20T00:00:00Z":
        parser.error("Source review must precede the EOC cutoff")
    wiki.CACHE_DIR = args.output / args.before.replace(":", "-")
    wiki.EOC_CUTOFF_TIMESTAMP = args.before
    wiki.USER_AGENT = "AnkiScape parity audit"
    args.output.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=2) as executor:
        for result in executor.map(inspect_title, dict.fromkeys(args.titles)):
            print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
