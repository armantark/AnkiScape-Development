#!/usr/bin/env python3
"""Render Phase-3 cadence shadow divergence by skill and route."""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from cadence_kernel import R  # noqa: E402
from constants import (  # noqa: E402
    COOKING_DATA,
    FIREMAKING_DATA,
    FISHING_DATA,
    HUNTER_DATA,
    ORE_DATA,
    TREE_DATA,
)
from cadence_shadow import (  # noqa: E402
    SOURCE_BLOCKED,
    SOURCE_READY,
    cadence_shadow_report_rows_pure,
    fraction_pair_pure,
    resolve_cadence_shadow_rate_pure,
)
from logic_pure import (  # noqa: E402
    calculate_fishing_success_probability_pure,
    eligible_fishing_fish_pure,
)
from xp_rate_audit import MEASURERS  # noqa: E402


def _fraction(pair) -> Fraction:
    return Fraction(int(pair[0]), int(pair[1]))


def _number(pair) -> float:
    return float(_fraction(pair))


def catalog_rows() -> list[dict]:
    """Return a level-99 projection for every live route in the six-skill scope."""

    route_tables = {
        "mining": ORE_DATA,
        "woodcutting": TREE_DATA,
        "fishing": FISHING_DATA,
        "hunter": HUNTER_DATA,
        "cooking": COOKING_DATA,
        "firemaking": FIREMAKING_DATA,
    }
    measured = {
        skill.lower(): MEASURERS[skill](99)[0]
        for skill in ("Mining", "Woodcutting", "Hunter", "Cooking", "Firemaking")
    }
    rows = []
    for skill_id, table in route_tables.items():
        skill = skill_id.title() if skill_id != "woodcutting" else "Woodcutting"
        for action_id in table:
            resolved = resolve_cadence_shadow_rate_pure(skill_id, action_id)
            if skill_id == "fishing":
                dry = Fraction(1, 1)
                expected_xp = Fraction(0, 1)
                for fish in eligible_fishing_fish_pure(table[action_id], 99, 99, 99):
                    chance = Fraction(str(calculate_fishing_success_probability_pure(99, fish)))
                    expected_xp += dry * chance * Fraction(str(fish.get("exp", 0)))
                    dry *= 1 - chance
                current_xp_hour = expected_xp * R
            else:
                current_entry = measured[skill_id].get(action_id)
                current_xp_hour = Fraction(str(current_entry[3])) * R if current_entry else Fraction(0, 1)
                if skill_id == "mining" and current_entry and table[action_id].get("weighted_outputs"):
                    weighted = table[action_id]["weighted_outputs"]
                    total_weight = sum(Fraction(str(row.get("weight", 0))) for row in weighted)
                    expected_xp = (
                        sum(
                            Fraction(str(row.get("weight", 0))) * Fraction(str(row.get("exp", 0)))
                            for row in weighted
                        )
                        / total_weight
                        if total_weight
                        else Fraction(0, 1)
                    )
                    current_xp_hour = expected_xp * Fraction(str(current_entry[2])) * R

            source_low = _fraction(resolved.get("source_low_xp_hour", [0, 1]))
            source_high = _fraction(resolved.get("source_high_xp_hour", [0, 1]))
            proposed_low = proposed_high = Fraction(0, 1)
            if resolved["source_status"] == SOURCE_READY:
                if skill_id in {"cooking", "firemaking"}:
                    current_entry = measured[skill_id].get(action_id)
                    proposed = (
                        Fraction(str(current_entry[0])) * Fraction(str(current_entry[1])) * R
                        if current_entry
                        else Fraction(0, 1)
                    )
                    proposed_low = proposed_high = proposed
                else:
                    source_xp = _fraction(resolved["source_xp_per_action"])
                    low_rate = _fraction(resolved["low_actions_per_hour"])
                    high_rate = _fraction(resolved["high_actions_per_hour"])
                    proposed_low = min(low_rate, R) * source_xp
                    proposed_high = min(high_rate, R) * source_xp
            rows.append(
                {
                    "skill_id": skill_id,
                    "action_id": action_id,
                    "source_key": resolved.get("source_key", ""),
                    "source_status": resolved["source_status"],
                    "source_blocked_reason": resolved.get("source_blocked_reason", ""),
                    "assigned_reviews": 0,
                    "current_xp_hour": fraction_pair_pure(current_xp_hour),
                    "proposed_low_xp_hour": fraction_pair_pure(proposed_low),
                    "proposed_high_xp_hour": fraction_pair_pure(proposed_high),
                    "source_low_xp_hour": fraction_pair_pure(source_low),
                    "source_high_xp_hour": fraction_pair_pure(source_high),
                }
            )
    return sorted(rows, key=lambda row: (row["skill_id"], row["action_id"]))


def _format_rate(low, high) -> str:
    lo = _number(low)
    hi = _number(high)
    if lo == hi:
        return f"{lo:,.0f}"
    return f"{lo:,.0f}–{hi:,.0f}"


def render_text(rows: list[dict]) -> str:
    lines = [
        "Cadence Phase 3 catalog projection (level 99)" if rows and not any(row.get("assigned_reviews") for row in rows) else "Cadence Phase 3 observed shadow divergence",
        f"R = {R} reviews per balancing-hour",
        "",
        f"{'skill':<13} {'route':<30} {'current XP/h':>15} {'kernel XP/h':>18} {'2012 XP/h':>16}  status",
        "-" * 112,
    ]
    for row in rows:
        status = row.get("source_status", SOURCE_BLOCKED)
        if status == SOURCE_READY:
            proposed = _format_rate(row["proposed_low_xp_hour"], row["proposed_high_xp_hour"])
        else:
            proposed = "source_blocked"
        sourced = (
            _format_rate(row["source_low_xp_hour"], row["source_high_xp_hour"])
            if _number(row["source_high_xp_hour"]) > 0
            else "source_blocked"
        )
        current = _format_rate(row["current_xp_hour"], row["current_xp_hour"])
        lines.append(
            f"{row['skill_id']:<13} {row['action_id']:<30} {current:>15} {proposed:>18} {sourced:>16}  {status}"
        )
        if status == SOURCE_BLOCKED and row.get("source_blocked_reason"):
            lines.append(f"  ↳ {row['source_blocked_reason']}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path, help="JSON player-data export containing cadence_shadow")
    source.add_argument("--catalog", action="store_true", help="render the pinned source-ledger projection")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    if args.input:
        player_data = json.loads(args.input.read_text(encoding="utf-8"))
        rows = list(cadence_shadow_report_rows_pure(player_data))
    else:
        rows = catalog_rows()
    if args.format == "json":
        print(json.dumps(rows, indent=2, sort_keys=True))
    else:
        print(render_text(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
