import unittest

from ui import compute_level_progress
from constants import EXP_TABLE

class TestReviewHUDProgress(unittest.TestCase):
    def test_progress_basic_mid_level(self):
        # Choose a level and midpoint exp
        lvl = 10
        prev = EXP_TABLE[lvl-1]
        nxt = EXP_TABLE[lvl]
        mid = (prev + nxt) / 2
        pct, remain, target = compute_level_progress(lvl, mid, EXP_TABLE)
        self.assertTrue(45 <= pct <= 55)  # around 50%
        self.assertAlmostEqual(remain, nxt - mid, delta=1e-6)
        self.assertEqual(target, min(lvl+1, 99))

    def test_progress_bounds_low(self):
        pct, remain, target = compute_level_progress(1, 0.0, EXP_TABLE)
        self.assertEqual(pct, 0)
        self.assertGreaterEqual(remain, 0.0)
        self.assertEqual(target, 2)

    def test_progress_bounds_high_level(self):
        # At very high levels ensure no crash and pct in range
        pct, remain, target = compute_level_progress(98, EXP_TABLE[98] - 1, EXP_TABLE)
        self.assertTrue(0 <= pct <= 100)
        self.assertGreaterEqual(remain, 0.0)
        self.assertEqual(target, 99)

    def test_progress_overflow_exp(self):
        lvl = 20
        pct, remain, _ = compute_level_progress(lvl, EXP_TABLE[lvl] + 12345, EXP_TABLE)
        self.assertEqual(pct, 100)
        self.assertEqual(remain, 0.0)

    def test_progress_handles_bad_inputs(self):
        # Negative level and None exp should not crash
        pct, remain, target = compute_level_progress(-5, None, EXP_TABLE)  # type: ignore[arg-type]
        self.assertTrue(0 <= pct <= 100)
        self.assertGreaterEqual(remain, 0.0)
        self.assertGreaterEqual(target, 2)

    def test_progress_max_level_bounds(self):
        # Level 99 boundary uses last table values
        lvl = 99
        pct, remain, target = compute_level_progress(lvl, EXP_TABLE[-1], EXP_TABLE)
        self.assertEqual(pct, 100)
        self.assertEqual(remain, 0.0)
        self.assertEqual(target, 99)

if __name__ == "__main__":
    unittest.main()
