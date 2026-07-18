#!/usr/bin/env python3
"""Report source-declared Slayer master readiness from live Combat data."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from combat_data import COMBAT_ENEMY_DATA  # noqa: E402
from slayer_data import SLAYER_MASTERS_BY_ID  # noqa: E402
from slayer_readiness import (  # noqa: E402
    slayer_catalog_integrity_issues_pure,
    slayer_master_readiness_pure,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()

    masters = [
        slayer_master_readiness_pure(master_id, COMBAT_ENEMY_DATA)
        for master_id in SLAYER_MASTERS_BY_ID
    ]
    issues = slayer_catalog_integrity_issues_pure(COMBAT_ENEMY_DATA)
    payload = {"integrity_issues": issues, "masters": masters}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for master in masters:
            state = "live" if master["runtime_enabled"] else "hidden"
            certification = "certified" if master["certified"] else "blocked"
            print(
                f"{master['master_id']}: {certification}, {state}, "
                f"{master['ready_family_count']}/{master['family_count']} families ready"
            )
            for blocker in master["blockers"]:
                print(f"  - {blocker}")
        if issues:
            print("integrity issues:")
            for issue in issues:
                print(f"  - {issue}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
