"""Behavior tests for the one-time Stronghold of Security landmark.

Covers the pure step/reward math, the storage default + migration seam, and the
review-answer integration that advances one level per card and pops the reward
callback the moment the fourth level is cleared.
"""
import unittest

from logic_pure import (
    STRONGHOLD_BOOT_CHOICES,
    STRONGHOLD_REWARD_COINS,
    STRONGHOLD_TOTAL_STEPS,
    apply_stronghold_step_pure,
    default_stronghold_state_pure,
    grant_stronghold_reward_pure,
    sanitize_stronghold_state_pure,
)
from runtime_actions import RuntimeActionContext, handle_utility_answer
from storage_pure import default_player_data, migrate_loaded_data


def _context(player_data, calls):
    return RuntimeActionContext(
        player_data=player_data,
        random_random=lambda: 0.0,
        show_error_message=lambda title, message: calls["errors"].append((title, message)),
        deactivate_current_skill=lambda: calls.__setitem__("deactivated", calls.get("deactivated", 0) + 1),
        award_skill_exp=lambda exp_key, base_exp: base_exp,
        award_hidden_skill_exp=lambda *a: None,
        level_up_check=lambda *a: None,
        check_achievements=lambda _data: calls.__setitem__("achievement_checks", calls.get("achievement_checks", 0) + 1),
        save_player_data=lambda: calls.__setitem__("saves", calls.get("saves", 0) + 1),
        refresh_skill_availability=lambda: None,
        refresh_skill_availability_partial=lambda *a: None,
        can_smith_any=lambda: False,
        show_exp=lambda exp: None,
        show_activity_gain=lambda text: calls.setdefault("activity", []).append(text),
        implemented_exp_keys_snapshot=lambda: {},
        show_quest_exp_delta=lambda _before: None,
        review_action_multiplier=1,
        prompt_stronghold_reward=lambda: calls.__setitem__("prompted", calls.get("prompted", 0) + 1),
    )


class TestStrongholdPure(unittest.TestCase):
    def test_step_advances_zero_to_four_then_no_ops(self):
        player_data = {}
        results = [apply_stronghold_step_pure(player_data) for _ in range(STRONGHOLD_TOTAL_STEPS)]
        self.assertEqual([r["step"] for r in results], [1, 2, 3, 4])
        self.assertTrue(all(r["advanced"] for r in results))
        self.assertEqual([r["just_completed"] for r in results], [False, False, False, True])
        self.assertTrue(player_data["stronghold_of_security"]["completed"])

        after = apply_stronghold_step_pure(player_data)
        self.assertFalse(after["advanced"])
        self.assertFalse(after["just_completed"])
        self.assertEqual(player_data["stronghold_of_security"]["step"], STRONGHOLD_TOTAL_STEPS)

    def test_reward_grants_exactly_coins_and_one_boot_once(self):
        player_data = {}
        for _ in range(STRONGHOLD_TOTAL_STEPS):
            apply_stronghold_step_pure(player_data)

        self.assertTrue(grant_stronghold_reward_pure(player_data, "Fancy boots"))
        self.assertEqual(player_data["inventory"]["Coins"], STRONGHOLD_REWARD_COINS)
        self.assertEqual(player_data["inventory"]["Fancy boots"], 1)
        self.assertEqual(player_data["stronghold_of_security"]["boots_choice"], "Fancy boots")

        # A second claim is inert and never adds more coins or a second boot.
        self.assertFalse(grant_stronghold_reward_pure(player_data, "Fighting boots"))
        self.assertEqual(player_data["inventory"]["Coins"], STRONGHOLD_REWARD_COINS)
        self.assertNotIn("Fighting boots", player_data["inventory"])

    def test_reward_rejects_unknown_boot_and_incomplete_state(self):
        completed = {}
        for _ in range(STRONGHOLD_TOTAL_STEPS):
            apply_stronghold_step_pure(completed)
        self.assertFalse(grant_stronghold_reward_pure(completed, "Rune boots"))

        incomplete = {}
        apply_stronghold_step_pure(incomplete)
        self.assertFalse(grant_stronghold_reward_pure(incomplete, STRONGHOLD_BOOT_CHOICES[0]))

    def test_sanitize_clamps_and_repairs(self):
        self.assertEqual(sanitize_stronghold_state_pure(None), default_stronghold_state_pure())
        clamped = sanitize_stronghold_state_pure({"step": 99, "boots_choice": "bogus"})
        self.assertEqual(clamped["step"], STRONGHOLD_TOTAL_STEPS)
        self.assertTrue(clamped["completed"])  # step at max implies completed
        self.assertIsNone(clamped["boots_choice"])

        garbage_step = sanitize_stronghold_state_pure({"step": "x"})
        self.assertEqual(garbage_step["step"], 0)
        self.assertFalse(garbage_step["completed"])


class TestStrongholdStorage(unittest.TestCase):
    def test_default_player_data_seeds_fresh_state(self):
        data = default_player_data({})
        self.assertEqual(data["stronghold_of_security"], default_stronghold_state_pure())

    def test_migration_backfills_and_sanitizes(self):
        migrated = migrate_loaded_data({}, {})
        self.assertEqual(migrated["stronghold_of_security"], default_stronghold_state_pure())

        repaired = migrate_loaded_data({"stronghold_of_security": {"step": 100}}, {})
        self.assertEqual(repaired["stronghold_of_security"]["step"], STRONGHOLD_TOTAL_STEPS)
        self.assertTrue(repaired["stronghold_of_security"]["completed"])


class TestStrongholdReviewIntegration(unittest.TestCase):
    def test_four_reviews_clear_it_and_the_last_pops_the_reward(self):
        player_data = {"current_utility": "stronghold_of_security"}
        calls = {"errors": []}

        for _ in range(STRONGHOLD_TOTAL_STEPS):
            self.assertTrue(handle_utility_answer(_context(player_data, calls)))

        self.assertTrue(player_data["stronghold_of_security"]["completed"])
        self.assertEqual(calls.get("prompted"), 1)
        self.assertEqual(calls.get("saves"), STRONGHOLD_TOTAL_STEPS)

        # A fifth review is a no-op: nothing advances, and the reward is not
        # re-prompted.
        self.assertFalse(handle_utility_answer(_context(player_data, calls)))
        self.assertEqual(calls.get("prompted"), 1)


if __name__ == "__main__":
    unittest.main()
