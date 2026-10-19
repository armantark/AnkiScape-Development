"""Every counter the player reads counts cards at the speed being played.

A short timer holds ticks and a card spends six per unit of game speed, so a
counter shows ceil(ticks / (6 x speed)) cards; a counter of six-tick steps shows
ceil(steps / speed). At x1 each count is the one shown before ticks.
"""

import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic.agility_logic import agility_aura_rows_pure
from ankiscape.logic.evil_tree_logic import advance_evil_tree_world_clock_pure, apply_evil_tree_review_pure
from ankiscape.logic.gnome_restaurant_logic import apply_gnome_restaurant_command_pure
from ankiscape.logic.pace.more_planks import more_planks_reviews_left_pure
from ankiscape.logic.review_strip_logic import dnd_notification_rows_pure, world_event_rows_pure
from ankiscape.logic.summoning_logic import (
    default_summoning_state_pure,
    familiar_reviews_remaining_pure,
    familiarisation_view_pure,
)
from ankiscape.data.evil_tree_data import EVIL_TREE_UTILITY_ID
from tests.test_evil_tree import _player as _evil_tree_player
from tests.pace.test_card_budget import _ReviewDispatcherCase
from tests.test_gnome_restaurant import _on_job, _rng
from tests.test_integration_smoke import _DummyCol, _DummyMW


def _blessed(speed: int):
    """A felled Normal tree: a six-minute (600-tick) blessing."""
    player, _ = advance_evil_tree_world_clock_pure(_evil_tree_player(answered_cards=20))
    for _phase in range(3):
        player, ok, result = apply_evil_tree_review_pure(
            player, has_usable_hatchet=True, reward_rolls=(0.0, 0.0, 0.0, 0.0), speed=speed
        )
        assert ok, result
    return player, result


class CountersAtSpeedTests(unittest.TestCase):
    def test_the_hard_decline_wait_counts_cards_at_the_speed(self):
        # Five source minutes, 500 ticks: 9 cards at x10, 84 at x1.
        for speed, cards in ((10, 9), (1, 84)):
            declined, ok, info = apply_gnome_restaurant_command_pure(
                _on_job("hard"), "decline_order", {}, _rng([0.0]), speed=speed
            )
            self.assertTrue(ok, info)
            self.assertIn(f"for {cards} more review(s)", info["message"])

    def test_the_evil_tree_blessing_counts_cards_at_the_speed(self):
        for speed, cards in ((10, 10), (1, 100)):
            player, felled = _blessed(speed)
            self.assertEqual(felled["blessing_reviews"], cards)
            statuses = dict(dnd_notification_rows_pure(player, activity_ids=(EVIL_TREE_UTILITY_ID,), speed=speed))
            self.assertEqual(statuses[EVIL_TREE_UTILITY_ID], f"Evil Tree blessing · {cards} reviews left")
            self.assertIn(
                (EVIL_TREE_UTILITY_ID, f"Evil Tree blessing · {cards} reviews left"),
                world_event_rows_pure(player, speed=speed),
            )

    def test_triple_charms_count_cards_at_the_speed(self):
        # A 40-minute blessing, 4,000 ticks: 67 cards at x10, 667 at x1.
        player = {
            "summoning_level": 99,
            "summoning_state": {**default_summoning_state_pure(), "triple_charm_ticks_remaining": 4_000},
        }
        for speed, cards in ((10, 67), (1, 667)):
            self.assertEqual(familiarisation_view_pure(player, speed)["triple_charm_reviews_remaining"], cards)

    def test_a_familiar_counts_cards_at_the_speed(self):
        # A six-minute spirit wolf, 600 ticks: 10 cards at x10, 100 at x1.
        follower = {"entity_id": "spirit_wolf", "remaining_ticks": 600}
        self.assertEqual(
            [familiar_reviews_remaining_pure(follower, speed) for speed in (10, 1)], [10, 100]
        )

    def test_more_planks_counts_cards_at_the_speed(self):
        # Twenty minutes, 2,000 ticks: 34 cards at x10, 334 at x1.
        state = {"more_planks_ticks_remaining": 2_000}
        self.assertEqual([more_planks_reviews_left_pure(state, speed) for speed in (10, 1)], [34, 334])

    def test_surefooted_counts_agility_cards_at_the_speed(self):
        # Charges count six-tick Agility steps; a card at speed M takes M of them.
        def state_text(charges: dict, speed: int) -> str:
            player = {"inventory": {"Surefooted aura": 1}, "agility_effect_charges": charges}
            return agility_aura_rows_pure(player, speed)[0]["state"]

        self.assertEqual(state_text({"surefooted_cooldown_reviews": 2_000}, 10), "Recharging · 200 reviews")
        self.assertEqual(state_text({"surefooted_cooldown_reviews": 2_000}, 1), "Recharging · 2,000 reviews")
        self.assertEqual(state_text({"surefooted_reviews": 333}, 10), "Active · 34 reviews left")
        self.assertEqual(state_text({"surefooted_reviews": 333}, 1), "Active · 333 reviews left")


class TheCallersPassThePlayedSpeedTests(_ReviewDispatcherCase):
    def test_a_speed_ten_felling_card_reports_the_blessing_in_speed_ten_cards(self):
        player, _ = advance_evil_tree_world_clock_pure(_evil_tree_player(answered_cards=20))
        player["current_utility"] = EVIL_TREE_UTILITY_ID
        addon = self._addon(player, 10, 0.0)
        shown = []
        addon._show_activity_gain = shown.append
        self._answer(addon)
        self.assertTrue(any("blessing 10 reviews" in line for line in shown), shown)

    def test_the_menu_reads_the_speed_the_player_set(self):
        from ankiscape.ui import ui

        with patch.object(ui, "mw", _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": 10}))):
            self.assertEqual(ui._game_speed(), 10)
        with patch.object(ui, "mw", None):
            self.assertEqual(ui._game_speed(), 1)


if __name__ == "__main__":
    unittest.main()
