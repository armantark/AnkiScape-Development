#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Batch-fetch the 11 OSRS worn-slot placeholder icons for the Equipment tab.

The Equipment tab renders every ``EQUIPMENT_SLOTS`` row even when empty, showing
the greyed OSRS slot silhouette (e.g. ``File:Head slot.png``) as a placeholder.
This script pulls each slot's wiki image into ``equipment_slots/<slot_id>.png``
so the runtime can show it with a plain ``QIcon(path)`` and degrade to a
text-only row when a file is missing. Developer-only; never runs inside Anki.

Why an explicit (slot id -> wiki File title) manifest instead of slug inference:
the slot ids are AnkiScape's internal keys (``ammunition``, ``weapon``) while the
wiki titles are the interface sprite names (``Ammunition slot.png``,
``Weapon slot.png``). Pinning the pair keeps the fetched files aligned with
``ui.equipment_slot_icon_path`` and with ``equipment_data.EQUIPMENT_SLOTS``. The
manifest is cross-checked against EQUIPMENT_SLOTS at startup so a future slot
addition fails loudly here rather than silently shipping without art.

Slot art is fetched alpha-cropped but unpadded (no ``--size``) for the same
"preprocess once, display with a plain QIcon" contract as the other AnkiScape
icons. Re-runs skip files that already exist unless ``--force`` is passed.

Usage:
    uv run tools/fetch_equipment_assets.py
    uv run tools/fetch_equipment_assets.py --dry-run
    uv run tools/fetch_equipment_assets.py --force
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

PROVENANCE = Path("assets_provenance.json")

# slot_id -> OSRS wiki File title for the greyed interface placeholder. Output
# lands in equipment_slots/<slot_id>.png to match ui.equipment_slot_icon_path.
SLOT_WIKI_TITLES: Dict[str, str] = {
    "head": "Head slot.png",
    "cape": "Cape slot.png",
    "neck": "Neck slot.png",
    "ammunition": "Ammo slot.png",
    "weapon": "Weapon slot.png",
    "body": "Body slot.png",
    "shield": "Shield slot.png",
    "legs": "Legs slot.png",
    "hands": "Hands slot.png",
    "feet": "Feet slot.png",
    "ring": "Ring slot.png",
}


def _build_manifest() -> List[Tuple[str, str, str]]:
    """Return (slot_id, wiki_title, output_rel) cross-checked vs EQUIPMENT_SLOTS."""
    try:
        from equipment_data import EQUIPMENT_SLOTS
    except ImportError as exc:  # pragma: no cover - dev tool only
        raise AssetFetchError("Could not import EQUIPMENT_SLOTS from equipment_data.py.") from exc

    slot_ids = [slot.id for slot in EQUIPMENT_SLOTS]
    missing = [sid for sid in slot_ids if sid not in SLOT_WIKI_TITLES]
    if missing:
        raise AssetFetchError(
            f"No wiki title mapped for slot(s) {missing!r}; update SLOT_WIKI_TITLES."
        )
    return [
        (sid, SLOT_WIKI_TITLES[sid], f"equipment_slots/{sid}.png")
        for sid in slot_ids
    ]


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Overwrite existing files.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve without downloading.")
    args = parser.parse_args(argv)

    try:
        manifest = _build_manifest()
    except AssetFetchError as exc:
        print(f"error: {exc}")
        return 2

    client = HttpWikiClient()
    ok = skipped = failed = 0
    failures: List[str] = []
    for slot_id, wiki_title, out_rel in manifest:
        request = AssetRequest(
            item_name=f"{slot_id} slot",
            wiki_title=wiki_title_for_item(slot_id, wiki_title),
            output_path=Path(out_rel),
            provenance_path=PROVENANCE,
        )
        try:
            outcome = fetch_asset(request, client, size=None, force=args.force, dry_run=args.dry_run)
        except AssetFetchError as exc:
            failed += 1
            failures.append(f"{slot_id}: {exc}")
            print(f"  FAIL {slot_id} -> {out_rel}: {exc}")
            continue
        if outcome.skipped_existing:
            skipped += 1
            print(f"  skip {slot_id} (exists) -> {out_rel}")
        else:
            ok += 1
            print(f"  ok   {slot_id} [{outcome.source_wiki}] -> {out_rel}")

    print(f"\nDone. {ok} fetched, {skipped} skipped, {failed} failed.")
    if failures:
        print("Failures:")
        for line in failures:
            print(f"  - {line}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
