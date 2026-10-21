#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch normalized cutoff-era Dominion Tower art."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.dominion_tower_data import DOMINION_TOWER_ASSET_MANIFEST  # noqa: E402
from tools.fetch_assets import fetch_manifest_assets  # noqa: E402


def main() -> int:
    return fetch_manifest_assets(DOMINION_TOWER_ASSET_MANIFEST, ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
