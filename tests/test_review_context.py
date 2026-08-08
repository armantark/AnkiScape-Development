import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.review_context import (
    PIT_REWARD_CONTEXT_ID,
    SHOOTING_STAR_NOTICE_CONTEXT_ID,
    ignored_review_context_choice_pure,
    remember_review_context_choice_pure,
    review_context_projection_pure,
    sanitize_review_context_state_pure,
)
from ankiscape.logic.shooting_star_logic import default_shooting_star_state_pure


class TestReviewContext(unittest.TestCase):
    def test_shooting_star_notice_is_the_unmissable_manual_context(self):
        state = default_shooting_star_state_pure()
        state["notice"] = {
            "kind": "unminable",
            "event_id": "shooting-star-20",
            "current_size": 5,
            "required_level": 50,
            "sprite_available": False,
        }
        projection = review_context_projection_pure(
            {
                "shooting_star": state,
                "agility_activity_state": {
                    "pit_reward": {"xp": 100.0, "course": "ape_atoll"}
                },
            }
        )

        active = projection["active"]
        self.assertEqual(active["family_id"], SHOOTING_STAR_NOTICE_CONTEXT_ID)
        self.assertEqual(active["label"], "Star unminable at your level")
        self.assertEqual(
            tuple(option["label"] for option in active["options"]),
            ("Watch this star", "Dismiss"),
        )
        self.assertEqual(active["presentation"], "neutral_outline")
        self.assertEqual(projection["queued_count"], 1)
        self.assertIsNone(ignored_review_context_choice_pure({"shooting_star": state}))

    def test_pit_reward_projects_one_default_safe_choice(self):
        data = {
            "agility_activity_state": {
                "pit_reward": {"xp": 1980.0, "course": "ape_atoll"}
            }
        }

        active = review_context_projection_pure(data)["active"]

        self.assertEqual(active["family_id"], PIT_REWARD_CONTEXT_ID)
        self.assertEqual(active["detail"], "1,980 Agility XP")
        self.assertEqual(
            tuple(option["id"] for option in active["options"]),
            ("take_xp", "gamble"),
        )
        self.assertEqual(active["default_option"], "take_xp")
        self.assertIsNone(active["remembered_option"])
        self.assertEqual(
            ignored_review_context_choice_pure(data),
            (PIT_REWARD_CONTEXT_ID, "take_xp"),
        )

    def test_remembered_valid_choice_controls_ignored_resolution(self):
        data = remember_review_context_choice_pure(
            {
                "agility_activity_state": {
                    "pit_reward": {"xp": 320.0, "course": "ape_atoll"}
                }
            },
            PIT_REWARD_CONTEXT_ID,
            "gamble",
        )

        self.assertEqual(
            ignored_review_context_choice_pure(data),
            (PIT_REWARD_CONTEXT_ID, "gamble"),
        )

    def test_invalid_preferences_are_removed_and_empty_reward_is_hidden(self):
        sanitized = sanitize_review_context_state_pure(
            {
                "review_context_preferences": {
                    PIT_REWARD_CONTEXT_ID: "invented",
                    "unknown_family": "choice",
                }
            }
        )

        self.assertEqual(sanitized["review_context_preferences"], {})
        self.assertIsNone(
            review_context_projection_pure(
                {"agility_activity_state": {"pit_reward": {"xp": 0}}}
            )["active"]
        )


if __name__ == "__main__":
    unittest.main()
