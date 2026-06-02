#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Batch-fetch the Mining parity icons through a single rate-limited client.

This drives ``tools/fetch_assets.py`` for the whole Mining manifest (ore-row
outputs, the variable Sandstone/Granite/Gem-rock outputs, Pure essence, and the
standard pickaxe tiers) in one process so the wiki rate limiter is shared and
provenance is recorded for each file. Developer-only; never runs inside Anki.

Why an explicit (wiki name -> output path) manifest instead of slug inference:
the bundled base ores use CamelCase filenames (``ores/Copper.png``) while the
parity additions use the snake_case names that ``constants.ORE_IMAGES`` already
expects (``ores/blurite_ore.png``, ``ores/sandstone_1kg.png``). Gem-rock gems
land in ``gems/`` with the short slug the GEM_IMAGES map keys on, and pickaxes
land in ``miningitems/`` with the ``_asset_slug`` of their display name. Pinning
each target path keeps the fetched files lined up with those maps.

Scope notes:
- Gilded pickaxes are intentionally omitted: they are cosmetic variants that
  don't resolve cleanly on the wikis, and they share their base tier's behavior.
  Those rows stay iconless rather than blocking the batch.
- Icons are fetched alpha-cropped but unpadded (no ``--size``) for the same
  "preprocess once, display with a plain QIcon" contract as the other art.
- Re-runs skip files that already exist unless ``--force`` is passed.

Usage:
    uv run tools/fetch_mining_assets.py
    uv run tools/fetch_mining_assets.py --dry-run
    uv run tools/fetch_mining_assets.py --force
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

# (wiki item name, repo-relative output path). The output paths must match the
# filenames constants.ORE_IMAGES / GEM_IMAGES / the mining tool wiring expect.
ORES: List[Tuple[str, str]] = [
    ("Pure essence", "ores/pure_essence.png"),
    ("Blurite ore", "ores/blurite_ore.png"),
    ("Limestone", "ores/limestone.png"),
    ("Sandstone (1kg)", "ores/sandstone_1kg.png"),
    ("Sandstone (2kg)", "ores/sandstone_2kg.png"),
    ("Sandstone (5kg)", "ores/sandstone_5kg.png"),
    ("Sandstone (10kg)", "ores/sandstone_10kg.png"),
    ("Granite (500g)", "ores/granite_500g.png"),
    ("Granite (2kg)", "ores/granite_2kg.png"),
    ("Granite (5kg)", "ores/granite_5kg.png"),
]

# Gem-rock outputs. Sapphire/emerald/ruby/diamond already ship in gems/; opal,
# jade, and red topaz are the parity additions the Gem rocks row needs.
GEMS: List[Tuple[str, str]] = [
    ("Uncut opal", "gems/opal.png"),
    ("Uncut jade", "gems/jade.png"),
    ("Uncut red topaz", "gems/red_topaz.png"),
]

# Standard pickaxe tiers (best-usable-pickaxe tooltip + Bank rows for owned
# pickaxes). Slugs match constants._asset_slug(display_name).
PICKAXES: List[Tuple[str, str]] = [
    ("Bronze pickaxe", "miningitems/bronze_pickaxe.png"),
    ("Iron pickaxe", "miningitems/iron_pickaxe.png"),
    ("Steel pickaxe", "miningitems/steel_pickaxe.png"),
    ("Mithril pickaxe", "miningitems/mithril_pickaxe.png"),
    ("Adamant pickaxe", "miningitems/adamant_pickaxe.png"),
    ("Rune pickaxe", "miningitems/rune_pickaxe.png"),
    ("Dragon pickaxe", "miningitems/dragon_pickaxe.png"),
]

MANIFEST: List[Tuple[str, str]] = ORES + GEMS + PICKAXES


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
