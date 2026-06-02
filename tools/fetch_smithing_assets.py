#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Batch-fetch the full Smithing icon set through one rate-limited client.

The forge table is ~157 rows; rather than hand-pick a few and leave the rest as
blank text rows, this derives its manifest directly from ``SMITHING_DATA`` so it
fetches *every* forged output (plus the one un-bundled smelt bar) and can never
drift out of sync with the data module. ``constants.SMITHING_EXTRA_ITEM_IMAGES``
stays existence-guarded, so any individual icon the wiki can't resolve simply
leaves that one row text-only instead of breaking the panel.

Output paths match what ``constants`` expects:
- **Blurite bar** -> ``bars/bluritebar.png`` (BAR_IMAGES filename; the other 8
  bars ship bundled).
- **Forged items** -> ``smithingitems/<_asset_slug(name)>.png`` so
  SMITHING_EXTRA_ITEM_IMAGES picks them up by slug.

Forged **pickaxes/hatchets** are skipped on purpose: their item names match the
gathering tools, so the registry already resolves their icons from
``miningitems/`` / ``woodcuttingitems/``. Re-fetching would duplicate art under a
second slug for no benefit.

Wiki naming: item inventory icons are ``File:<item name>.png`` with redirects, so
the display name resolves directly in almost every case (OSRS first, RS3
fallback). Genuine title mismatches go in WIKI_TITLE_OVERRIDES below.

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
from typing import Dict, List, Optional, Sequence, Tuple

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
from constants import (  # noqa: E402
    MINING_EXTRA_ITEM_IMAGES,
    SMITHING_DATA,
    SMITHING_ITEMS_FOLDER,
    WOODCUTTING_EXTRA_ITEM_IMAGES,
    _asset_slug,
)

PROVENANCE = Path("assets_provenance.json")
_SMITHING_ITEMS_REL = Path(SMITHING_ITEMS_FOLDER).relative_to(REPO_ROOT)

# The only smelt output without bundled art. BAR_IMAGES expects this filename.
BARS: List[Tuple[str, str]] = [
    ("Blurite bar", "bars/bluritebar.png"),
]

# Forged item display name -> wiki File title override, for the handful whose
# inventory-icon page is not simply "<name>.png". Filled in from --dry-run/run
# failures so a re-run resolves the stragglers instead of leaving them iconless.
WIKI_TITLE_OVERRIDES: Dict[str, str] = {}

# Item names already carrying gathering-tool art; the registry resolves these
# from miningitems/ / woodcuttingitems/, so skip re-fetching them here.
_REUSED_TOOL_NAMES = set(MINING_EXTRA_ITEM_IMAGES) | set(WOODCUTTING_EXTRA_ITEM_IMAGES)


def _forged_manifest() -> List[Tuple[str, str, Optional[str]]]:
    """(item_name, out_path, wiki_override) for every anvil output, deduped."""
    seen: set = set()
    rows: List[Tuple[str, str, Optional[str]]] = []
    for spec in SMITHING_DATA.values():
        if spec.get("station") != "anvil":
            continue
        name = str(spec.get("output_item", ""))
        if not name or name in seen or name in _REUSED_TOOL_NAMES:
            continue
        seen.add(name)
        out_rel = str(_SMITHING_ITEMS_REL / f"{_asset_slug(name)}.png")
        rows.append((name, out_rel, WIKI_TITLE_OVERRIDES.get(name)))
    return rows


def _build_manifest() -> List[Tuple[str, str, Optional[str]]]:
    manifest: List[Tuple[str, str, Optional[str]]] = [
        (name, out, None) for name, out in BARS
    ]
    manifest.extend(_forged_manifest())
    return manifest


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Overwrite existing files.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve without downloading.")
    args = parser.parse_args(argv)

    MANIFEST = _build_manifest()

    client = HttpWikiClient()
    ok = skipped = failed = 0
    failures: List[str] = []
    print(f"Resolving {len(MANIFEST)} Smithing icons...")
    for item_name, out_rel, wiki_override in MANIFEST:
        request = AssetRequest(
            item_name=item_name,
            wiki_title=wiki_title_for_item(item_name, wiki_override),
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
