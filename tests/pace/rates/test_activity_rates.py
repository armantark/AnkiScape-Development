"""Plan Part J item 1, XP per tick at speed 1 and speed 10: Utility / Activities."""

import random

from tests.pace.rates import rate_property


class ActivityRateTests(rate_property.RatePropertyCase):
    GROUPS = ("utility",)

    def test_fight_cave_recovery_matches_over_ten_small_cards_and_one_large_card(self):
        route = rate_property.SAMPLE["utility"][0]
        states = []
        for speed in (1, 10):
            self.addon._review_action_multiplier = lambda: speed
            self.addon._state.player_data = route.player()
            self.addon._state.player_data.update(combat_lifepoints=400, attack_level=1, strength_level=1)
            self.addon._state.current_skill = route.skill
            random.seed(20261104)
            for _ in range(10 // speed):
                self.assertEqual(self._card_ticks(route.skill, 60), 6 * speed)
            data = self.addon._state.player_data
            states.append((data["combat_lifepoints"], data["fight_caves"],
                           self.addon._implemented_exp_keys_snapshot()))
        self.assertEqual(states[0], states[1])
