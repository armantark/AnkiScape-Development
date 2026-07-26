from __future__ import annotations

import copy
import json
import os
import random
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import (
    ITEM_DEFINITIONS,
    ORE_DATA,
    UTILITY_ACTIVITY_DATA,
)
from ankiscape.core.skill_registry import trainable_skill_definitions
from ankiscape.core.storage_pure import (
    CURRENT_CONFIG_VERSION,
    default_player_data,
    migrate_loaded_data,
)
from ankiscape.data.tears_of_guthix_data import (
    ORNATE_BOWL_CRAFTING_LEVEL,
    ORNATE_BOWL_MINING_LEVEL,
    ORNATE_BOWL_TOOL,
    TEARS_OF_GUTHIX_ACTIVITY_ID,
    TEARS_OF_GUTHIX_ENTRY_CAP,
    TEARS_OF_GUTHIX_MAX_COLLECTION_TICKS,
    TEARS_OF_GUTHIX_ORNATE_BOWL_XP_CAP,
    TEARS_OF_GUTHIX_PROGRESS_EXP,
    TEARS_OF_GUTHIX_STONE_BOWL_XP_CAP,
    TEARS_OF_GUTHIX_TICKS_PER_REVIEW,
    TEARS_OF_GUTHIX_WEEK_REVIEWS,
    TEARS_OF_GUTHIX_XP_PER_LEVEL,
)
from ankiscape.logic.shop_logic import advance_shop_market_clock_pure
from ankiscape.logic.tears_of_guthix_logic import (
    apply_tears_of_guthix_command_pure,
    apply_tears_of_guthix_review_pure,
    collection_ticks_pure,
    default_tears_of_guthix_state_pure,
    reward_skill_pure,
    sanitize_tears_of_guthix_state_pure,
    tears_of_guthix_view_pure,
    total_experience_pure,
    xp_per_tear_pure,
)
from ankiscape.runtime.runtime_actions import RuntimeActionContext, handle_utility_answer


_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _player(**overrides):
    """A save that has finished the quest, with the quest's own point awarded."""
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data["quests"]["tears_of_guthix"] = {
        "started": True,
        "progress": 3,
        "completed": True,
    }
    data["quest_points"] = 44
    data.update(overrides)
    return data


def _entered(**overrides):
    data = _player(**overrides)
    entered, ok, info = apply_tears_of_guthix_command_pure(data, "enter")
    if not ok:
        raise AssertionError(info)
    return entered


def _drain(data, rng, *, limit=200):
    """Review until the cavern session resolves, yielding each beat."""
    for _ in range(limit):
        data, ok, result = apply_tears_of_guthix_review_pure(data, rng)
        if not ok:
            raise AssertionError(result)
        yield data, result
        if result.get("completed"):
            return
    raise AssertionError("the cavern session never resolved")


def _advance_a_week(data):
    for _ in range(tears_of_guthix_view_pure(data)["reviews_to_entry"]):
        data.update(advance_shop_market_clock_pure(data))
    return data


class TearsOfGuthixDataAndGatesTests(unittest.TestCase):
    def test_the_activity_row_and_period_art_are_registered(self):
        spec = UTILITY_ACTIVITY_DATA[TEARS_OF_GUTHIX_ACTIVITY_ID]
        self.assertEqual(spec["surface"], "activities")
        self.assertEqual(spec["group"], "distractions_and_diversions")
        self.assertIn("oldid=6579712", spec["source"])
        self.assertTrue(os.path.isfile(spec["icon_path"]))

    def test_period_assets_are_local_registered_and_cutoff_pinned(self):
        with open(
            os.path.join(_ROOT, "assets_provenance.json"),
            encoding="utf-8",
        ) as handle:
            provenance = json.load(handle)
        for relative in (
            "activityicons/tears_of_guthix.png",
            "activityitems/stone_bowl.png",
            "activityitems/ornate_bowl.png",
        ):
            self.assertTrue(os.path.isfile(os.path.join(_ROOT, relative)), relative)
            self.assertIn(relative, provenance)
            self.assertLessEqual(
                provenance[relative]["timestamp"],
                "2012-11-20T00:00:00Z",
                relative,
            )

    def test_the_quest_is_the_entry_gate(self):
        data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        data["quest_points"] = 44
        view = tears_of_guthix_view_pure(data)
        self.assertFalse(view["requirements_met"])
        self.assertIn("Complete the Tears of Guthix quest", view["missing_requirements"])
        blocked, ok, info = apply_tears_of_guthix_command_pure(data, "enter")
        self.assertFalse(ok)
        self.assertIn("Tears of Guthix quest", info["reason"])
        self.assertFalse(blocked["tears_of_guthix"]["active"])

    def test_quest_points_buy_the_cavern_timer_up_to_the_three_minute_cap(self):
        self.assertEqual(collection_ticks_pure(_player(quest_points=44)), 44)
        self.assertEqual(
            collection_ticks_pure(_player(quest_points=TEARS_OF_GUTHIX_MAX_COLLECTION_TICKS)),
            TEARS_OF_GUTHIX_MAX_COLLECTION_TICKS,
        )
        self.assertEqual(
            collection_ticks_pure(_player(quest_points=999)),
            TEARS_OF_GUTHIX_MAX_COLLECTION_TICKS,
        )
        # A player with the quest but no points has no cavern time at all.
        starved = _player(quest_points=0)
        self.assertIn(
            "Earn a Quest Point to buy time in the cavern",
            tears_of_guthix_view_pure(starved)["missing_requirements"],
        )

    def test_xp_per_tear_is_level_times_six_under_each_bowl_cap(self):
        self.assertEqual(xp_per_tear_pure(1, False), TEARS_OF_GUTHIX_XP_PER_LEVEL)
        self.assertEqual(xp_per_tear_pure(29, False), 29 * TEARS_OF_GUTHIX_XP_PER_LEVEL)
        self.assertEqual(xp_per_tear_pure(30, False), TEARS_OF_GUTHIX_STONE_BOWL_XP_CAP)
        self.assertEqual(xp_per_tear_pure(99, False), TEARS_OF_GUTHIX_STONE_BOWL_XP_CAP)
        self.assertEqual(xp_per_tear_pure(30, True), 30 * TEARS_OF_GUTHIX_XP_PER_LEVEL)
        self.assertEqual(xp_per_tear_pure(50, True), TEARS_OF_GUTHIX_ORNATE_BOWL_XP_CAP)
        self.assertEqual(xp_per_tear_pure(99, True), TEARS_OF_GUTHIX_ORNATE_BOWL_XP_CAP)

    def test_the_reward_skill_is_least_experience_not_lowest_level(self):
        data = _player()
        for skill in trainable_skill_definitions():
            data[skill.exp_key] = 50_000.0
            data[skill.level_key] = 90
        # Herblore is left with more levels but the least experience, which is
        # the case the period article calls out against the level reading.
        data["herblore_exp"] = 10.0
        data["herblore_level"] = 99
        data["agility_exp"] = 40_000.0
        data["agility_level"] = 1
        self.assertEqual(reward_skill_pure(data)["id"], "herblore")

    def test_commands_rebuild_owned_state_without_mutating_the_input(self):
        original = _player()
        frozen = copy.deepcopy(original)
        updated, ok, info = apply_tears_of_guthix_command_pure(original, "enter")
        self.assertTrue(ok, info)
        self.assertEqual(original, frozen)
        self.assertIsNot(updated["tears_of_guthix"], original["tears_of_guthix"])


class TearsOfGuthixMechanicsTests(unittest.TestCase):
    def test_a_beat_spends_six_ticks_and_the_session_is_finite(self):
        data = _entered()
        beats = tears_of_guthix_view_pure(data)["session_beats"]
        self.assertEqual(
            data["tears_of_guthix"]["remaining_ticks"],
            collection_ticks_pure(data),
        )
        seen = 0
        for data, _result in _drain(data, lambda: 1.0):
            seen += 1
        self.assertEqual(seen, beats)
        self.assertFalse(tears_of_guthix_view_pure(data)["active"])

    def test_green_tears_subtract_and_the_count_never_goes_negative(self):
        # Every roll below the green chance, so every tick is a green tear.
        data = _entered()
        for data, result in _drain(data, lambda: 0.0):
            self.assertEqual(result["blue_tears"], 0)
            self.assertGreater(result["green_tears"], 0)
            self.assertEqual(result["tears"], 0)
        self.assertEqual(result["tears"], 0)
        self.assertEqual(data["agility_exp"], 0.0)

    def test_leaving_preserves_the_exact_remaining_beat_count(self):
        data = _entered()
        data, _result = next(_drain(data, lambda: 1.0))
        before = tears_of_guthix_view_pure(data)
        left, ok, info = apply_tears_of_guthix_command_pure(data, "leave")
        self.assertTrue(ok, info)
        self.assertEqual(left["activity_session"], {"active_id": ""})
        after = tears_of_guthix_view_pure(left)
        self.assertTrue(after["active"])
        self.assertEqual(after["remaining_beats"], before["remaining_beats"])
        self.assertEqual(after["tears"], before["tears"])
        # Re-entering resumes the same session rather than charging a new visit.
        resumed, ok, info = apply_tears_of_guthix_command_pure(left, "enter")
        self.assertTrue(ok, info)
        self.assertEqual(
            resumed["tears_of_guthix"]["remaining_ticks"],
            left["tears_of_guthix"]["remaining_ticks"],
        )
        self.assertEqual(
            resumed["activity_session"],
            {"active_id": TEARS_OF_GUTHIX_ACTIVITY_ID},
        )

    def test_a_review_outside_the_cavern_is_refused_without_a_payout(self):
        data = _player()
        unchanged, ok, info = apply_tears_of_guthix_review_pure(data, lambda: 1.0)
        self.assertFalse(ok)
        self.assertIn("cavern", info["reason"])
        self.assertEqual(unchanged["agility_exp"], 0.0)

    def test_the_ornate_bowl_needs_both_levels_and_a_chisel(self):
        data = _player()
        blocked, ok, info = apply_tears_of_guthix_command_pure(
            data, "craft_ornate_bowl"
        )
        self.assertFalse(ok)
        self.assertIn(f"Mining level {ORNATE_BOWL_MINING_LEVEL}", info["reason"])
        self.assertIn(f"Crafting level {ORNATE_BOWL_CRAFTING_LEVEL}", info["reason"])
        self.assertFalse(blocked["tears_of_guthix"]["ornate_bowl"])

        data["mining_level"] = ORNATE_BOWL_MINING_LEVEL
        data["crafting_level"] = ORNATE_BOWL_CRAFTING_LEVEL
        toolless, ok, info = apply_tears_of_guthix_command_pure(
            data, "craft_ornate_bowl"
        )
        self.assertFalse(ok)
        self.assertIn(ORNATE_BOWL_TOOL, info["reason"])
        self.assertFalse(toolless["tears_of_guthix"]["ornate_bowl"])

        data["inventory"][ORNATE_BOWL_TOOL] = 1
        made, ok, info = apply_tears_of_guthix_command_pure(data, "craft_ornate_bowl")
        self.assertTrue(ok, info)
        self.assertTrue(made["tears_of_guthix"]["ornate_bowl"])
        # It is a permanent upgrade, so it cannot be made twice.
        again, ok, info = apply_tears_of_guthix_command_pure(made, "craft_ornate_bowl")
        self.assertFalse(ok)
        self.assertTrue(again["tears_of_guthix"]["ornate_bowl"])

    def test_the_view_owns_every_button_decision_the_panel_renders(self):
        locked = tears_of_guthix_view_pure(
            default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        )
        self.assertFalse(locked["enter_enabled"])
        self.assertFalse(locked["leave_enabled"])
        self.assertFalse(locked["craft_ornate_enabled"])
        self.assertTrue(locked["craft_ornate_visible"])

        ready = tears_of_guthix_view_pure(_player())
        self.assertTrue(ready["enter_enabled"])
        self.assertFalse(ready["leave_enabled"])

        inside = tears_of_guthix_view_pure(_entered())
        self.assertTrue(inside["enter_enabled"])
        self.assertTrue(inside["leave_enabled"])

        upgraded = _player(
            mining_level=ORNATE_BOWL_MINING_LEVEL,
            crafting_level=ORNATE_BOWL_CRAFTING_LEVEL,
        )
        upgraded["inventory"][ORNATE_BOWL_TOOL] = 1
        self.assertTrue(
            tears_of_guthix_view_pure(upgraded)["craft_ornate_enabled"]
        )
        made, ok, info = apply_tears_of_guthix_command_pure(
            upgraded, "craft_ornate_bowl"
        )
        self.assertTrue(ok, info)
        self.assertFalse(tears_of_guthix_view_pure(made)["craft_ornate_visible"])


class TearsOfGuthixPersistenceAndRuntimeTests(unittest.TestCase):
    def test_sanitizer_and_migration_restore_a_suspended_cavern_session(self):
        raw = {
            "ornate_bowl": True,
            "active": True,
            "session_ticks": 300,
            "remaining_ticks": 120,
            "tears": 44,
            "visits": 3,
            "available_entries": 99,
            "wall_clock_deadline": 12345,
        }
        clean = sanitize_tears_of_guthix_state_pure(raw)
        self.assertEqual(clean["remaining_ticks"], 120)
        self.assertEqual(clean["available_entries"], TEARS_OF_GUTHIX_ENTRY_CAP)
        self.assertNotIn("wall_clock_deadline", clean)

        migrated = migrate_loaded_data(
            {"tears_of_guthix": raw},
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["tears_of_guthix"]["remaining_ticks"], 120)
        self.assertEqual(migrated["tears_of_guthix"]["tears"], 44)
        # A suspended session does not silently re-claim the review surface.
        self.assertEqual(migrated["activity_session"], {"active_id": ""})

    def test_a_save_that_left_the_cavern_keeps_its_beats_across_a_reload(self):
        data = _entered()
        data, _result = next(_drain(data, lambda: 1.0))
        left, ok, info = apply_tears_of_guthix_command_pure(data, "leave")
        self.assertTrue(ok, info)
        reloaded = migrate_loaded_data(
            copy.deepcopy(left),
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(
            reloaded["tears_of_guthix"]["remaining_ticks"],
            left["tears_of_guthix"]["remaining_ticks"],
        )
        self.assertEqual(reloaded["activity_session"], {"active_id": ""})

    def test_a_fresh_save_starts_with_no_inert_or_wall_clock_fields(self):
        state = default_tears_of_guthix_state_pure()
        self.assertEqual(
            set(state),
            {
                "version",
                "ornate_bowl",
                "active",
                "remaining_ticks",
                "session_ticks",
                "tears",
                "visits",
                "allowance_week_index",
                "available_entries",
                "last_visit_exp",
                "last_visit_quest_points",
                "last_result",
            },
        )
        self.assertEqual(
            default_player_data(ORE_DATA, ITEM_DEFINITIONS)["tears_of_guthix"],
            state,
        )
        self.assertNotIn("timestamp", tears_of_guthix_view_pure(_player()))

    def test_the_runtime_routes_a_selected_cavern_review_and_persists(self):
        player = _entered()
        saved = []
        gains = []
        ctx = RuntimeActionContext(
            player_data=player,
            random_random=lambda: 1.0,
            show_error_message=lambda *_args: self.fail("unexpected runtime error"),
            deactivate_current_skill=lambda: None,
            award_skill_exp=lambda *_args: self.fail("the pure activity owns XP"),
            award_hidden_skill_exp=lambda *_args: None,
            level_up_check=lambda *_args: None,
            check_achievements=lambda *_args: None,
            save_player_data=lambda: saved.append(True),
            refresh_skill_availability=lambda: None,
            refresh_skill_availability_partial=lambda *_args: None,
            can_smith_any=lambda: True,
            show_exp=lambda amount: gains.append(float(amount)),
            show_activity_gain=lambda message: gains.append(str(message)),
            implemented_exp_keys_snapshot=lambda: {},
            show_quest_exp_delta=lambda *_args: None,
        )
        self.assertTrue(handle_utility_answer(ctx))
        self.assertEqual(saved, [True])
        self.assertEqual(
            player["tears_of_guthix"]["tears"],
            TEARS_OF_GUTHIX_TICKS_PER_REVIEW,
        )
        self.assertTrue(any("tears" in str(value) for value in gains))


class TearsOfGuthixRealRewardPathTests(unittest.TestCase):
    """Every reward reached by constructing the state a player would reach."""

    def test_a_first_visit_pays_the_least_experience_skill_through_real_beats(self):
        data = _player()
        before = reward_skill_pure(data)
        self.assertEqual(before["exp"], 0.0)
        data, ok, info = apply_tears_of_guthix_command_pure(data, "enter")
        self.assertTrue(ok, info)

        rng = random.Random(20121120).random
        for data, result in _drain(data, rng):
            pass

        self.assertTrue(result["completed"])
        self.assertGreater(result["tears"], 0)
        self.assertEqual(result["reward_skill_id"], before["id"])
        self.assertEqual(
            result["xp_per_tear"],
            xp_per_tear_pure(before["level"], False),
        )
        self.assertEqual(
            data[before["exp_key"]],
            float(result["tears"] * result["xp_per_tear"]),
        )
        self.assertEqual(data["tears_of_guthix"]["visits"], 1)
        self.assertFalse(tears_of_guthix_view_pure(data)["active"])
        self.assertEqual(data["activity_session"], {"active_id": ""})

    def test_the_ornate_bowl_actually_raises_the_cap_a_player_can_reach(self):
        """The 300-XP cap is only reachable at level 50+, so build that player."""
        data = _player(quest_points=TEARS_OF_GUTHIX_MAX_COLLECTION_TICKS)
        for skill in trainable_skill_definitions():
            data[skill.level_key] = 60
            data[skill.exp_key] = 300_000.0
        data["mining_level"] = ORNATE_BOWL_MINING_LEVEL
        data["crafting_level"] = ORNATE_BOWL_CRAFTING_LEVEL
        data["inventory"][ORNATE_BOWL_TOOL] = 1

        stone = tears_of_guthix_view_pure(data)
        self.assertEqual(stone["xp_per_tear"], TEARS_OF_GUTHIX_STONE_BOWL_XP_CAP)

        data, ok, info = apply_tears_of_guthix_command_pure(
            data, "craft_ornate_bowl"
        )
        self.assertTrue(ok, info)
        ornate = tears_of_guthix_view_pure(data)
        self.assertEqual(ornate["xp_per_tear"], TEARS_OF_GUTHIX_ORNATE_BOWL_XP_CAP)

        reward = reward_skill_pure(data)
        before_exp = float(data[reward["exp_key"]])
        data, ok, info = apply_tears_of_guthix_command_pure(data, "enter")
        self.assertTrue(ok, info)
        rng = random.Random(7).random
        for data, result in _drain(data, rng):
            pass
        self.assertEqual(result["xp_per_tear"], TEARS_OF_GUTHIX_ORNATE_BOWL_XP_CAP)
        self.assertEqual(
            data[reward["exp_key"]] - before_exp,
            float(result["tears"] * TEARS_OF_GUTHIX_ORNATE_BOWL_XP_CAP),
        )
        # The upgrade survives the visit that used it.
        self.assertTrue(data["tears_of_guthix"]["ornate_bowl"])

    def test_a_second_visit_needs_both_a_new_week_and_new_progress(self):
        data = _player()
        data, ok, info = apply_tears_of_guthix_command_pure(data, "enter")
        self.assertTrue(ok, info)
        rng = random.Random(3).random
        for data, _result in _drain(data, rng):
            pass

        blocked, ok, info = apply_tears_of_guthix_command_pure(data, "enter")
        self.assertFalse(ok)
        self.assertFalse(blocked["tears_of_guthix"]["active"])

        # A real simulated week of answered cards banks the visit...
        data = _advance_a_week(data)
        self.assertTrue(tears_of_guthix_view_pure(data)["week_ready"])
        # ...but Juna still wants a new story.
        view = tears_of_guthix_view_pure(data)
        self.assertFalse(view["progress_met"])
        still_blocked, ok, info = apply_tears_of_guthix_command_pure(data, "enter")
        self.assertFalse(ok)
        self.assertIn("more experience", info["reason"])
        self.assertFalse(still_blocked["tears_of_guthix"]["active"])

        # Either half of the sourced progress gate opens it. A quest point is
        # the cheaper half.
        data["quest_points"] = int(data["quest_points"]) + 1
        self.assertTrue(tears_of_guthix_view_pure(data)["progress_met"])
        second, ok, info = apply_tears_of_guthix_command_pure(data, "enter")
        self.assertTrue(ok, info)
        self.assertTrue(second["tears_of_guthix"]["active"])
        self.assertEqual(second["tears_of_guthix"]["available_entries"], 0)

    def test_a_hundred_thousand_experience_opens_the_gate_on_its_own(self):
        data = _player()
        data, ok, info = apply_tears_of_guthix_command_pure(data, "enter")
        self.assertTrue(ok, info)
        for data, _result in _drain(data, random.Random(11).random):
            pass
        data = _advance_a_week(data)

        baseline = total_experience_pure(data)
        data["woodcutting_exp"] = (
            float(data.get("woodcutting_exp", 0.0)) + TEARS_OF_GUTHIX_PROGRESS_EXP
        )
        self.assertEqual(
            total_experience_pure(data) - baseline,
            TEARS_OF_GUTHIX_PROGRESS_EXP,
        )
        view = tears_of_guthix_view_pure(data)
        self.assertTrue(view["progress_met"])
        self.assertEqual(view["quest_points_since_visit"], 0)
        opened, ok, info = apply_tears_of_guthix_command_pure(data, "enter")
        self.assertTrue(ok, info)
        self.assertTrue(opened["tears_of_guthix"]["active"])

    def test_the_previous_visit_payout_does_not_count_toward_new_progress(self):
        data = _player()
        data, ok, info = apply_tears_of_guthix_command_pure(data, "enter")
        self.assertTrue(ok, info)
        for data, result in _drain(data, lambda: 1.0):
            pass
        self.assertGreater(sum(result["xp_rewards"].values()), 0)
        data = _advance_a_week(data)

        data["woodcutting_exp"] = (
            float(data.get("woodcutting_exp", 0.0))
            + TEARS_OF_GUTHIX_PROGRESS_EXP
            - 1
        )
        view = tears_of_guthix_view_pure(data)
        self.assertFalse(view["progress_met"])
        self.assertEqual(
            view["experience_since_visit"], TEARS_OF_GUTHIX_PROGRESS_EXP - 1
        )

    def test_banked_visits_stop_at_the_carryover_cap(self):
        data = _player()
        data, ok, info = apply_tears_of_guthix_command_pure(data, "enter")
        self.assertTrue(ok, info)
        for data, _result in _drain(data, random.Random(5).random):
            pass
        for _ in range(TEARS_OF_GUTHIX_ENTRY_CAP + 3):
            for _card in range(TEARS_OF_GUTHIX_WEEK_REVIEWS):
                data.update(advance_shop_market_clock_pure(data))
        self.assertEqual(
            tears_of_guthix_view_pure(data)["available_entries"],
            TEARS_OF_GUTHIX_ENTRY_CAP,
        )


if __name__ == "__main__":
    unittest.main()
