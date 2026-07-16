#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Batch-fetch Firemaking icons needed by the v1 skill expansion.

Most burnable logs reuse the Woodcutting tree/log art already registered in
``constants.LOG_IMAGES``. This script fetches only the Firemaking-only inventory
sprites plus Ashes and the high-resolution ``Firemaking icon (detail)`` asset.

Usage:
    uv run tools/fetch_firemaking_assets.py
    uv run tools/fetch_firemaking_assets.py --force
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from firemaking_data import FIREMAKING_TARGETS  # noqa: E402
from tools.fetch_assets import (  # noqa: E402
    AssetFetchError,
    AssetRequest,
    HttpWikiClient,
    fetch_asset,
    wiki_title_for_item,
)

PROVENANCE = Path("assets_provenance.json")
FM_ITEMS_DIR = "firemakingitems"

REUSED_LOG_ART = {
    "Logs",
    "Achey tree logs",
    "Oak logs",
    "Willow logs",
    "Teak logs",
    "Maple logs",
    "Mahogany logs",
    "Yew logs",
    "Magic logs",
}

WIKI_TITLE_OVERRIDES = {
    "Firemaking": "Firemaking icon (detail).png",
    "Candle lantern (unlit, 4529)": "Candle lantern (white)",
    "Candle lantern (lit, 4531)": "Candle lantern (lit white)",
    "Candle lantern (unlit, 4532)": "Candle lantern (black)",
    "Candle lantern (lit, 4534)": "Candle lantern (lit black)",
    "Oil lamp (unlit)": "Oil lamp (oil)",
    "Oil lamp (lit)": "Oil lamp",
    "Oil lantern (unlit)": "Oil lantern (oil)",
    "Oil lantern (lit)": "Oil lantern",
    "Bullseye lantern (unlit)": "Bullseye lantern (oil)",
    "Bullseye lantern (lit)": "Bullseye lantern (lit)",
    "Sapphire lantern (unlit)": "Sapphire lantern (oil)",
    "Sapphire lantern (lit)": "Sapphire lantern (lit)",
    "Emerald lantern (unlit)": "Emerald lantern",
    "Emerald lantern (lit)": "Emerald lantern (lit)",
    "Mining helmet (unlit)": "Mining helmet",
}

LIGHT_SOURCE_ITEMS = (
    "Candle lantern (empty)",
    "Candle lantern (unlit, 4529)",
    "Candle lantern (lit, 4531)",
    "Candle lantern (unlit, 4532)",
    "Candle lantern (lit, 4534)",
    "Oil lamp (empty)",
    "Oil lamp (unlit)",
    "Oil lamp (lit)",
    "Oil lantern (empty)",
    "Oil lantern (unlit)",
    "Oil lantern (lit)",
    "Bullseye lantern (unf)",
    "Bullseye lantern (empty)",
    "Bullseye lantern (unlit)",
    "Bullseye lantern (lit)",
    "Sapphire lantern (empty)",
    "Sapphire lantern (unlit)",
    "Sapphire lantern (lit)",
    "Emerald lantern (unlit)",
    "Emerald lantern (lit)",
    "Mining helmet (unlit)",
    "Mining helmet (lit)",
)


def _slug(name: str) -> str:
    return "_".join(re.findall(r"[a-z0-9]+", name.lower()))


def _fm_item(name: str) -> str:
    return f"{FM_ITEMS_DIR}/{_slug(name)}.png"


def _manifest() -> List[Tuple[str, str, str, Optional[int]]]:
    manifest: List[Tuple[str, str, str, Optional[int]]] = [
        ("Firemaking", WIKI_TITLE_OVERRIDES["Firemaking"], "icon/firemaking_icon.png", 64),
        ("Ashes", "Ashes.png", _fm_item("Ashes"), None),
    ]
    seen = {"Ashes"}
    for target in FIREMAKING_TARGETS:
        input_item = target.input_item
        if input_item in seen or input_item in REUSED_LOG_ART:
            continue
        manifest.append((input_item, wiki_title_for_item(input_item), _fm_item(input_item), None))
        seen.add(input_item)
    for item_name in LIGHT_SOURCE_ITEMS:
        manifest.append(
            (
                item_name,
                wiki_title_for_item(item_name, WIKI_TITLE_OVERRIDES.get(item_name)),
                _fm_item(item_name),
                None,
            )
        )
    return manifest


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Overwrite existing files.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve without downloading.")
    parser.add_argument(
        "--item",
        action="append",
        default=[],
        help="Fetch only this exact manifest item; repeat for multiple items.",
    )
    args = parser.parse_args(argv)

    manifest = _manifest()
    if args.item:
        requested = set(args.item)
        known = {item_name for item_name, _wiki_title, _out_rel, _size in manifest}
        unknown = sorted(requested - known)
        if unknown:
            parser.error(f"unknown Firemaking item(s): {', '.join(unknown)}")
        manifest = [row for row in manifest if row[0] in requested]

    client = HttpWikiClient()
    ok = skipped = failed = 0
    failures: List[str] = []
    for item_name, wiki_title, out_rel, size in manifest:
        request = AssetRequest(
            item_name=item_name,
            wiki_title=wiki_title_for_item(item_name, wiki_title),
            output_path=Path(out_rel),
            provenance_path=PROVENANCE,
        )
        try:
            outcome = fetch_asset(request, client, size=size, force=args.force, dry_run=args.dry_run)
        except AssetFetchError as exc:
            failed += 1
            failures.append(f"{item_name}: {exc}")
            print(f"  FAIL {item_name} -> {out_rel}: {exc}")
            continue
        if outcome.skipped_existing:
            skipped += 1
            print(f"  skip {item_name} (exists) -> {out_rel}")
        else:
            ok += 1
            print(f"  ok   {item_name} [{outcome.source_wiki}] -> {out_rel}")

    print(f"\nDone. {ok} fetched, {skipped} skipped, {failed} failed.")
    if failures:
        print("Failures:")
        for line in failures:
            print(f"  - {line}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
