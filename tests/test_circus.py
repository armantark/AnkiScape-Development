import unittest

from circus_data import (
    CIRCUS_PERFORMANCES,
    CIRCUS_REWARDS,
    CIRCUS_WEEK_REVIEWS,
)
from circus_logic import (
    apply_circus_command_pure,
    apply_circus_review_pure,
    circus_view_pure,
    default_circus_state_pure,
    migrate_legacy_circus_state_pure,
    sanitize_circus_state_pure,
)


def _player(**overrides):
    player = {
        "circus": default_circus_state_pure(),
        "inventory": {},
        "quests": {},
        "shop_market_clock": {"answered_cards": 0},
        "magic_level": 99,
        "ranged_level": 99,
        "agility_level": 99,
        "firemaking_level": 99,
        "thieving_level": 99,
    }
    player.update(overrides)
    return player


class CircusDataTest(unittest.TestCase):
    def test_period_tables_cover_all_six_performances(self):
        self.assertEqual(tuple(CIRCUS_PERFORMANCES), (
            "magic",
            "ranged",
            "agility",
            "fire_breathing",
            "flaming_poi",
            "thieving",
        ))
        self.assertEqual(
            {key: row.max_attempts for key, row in CIRCUS_PERFORMANCES.items()},
            {
                "magic": 10,
                "ranged": 10,
                "agility": 10,
                "fire_breathing": 6,
                "flaming_poi": 6,
                "thieving": 10,
            },
        )
        self.assertEqual(len(CIRCUS_PERFORMANCES["magic"].tricks), 20)
        self.assertEqual(len(CIRCUS_PERFORMANCES["ranged"].tricks), 20)
        self.assertEqual(len(CIRCUS_PERFORMANCES["agility"].tricks), 20)
        self.assertEqual(len(CIRCUS_PERFORMANCES["fire_breathing"].tricks), 6)
        self.assertEqual(len(CIRCUS_PERFORMANCES["flaming_poi"].tricks), 6)
        self.assertEqual(len(CIRCUS_PERFORMANCES["thieving"].tricks), 5)
        self.assertEqual(CIRCUS_PERFORMANCES["magic"].tricks[0].xp, 970.0)
        self.assertEqual(CIRCUS_PERFORMANCES["agility"].tricks[-1].xp, 1354.0)
        self.assertEqual(CIRCUS_PERFORMANCES["fire_breathing"].tricks[-1].xp, 3830.0)
        self.assertEqual(CIRCUS_REWARDS["ringmaster"]["minimum_score"], 1201)


class CircusLogicTest(unittest.TestCase):
    def test_base_and_quest_performance_gates_are_independent(self):
        view = circus_view_pure(_player())
        available = {row["id"]: row["available"] for row in view["performances"]}
        self.assertTrue(available["magic"])
        self.assertTrue(available["ranged"])
        self.assertTrue(available["agility"])
        self.assertFalse(available["fire_breathing"])
        self.assertFalse(available["flaming_poi"])
        self.assertFalse(available["thieving"])

        player = _player(
            quests={
                "the_firemakers_curse": {"completed": True},
                "some_like_it_cold": {"completed": True},
            }
        )
        self.assertTrue(all(row["available"] for row in circus_view_pure(player)["performances"]))

        unchanged, ok, info = apply_circus_command_pure(
            _player(),
            "set_policy",
            {
                "performance_id": "fire_breathing",
                "strategy": "balanced",
                "automation_mode": "casual",
            },
        )
        self.assertFalse(ok)
        self.assertIn("The Firemaker's Curse", info["reason"])
        self.assertNotEqual(unchanged.get("current_utility"), "big_top_bonanza")

        unchanged, ok, info = apply_circus_command_pure(
            _player(),
            "set_routine",
            {
                "performance_id": "fire_breathing",
                "routine": ["fire_breath_74"],
            },
        )
        self.assertFalse(ok)
        self.assertIn("The Firemaker's Curse", info["reason"])
        self.assertEqual(unchanged["circus"]["selected_performance"], "agility")

    def test_one_review_resolves_and_closes_only_selected_performance(self):
        player = _player()
        updated, ok, _ = apply_circus_command_pure(
            player,
            "set_policy",
            {"performance_id": "agility", "strategy": "balanced", "automation_mode": "casual"},
        )
        self.assertTrue(ok)
        updated, result = apply_circus_review_pure(updated, (0.0,) * 10)
        self.assertTrue(result["allowed"])
        self.assertEqual(result["attempts"], 10)
        self.assertEqual(result["successes"], 10)
        self.assertTrue(result["terminal"])
        self.assertGreater(result["xp"], 0)
        view = circus_view_pure(updated)
        rows = {row["id"]: row for row in view["performances"]}
        self.assertTrue(rows["agility"]["used_this_week"])
        self.assertFalse(rows["magic"]["used_this_week"])
        self.assertEqual(result["outputs"], {"Clown hat": 1})

    def test_failure_awards_no_xp_and_still_consumes_performance(self):
        player = _player(agility_level=1)
        updated, result = apply_circus_review_pure(player, (0.999,) * 10)
        self.assertTrue(result["allowed"])
        self.assertFalse(result["success"])
        self.assertEqual(result["xp"], 0.0)
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["outputs"], {})
        self.assertFalse(circus_view_pure(updated)["can_review"])

    def test_each_level_band_awards_xp_only_once(self):
        player = _player()
        player, ok, _ = apply_circus_command_pure(
            player,
            "set_routine",
            {"performance_id": "agility", "routine": ["tightrope_99", "juggle_99"]},
        )
        self.assertTrue(ok)
        _updated, result = apply_circus_review_pure(player, (0.0, 0.0))
        self.assertEqual(result["attempts"], 2)
        self.assertEqual(result["xp"], 1354.0)

    def test_entertain_strategy_uses_variety_before_repeating(self):
        player, ok, _ = apply_circus_command_pure(
            _player(),
            "set_policy",
            {
                "performance_id": "agility",
                "strategy": "entertain",
                "automation_mode": "casual",
            },
        )
        self.assertTrue(ok)
        _updated, result = apply_circus_review_pure(player, (0.0,) * 10)
        self.assertEqual(len(result["trick_ids"]), 10)
        self.assertEqual(len(set(result["trick_ids"])), 10)

    def test_above_level_success_uses_disclosed_barely_success_band(self):
        player = _player(agility_level=40)
        player, ok, _ = apply_circus_command_pure(
            player,
            "set_routine",
            {"performance_id": "agility", "routine": ["tightrope_99"]},
        )
        self.assertTrue(ok)
        _updated, result = apply_circus_review_pure(player, (0.0,))
        self.assertEqual(result["xp"], 419.0)

    def test_performance_reopens_on_next_answered_card_week(self):
        player, result = apply_circus_review_pure(_player(), (0.0,) * 10)
        self.assertTrue(result["allowed"])
        self.assertFalse(circus_view_pure(player)["can_review"])
        player["shop_market_clock"]["answered_cards"] = CIRCUS_WEEK_REVIEWS
        self.assertTrue(circus_view_pure(player)["can_review"])

    def test_direct_abandon_closes_only_named_performance(self):
        player, ok, _ = apply_circus_command_pure(
            _player(),
            "abandon",
            {"performance_id": "magic"},
        )
        self.assertTrue(ok)
        rows = {row["id"]: row for row in circus_view_pure(player)["performances"]}
        self.assertTrue(rows["magic"]["used_this_week"])
        self.assertFalse(rows["agility"]["used_this_week"])

    def test_reclaim_restores_only_missing_unlocked_costumes(self):
        player = _player()
        player["circus"]["unlocked_costumes"] = ["Giant's hand", "Acrobat hood"]
        player["inventory"] = {"Giant's hand": 1}
        player, ok, info = apply_circus_command_pure(player, "reclaim_costumes")
        self.assertTrue(ok)
        self.assertEqual(info["outputs"], {"Acrobat hood": 1})
        self.assertEqual(player["inventory"], {"Giant's hand": 1, "Acrobat hood": 1})

    def test_reclaim_does_not_duplicate_an_equipped_costume(self):
        player = _player(equipment={"head": "Clown hat"})
        player["circus"]["unlocked_costumes"] = ["Clown hat"]
        unchanged, ok, info = apply_circus_command_pure(
            player,
            "reclaim_costumes",
        )
        self.assertFalse(ok)
        self.assertIn("No unlocked", info["reason"])
        self.assertEqual(unchanged["equipment"], {"head": "Clown hat"})
        self.assertEqual(unchanged["inventory"], {})

    def test_legacy_agility_week_and_audience_score_migrate(self):
        migrated = migrate_legacy_circus_state_pure(
            {
                "agility_circus_last_week": 3,
                "agility_activity_currencies": {"circus_audience": 777},
            }
        )
        self.assertEqual(migrated["used_week_by_performance"], {"agility": 3})
        self.assertEqual(migrated["lifetime_score"], 777)

    def test_sanitizer_drops_invalid_policy_and_routine_values(self):
        state = sanitize_circus_state_pure(
            {
                "selected_performance": "invalid",
                "automation_mode": "invalid",
                "strategies": {"agility": "invalid"},
                "advanced_routines": {"agility": ["invalid", "tightrope_10"]},
                "unlocked_costumes": ["invalid", "Acrobat hood"],
            }
        )
        self.assertEqual(state["selected_performance"], "agility")
        self.assertEqual(state["automation_mode"], "casual")
        self.assertEqual(state["strategies"]["agility"], "balanced")
        self.assertEqual(state["advanced_routines"]["agility"], ["tightrope_10"])
        self.assertEqual(state["unlocked_costumes"], ["Acrobat hood"])


if __name__ == "__main__":
    unittest.main()
