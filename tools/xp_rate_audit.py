"""Grade AnkiScape's effective XP-per-review against sourced pre-EOC XP/hour.

AnkiScape pays XP per review. RuneScape was balanced in XP per hour. Those agree
only if a review's worth of game time is the same for every action — which is
exactly what nothing in the codebase currently guarantees. This tool measures
the gap, using the *shipped* probability functions rather than a reimplementation
of them, so it grades what the player actually experiences.

Two numbers matter per target:

  implied R   reviews the player must answer to earn one balancing-hour of this
              method. If two methods disagree wildly on R, one of them is
              over-rewarded relative to the other, and the ratio is the damage.

  inversions  where AnkiScape's XP/review ordering contradicts the sourced
              XP/hour ordering. An inversion means the game rewards content the
              real game made unattractive. These are the bugs with teeth.

Usage:
    python3 tools/xp_rate_audit.py            # all skills, level 99
    python3 tools/xp_rate_audit.py --level 70
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logic_pure  # noqa: E402
import mining_data  # noqa: E402
import woodcutting_data  # noqa: E402
from sourced_xp_rates import BY_SKILL  # noqa: E402


def _best(specs, level, key="level"):
    usable = [s for s in specs if s.get(key, 1) <= level]
    return max(usable, key=lambda s: s.get(key, 1)) if usable else None


def measure_mining(level):
    targets = mining_data.mining_targets_as_dict()
    picks = list(mining_data.mining_pickaxes_as_dict().values())
    pick = _best(picks, level)
    out = {}
    for tid, spec in targets.items():
        if spec.get("level", 1) > level:
            continue
        raw = logic_pure.mining_source_roll_chance_pure(level, spec, pick)
        p = logic_pure.calculate_mining_success_probability_pure(level, spec, pick)
        out[tid] = (spec["exp"], raw, p, spec["exp"] * p)
    return out, pick.get("display_name", "?")


def measure_woodcutting(level):
    targets = woodcutting_data.woodcutting_targets_as_dict()
    axes = list(woodcutting_data.woodcutting_axes_as_dict().values())
    axe = _best(axes, level)
    out = {}
    for tid, spec in targets.items():
        if spec.get("level", 1) > level:
            continue
        raw = logic_pure.woodcutting_source_roll_chance_pure(level, spec, axe)
        p = logic_pure.calculate_woodcutting_success_probability_pure(level, spec, axe)
        out[tid] = (spec["exp"], raw, p, spec["exp"] * p)
    return out, axe.get("display_name", "?")


MEASURERS = {"Mining": measure_mining, "Woodcutting": measure_woodcutting}


def audit(level):
    print(f"\nAnkiScape XP-rate audit  ·  player level {level}\n" + "=" * 96)
    all_R = []

    for skill, rates in BY_SKILL.items():
        measurer = MEASURERS.get(skill)
        if measurer is None:
            print(f"\n{skill}: not implemented yet — {len(rates)} sourced rates on file, "
                  f"nothing to grade.")
            continue

        measured, tool = measurer(level)
        print(f"\n{skill}  (best tool: {tool})")
        print(f"{'target':<14}{'xp/act':>8}{'raw p':>8}{'shipped p':>11}"
              f"{'xp/review':>11}{'sourced xp/hr':>16}{'implied R':>12}")
        print("-" * 96)

        rows = []
        for tid, (xp, raw, p, eff) in sorted(measured.items(), key=lambda kv: -kv[1][3]):
            rate = rates.get(tid)
            if rate is None:
                print(f"{tid:<14}{xp:>8.1f}{raw:>7.1%}{p:>11.1%}{eff:>11.1f}"
                      f"{'— no source —':>16}{'':>12}")
                continue
            lo, hi, _xp_src, _lvl, _cite = rate
            mid = (lo + hi) / 2
            R = mid / eff if eff else float("inf")
            all_R.append((skill, tid, R))
            rows.append((tid, eff, mid))
            src = f"{lo:,}-{hi:,}" if lo != hi else f"{lo:,}"
            print(f"{tid:<14}{xp:>8.1f}{raw:>7.1%}{p:>11.1%}{eff:>11.1f}{src:>16}{R:>12,.0f}")

        # Ordering check: does AnkiScape agree with reality about what's best?
        if len(rows) >= 2:
            ours = [t for t, _, _ in sorted(rows, key=lambda r: -r[1])]
            theirs = [t for t, _, _ in sorted(rows, key=lambda r: -r[2])]
            if ours != theirs:
                print(f"\n  !! INVERTED — AnkiScape ranks: {' > '.join(ours)}")
                print(f"     reality ranks:        {' > '.join(theirs)}")
                best_ours, best_theirs = ours[0], theirs[0]
                if best_ours != best_theirs:
                    e = dict((t, (e_, m)) for t, e_, m in rows)
                    print(f"     AnkiScape's best ({best_ours}) is only "
                          f"#{theirs.index(best_ours) + 1} in reality; reality's best "
                          f"({best_theirs}) pays {e[best_theirs][0]:.1f} xp/review here "
                          f"vs {e[best_ours][0]:.1f}.")
            else:
                print("\n  ok — ordering matches the sourced ranking.")

    if all_R:
        print("\n" + "=" * 96)
        lo = min(all_R, key=lambda r: r[2])
        hi = max(all_R, key=lambda r: r[2])
        print(f"implied R spans {lo[2]:,.0f} ({lo[0]}/{lo[1]}) to {hi[2]:,.0f} ({hi[0]}/{hi[1]}).")
        print(f"spread: {hi[2] / lo[2]:.1f}x  — every method should agree on R. "
              f"The spread IS the imbalance.")
        print(f"\nreference: combat runs at 50 ticks/review = 120 reviews per balancing-hour.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", type=int, default=99)
    audit(ap.parse_args().level)
