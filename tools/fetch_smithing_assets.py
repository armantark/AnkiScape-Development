#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Batch-fetch the high-value Smithing parity icons through one rate-limited client.

The full forge table is ~150 rows; fetching every one is neither practical nor
worthwhile while most forged gear has no in-game use yet. Instead this fetches a
curated, high-signal subset and lets every other row degrade to a text-only entry
(``constants.SMITHING_EXTRA_ITEM_IMAGES`` is existence-guarded, so an unfetched
icon never breaks the panel or trips ``missing_required_asset_paths()``).

Curation rationale:
- **Blurite bar** is the one smelt output with no bundled icon (the other 8 bars
  ship in ``bars/``); constants.BAR_IMAGES already points at ``bars/bluritebar.png``.
- **Marquee forged armour** (platebodies per tier) are the iconic high-XP forge
  targets players actually chase, so they earn an icon.
- Forged **pickaxes/hatchets** are intentionally NOT listed here: their item names
  match the gathering tools, so the registry already resolves their icons from
  ``miningitems/`` / ``woodcuttingitems/`` (fetched by the gathering asset tools).
  Re-fetching them would just duplicate art under a second slug.

Output paths match what ``constants`` expects: the Blurite bar lands in ``bars/``
with the BAR_IMAGES filename; forged items land in ``smithingitems/`` keyed by
``constants._asset_slug(display_name)`` so SMITHING_EXTRA_ITEM_IMAGES picks them up.

Developer-only; never runs inside Anki. Re-runs skip existing files unless --force.

Usage:
    uv run tools/fetch_smithing_assets.py
    uv run tools/fetch_smithing_assets.py --dry-run
    uv run tools/fetch_smithing_assets.py --force
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.fetch_assets import (  # noqa: E402
    AssetFetchError,
    AssetRequest,
    HttpWikiClient,
    fetch_asset,
    wiki_title_for_item,
)

PROVENANCE = Path("assets_provenance.json")

# The only smelt output without a bundled icon. BAR_IMAGES expects this filename.
BARS: List[Tuple[str, str]] = [
    ("Blurite bar", "bars/bluritebar.png"),
]

# Marquee forged armour: the high-XP plate targets players grind toward. Slugs
# match constants._asset_slug(display_name) so SMITHING_EXTRA_ITEM_IMAGES wires
# them automatically. Extend this list as more forged gear earns a real use.
FORGED: List[Tuple[str, str]] = [
    ("Steel platebody", "smithingitems/steel_platebody.png"),
    ("Mithril platebody", "smithingitems/mithril_platebody.png"),
    ("Adamant platebody", "smithingitems/adamant_platebody.png"),
    ("Rune platebody", "smithingitems/rune_platebody.png"),
    ("Rune full helm", "smithingitems/rune_full_helm.png"),
    ("Rune kiteshield", "smithingitems/rune_kiteshield.png"),
]

MANIFEST: List[Tuple[str, str]] = BARS + FORGED


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Overwrite existing files.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve without downloading.")
    args = parser.parse_args(argv)

    client = HttpWikiClient()
    ok = skipped = failed = 0
    failures: List[str] = []
    for item_name, out_rel in MANIFEST:
        request = AssetRequest(
            item_name=item_name,
            wiki_title=wiki_title_for_item(item_name),
            output_path=Path(out_rel),
            provenance_path=PROVENANCE,
        )
        try:
            outcome = fetch_asset(request, client, size=None, force=args.force, dry_run=args.dry_run)
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
