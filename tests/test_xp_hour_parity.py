"""XP/hour parity: does AnkiScape rank training methods the way 2012 did?

RuneScape was balanced in XP per *hour*. AnkiScape pays XP per *review*. Those
agree only if a review buys the same amount of game time for every action, and
nothing in the codebase guarantees that — so a method can be rare, slow, and
lucrative in the real game yet come out as the best experience here.

The specific culprit is `normalize_review_success_probability_pure`
(`logic_pure.py:388`), which maps a source tick probability to a per-review one
via `0.20 + 0.72 * sqrt(p)`. Its distortion grows as p falls: near certainty the
square root is nearly the identity, but a 6.3% action is inflated to 38%. In
RuneScape a rare action is the signature of a *money* method — that is why it was
made rare — so the adapter systematically promotes exactly the content the period
game made unattractive to train.

These tests assert the invariant: **ordering by effective XP/review must match
ordering by sourced pre-EOC XP/hour.** Skills the adapter does not distort pass
today, and these are real regression guards for them. Woodcutting and Fishing are
marked `expectedFailure` — they are inverted right now. That is deliberate. When
the cadence work lands, unittest will report an *unexpected success*, which fails
the suite and forces these markers to be removed rather than forgotten.

Rates and provenance: `tools/sourced_xp_rates.py`.
Full analysis: `memory-bank/source-audits/xp-hour-provenance-ledger-2026-07-13.md`.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from sourced_xp_rates import BY_SKILL  # noqa: E402
from xp_rate_audit import MEASURERS  # noqa: E402


def _ranked_pair(skill, level=99):
    """Return (ours, theirs): method ids ranked by our XP/review, and by sourced XP/hour."""
    measured, _tool = MEASURERS[skill](level)
    rates = BY_SKILL[skill]
    rows = []
    for tid, (_xp, _raw, _p, effective) in measured.items():
        rate = rates.get(tid)
        if rate is None:
            continue  # no pre-cutoff rate; absence is a finding, not a test failure
        base_lo, base_hi = rate.base_xp_hr()
        rows.append((tid, effective, (base_lo + base_hi) / 2))
    ours = [t for t, _, _ in sorted(rows, key=lambda r: -r[1])]
    theirs = [t for t, _, _ in sorted(rows, key=lambda r: -r[2])]
    return ours, theirs


class XpHourOrderingTest(unittest.TestCase):
    # Sourced rates are quoted as wide, overlapping ranges — three Hunter methods
    # share a midpoint of exactly 75,000. Demanding an exact total order would fail
    # on tie-breaking noise and say nothing. So compare only pairs the period record
    # actually separates, and assert none of those is discordant.
    MEANINGFUL_GAP = 1.25

    def assert_no_inversion(self, skill):
        measured, _tool = MEASURERS[skill](99)
        rates = BY_SKILL[skill]
        rows = [
            (tid, eff, sum(rates[tid].base_xp_hr()) / 2)
            for tid, (_xp, _raw, _p, eff) in measured.items()
            if tid in rates
        ]
        self.assertGreaterEqual(len(rows), 2, f"{skill}: need >=2 sourced rates to rank")

        discordant = []
        for a_id, a_ours, a_theirs in rows:
            for b_id, b_ours, b_theirs in rows:
                if a_theirs <= b_theirs * self.MEANINGFUL_GAP:
                    continue  # the period record does not meaningfully separate these
                if a_ours < b_ours:  # 2012 says a is clearly better; we say b is
                    discordant.append(
                        f"{a_id} beats {b_id} in 2012 "
                        f"({a_theirs:,.0f} vs {b_theirs:,.0f} XP/hr) "
                        f"but loses here ({a_ours:.1f} vs {b_ours:.1f} XP/review)"
                    )
        self.assertEqual(
            [], discordant, f"\n{skill} is INVERTED against the period record:\n  "
            + "\n  ".join(discordant),
        )

    # --- Skills the adapter does not distort. Real regression guards. ---

    def test_mining_ordering_matches_sourced_rates(self):
        self.assert_no_inversion("Mining")

    def test_hunter_ordering_matches_sourced_rates(self):
        # Hunter's catches roll at 78-100%, where sqrt(p) is nearly the identity.
        self.assert_no_inversion("Hunter")

    def test_cooking_ordering_matches_sourced_rates(self):
        # Cooking's roll decides an outcome (burn), not a rate, and sits near 100%.
        self.assert_no_inversion("Cooking")

    # --- Known inversions. These MUST fail until the cadence work lands. ---

    @unittest.expectedFailure
    def test_woodcutting_ordering_matches_sourced_rates(self):
        """Magic logs (9% raw -> 41.6% shipped) are our 2nd-best training tree and
        2012's 2nd-worst at 17-30k XP/hr. Yew is inverted the same way. Both are
        money trees."""
        self.assert_no_inversion("Woodcutting")

    @unittest.expectedFailure
    def test_fishing_ordering_matches_sourced_rates(self):
        """Sharks (16% raw -> 48.9% shipped) are our 3rd-best fishing method and
        2012's worst — the period guide's own words are "only 20k experience per
        hour"."""
        self.assert_no_inversion("Fishing")


class ImpliedReviewRateTest(unittest.TestCase):
    """Every method should imply the same reviews-per-balancing-hour.

    It is the single global constant that converts a flashcard into game time. A
    spread means one method is over-rewarded relative to another, and the ratio is
    the damage. This test pins the undistorted skills to a sane band so a future
    change cannot quietly widen it.
    """

    UNDISTORTED = ("Mining", "Hunter", "Cooking")

    @unittest.expectedFailure
    def test_undistorted_skills_agree_on_a_review_rate(self):
        """KNOWN FAILURE. Hunter implies R = 281-833 while Cooking implies ~1,375.

        Hunter's ordering is fine — its rolls sit at 78-100%, where the adapter
        barely bites — but it still pays 2-4x too much per review, because trap
        catches carry DEAD TIME. You lay a trap and wait. AnkiScape charges one
        review per catch and ignores the wait, which is precisely the Thieving
        stall defect, already live in a shipped skill.

        So the two defects are independent: the adapter breaks *ordering* in
        Woodcutting and Fishing, and unmodelled dead time breaks *rate* in Hunter.
        A skill can pass the ordering test and still be wrong.
        """
        implied = {}
        for skill in self.UNDISTORTED:
            measured, _tool = MEASURERS[skill](99)
            for tid, (_xp, _raw, _p, effective) in measured.items():
                rate = BY_SKILL[skill].get(tid)
                if rate is None or not effective:
                    continue
                lo, hi = rate.base_xp_hr()
                implied[f"{skill}/{tid}"] = ((lo + hi) / 2) / effective

        self.assertTrue(implied, "no sourced rates measured")
        spread = max(implied.values()) / min(implied.values())
        self.assertLess(
            spread,
            4.0,
            "The skills the adapter does not distort should broadly agree on the "
            "review-to-game-time exchange rate. They no longer do:\n  "
            + "\n  ".join(f"{k}: {v:,.0f}" for k, v in sorted(implied.items(), key=lambda i: i[1])),
        )


if __name__ == "__main__":
    unittest.main()
