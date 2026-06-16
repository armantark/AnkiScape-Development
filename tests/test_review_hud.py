import unittest

from ui import compute_level_progress, current_target_display_name
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

class TestCurrentTargetDisplayName(unittest.TestCase):
    def test_echoes_selected_target_display_name(self):
        pd = {"current_craft": "fire_empty_pot"}
        self.assertEqual(current_target_display_name("Crafting", pd), "Empty pot")

    def test_falls_back_to_skill_default_when_unset(self):
        # Empty player data should resolve to the registry default target.
        self.assertEqual(current_target_display_name("Mining", {}), "Rune essence")

    def test_resolves_for_each_target_skill(self):
        cases = {
            "Woodcutting": ("current_tree", "oak", "Oak"),
            "Crafting": ("current_craft", "form_pot_unfired", "Pot (unfired)"),
            "Firemaking": ("current_firemaking", "oak_logs", "Oak logs"),
        }
        for skill, (key, target_id, expected) in cases.items():
            with self.subTest(skill=skill):
                self.assertEqual(
                    current_target_display_name(skill, {key: target_id}), expected
                )

    def test_unknown_target_id_echoes_raw_id(self):
        # Defensive: a stale/unknown id still shows something rather than blanking.
        out = current_target_display_name("Crafting", {"current_craft": "bogus_id"})
        self.assertEqual(out, "bogus_id")

    def test_returns_none_for_skill_without_target(self):
        # Combat skills have no selectable target -> label should hide.
        self.assertIsNone(current_target_display_name("Attack", {}))

    def test_returns_none_for_unknown_skill(self):
        self.assertIsNone(current_target_display_name("Nonsense", {}))


if __name__ == "__main__":
    unittest.main()
