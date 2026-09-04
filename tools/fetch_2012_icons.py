#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Run the strict pre-EOC RuneScape icon sweep."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.historical_assets.fetch_2012_icons import (  # noqa: E402
    main,
    select_newest_revision,
)

__all__ = ["main", "select_newest_revision"]

if __name__ == "__main__":
    raise SystemExit(main())
