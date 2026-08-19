import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic.cadence_coverage import cadence_coverage_rows_pure
from ankiscape.core.constants import (
    ITEM_DEFINITIONS,
    SORCERESS_GARDEN_ITEM_IMAGES,
    UTILITY_ACTIVITY_DATA,
)
from ankiscape.logic_pure.logic_pure import apply_consumable_pure
from ankiscape.runtime.runtime_actions import RuntimeActionContext, handle_utility_answer
from ankiscape.data.sorceress_garden_data import SORCERESS_GARDEN_HERB_POOL
from ankiscape.logic.sorceress_garden_logic import (
    apply_sorceress_garden_command_pure,
    apply_sorceress_garden_review_pure,
    default_sorceress_garden_state_pure,
    sanitize_sorceress_garden_state_pure,
    sorceress_garden_locked_reasons_pure,
    sorceress_garden_view_pure,
)
from ankiscape.core.storage_pure import CURRENT_CONFIG_VERSION, default_player_data, migrate_loaded_data


def _player(*, level=99, introduced=True):
    state = default_sorceress_garden_state_pure()
    state["introduced"] = introduced
    return {
        "inventory": {},
        "quests": {"diamond_in_the_rough": {"completed": True}},
        "thieving_level": level,
        "thieving_exp": 0.0,
        "farming_level": 1,
        "farming_exp": 0.0,
        "completed_achievements": [],
        "sorceress_garden": state,
    }


def _context(player_data, calls, rolls=(0.0, 0.5)):
    random_values = iter(rolls)

    def award_skill_exp(exp_key, amount):
        player_data[exp_key] = float(player_data.get(exp_key, 0.0) or 0.0) + amount
        return amount

    return RuntimeActionContext(
        player_data=player_data,
        random_random=lambda: next(random_values, 0.0),
        show_error_message=lambda title, message: calls["errors"].append((title, message)),
        deactivate_current_skill=lambda: calls.__setitem__("deactivated", True),
        award_skill_exp=award_skill_exp,
        award_hidden_skill_exp=lambda *_args: None,
        level_up_check=lambda skill, _data: calls["levels"].append(skill),
        check_achievements=lambda _data: calls.__setitem__("achievements", True),
        save_player_data=lambda: calls.__setitem__("saves", calls["saves"] + 1),
        refresh_skill_availability=lambda: calls.__setitem__("refresh", True),
        show_exp=lambda amount: calls["xp"].append(amount),
        show_activity_gain=lambda message: calls["activity"].append(message),
        implemented_exp_keys_snapshot=lambda: {},
        show_quest_exp_delta=lambda _before: None,
    )


class SorceressGardenPureTest(unittest.TestCase):
    def test_quest_introduction_and_season_level_are_real_entry_gates(self):
        player = _player(level=24, introduced=False)
        self.assertEqual(
            sorceress_garden_locked_reasons_pure(player),
            ("the Osman introduction",),
        )
        player, ok, _ = apply_sorceress_garden_command_pure(player, "introduce")
        self.assertTrue(ok)
        player, ok, _ = apply_sorceress_garden_command_pure(
            player, "set_preferences", {"season_id": "spring"}
        )
        self.assertTrue(ok)
        self.assertEqual(
            sorceress_garden_locked_reasons_pure(player),
            ("Thieving 25",),
        )

    def test_fruit_auto_squeezes_and_osman_turn_in_is_atomic(self):
        player = _player()
        player["sorceress_garden"].update(
            {"season_id": "summer", "harvest_mode": "fruit", "juice_mode": "osman"}
        )
        first, first_result = apply_sorceress_garden_review_pure(player)
        self.assertEqual(first["inventory"]["Summer sq'irk"], 1)
        self.assertEqual(first_result["farming_xp"], 60.0)
        first_view = sorceress_garden_view_pure(first)
        self.assertEqual(first_view["fruit_progress"], 1)
        self.assertEqual(first_view["fruit_per_juice"], 2)
        second, second_result = apply_sorceress_garden_review_pure(first)
        self.assertNotIn("Summer sq'irk", second["inventory"])
        self.assertNotIn("Summer sq'irkjuice", second["inventory"])
        self.assertEqual(second_result["thieving_xp"], 3_000.0)
        self.assertEqual(second_result["juices_completed"], 1)

    def test_kept_juice_is_a_real_consumable_with_glass_boost_and_run_credit(self):
        player = _player(level=65)
        player["sorceress_garden"].update(
            {"season_id": "summer", "harvest_mode": "fruit", "juice_mode": "keep"}
        )
        player["inventory"]["Summer sq'irk"] = 1
        harvested, result = apply_sorceress_garden_review_pure(player)
        self.assertEqual(result["juices_completed"], 1)
        self.assertEqual(harvested["inventory"]["Summer sq'irkjuice"], 1)

        consumed, consume_result = apply_consumable_pure(
            harvested, "Summer sq'irkjuice"
        )
        self.assertTrue(consume_result["allowed"])
        self.assertEqual(consumed["combat_current_levels"]["thieving"], 68)
        self.assertEqual(consumed["agility_run_energy_credit_pct"], 40)
        self.assertEqual(consumed["inventory"]["Beer glass"], 1)

    def test_herb_and_alternate_modes_return_two_period_herbs_without_hidden_progress(self):
        player = _player()
        player["sorceress_garden"]["harvest_mode"] = "alternate"
        first, first_result = apply_sorceress_garden_review_pure(player)
        self.assertEqual(first_result["harvest"], "fruit")
        self.assertEqual(first["sorceress_garden"]["alternate_next"], "herbs")
        second, second_result = apply_sorceress_garden_review_pure(
            first, (0.0, 0.999999)
        )
        self.assertEqual(second_result["harvest"], "herbs")
        self.assertEqual(sum(second_result["outputs"].values()), 2)
        self.assertEqual(
            set(second_result["outputs"]),
            {SORCERESS_GARDEN_HERB_POOL[0], SORCERESS_GARDEN_HERB_POOL[-1]},
        )
        self.assertEqual(second["sorceress_garden"]["alternate_next"], "fruit")

    def test_sanitizer_registry_storage_and_cadence_declaration_close_the_surface(self):
        state = sanitize_sorceress_garden_state_pure(
            {"season_id": "monsoon", "harvest_mode": "loot", "successful_trips": -1}
        )
        self.assertEqual(state["season_id"], "winter")
        self.assertEqual(state["harvest_mode"], "fruit")
        self.assertEqual(state["successful_trips"], 0)
        self.assertEqual(
            UTILITY_ACTIVITY_DATA["sorceress_garden"]["surface"], "activities"
        )
        registered = {item.storage_key: item for item in ITEM_DEFINITIONS}
        self.assertTrue(registered["Summer sq'irkjuice"].asset_path)
        self.assertEqual(
            set(SORCERESS_GARDEN_ITEM_IMAGES),
            {
                "Winter sq'irk",
                "Winter sq'irkjuice",
                "Spring sq'irk",
                "Spring sq'irkjuice",
                "Autumn sq'irk",
                "Autumn sq'irkjuice",
                "Summer sq'irk",
                "Summer sq'irkjuice",
            },
        )
        defaults = default_player_data({})
        self.assertEqual(defaults["config_version"], CURRENT_CONFIG_VERSION)
        migrated = migrate_loaded_data({"config_version": 54}, {})
        self.assertEqual(migrated["sorceress_garden"]["season_id"], "winter")
        row = next(
            row for row in cadence_coverage_rows_pure()
            if row["handler_key"] == "utility" and row["action_id"] == "sorceress_garden"
        )
        self.assertEqual(row["mode"], "passthrough")
        self.assertEqual(row["source_status"], "sourced")


class SorceressGardenRuntimeIntegrationTest(unittest.TestCase):
    def test_runtime_awards_both_skills_records_action_and_saves_once(self):
        player = _player()
        player.update({"current_utility": "sorceress_garden"})
        player["sorceress_garden"].update(
            {"season_id": "summer", "juice_mode": "osman"}
        )
        player["inventory"]["Summer sq'irk"] = 1
        calls = {
            "errors": [], "levels": [], "xp": [], "activity": [], "saves": 0
        }
        self.assertTrue(handle_utility_answer(_context(player, calls)))
        self.assertEqual(player["farming_exp"], 60.0)
        self.assertEqual(player["thieving_exp"], 3_000.0)
        self.assertEqual(calls["saves"], 1)
        self.assertIn("Summer garden", calls["activity"][-1])
        telemetry = player["action_telemetry"]["actions"]
        self.assertEqual(telemetry["farming:summer_fruit"]["successes"], 1)

    def test_runtime_draws_rng_only_for_the_two_random_herbs(self):
        player = _player()
        player["current_utility"] = "sorceress_garden"
        calls = {
            "errors": [], "levels": [], "xp": [], "activity": [], "saves": 0
        }
        fruit_rolls = []
        fruit_context = _context(player, calls)
        fruit_context.random_random = lambda: fruit_rolls.append(1) or 0.0
        self.assertTrue(handle_utility_answer(fruit_context))
        self.assertEqual(fruit_rolls, [])

        player["sorceress_garden"]["harvest_mode"] = "herbs"
        herb_rolls = []
        herb_context = _context(player, calls)
        herb_context.random_random = lambda: herb_rolls.append(1) or 0.0
        self.assertTrue(handle_utility_answer(herb_context))
        self.assertEqual(len(herb_rolls), 2)


if __name__ == "__main__":
    unittest.main()
