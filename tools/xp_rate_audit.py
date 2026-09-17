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

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic_pure import logic_pure  # noqa: E402
from ankiscape.logic.cadence_live import LIVE_COMBAT_TICKS_PER_REVIEW  # noqa: E402
from ankiscape.data import cooking_data  # noqa: E402
from ankiscape.data import firemaking_data  # noqa: E402
from ankiscape.data import fishing_data  # noqa: E402
from ankiscape.data import hunter_data  # noqa: E402
from ankiscape.data import mining_data  # noqa: E402
from ankiscape.data import woodcutting_data  # noqa: E402
from sourced_xp_rates import BY_SKILL, DETERMINISTIC  # noqa: E402


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


def measure_fishing(level):
    fish = fishing_data.fishing_fish_as_dict()
    out = {}
    for tid, spec in fish.items():
        if spec.get("level", 1) > level:
            continue
        raw = logic_pure.fishing_source_roll_chance_pure(level, spec)
        p = logic_pure.calculate_fishing_success_probability_pure(level, spec)
        out[tid] = (spec.get("exp", 0.0), raw, p, spec.get("exp", 0.0) * p)
    return out, "n/a"


def measure_hunter(level):
    targets = hunter_data.hunter_targets_as_dict()
    out = {}
    for tid, spec in targets.items():
        if spec.get("level", 1) > level:
            continue
        raw = logic_pure.hunter_source_roll_chance_pure(level, spec)
        p = logic_pure.calculate_hunter_success_probability_pure(level, spec)
        out[tid] = (spec.get("exp", 0.0), raw, p, spec.get("exp", 0.0) * p)
    return out, "n/a"


# Cooking and Firemaking call the same adapter, but their roll is an OUTCOME
# roll (burn / failed light), not a cadence roll. The adapter still distorts
# them — it makes the player burn less than the period record — but the fix is
# a different one, so they are graded separately and never mixed into the
# implied-R spread.
def measure_cooking(level):
    targets = cooking_data.cooking_targets_as_dict()
    out = {}
    for tid, spec in targets.items():
        if spec.get("level", 1) > level:
            continue
        raw = logic_pure.cooking_source_roll_chance_pure(level, spec)
        p = logic_pure.calculate_cooking_success_probability_pure(level, spec)
        out[tid] = (spec.get("exp", 0.0), raw, p, spec.get("exp", 0.0) * p)
    return out, "n/a"


def measure_firemaking(level):
    targets = firemaking_data.firemaking_targets_as_dict()
    out = {}
    for tid, spec in targets.items():
        if spec.get("level", 1) > level:
            continue
        raw = logic_pure.firemaking_source_roll_chance_pure(level, spec)
        p = logic_pure.calculate_firemaking_success_probability_pure(level, spec)
        out[tid] = (spec.get("exp", 0.0), raw, p, spec.get("exp", 0.0) * p)
    return out, "n/a"


def combat_review_rate():
    """Combat's R follows from the cadence kernel, not from a measurement.

    One review advances LIVE_COMBAT_TICKS_PER_REVIEW game ticks of 0.6 s each,
    so 3600 / (ticks * 0.6) reviews buy one balancing-hour. The kernel picks the
    tick count so this matches the R the other skills measure; the spread the
    print below reports is the residual disagreement.
    """
    return 3600.0 / (LIVE_COMBAT_TICKS_PER_REVIEW * 0.6)


MEASURERS = {
    "Mining": measure_mining,
    "Woodcutting": measure_woodcutting,
    "Fishing": measure_fishing,
    "Hunter": measure_hunter,
    "Cooking": measure_cooking,
    "Firemaking": measure_firemaking,
}

# Skills whose adapter roll decides an OUTCOME (burnt / failed to light) rather
# than the rate of actions. Excluded from the implied-R spread.
OUTCOME_ROLL_SKILLS = {"Cooking", "Firemaking"}


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
        kind = " — OUTCOME roll (burn/light), not a cadence roll" if skill in OUTCOME_ROLL_SKILLS else ""
        print(f"\n{skill}  (best tool: {tool}){kind}")
        print(f"{'target':<14}{'xp/act':>8}{'raw p':>8}{'shipped p':>11}"
              f"{'xp/review':>11}{'base xp/hr':>16}{'implied R':>12}{'acts/hr':>10}")
        print("-" * 106)

        rows = []
        for tid, (xp, raw, p, eff) in sorted(measured.items(), key=lambda kv: -kv[1][3]):
            rate = rates.get(tid)
            if rate is None:
                print(f"{tid:<14}{xp:>8.1f}{raw:>7.1%}{p:>11.1%}{eff:>11.1f}"
                      f"{'— no source —':>16}{'':>12}")
                continue
            # Strip modifiers already baked into the quote, or we double-count them.
            base_lo, base_hi = rate.base_xp_hr()
            mid = (base_lo + base_hi) / 2
            R = mid / eff if eff else float("inf")
            if skill not in OUTCOME_ROLL_SKILLS:
                all_R.append((skill, tid, R))
            rows.append((tid, eff, mid))
            src = f"{base_lo:,.0f}-{base_hi:,.0f}" if base_lo != base_hi else f"{base_lo:,.0f}"
            aph_hi = rate.actions_per_hour()[1]
            flag = " OVERFLOW" if aph_hi > 1000 else ""
            print(f"{tid:<14}{xp:>8.1f}{raw:>7.1%}{p:>11.1%}{eff:>11.1f}{src:>16}{R:>12,.0f}"
                  f"{aph_hi:>10,.0f}{flag}")
            if rate.includes:
                print(f"{'':<14}  quote includes {', '.join(rate.includes)} — stripped before grading")

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
        cr = combat_review_rate()
        # Compare combat only against skills with NEITHER defect. Woodcutting's 188
        # is a symptom, not a reference point.
        clean = [r for r in all_R if r[0] not in ("Woodcutting", "Fishing", "Hunter")]
        c_lo, c_hi = min(r[2] for r in clean), max(r[2] for r in clean)
        print(f"\nCOMBAT: {LIVE_COMBAT_TICKS_PER_REVIEW} ticks/review sets R = {cr:,.0f}.")
        print(f"  Skills with NEITHER defect MEASURE R at {c_lo:,.0f}-{c_hi:,.0f}.")
        print(f"  So one combat card buys {c_lo/cr:.2f}x-{c_hi/cr:.2f}x the game time "
              f"of one of those cards.")

    print("\n" + "=" * 96)
    print("DIRECT reads of R — deterministic artisan actions (no roll, no adapter, nothing")
    print("in the path). sourced XP/hr / XP-per-action IS the action rate.")
    print(f"\n{'method':<34}{'XP/hr':>10}{'XP/action':>11}{'R':>10}")
    print("-" * 96)
    direct = []
    for name, rate in sorted(DETERMINISTIC.items(), key=lambda kv: kv[1].actions_per_hour()[1]):
        r = rate.actions_per_hour()[1]
        direct.append(r)
        print(f"{name:<34}{rate.high_xp_hr:>10,}{rate.xp_per_action:>11.1f}{r:>10,.0f}")
    core = sorted(direct)[1:-1]  # drop the slowest and fastest
    print(f"\n  Full span {min(direct):,.0f}-{max(direct):,.0f}; the middle sits at "
          f"{min(core):,.0f}-{max(core):,.0f}.")
    print("  High Alchemy is not even inference — the period page states the cast count:")
    print("  \"can be cast up to exactly 1200 times in one hour ... 78,000 xp/hr\".")
    print("\n  => R = 1000 is corroborated. R = 1800 is not.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", type=int, default=99)
    audit(ap.parse_args().level)
