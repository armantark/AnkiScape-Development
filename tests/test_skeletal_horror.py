from __future__ import annotations

import copy
import json
import os
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import (
    EQUIPMENT_DATA,
    EXTRA_ITEM_DATA,
    EXTRA_ITEM_IMAGES,
    ITEM_DEFINITIONS,
    ORE_DATA,
    UTILITY_ACTIVITY_DATA,
)
from ankiscape.core.storage_pure import (
    CURRENT_CONFIG_VERSION,
    default_player_data,
    migrate_loaded_data,
)
from ankiscape.data.skeletal_horror_data import (
    SKELETAL_HORROR_ACTIVITY_ID,
    SKELETAL_HORROR_ELITE_CLUE_ITEM,
    SKELETAL_HORROR_PHASES,
    SKELETAL_HORROR_TARGET_ID,
    skeletal_horror_enemy_pure,
)
from ankiscape.logic.skeletal_horror_logic import (
    apply_skeletal_horror_command_pure,
    apply_skeletal_horror_review_pure,
    default_skeletal_horror_state_pure,
    sanitize_skeletal_horror_state_pure,
    skeletal_horror_view_pure,
)
from ankiscape.logic_pure.logic_pure import apply_combat_burst_pure
from ankiscape.runtime.runtime_actions import RuntimeActionContext, handle_utility_answer


_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _player(**overrides):
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    for quest_id in ("rag_and_bone_man", "fur_n_seek"):
        data["quests"][quest_id] = {
            "started": True,
            "progress": 1,
            "completed": True,
        }
    data.update(
        {
            "slayer_level": 99,
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "magic_level": 99,
            "ranged_level": 99,
            "combat_lifepoints": 990,
        }
    )
    data.update(overrides)
    return data


def _unlocked(**overrides):
    data = _player(**overrides)
    for action_id in ("complete_rag_wish_list", "complete_fur_wish_list"):
        data, ok, info = apply_skeletal_horror_command_pure(data, action_id)
        if not ok:
            raise AssertionError(info)
    return data


def _entered(**overrides):
    data = _unlocked(**overrides)
    entered, ok, info = apply_skeletal_horror_command_pure(
        data,
        "enter",
        equipment_data=EQUIPMENT_DATA,
    )
    if not ok:
        raise AssertionError(info)
    return entered


def _combat_result(*, killed=False, died=False, fled=False, lifepoints=3000):
    def _apply(data, *_args, **_kwargs):
        updated = copy.deepcopy(data)
        updated["combat_encounter"] = (
            {}
            if killed or died or fled
            else {
                "target_id": SKELETAL_HORROR_TARGET_ID,
                "enemy_lifepoints": lifepoints,
            }
        )
        return updated, True, {
            "reason": "combat_burst",
            "killed": killed,
            "died": died,
            "fled": fled,
            "enemy_lifepoints": 0 if killed else lifepoints,
            "xp_rewards": {"constitution_exp": 12.0},
            "drops": {},
        }

    return _apply


def _win(data, *, repeat_roll=0.5):
    rolls = iter((repeat_roll,))
    with patch(
        "ankiscape.logic.skeletal_horror_logic.apply_combat_burst_pure",
        side_effect=_combat_result(killed=True),
    ):
        return apply_skeletal_horror_review_pure(
            data,
            lambda: next(rolls, repeat_roll),
            equipment_data=EQUIPMENT_DATA,
        )


class SkeletalHorrorDataAndGatesTests(unittest.TestCase):
    def test_period_rows_registry_item_and_dynamic_enemy_are_complete(self):
        self.assertEqual(
            [
                (
                    row["combat_level"],
                    row["remaining_lifepoints"],
                    row["max_hit"],
                    row["attack_styles"],
                )
                for row in SKELETAL_HORROR_PHASES
            ],
            [
                (320, 3500, 334, ("melee", "magic")),
                (260, 2750, 214, ("melee", "magic")),
                (180, 2000, 154, ("melee",)),
                (100, 1250, 74, ("melee",)),
            ],
        )
        enemy = skeletal_horror_enemy_pure(2, "magic")
        self.assertEqual(enemy["attack_style"], "melee")
        self.assertEqual(enemy["attack_speed"], 4)
        self.assertEqual(enemy["drops"], {"guaranteed": (), "tables": ()})
        self.assertTrue(enemy["encounter_only"])
        self.assertIn(SKELETAL_HORROR_ACTIVITY_ID, UTILITY_ACTIVITY_DATA)
        self.assertIn(SKELETAL_HORROR_ELITE_CLUE_ITEM, EXTRA_ITEM_DATA)
        self.assertTrue(
            os.path.isfile(EXTRA_ITEM_IMAGES[SKELETAL_HORROR_ELITE_CLUE_ITEM])
        )

    def test_both_post_quest_wish_lists_and_slayer_78_are_real_command_gates(self):
        data = _player(slayer_level=77)
        blocked, ok, info = apply_skeletal_horror_command_pure(
            data, "complete_fur_wish_list"
        )
        self.assertFalse(ok)
        self.assertIn("Slayer level 78", info["reason"])
        self.assertFalse(blocked["skeletal_horror"]["fur_wish_list_complete"])

        data["slayer_level"] = 78
        data, ok, info = apply_skeletal_horror_command_pure(
            data, "complete_fur_wish_list"
        )
        self.assertTrue(ok, info)
        blocked, can_enter, info = apply_skeletal_horror_command_pure(data, "enter")
        self.assertFalse(can_enter)
        self.assertIn("Rag and Bone Man's wish list", info["reason"])

        data, ok, info = apply_skeletal_horror_command_pure(
            data, "complete_rag_wish_list"
        )
        self.assertTrue(ok, info)
        entered, ok, info = apply_skeletal_horror_command_pure(
            data, "enter", equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok, info)
        self.assertEqual(
            entered["activity_session"],
            {"active_id": SKELETAL_HORROR_ACTIVITY_ID},
        )
        self.assertEqual(entered["skeletal_horror"]["lifepoints"], 3500)

    def test_commands_rebuild_owned_nested_state_without_mutating_input(self):
        original = _player()
        frozen = copy.deepcopy(original)
        updated, ok, info = apply_skeletal_horror_command_pure(
            original, "complete_rag_wish_list"
        )
        self.assertTrue(ok, info)
        self.assertEqual(original, frozen)
        self.assertIsNot(updated["skeletal_horror"], original["skeletal_horror"])


class SkeletalHorrorMechanicsTests(unittest.TestCase):
    def test_real_combat_reducer_receives_live_six_tick_safe_instance(self):
        data = _entered()
        with patch(
            "ankiscape.logic.skeletal_horror_logic.apply_combat_burst_pure",
            wraps=apply_combat_burst_pure,
        ) as reducer:
            updated, ok, result = apply_skeletal_horror_review_pure(
                data,
                lambda: 0.5,
                equipment_data=EQUIPMENT_DATA,
            )
        self.assertTrue(ok, result)
        self.assertTrue(updated["skeletal_horror"]["active"])
        self.assertEqual(reducer.call_args.kwargs["ticks"], 6)
        self.assertTrue(reducer.call_args.kwargs["live_cadence"])
        self.assertTrue(reducer.call_args.kwargs["safe_death"])
        self.assertFalse(reducer.call_args.kwargs["allow_bank_run"])

    def test_thresholds_remove_bury_and_switch_styles_in_one_review(self):
        data = _entered()
        with patch(
            "ankiscape.logic.skeletal_horror_logic.apply_combat_burst_pure",
            side_effect=_combat_result(lifepoints=1240),
        ):
            updated, ok, result = apply_skeletal_horror_review_pure(
                data, lambda: 0.0, equipment_data=EQUIPMENT_DATA
            )
        self.assertTrue(ok, result)
        self.assertEqual(
            result["removed_limbs"], ("right arm", "left arm", "tail")
        )
        self.assertEqual(updated["skeletal_horror"]["phase_index"], 3)
        self.assertEqual(
            skeletal_horror_view_pure(updated)["attack_styles"], ("melee",)
        )
        self.assertNotIn("Arm", updated["inventory"])
        self.assertNotIn("Tail", updated["inventory"])

    def test_first_and_repeat_victories_grant_exact_rewards_and_clue(self):
        data = _entered()
        first_slayer = float(data["slayer_exp"])
        first_prayer = float(data["prayer_exp"])
        won, ok, result = _win(data, repeat_roll=0.0)
        self.assertTrue(ok, result)
        self.assertTrue(result["first_completion"])
        self.assertEqual(won["slayer_exp"] - first_slayer, 10_000.0)
        self.assertEqual(won["prayer_exp"] - first_prayer, 7_000.0)
        self.assertEqual(won["skeletal_horror"]["kills"], 1)
        self.assertEqual(won["inventory"][SKELETAL_HORROR_ELITE_CLUE_ITEM], 0)

        won["shop_market_clock"]["answered_cards"] = 1680
        repeat, ok, info = apply_skeletal_horror_command_pure(
            won, "enter", equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok, info)
        repeat_slayer = float(repeat["slayer_exp"])
        repeat_prayer = float(repeat["prayer_exp"])
        repeated, ok, result = _win(repeat, repeat_roll=0.0)
        self.assertTrue(ok, result)
        self.assertFalse(result["first_completion"])
        self.assertTrue(result["clue_dropped"])
        self.assertEqual(repeated["slayer_exp"] - repeat_slayer, 1_250.0)
        self.assertEqual(repeated["prayer_exp"] - repeat_prayer, 1_000.0)
        self.assertEqual(
            repeated["inventory"][SKELETAL_HORROR_ELITE_CLUE_ITEM], 1
        )

    def test_weekly_carryover_banks_two_and_consumes_only_on_repeat_victory(self):
        won, ok, result = _win(_entered())
        self.assertTrue(ok, result)
        won["shop_market_clock"]["answered_cards"] = 1680 * 3
        view = skeletal_horror_view_pure(won)
        self.assertEqual(view["available_entries"], 2)

        entered, ok, info = apply_skeletal_horror_command_pure(
            won, "enter", equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok, info)
        self.assertEqual(entered["skeletal_horror"]["available_entries"], 2)
        left, ok, info = apply_skeletal_horror_command_pure(entered, "leave")
        self.assertTrue(ok, info)
        self.assertEqual(left["skeletal_horror"]["available_entries"], 2)

        entered, ok, info = apply_skeletal_horror_command_pure(
            left, "enter", equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok, info)
        repeated, ok, result = _win(entered)
        self.assertTrue(ok, result)
        self.assertEqual(repeated["skeletal_horror"]["available_entries"], 1)

    def test_safe_death_clears_instance_without_items_or_weekly_charge(self):
        data = _entered()
        data["inventory"]["Shark"] = 3
        data["equipment"]["weapon"] = "Bronze sword"
        with patch(
            "ankiscape.logic.skeletal_horror_logic.apply_combat_burst_pure",
            side_effect=_combat_result(died=True),
        ):
            defeated, ok, result = apply_skeletal_horror_review_pure(
                data, lambda: 0.5, equipment_data=EQUIPMENT_DATA
            )
        self.assertTrue(ok, result)
        self.assertTrue(result["died"])
        self.assertFalse(defeated["skeletal_horror"]["active"])
        self.assertEqual(defeated["inventory"]["Shark"], 3)
        self.assertEqual(defeated["equipment"]["weapon"], "Bronze sword")
        self.assertEqual(defeated["skeletal_horror"]["kills"], 0)
        self.assertEqual(defeated["skeletal_horror"]["available_entries"], 0)
        self.assertEqual(defeated["combat_grave"], {})


class SkeletalHorrorPersistenceRuntimeAndAssetTests(unittest.TestCase):
    def test_sanitizer_and_migration_restore_active_continuous_instance(self):
        raw = {
            "active": True,
            "lifepoints": 1900,
            "encounter": {"target_id": "wrong", "enemy_lifepoints": 1900},
            "rag_wish_list_complete": True,
            "fur_wish_list_complete": True,
            "kills": 2,
            "available_entries": 99,
            "timer": 12,
        }
        clean = sanitize_skeletal_horror_state_pure(raw)
        self.assertEqual(clean["phase_index"], 2)
        self.assertEqual(clean["available_entries"], 2)
        self.assertNotIn("timer", clean)
        migrated = migrate_loaded_data(
            {"skeletal_horror": raw},
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(
            migrated["activity_session"],
            {"active_id": SKELETAL_HORROR_ACTIVITY_ID},
        )
        self.assertEqual(migrated["skeletal_horror"]["lifepoints"], 1900)

    def test_runtime_routes_selected_active_reviews_and_persists(self):
        player = _entered()
        saved = []
        gains = []
        ctx = RuntimeActionContext(
            player_data=player,
            random_random=lambda: 0.5,
            show_error_message=lambda *_args: self.fail("unexpected runtime error"),
            deactivate_current_skill=lambda: None,
            award_skill_exp=lambda *_args: self.fail("pure activity owns XP"),
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
        with patch(
            "ankiscape.logic.skeletal_horror_logic.apply_combat_burst_pure",
            side_effect=_combat_result(lifepoints=2740),
        ):
            self.assertTrue(handle_utility_answer(ctx))
        self.assertEqual(saved, [True])
        self.assertEqual(player["skeletal_horror"]["phase_index"], 1)
        self.assertTrue(any("right arm" in str(value) for value in gains))

    def test_period_assets_are_local_registered_and_cutoff_pinned(self):
        paths = (
            "combatenemies/skeletal_horror.png",
            "combatitems/clue_scroll_elite.png",
        )
        with open(
            os.path.join(_ROOT, "assets_provenance.json"),
            encoding="utf-8",
        ) as handle:
            provenance = json.load(handle)
        for relative in paths:
            self.assertTrue(os.path.isfile(os.path.join(_ROOT, relative)))
            self.assertIn(relative, provenance)
            self.assertLessEqual(
                provenance[relative]["timestamp"],
                "2012-11-20T00:00:00Z",
            )
        self.assertTrue(
            os.path.isfile(
                UTILITY_ACTIVITY_DATA[SKELETAL_HORROR_ACTIVITY_ID]["icon_path"]
            )
        )

    def test_default_state_contains_no_inert_or_wall_clock_fields(self):
        state = default_skeletal_horror_state_pure()
        self.assertEqual(
            set(state),
            {
                "version",
                "rag_wish_list_complete",
                "fur_wish_list_complete",
                "active",
                "lifepoints",
                "phase_index",
                "encounter",
                "previous_combat_target",
                "kills",
                "allowance_week_index",
                "available_entries",
                "last_result",
            },
        )
        self.assertNotIn("timestamp", skeletal_horror_view_pure(_player()))


if __name__ == "__main__":
    unittest.main()
