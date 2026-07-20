import unittest

from evil_tree_data import (
    EVIL_TREE_ACTIVE_REVIEWS,
    EVIL_TREE_KINDLING,
    EVIL_TREE_SPAWN_REVIEWS,
    EVIL_TREE_TIERS_BY_ID,
)
from evil_tree_logic import (
    advance_evil_tree_world_clock_pure,
    apply_evil_tree_review_pure,
    default_evil_tree_state_pure,
    evil_tree_entry_mode_pure,
    evil_tree_spawn_due_pure,
    evil_tree_view_pure,
    sanitize_evil_tree_state_pure,
)


def _player(*, answered_cards=0, level=99):
    return {
        "inventory": {},
        "toolbelt": {"woodcutting": ["dragon_hatchet"]},
        "shop_market_clock": {"answered_cards": answered_cards},
        "woodcutting_level": level,
        "farming_level": level,
        "firemaking_level": level,
        "woodcutting_exp": 0.0,
        "farming_exp": 0.0,
        "firemaking_exp": 0.0,
        "evil_tree": default_evil_tree_state_pure(),
    }


class TestEvilTreeData(unittest.TestCase):
    def test_period_table_keeps_recovered_gates_and_xp(self):
        normal = EVIL_TREE_TIERS_BY_ID["normal"]
        elder = EVIL_TREE_TIERS_BY_ID["elder"]

        self.assertEqual(
            (
                normal.woodcutting_level,
                normal.farming_level,
                normal.firemaking_level,
                normal.nurture_xp,
                normal.root_xp,
                normal.tree_xp,
                normal.firemaking_xp,
            ),
            (1, 1, 1, 20.0, 3.0, 15.1, 200.0),
        )
        self.assertEqual(
            (
                elder.woodcutting_level,
                elder.farming_level,
                elder.firemaking_level,
                elder.nurture_xp,
                elder.root_xp,
                elder.tree_xp,
                elder.firemaking_xp,
            ),
            (85, 42, 85, 687.5, 15.5, 77.8, 2000.5),
        )


class TestEvilTreeWorldClock(unittest.TestCase):
    def test_spawn_and_expiry_use_only_answered_cards(self):
        player = _player(answered_cards=EVIL_TREE_SPAWN_REVIEWS - 1)
        self.assertFalse(evil_tree_spawn_due_pure(player))

        before, events = advance_evil_tree_world_clock_pure(player)
        self.assertEqual(events, ())
        before["shop_market_clock"]["answered_cards"] = EVIL_TREE_SPAWN_REVIEWS
        self.assertTrue(evil_tree_spawn_due_pure(before))

        active, events = advance_evil_tree_world_clock_pure(
            before, tier_roll=0.0, location_roll=0.0
        )
        self.assertEqual(events[0]["kind"], "spawned")
        self.assertEqual(active["evil_tree"]["active_event"]["tier_id"], "normal")
        self.assertEqual(
            active["evil_tree"]["active_event"]["reviews_remaining"],
            EVIL_TREE_ACTIVE_REVIEWS,
        )

        active["shop_market_clock"]["answered_cards"] += EVIL_TREE_ACTIVE_REVIEWS
        expired, events = advance_evil_tree_world_clock_pure(active)
        self.assertEqual(events[0]["kind"], "expired")
        self.assertEqual(expired["evil_tree"]["active_event"], {})
        self.assertEqual(
            expired["evil_tree"]["next_spawn_card"],
            EVIL_TREE_SPAWN_REVIEWS + EVIL_TREE_ACTIVE_REVIEWS
            + EVIL_TREE_SPAWN_REVIEWS,
        )

    def test_new_blessing_is_not_spent_on_its_grant_card(self):
        player = _player(answered_cards=20)
        player, _ = advance_evil_tree_world_clock_pure(player)
        for _phase in range(3):
            player, ok, result = apply_evil_tree_review_pure(
                player,
                has_usable_hatchet=True,
                reward_rolls=(0.0, 0.0, 0.0, 0.0),
            )
            self.assertTrue(ok)
        granted = int(result["blessing_reviews"])

        same_card, _ = advance_evil_tree_world_clock_pure(player)
        self.assertEqual(
            same_card["evil_tree"]["blessing_reviews_remaining"], granted
        )
        same_card["shop_market_clock"]["answered_cards"] += 1
        next_card, _ = advance_evil_tree_world_clock_pure(same_card)
        self.assertEqual(
            next_card["evil_tree"]["blessing_reviews_remaining"], granted - 1
        )


class TestEvilTreeSession(unittest.TestCase):
    def test_full_visit_is_three_atomic_phases_with_bounded_rewards(self):
        player = _player(answered_cards=20)
        player, _ = advance_evil_tree_world_clock_pure(player)

        player, ok, nurture = apply_evil_tree_review_pure(
            player, has_usable_hatchet=True
        )
        self.assertTrue(ok)
        self.assertEqual(nurture["phase"], "nurture")
        self.assertEqual(player["farming_exp"], 20.0)
        self.assertEqual(player["evil_tree"]["session"]["phase"], "prepare")

        player, ok, prepare = apply_evil_tree_review_pure(
            player, has_usable_hatchet=True
        )
        self.assertTrue(ok)
        self.assertEqual(prepare["outputs"], {EVIL_TREE_KINDLING: 1})
        self.assertEqual(player["woodcutting_exp"], 3.0)
        self.assertEqual(player["evil_tree"]["session"]["phase"], "fell")

        player, ok, fell = apply_evil_tree_review_pure(
            player,
            has_usable_hatchet=True,
            reward_rolls=(0.0, 0.0, 0.0, 0.0),
        )
        self.assertTrue(ok)
        self.assertTrue(fell["completed"])
        self.assertEqual(fell["outputs"], {"Logs": 6, "Coins": 92, "Acorn": 1})
        self.assertEqual(player["woodcutting_exp"], 18.1)
        self.assertEqual(player["firemaking_exp"], 200.0)
        self.assertEqual(player["inventory"].get(EVIL_TREE_KINDLING), 0)
        self.assertEqual(player["evil_tree"]["active_event"], {})

    def test_nurture_only_visit_is_explicit_and_consumes_one_interaction(self):
        player = _player(answered_cards=20, level=1)
        player["farming_level"] = 99
        player, _ = advance_evil_tree_world_clock_pure(
            player, tier_roll=0.8, location_roll=0.0
        )

        mode, reasons = evil_tree_entry_mode_pure(
            player, has_usable_hatchet=False
        )
        self.assertEqual(mode, "nurture_only")
        self.assertIn("75 Woodcutting", reasons)
        self.assertIn("75 Firemaking", reasons)

        updated, ok, result = apply_evil_tree_review_pure(
            player, has_usable_hatchet=False
        )
        self.assertTrue(ok)
        self.assertTrue(result["partial"])
        self.assertEqual(updated["farming_exp"], 311.0)
        self.assertEqual(updated["evil_tree"]["participations_today"], 1)
        self.assertEqual(updated["evil_tree"]["session"], {})

    def test_view_and_sanitizer_reject_malformed_nested_state(self):
        sanitized = sanitize_evil_tree_state_pure(
            {
                "active_event": "bad",
                "session": {"phase": "teleport"},
                "participations_today": 99,
                "blessing_reviews_remaining": 99,
            }
        )
        self.assertEqual(sanitized["active_event"], {})
        self.assertEqual(sanitized["session"], {})
        self.assertEqual(sanitized["participations_today"], 2)
        self.assertEqual(sanitized["blessing_reviews_remaining"], 5)

        view = evil_tree_view_pure(
            _player(answered_cards=7), has_usable_hatchet=True
        )
        self.assertFalse(view["active"])
        self.assertEqual(view["next_reviews"], 13)

    def test_expired_session_reason_survives_until_the_next_attempt(self):
        player = _player(answered_cards=20)
        player, _ = advance_evil_tree_world_clock_pure(player)
        player, ok, _ = apply_evil_tree_review_pure(
            player, has_usable_hatchet=True
        )
        self.assertTrue(ok)
        player["shop_market_clock"]["answered_cards"] += 5
        player, events = advance_evil_tree_world_clock_pure(player)
        self.assertEqual(events[0]["kind"], "expired")

        _unchanged, ok, result = apply_evil_tree_review_pure(
            player, has_usable_hatchet=True
        )
        self.assertFalse(ok)
        self.assertEqual(
            result["reason"],
            "The Evil Tree withered before the session finished.",
        )


if __name__ == "__main__":
    unittest.main()
