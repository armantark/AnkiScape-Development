#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch the six supported period brawling-glove item sprites."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pkg_alias  # noqa: F401
from ankiscape.data.brawling_gloves_data import BRAWLING_GLOVE_DATA  # noqa: E402
from tools.fetch_assets import (  # noqa: E402
    PRE_EOC_CUTOFF,
    AssetFetchError,
    AssetRequest,
    HttpWikiClient,
    OSRS_WIKI,
    RS3_WIKI,
    fetch_asset,
    wiki_title_for_item,
)


def _slug(value: str) -> str:
    return "_".join(re.findall(r"[a-z0-9]+", value.lower()))


def fetch_brawling_assets(*, force: bool = False, size: int = 64) -> int:
    client = HttpWikiClient(before_timestamp=PRE_EOC_CUTOFF)
    failures = []
    for skill_id, spec in BRAWLING_GLOVE_DATA.items():
        item_name = str(spec["item_name"])
        output_path = REPO_ROOT / "brawlingitems" / f"{_slug(item_name)}.png"
        candidates = (
            wiki_title_for_item(item_name),
            wiki_title_for_item(
                item_name, f"Brawling gloves ({skill_id.title()}).png"
            ),
        )
        last_error = ""
        for title in dict.fromkeys(candidates):
            try:
                outcome = fetch_asset(
                    AssetRequest(
                        item_name=item_name,
                        wiki_title=title,
                        output_path=output_path,
                        provenance_path=REPO_ROOT / "assets_provenance.json",
                    ),
                    client,
                    size=size,
                    force=force,
                    sources=(RS3_WIKI, OSRS_WIKI),
                )
            except AssetFetchError as exc:
                last_error = str(exc)
                continue
            print(asdict(outcome))
            break
        else:
            failures.append(f"{skill_id}: {last_error}")
    for failure in failures:
        print(f"FAIL {failure}", file=sys.stderr)
    return 1 if failures else 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--size", type=int, default=64)
    args = parser.parse_args(argv)
    return fetch_brawling_assets(force=args.force, size=args.size)


if __name__ == "__main__":
    raise SystemExit(main())
