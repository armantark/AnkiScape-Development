#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Batch-fetch the full Crafting icon set through one rate-limited client.

Like ``tools/fetch_smithing_assets.py``, this derives its manifest directly from
``CRAFTING_DATA`` so it can never drift out of sync with the data module. It
fetches:

- Every distinct Crafting **output** item (one icon per craftable target row).
- The crafting-specific **raw materials** that have no home in another skill's
  art (e.g. Molten glass, Leather, dragonhide, orbs, Sinew, runes). Materials
  already covered by Mining/Smithing/Woodcutting art (ores, gems, bars, logs)
  are skipped — the item registry resolves those from their own folders.
- The Utility/Activities outputs that live under ``crafteditems/`` (Soft clay,
  Wool, Flax), so the no-XP prep outputs and their craft inputs share one icon.

All icons land in ``crafteditems/<_asset_slug(name)>.png``; ``constants`` wires
``CRAFTED_ITEM_IMAGES`` from that folder, existence-guarded, so any single icon
the wiki cannot resolve leaves that one row text-only instead of breaking.

Wiki naming: inventory icons are ``File:<item name>.png`` with redirects, so the
display name resolves directly in most cases (OSRS first, RS3 fallback). Genuine
title mismatches go in WIKI_TITLE_OVERRIDES below; fill them from run failures.

Developer-only; never runs inside Anki. Re-runs skip existing files unless --force.

Usage:
    uv run tools/fetch_crafting_assets.py
    uv run tools/fetch_crafting_assets.py --dry-run
    uv run tools/fetch_crafting_assets.py --force
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
    BAR_IMAGES,
    CRAFTED_ITEMS_FOLDER,
    CRAFTING_DATA,
    GEM_IMAGES,
    LOG_IMAGES,
    ORE_IMAGES,
    TREE_IMAGES,
    UTILITY_ITEM_IMAGES,
    _asset_slug,
)
from crafting_data import crafting_output_items  # noqa: E402

PROVENANCE = Path("assets_provenance.json")
_CRAFTED_ITEMS_REL = Path(CRAFTED_ITEMS_FOLDER).relative_to(REPO_ROOT)

# Item names whose art already ships under another skill's folder; the registry
# resolves these from ore/gem/bar/log maps, so don't re-fetch them here.
_COVERED_ELSEWHERE = set(ORE_IMAGES) | set(GEM_IMAGES) | set(BAR_IMAGES) | set(LOG_IMAGES) | set(TREE_IMAGES)

# Utility/Activities outputs that live under crafteditems/ (shared with craft
# inputs). UTILITY_ITEM_IMAGES already points them here.
_UTILITY_CRAFTED = {
    name for name, path in UTILITY_ITEM_IMAGES.items()
    if str(CRAFTED_ITEMS_FOLDER) in str(path)
}

# Display name -> wiki File title override, for items whose inventory-icon page
# is not simply "<name>.png" (abbreviations, unstrung/unfired states, etc.).
# Fill in from --dry-run / run failures so a re-run resolves the stragglers.
WIKI_TITLE_OVERRIDES: Dict[str, str] = {
    # Crafted amulets are the *unstrung* item in our economy (stringing is a
    # separate combination step); point at the unstrung inventory icon.
    "Dragonstone ammy": "Dragonstone amulet (unstrung)",
    "Gold amulet": "Gold amulet (unstrung)",
    "Sapphire amulet": "Sapphire amulet (unstrung)",
    "Unstrung emblem": "Unblessed symbol",
    # Intermediate pottery/urn states have no distinct inventory-icon page on the
    # wikis; fall back to the finished item's icon (same object, visually fine).
    "Plant pot (unfired)": "Plant pot",
    "Pot lid (unfired)": "Pot lid",
    "Cracked mining urn (unf)": "Cracked mining urn",
    "Cracked mining urn (nr)": "Cracked mining urn",
    "Cracked cooking urn (unf)": "Cracked cooking urn",
    "Cracked cooking urn (nr)": "Cracked cooking urn",
    "Decorated mining urn (unf)": "Decorated mining urn",
    "Decorated mining urn (nr)": "Decorated mining urn",
}


def _build_manifest() -> List[Tuple[str, str, Optional[str]]]:
    """(item_name, out_rel, wiki_override) for every crafting icon we need."""
    want: set = set(crafting_output_items()) | _UTILITY_CRAFTED
    for spec in CRAFTING_DATA.values():
        for material in spec.get("requirements", {}):
            name = str(material)
            if name in want or name in _COVERED_ELSEWHERE:
                continue
            want.add(name)

    rows: List[Tuple[str, str, Optional[str]]] = []
    for name in sorted(want):
        out_rel = str(_CRAFTED_ITEMS_REL / f"{_asset_slug(name)}.png")
        rows.append((name, out_rel, WIKI_TITLE_OVERRIDES.get(name)))
    return rows


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Overwrite existing files.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve without downloading.")
    args = parser.parse_args(argv)

    manifest = _build_manifest()
    client = HttpWikiClient()
    ok = skipped = failed = 0
    failures: List[str] = []
    print(f"Resolving {len(manifest)} Crafting icons...")
    for item_name, out_rel, wiki_override in manifest:
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
