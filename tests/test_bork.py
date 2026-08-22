from __future__ import annotations

import copy
import os
import random
import sys
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import (
    EQUIPMENT_DATA,
    EXTRA_ITEM_DATA,
    ITEM_DEFINITIONS,
    ORE_DATA,
    UTILITY_ACTIVITY_DATA,
)
from ankiscape.core.storage_pure import (
    default_player_data,
    migrate_loaded_data,
)
from ankiscape.data.bork_data import (
    BORK_ACTIVITY_ID,
    BORK_EFFIGY_ITEM,
    BORK_MAGE_TICKS_PER_ATTACK,
    BORK_MAX_LIFEPOINTS,
    BORK_ORK_SUMMON_MAXIMUM,
    BORK_ORK_SUMMON_MINIMUM,
    BORK_ORK_SUMMON_THRESHOLD_LIFEPOINTS,
    BORK_QUEST_ID,
    BORK_RARE_DROPS,
    BORK_REVIEW_TICKS,
    BORK_TARGET_ID,
    BORK_WORLD_DAY_REVIEWS,
    bork_enemy_pure,
    bork_guaranteed_drops_pure,
    ork_legion_enemy_pure,
)
from ankiscape.logic.achievement_diary_logic import diary_tier_by_id_pure
from ankiscape.logic.bork_logic import (
    apply_bork_command_pure,
    apply_bork_review_pure,
    bork_view_pure,
    default_bork_state_pure,
    sanitize_bork_state_pure,
)
from ankiscape.logic.cadence_coverage import cadence_coverage_rows_pure
from ankiscape.runtime.runtime_actions import RuntimeActionContext, handle_utility_answer
from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package


def _player(**overrides):
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data["quests"][BORK_QUEST_ID] = {
        "started": True,
        "progress": 6,
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


def _with_varrock_elite(data):
    resolved = diary_tier_by_id_pure("varrock_elite")
    assert resolved is not None
    _family, tier = resolved
    diaries = copy.deepcopy(data["achievement_diaries"])
    diaries["completed_tasks"] = sorted(
        set(diaries["completed_tasks"]) | {task.id for task in tier.tasks}
    )
    data["achievement_diaries"] = diaries
    return data


def _entered(**overrides):
    data = _player(**overrides)
    entered, ok, info = apply_bork_command_pure(
        data, "enter", equipment_data=EQUIPMENT_DATA
    )
    if not ok:
        raise AssertionError(info)
    return entered


def _loaded_player(**overrides):
    """A 99s player equipped and provisioned well enough to win the fight."""
    data = _player(**overrides)
    data["equipment"] = {
        **dict(data.get("equipment", {})),
        "weapon": "Dragon scimitar",
    }
    data["combat_supply_loadout"] = {"food": {"Shark": 28}}
    data["combat_auto_eat_food"] = ["Shark"]
    entered, ok, info = apply_bork_command_pure(
        data, "enter", equipment_data=EQUIPMENT_DATA
    )
    if not ok:
        raise AssertionError(info)
    return entered


def _burst(*, killed=False, died=False, lifepoints=BORK_MAX_LIFEPOINTS):
    def _apply(data, *_args, **_kwargs):
        updated = copy.deepcopy(data)
        updated["combat_encounter"] = (
            {}
            if killed or died
            else {
                "target_id": BORK_TARGET_ID,
                "enemy_lifepoints": lifepoints,
            }
        )
        return updated, True, {
            "killed": killed,
            "died": died,
            "fled": False,
            "enemy_lifepoints": 0 if killed else lifepoints,
            "xp_rewards": {"constitution_exp": 12.0},
        }

    return _apply


def _review(data, rolls, *, burst=None):
    """Drive one Bork review with a scripted rng and a scripted burst."""
    stream = iter(rolls)
    with patch(
        "ankiscape.logic.bork_logic.apply_combat_burst_pure",
        side_effect=burst or _burst(),
    ):
        return apply_bork_review_pure(
            data,
            lambda: next(stream, 0.999),
            equipment_data=EQUIPMENT_DATA,
        )


class BorkPeriodDataTests(unittest.TestCase):
    def test_enemy_rows_match_the_pinned_combat_definitions(self):
        bork = bork_enemy_pure()
        self.assertEqual(bork["level"], 267)
        self.assertEqual(bork["stats"]["hitpoints"], 3000)
        self.assertEqual(bork["max_hit"], 254)
        self.assertEqual(bork["attack_speed"], 6)
        self.assertEqual(bork["attack_style"], "melee")
        self.assertEqual(bork["attack_bonus"], "crush_att")
        self.assertTrue(bork["encounter_only"])
        self.assertEqual(set(bork["bonuses"].values()), {0})
        # Both npcs print `immune to poison = Yes`.
        self.assertTrue(bork["poison_immune"])

        ork = ork_legion_enemy_pure()
        self.assertEqual(ork["level"], 70)
        self.assertEqual(ork["stats"]["hitpoints"], 500)
        self.assertEqual(ork["max_hit"], 82)
        # The collapsed stand-near route uses Darkan's exact adjacent branch.
        self.assertEqual(ork["attack_style"], "melee")
        self.assertTrue(ork["poison_immune"])
        self.assertEqual(ork["slayer_xp"], 50.0)

    def test_both_stat_blocks_are_exactly_the_registered_conversion(self):
        """72% of combat level, capped at 99, in all four stats and no others.

        The register describes one conversion; a block that quietly ships a
        different magic value, or a ranged stat the conversion never produces,
        makes the register untrue of the code it is cited for.
        """
        for enemy, level in ((bork_enemy_pure(), 267), (ork_legion_enemy_pure(), 70)):
            converted = max(1, min(99, round(level * 0.72)))
            stats = enemy["stats"]
            self.assertEqual(
                {key: value for key, value in stats.items() if key != "hitpoints"},
                {
                    "attack": converted,
                    "strength": converted,
                    "defence": converted,
                    "magic": converted,
                },
                enemy["display_name"],
            )

    def test_guaranteed_drop_columns_reproduce_the_pinned_table(self):
        default = bork_guaranteed_drops_pure(False, False, 0)
        self.assertEqual(
            (
                default["Blue charm"],
                default["Crimson charm"],
                default["Green charm"],
            ),
            (5, 7, 2),
        )
        # Zero-quantity rows are absent, not present at zero.
        self.assertNotIn("Uncut diamond", default)
        self.assertEqual(default["Uncut sapphire"], 1)

        wealth = bork_guaranteed_drops_pure(False, True, 0)
        self.assertEqual(wealth["Crimson charm"], 10)
        self.assertEqual(wealth["Uncut diamond"], 1)
        self.assertNotIn("Uncut sapphire", wealth)

        elite = bork_guaranteed_drops_pure(True, False, 0)
        self.assertEqual(
            (elite["Blue charm"], elite["Crimson charm"], elite["Green charm"]),
            (10, 14, 4),
        )

        both = bork_guaranteed_drops_pure(True, True, 4321)
        self.assertEqual(
            (both["Blue charm"], both["Crimson charm"], both["Green charm"]),
            (10, 17, 5),
        )
        self.assertEqual(both["Coins"], 4321)
        self.assertEqual(both["Big bones"], 1)

    def test_activity_item_and_cadence_registrations_exist(self):
        self.assertIn(BORK_ACTIVITY_ID, UTILITY_ACTIVITY_DATA)
        self.assertEqual(
            UTILITY_ACTIVITY_DATA[BORK_ACTIVITY_ID]["surface"], "activities"
        )
        self.assertIn(BORK_EFFIGY_ITEM, EXTRA_ITEM_DATA)
        self.assertTrue(
            os.path.isfile(UTILITY_ACTIVITY_DATA[BORK_ACTIVITY_ID]["icon_path"])
        )
        row = next(
            row
            for row in cadence_coverage_rows_pure()
            if row["action_id"] == BORK_ACTIVITY_ID
        )
        self.assertEqual(row["handler_key"], "utility")
        self.assertEqual(row["source_status"], "sourced")
        self.assertEqual(row["undo_boundary"], "one answered-card transaction")


class BorkGateTests(unittest.TestCase):
    def test_the_miniquest_is_a_real_entry_gate(self):
        data = _player()
        data["quests"][BORK_QUEST_ID]["completed"] = False
        view = bork_view_pure(data)
        self.assertFalse(view["requirements_met"])
        self.assertEqual(
            view["missing_requirements"], ("Complete The Hunt for Surok",)
        )
        blocked, ok, info = apply_bork_command_pure(
            data, "enter", equipment_data=EQUIPMENT_DATA
        )
        self.assertFalse(ok)
        self.assertIn("Hunt for Surok", info["reason"])
        self.assertFalse(blocked["bork"]["active"])

    def test_a_kill_closes_the_world_day_and_the_next_day_reopens_it(self):
        data = _entered()
        data, ok, result = _review(data, [0.5], burst=_burst(killed=True))
        self.assertTrue(ok, result)
        self.assertFalse(data["bork"]["active"])
        self.assertEqual(data["bork"]["kills"], 1)
        self.assertEqual(data["bork"]["last_completed_world_day"], 0)

        blocked, ok, info = apply_bork_command_pure(
            data, "enter", equipment_data=EQUIPMENT_DATA
        )
        self.assertFalse(ok)
        self.assertIn("already been defeated this world day", info["reason"])
        view = bork_view_pure(blocked)
        self.assertFalse(view["daily_ready"])
        self.assertEqual(view["reviews_to_reset"], BORK_WORLD_DAY_REVIEWS)

        data["shop_market_clock"] = {
            **(data.get("shop_market_clock") or {}),
            "answered_cards": BORK_WORLD_DAY_REVIEWS,
        }
        self.assertTrue(bork_view_pure(data)["daily_ready"])
        reopened, ok, info = apply_bork_command_pure(
            data, "enter", equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok, info)
        self.assertTrue(reopened["bork"]["active"])
        self.assertEqual(reopened["bork"]["lifepoints"], BORK_MAX_LIFEPOINTS)

    def test_leaving_and_dying_both_preserve_the_daily_kill(self):
        data = _entered()
        left, ok, info = apply_bork_command_pure(data, "leave")
        self.assertTrue(ok, info)
        self.assertFalse(left["bork"]["active"])
        self.assertEqual(left["bork"]["last_completed_world_day"], -1)
        self.assertTrue(bork_view_pure(left)["daily_ready"])

        data = _entered()
        died, ok, result = _review(data, [0.5], burst=_burst(died=True))
        self.assertTrue(ok, result)
        self.assertFalse(died["bork"]["active"])
        self.assertEqual(died["bork"]["last_completed_world_day"], -1)
        self.assertIn("not consumed", result["status"])

    def test_only_one_persistent_activity_may_hold_the_reviewer(self):
        data = _player()
        data["activity_session"] = {"active_id": "skeletal_horror"}
        blocked, ok, info = apply_bork_command_pure(
            data, "enter", equipment_data=EQUIPMENT_DATA
        )
        self.assertFalse(ok)
        self.assertIn("Another persistent activity", info["reason"])


class BorkEncounterTests(unittest.TestCase):
    def test_the_legion_arrives_once_at_the_sourced_threshold(self):
        data = _entered()
        above = BORK_ORK_SUMMON_THRESHOLD_LIFEPOINTS + 1
        data, ok, result = _review(data, [0.5], burst=_burst(lifepoints=above))
        self.assertTrue(ok, result)
        self.assertEqual(result["orks_summoned"], 0)
        self.assertFalse(data["bork"]["orks_summoned"])

        # rng 0.0 is the low end of Utils.random(3, 10).
        data, ok, result = _review(
            data,
            [0.0],
            burst=_burst(lifepoints=BORK_ORK_SUMMON_THRESHOLD_LIFEPOINTS),
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["orks_summoned"], BORK_ORK_SUMMON_MINIMUM)
        self.assertEqual(data["bork"]["ork_count"], BORK_ORK_SUMMON_MINIMUM)

        before = data["bork"]["ork_count"]
        data, ok, result = _review(
            data, [0.999], burst=_burst(lifepoints=1500)
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["orks_summoned"], 0)
        self.assertEqual(data["bork"]["ork_count"], before)

    def test_the_legion_size_stays_inside_the_sourced_range(self):
        for roll in (0.0, 0.34, 0.67, 0.999):
            data = _entered()
            _data, ok, result = _review(
                data,
                [roll],
                burst=_burst(lifepoints=BORK_ORK_SUMMON_THRESHOLD_LIFEPOINTS),
            )
            self.assertTrue(ok, result)
            self.assertGreaterEqual(result["orks_summoned"], BORK_ORK_SUMMON_MINIMUM)
            self.assertLessEqual(result["orks_summoned"], BORK_ORK_SUMMON_MAXIMUM)

    def test_the_caster_fires_on_its_own_tick_budget(self):
        data = _entered()
        reviews_to_bolt = -(-BORK_MAGE_TICKS_PER_ATTACK // 6)
        for _ in range(reviews_to_bolt - 1):
            data, ok, result = _review(data, [0.999])
            self.assertTrue(ok, result)
            self.assertEqual(result["pressure_damage"], 0)
        data, ok, result = _review(data, [0.0])
        self.assertTrue(ok, result)
        self.assertGreater(result["pressure_damage"], 0)
        self.assertLessEqual(result["pressure_damage"], 250)

    def test_protect_from_magic_zeroes_the_caster(self):
        data = _entered()
        data["prayer_level"] = 99
        data["combat_prayer_points"] = 990
        data["combat_prayer_uptime"] = "100"
        data["combat_selected_prayers"] = ["protect_from_magic"]
        reviews_to_bolt = -(-BORK_MAGE_TICKS_PER_ATTACK // 6)
        for _ in range(reviews_to_bolt):
            data, ok, result = _review(data, [0.0])
            self.assertTrue(ok, result)
            self.assertEqual(result["pressure_damage"], 0)

    def test_the_legion_presses_every_review_until_bork_falls(self):
        data = _entered()
        data, ok, result = _review(
            data,
            [0.999],
            burst=_burst(lifepoints=BORK_ORK_SUMMON_THRESHOLD_LIFEPOINTS),
        )
        self.assertTrue(ok, result)
        self.assertEqual(data["bork"]["ork_count"], BORK_ORK_SUMMON_MAXIMUM)
        # Every legion attack lands when the accuracy roll is zero.
        data, ok, result = _review(data, [0.0] * 40, burst=_burst(lifepoints=1200))
        self.assertTrue(ok, result)
        self.assertGreater(result["pressure_damage"], 0)


class BorkRewardTests(unittest.TestCase):
    def test_a_repeat_kill_pays_the_sourced_default_bundle(self):
        data = _entered()
        before_slayer = float(data.get("slayer_exp", 0.0))
        # coin roll then three rare rolls, all above their thresholds.
        data, ok, result = _review(
            data, [0.0, 0.999, 0.999, 0.999], burst=_burst(killed=True)
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["slayer_xp"], 250.0)
        self.assertEqual(float(data["slayer_exp"]) - before_slayer, 250.0)
        self.assertEqual(result["coins"], 2000)
        self.assertEqual(result["rare_drops"], {})
        inventory = data["inventory"]
        self.assertEqual(inventory["Blue charm"], 5)
        self.assertEqual(inventory["Crimson charm"], 7)
        self.assertEqual(inventory["Green charm"], 2)
        self.assertEqual(inventory["Big bones"], 1)
        self.assertEqual(inventory["Coins"], 2000)

    def test_known_varrock_elite_rows_do_not_bypass_the_twelve_task_gate(self):
        data = _with_varrock_elite(_player())
        data, ok, info = apply_bork_command_pure(
            data, "enter", equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok, info)
        self.assertFalse(bork_view_pure(data)["varrock_elite"])
        data, ok, result = _review(
            data, [0.0, 0.999, 0.999, 0.999], burst=_burst(killed=True)
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["slayer_xp"], 250.0)
        self.assertEqual(result["coins"], 2000)
        self.assertEqual(data["inventory"]["Blue charm"], 5)
        self.assertEqual(data["inventory"]["Crimson charm"], 7)
        self.assertEqual(data["inventory"]["Green charm"], 2)

    def test_a_worn_ring_of_wealth_shifts_the_gem_and_charm_column(self):
        data = _entered()
        data["equipment"] = {**(data.get("equipment") or {}), "ring": "Ring of wealth"}
        self.assertTrue(bork_view_pure(data)["ring_of_wealth"])
        data, ok, result = _review(
            data, [0.0, 0.999, 0.999, 0.999], burst=_burst(killed=True)
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["coins"], 2000)
        self.assertEqual(data["inventory"]["Crimson charm"], 10)
        self.assertEqual(data["inventory"]["Uncut diamond"], 1)
        self.assertEqual(data["inventory"].get("Uncut sapphire", 0), 0)

    def test_the_three_rare_rolls_are_independent_and_sourced(self):
        self.assertEqual(
            [name for name, _ in BORK_RARE_DROPS],
            [BORK_EFFIGY_ITEM, "Clue scroll (elite)", "Clue scroll (hard)"],
        )
        data = _entered()
        data, ok, result = _review(
            data, [0.5, 0.0, 0.0, 0.0], burst=_burst(killed=True)
        )
        self.assertTrue(ok, result)
        self.assertEqual(
            result["rare_drops"],
            {BORK_EFFIGY_ITEM: 1, "Clue scroll (elite)": 1},
        )
        self.assertEqual(data["inventory"][BORK_EFFIGY_ITEM], 1)
        self.assertEqual(data["inventory"]["Clue scroll (elite)"], 1)
        self.assertEqual(data["inventory"].get("Clue scroll (hard)", 0), 0)

    def test_a_held_clue_refuses_and_reports_borks_clue_rolls(self):
        data = _entered()
        data["inventory"]["Clue scroll (easy)"] = 1

        data, ok, result = _review(
            data, [0.5, 0.0, 0.0, 0.0], burst=_burst(killed=True)
        )

        self.assertTrue(ok, result)
        self.assertEqual(result["rare_drops"], {BORK_EFFIGY_ITEM: 1})
        self.assertEqual(data["inventory"]["Clue scroll (easy)"], 1)
        self.assertEqual(data["inventory"].get("Clue scroll (elite)", 0), 0)
        self.assertEqual(data["inventory"].get("Clue scroll (hard)", 0), 0)
        self.assertIn("already have a clue scroll", result["status"])


class BorkPersistenceTests(unittest.TestCase):
    def test_the_state_round_trips_and_an_inactive_row_carries_no_encounter(self):
        data = _entered()
        data["bork"]["lifepoints"] = 1800
        data["bork"]["ork_count"] = 4
        data["bork"]["orks_summoned"] = True
        data["bork"]["mage_ticks"] = 12
        restored = migrate_loaded_data(
            copy.deepcopy(data), ORE_DATA, ITEM_DEFINITIONS
        )
        self.assertEqual(restored["bork"]["lifepoints"], 1800)
        self.assertEqual(restored["bork"]["ork_count"], 4)
        self.assertEqual(restored["bork"]["mage_ticks"], 12)
        self.assertEqual(restored["activity_session"]["active_id"], BORK_ACTIVITY_ID)

        stale = sanitize_bork_state_pure(
            {
                "active": False,
                "lifepoints": 2500,
                "ork_count": 9,
                "orks_summoned": True,
                "mage_ticks": 30,
                "encounter": {"target_id": BORK_TARGET_ID},
                "kills": 3,
                "last_completed_world_day": 7,
            }
        )
        self.assertEqual(stale["lifepoints"], 0)
        self.assertEqual(stale["ork_count"], 0)
        self.assertFalse(stale["orks_summoned"])
        self.assertEqual(stale["mage_ticks"], 0)
        self.assertEqual(stale["encounter"], {})
        self.assertEqual(stale["kills"], 3)
        self.assertEqual(stale["last_completed_world_day"], 7)

    def test_a_save_without_bork_gets_the_default_row(self):
        data = _player()
        data.pop("bork")
        restored = migrate_loaded_data(data, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(restored["bork"], default_bork_state_pure())

    def test_a_higher_priority_session_deactivates_bork(self):
        data = _entered()
        data["skeletal_horror"] = {
            **data["skeletal_horror"],
            "active": True,
            "lifepoints": 3500,
        }
        restored = migrate_loaded_data(data, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(restored["activity_session"]["active_id"], "skeletal_horror")
        self.assertFalse(restored["bork"]["active"])
        self.assertEqual(restored["bork"]["encounter"], {})


class BorkReviewSeamTests(unittest.TestCase):
    def test_the_reviewer_routes_an_answered_card_into_the_real_encounter(self):
        data = _entered()
        data["current_utility"] = BORK_ACTIVITY_ID
        gains: list[object] = []
        saved: list[bool] = []
        ctx = RuntimeActionContext(
            player_data=data,
            random_random=lambda: 0.5,
            show_error_message=lambda *_args: self.fail("unexpected runtime error"),
            deactivate_current_skill=lambda: None,
            award_skill_exp=lambda *_args: self.fail("the pure encounter owns XP"),
            award_hidden_skill_exp=lambda *_args: None,
            level_up_check=lambda *_args: None,
            check_achievements=lambda *_args: None,
            save_player_data=lambda: saved.append(True),
            refresh_skill_availability=lambda: None,
            show_exp=lambda amount: gains.append(float(amount)),
            show_activity_gain=lambda message: gains.append(str(message)),
            implemented_exp_keys_snapshot=lambda: {},
            show_quest_exp_delta=lambda *_args: None,
        )
        self.assertTrue(handle_utility_answer(ctx))
        self.assertEqual(saved, [True])
        self.assertTrue(gains)
        self.assertTrue(data["bork"]["active"])
        self.assertLessEqual(data["bork"]["lifepoints"], BORK_MAX_LIFEPOINTS)

    def test_the_real_kernel_pays_the_period_kill_and_closes_the_world_day(self):
        """One whole fight through the real Combat kernel, no burst stub.

        The stubbed tests above pin the reducer's own arithmetic; this one is
        the only check that the fight itself resolves — that a fully equipped
        player kills Bork in a plausible number of reviews and is paid exactly
        the sourced repeat reward.
        """
        data = _loaded_player()
        rng = random.Random(3).random
        for review in range(1, 60):
            data, ok, result = apply_bork_review_pure(
                data, rng, equipment_data=EQUIPMENT_DATA
            )
            self.assertTrue(ok, result)
            if result.get("outcome"):
                break
        else:
            self.fail("the real kernel never resolved the fight")

        self.assertIn("Bork defeated", result["outcome"])
        self.assertLess(review, 40)
        self.assertEqual(result["slayer_xp"], 250.0)
        self.assertEqual(data["slayer_exp"], 250.0)
        self.assertEqual(
            (
                result["drops"]["Blue charm"],
                result["drops"]["Crimson charm"],
                result["drops"]["Green charm"],
            ),
            (5, 7, 2),
        )
        self.assertGreaterEqual(result["coins"], 2000)
        self.assertLessEqual(result["coins"], 10000)
        self.assertFalse(data["bork"]["active"])
        self.assertEqual(data["bork"]["kills"], 1)
        self.assertEqual(data["bork"]["last_completed_world_day"], 0)

        _refused, ok, info = apply_bork_command_pure(
            data, "enter", equipment_data=EQUIPMENT_DATA
        )
        self.assertFalse(ok)
        self.assertIn("already been defeated this world day", info["reason"])

        data["shop_market_clock"] = {
            **dict(data.get("shop_market_clock", {})),
            "answered_cards": BORK_WORLD_DAY_REVIEWS,
        }
        reopened, ok, info = apply_bork_command_pure(
            data, "enter", equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok, info)
        self.assertTrue(reopened["bork"]["active"])

    def test_the_real_kernel_reports_an_ork_death_as_a_death(self):
        """The orks kill the player after the burst itself survived.

        `combat_result["died"]` is False on that path, so the reducer has to
        raise the flag itself or the runtime logs the death as a clean success.
        """
        data = _loaded_player()
        rng = random.Random(41).random
        for _review in range(1, 60):
            data, ok, result = apply_bork_review_pure(
                data, rng, equipment_data=EQUIPMENT_DATA
            )
            self.assertTrue(ok, result)
            if result.get("outcome"):
                break
        else:
            self.fail("the real kernel never resolved the fight")

        self.assertIn("legion", result["outcome"])
        self.assertTrue(result["died"])
        self.assertFalse(data["bork"]["active"])
        # A death does not spend the daily kill.
        self.assertEqual(data["bork"]["last_completed_world_day"], -1)

    def test_a_review_without_an_encounter_is_refused_not_silently_absorbed(self):
        data = _player()
        refused, ok, info = apply_bork_review_pure(
            data, lambda: 0.5, equipment_data=EQUIPMENT_DATA
        )
        self.assertFalse(ok)
        self.assertIn("Enter Bork's chamber", info["reason"])
        self.assertFalse(refused["bork"]["active"])


class BorkCadenceTests(unittest.TestCase):
    """The contract's "never foreground-multiplied" claim, driven end to end."""

    def setUp(self):
        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_one_answered_card_is_one_six_tick_bork_interval(self):
        addon = _load_addon_as_package("ankiscape_bork_hook")
        addon.player_data = _entered()
        addon.player_data["current_utility"] = BORK_ACTIVITY_ID
        addon.current_skill = "Utility / Activities"
        addon.exp_awarded = False
        addon._review_action_multiplier = lambda: 3
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _message: None
        addon._show_exp = lambda _amount: None
        addon._advance_world_events_after_review = lambda: None
        addon._save_player_data_if_anki_ready = lambda: None
        addon._remember_review_award_snapshot = lambda _before: None

        addon.on_good_answer()

        # The caster's clock is the durable witness: it gains the review's six
        # ticks once. A multiplied answer would have spent three slices on it.
        self.assertTrue(addon.player_data["bork"]["active"])
        self.assertEqual(
            addon.player_data["bork"]["mage_ticks"], BORK_REVIEW_TICKS
        )


if __name__ == "__main__":
    unittest.main()
