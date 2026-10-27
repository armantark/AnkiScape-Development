"""A ticked Prayers/Curses runs its prayers in a fight answered through the
real review handler, and the Combat target row's max hit is the hit that
fight rolls."""

import re
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.combat_prayer_config import apply_combat_prayer_config_pure
from ankiscape.core.constants import EQUIPMENT_ITEM_DATA
from ankiscape.core.target_metadata import combat_target_rows
from ankiscape.logic_pure.logic_pure_combat_engine import combat_hud_state_pure
from ankiscape.logic_pure.logic_pure_combat_hud import combat_setup_panel_view_pure
from tests.pace.test_combat_danger_stops import ENEMY, answer_combat
from tests.test_combat_logic import _player


def _melee_player(**settings):
    # Strength 72 sits where Burst of Strength lifts the whole old-HP max hit.
    return _player(**{
        "current_combat_target": "chicken", "combat_auto_flee": False,
        "attack_level": 70, "strength_level": 72, "prayer_level": 43, "combat_prayer_points": 430,
        "equipment": {"weapon": "Rune scimitar"}, "combat_attack_style": "aggressive", **settings,
    })


def _fight(player):
    """Answer one card; return the save after it and the max hits it rolled."""
    rolled = []

    def miss(_accuracy, max_hit_old_hp, _rng, blocked=False):
        rolled.append(max_hit_old_hp)
        return False, 0

    ctx, _calls, ok = answer_combat(player, hits=miss)
    assert ok and rolled
    return ctx.player_data, rolled


def _tooltip_max_hit(player):
    (row,) = combat_target_rows(player, {"chicken": ENEMY}, {}, EQUIPMENT_ITEM_DATA, "chicken")
    return int(re.search(r"Your max hit: (\d+) LP", row.tooltip).group(1))


class TickedPrayersTests(unittest.TestCase):
    def test_a_chosen_prayer_drains_points_and_raises_the_max_hit(self):
        unticked, plain_hits = _fight(_melee_player(combat_prayers_enabled=False))
        prayed, prayer_hits = _fight(_melee_player(combat_selected_prayers=["burst_of_strength"]))
        self.assertEqual(unticked["combat_prayer_points"], 430)
        self.assertLess(prayed["combat_prayer_points"], 430)
        self.assertGreater(prayer_hits[0], plain_hits[0])
        self.assertEqual(prayed["combat_selected_prayers"], ["burst_of_strength"])

    def test_with_none_chosen_the_fight_runs_the_best_prayers_for_the_weapon(self):
        player = _melee_player()
        self.assertEqual(
            combat_hud_state_pure(player)["prayer_texts"][0],
            "43/43 · Incredible Reflexes, Ultimate Strength, Steel Skin",
        )
        self.assertEqual(
            combat_setup_panel_view_pure(player, EQUIPMENT_ITEM_DATA)["max_hit_text"],
            "Your max hit: 160 LP with Incredible Reflexes, Ultimate Strength and Steel Skin (picked for you) · accuracy 99%",
        )
        prayed, _hits = _fight(player)
        self.assertLess(prayed["combat_prayer_points"], 430)

    def test_the_tooltip_max_hit_follows_each_prayer_setting_and_matches_the_fight(self):
        player = _melee_player(combat_prayers_enabled=False)
        self.assertEqual(_tooltip_max_hit(player), 140)
        for key, value, max_hit in (
            ("combat_prayers_enabled", True, 160),
            ("combat_selected_prayers", ["burst_of_strength"], 150),
            ("combat_prayer_uptime", "40", 140),
            ("combat_prayer_uptime", "100", 150),
            ("combat_prayers_enabled", False, 140),
        ):
            with self.subTest(key=key, value=value):
                player = apply_combat_prayer_config_pure(player, key, value)
                _after, rolled = _fight(dict(player))
                self.assertEqual(_tooltip_max_hit(player), max_hit)
                self.assertEqual(rolled[0] * 10, max_hit)

    def test_the_hud_names_the_prayers_and_a_shorter_prayer_time(self):
        player = _melee_player(combat_selected_prayers=["burst_of_strength"], combat_prayer_points=380)
        self.assertEqual(combat_hud_state_pure(player)["prayer_texts"], ["38/43 · Burst of Strength"])
        player["combat_prayer_uptime"] = "40"
        self.assertEqual(combat_hud_state_pure(player)["prayer_texts"], ["38/43 · Burst of Strength (40%)"])
        player["combat_prayers_enabled"] = False
        self.assertEqual(combat_hud_state_pure(player)["prayer_texts"], ["38/43"])

    def test_a_long_hud_prayer_list_gives_way_to_plus_n_then_a_count(self):
        self.assertEqual(combat_hud_state_pure(_melee_player(combat_prayer_points=380))["prayer_texts"], [
            "38/43 · Incredible Reflexes, Ultimate Strength, Steel Skin",
            "38/43 · Incredible Reflexes, Ultimate Strength +1",
            "38/43 · Incredible Reflexes +2",
            "38/43 · 3 prayers",
        ])


if __name__ == "__main__":
    unittest.main()
