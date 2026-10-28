"""Every counter the player reads counts cards at the speed being played.

A short timer holds ticks and a card spends six per unit of game speed, so a
counter shows ceil(ticks / (6 x speed)) cards; a counter of six-tick steps shows
ceil(steps / speed). At x1 each count is the one shown before ticks.
"""

import re
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic.agility_logic import agility_aura_rows_pure, apply_agility_command_pure
from ankiscape.logic.evil_tree_logic import advance_evil_tree_world_clock_pure, apply_evil_tree_review_pure
from ankiscape.logic.gnome_restaurant_logic import apply_gnome_restaurant_command_pure
from ankiscape.logic.fist_of_guthix_logic import fist_of_guthix_view_pure, start_fist_of_guthix_match_pure
from ankiscape.logic.pace.more_planks import more_planks_reviews_left_pure
from ankiscape.logic.pace.short_timers import cards_left_text_pure
from ankiscape.logic.review_strip_logic import dnd_notification_rows_pure, world_event_rows_pure
from ankiscape.logic.shooting_star_logic import shooting_star_view_pure
from ankiscape.logic.summoning_logic import (
    default_summoning_state_pure,
    familiar_reviews_remaining_pure,
    familiarisation_view_pure,
    triple_charms_active_pure,
)
from ankiscape.data.evil_tree_data import EVIL_TREE_UTILITY_ID
from ankiscape.logic_pure.logic_pure_combat_card import review_combat_card_view_pure
from tests.test_evil_tree import _player as _evil_tree_player
from tests.pace.rates.rate_property import _FED, skilling
from tests.pace.test_card_budget import _ReviewDispatcherCase
from tests.pace.test_combat_danger_stops import ENEMY, answer_combat
from tests.pace.test_short_timers import _HostCase, _summoned
from tests.test_fist_of_guthix_logic import _player as _fog_player
from tests.test_gnome_restaurant import _on_job, _rng
from tests.test_combat_logic import _player as _combat_player
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


class RemainingTimesReadInCardsTests(unittest.TestCase):
    def test_a_remaining_time_rounds_up_to_whole_cards(self):
        # A card buys 60 ticks at x10: an antipoison dose is 150, a super 600.
        self.assertEqual(
            [cards_left_text_pure(ticks, 10) for ticks in (150, 60, 600)],
            ["3 cards left", "1 card left", "10 cards left"],
        )

    def test_a_real_antipoison_dose_shows_the_immunity_in_cards_on_the_combat_card(self):
        player = _combat_player(
            combat_auto_flee=False, combat_supply_loadout={"potions": {"Antipoison (4)": 1}}
        )
        ctx, _calls, ok = answer_combat(player, enemy={**ENEMY, "poison_damage": 10})
        self.assertTrue(ok)
        left = ctx.player_data["combat_status_effects"]["poison_immunity"]["ticks_left"]
        card = review_combat_card_view_pure(ctx.player_data, "Combat", {}, {}, 10)
        self.assertTrue(card["target_text"].endswith(f"Poison immune: {-(-left // 60)} cards left"), card["target_text"])

    def test_the_mining_bonus_and_the_fist_of_guthix_round_read_cards_left(self):
        # 1,500 bonus ticks and a 1,000-tick round: 25 and 17 cards at x10.
        star = shooting_star_view_pure({"shooting_star": {"ore_bonus_ticks_remaining": 1_500}}, speed=10)
        self.assertEqual(star["ore_bonus_left_text"], "25 cards left")
        player = _fog_player()
        player["fist_of_guthix"]["tutorial_complete"] = True
        player, ok, _ = start_fist_of_guthix_match_pure(player, iter((0.4, 0.5, 0.2, 0.8, 0.1)).__next__)
        self.assertTrue(ok)
        self.assertEqual(fist_of_guthix_view_pure(player, speed=10)["match"]["round_left_text"], "17 cards left")


class AnsweringTheShownCardsEndsTheWaitTests(_HostCase):
    """Answering the number of cards a counter shows ends its wait; one card fewer does not."""

    def _assert_wait_ends_on_the_shown_card(self, start, ended, skill: str = "None", speeds=(10, 1)) -> None:
        """``start(speed)`` returns a save and the count it shows; ``ended(save)`` reads the gate."""
        for speed in speeds:
            player, shown = start(speed)
            addon = self._addon(speed, player)
            addon._state.current_skill = skill
            with self.subTest(speed=speed, shown=shown):
                for card in range(1, shown + 1):
                    self.assertEqual(ended(self._answer(addon, 3)), card == shown, f"card {card}")

    def test_a_declined_hard_order(self):
        def start(speed):
            player, ok, info = apply_gnome_restaurant_command_pure(
                _on_job("hard"), "decline_order", {}, _rng([0.0]), speed=speed
            )
            self.assertTrue(ok, info)
            return player, int(re.search(r"for (\d+) more review", info["message"]).group(1))

        def ended(player):
            return apply_gnome_restaurant_command_pure(player, "accept_order", {"difficulty": "hard"}, _rng([0.0]))[1]

        self._assert_wait_ends_on_the_shown_card(start, ended)

    def test_the_evil_tree_blessing(self):
        def start(speed):
            player, felled = _blessed(speed)
            return player, felled["blessing_reviews"]

        self._assert_wait_ends_on_the_shown_card(start, lambda player: not player["evil_tree"]["blessing_ticks_remaining"])

    def test_triple_charms(self):
        def start(speed):
            player = {
                "inventory": {},
                "summoning_level": 99,
                "summoning_state": {**default_summoning_state_pure(), "triple_charm_ticks_remaining": 4_000},
            }
            return player, familiarisation_view_pure(player, speed)["triple_charm_reviews_remaining"]

        self._assert_wait_ends_on_the_shown_card(start, lambda player: not triple_charms_active_pure(player))

    def test_a_familiar(self):
        def start(speed):
            player = _summoned("spiritwolf", "Spirit wolf pouch")
            return player, familiar_reviews_remaining_pure(player["summoning_state"]["active_follower"], speed)

        self._assert_wait_ends_on_the_shown_card(start, lambda player: not player["summoning_state"]["active_follower"])

    def test_more_planks(self):
        def start(speed):
            player = {"inventory": {}, "livid_farm": {"more_planks_ticks_remaining": 2_000}}
            return player, more_planks_reviews_left_pure(player["livid_farm"], speed)

        self._assert_wait_ends_on_the_shown_card(start, lambda player: not player["livid_farm"]["more_planks_ticks_remaining"])

    def test_the_surefooted_recharge(self):
        def start(speed):
            player = skilling("agility", "barbarian_normal", **_FED).player()
            player["inventory"]["Surefooted aura"] = 1
            player, command = apply_agility_command_pure(player, "activate_surefooted")
            self.assertTrue(command["allowed"], command)
            shown = agility_aura_rows_pure(player, speed)[0]["state"]
            return player, int(re.fullmatch(r"Recharging · ([\d,]+) reviews", shown).group(1).replace(",", ""))

        def ended(player):
            return apply_agility_command_pure(player, "activate_surefooted")[1]["allowed"]

        # At speed 1 the count is the 2,000 steps themselves: 2,000 Agility cards
        # take 20 seconds and check nothing the speed-10 run does not.
        self._assert_wait_ends_on_the_shown_card(start, ended, skill="Agility", speeds=(10,))


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
