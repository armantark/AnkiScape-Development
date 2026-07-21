from __future__ import annotations

import copy
import unittest
from pathlib import Path
from unittest.mock import patch

from constants import ITEM_DEFINITIONS, ORE_DATA, UTILITY_ACTIVITY_DATA
from runtime_actions import RuntimeActionContext, handle_utility_answer
from stealing_creation_data import (
    STEALING_CREATION_REWARD_FORM_BY_ID,
    STEALING_CREATION_SESSION_EQUIPMENT,
)
from stealing_creation_logic import (
    apply_stealing_creation_command_pure,
    apply_stealing_creation_review_pure,
    apply_stealing_creation_xp_bonus_pure,
    purchase_stealing_creation_tool_pure,
    sanitize_stealing_creation_state_pure,
    stealing_creation_points_for_score_pure,
    stealing_creation_tool_can_apply_pure,
    stealing_creation_view_pure,
)
from storage_pure import CURRENT_CONFIG_VERSION, default_player_data, migrate_loaded_data


def _player(**overrides):
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data.update(
        {
            "attack_level": 80,
            "strength_level": 80,
            "defense_level": 80,
            "constitution_level": 80,
            "mining_level": 80,
            "fishing_level": 80,
            "hunter_level": 80,
            "woodcutting_level": 80,
            "construction_level": 80,
            "smithing_level": 80,
            "combat_lifepoints": 800,
            "inventory": {},
        }
    )
    data.update(overrides)
    return data


def _entered(**overrides):
    data, ok, info = apply_stealing_creation_command_pure(
        _player(**overrides), "enter", rng=lambda: 0.5
    )
    assert ok, info
    return data


def _combat_result(*, killed=False, died=False, enemy_lifepoints=100):
    def _apply(data, _enemies, _equipment, **_kwargs):
        updated = copy.deepcopy(data)
        updated["combat_encounter"] = (
            {}
            if killed or died
            else {
                "target_id": "stealing_creation_raider",
                "enemy_lifepoints": enemy_lifepoints,
            }
        )
        if died:
            updated["combat_lifepoints"] = updated["constitution_level"] * 10
        return updated, True, {
            "killed": killed,
            "died": died,
            "xp_rewards": {"attack_exp": 999.0},
        }

    return _apply


class StealingCreationDataTests(unittest.TestCase):
    def test_activity_and_reward_items_are_registered(self):
        activity = UTILITY_ACTIVITY_DATA["stealing_creation"]
        self.assertEqual(activity["group"], "minigames")
        self.assertEqual(activity["outputs"], ("Proto-tool", "Volatile clay tool"))
        if activity.get("icon_path"):
            self.assertTrue(Path(activity["icon_path"]).is_file())
        definitions = {definition.storage_key: definition for definition in ITEM_DEFINITIONS}
        self.assertEqual(definitions["Proto-tool"].source_item_id, 14106)
        self.assertFalse(definitions["Proto-tool"].stackable)
        self.assertEqual(definitions["Volatile clay tool"].source_item_id, 14098)
        self.assertEqual(len(STEALING_CREATION_SESSION_EQUIPMENT), 10)

    def test_period_score_conversion_boundaries_are_exact(self):
        expected = {
            0: 0,
            19_999: 19,
            20_000: 20,
            21_999: 20,
            22_000: 21,
            25_999: 21,
            26_000: 22,
            33_999: 22,
            34_000: 23,
            49_999: 23,
            50_000: 24,
            81_999: 24,
            82_000: 25,
            145_999: 25,
            146_000: 26,
        }
        for score, points in expected.items():
            with self.subTest(score=score):
                self.assertEqual(stealing_creation_points_for_score_pure(score), points)


class StealingCreationSessionTests(unittest.TestCase):
    def test_entry_reserves_session_and_requires_follower_confirmation(self):
        competing = _player(activity_session={"active_id": "fight_caves"})
        _data, ok, info = apply_stealing_creation_command_pure(competing, "enter")
        self.assertFalse(ok)
        self.assertIn("persistent activity", info["reason"])

        follower = _player()
        follower["summoning_state"]["active_follower"] = {
            "kind": "familiar",
            "entity_id": "spiritwolf",
            "remaining_reviews": 4,
            "max_reviews": 4,
            "storage": {},
        }
        unchanged, ok, info = apply_stealing_creation_command_pure(follower, "enter")
        self.assertFalse(ok)
        self.assertTrue(info["requires_confirmation"])
        self.assertTrue(unchanged["summoning_state"]["active_follower"])
        entered, ok, _info = apply_stealing_creation_command_pure(
            follower,
            "enter",
            {"confirm_dismiss_follower": True},
        )
        self.assertTrue(ok)
        self.assertEqual(entered["summoning_state"]["active_follower"], {})
        self.assertEqual(entered["activity_session"], {"active_id": "stealing_creation"})
        self.assertEqual(entered["current_utility"], "stealing_creation")

        fighting = _player(
            combat_encounter={"target_id": "chicken", "enemy_lifepoints": 10}
        )
        _blocked, ok, info = apply_stealing_creation_command_pure(fighting, "enter")
        self.assertFalse(ok)
        self.assertIn("Combat encounter", info["reason"])

    def test_casual_policy_builds_each_temporary_consumer_and_never_leaks_items(self):
        data = _entered()
        data["stealing_creation"]["active_session"]["next_raid_review"] = 20
        for _ in range(11):
            data, ok, _result = apply_stealing_creation_review_pure(data, lambda: 0.0)
            self.assertTrue(ok)
        session = data["stealing_creation"]["active_session"]
        self.assertGreater(session["equipment"]["tool"], 0)
        self.assertGreater(session["equipment"]["weapon"], 0)
        self.assertGreater(session["equipment"]["armour"], 0)
        self.assertGreater(session["equipment"]["barrier"], 0)
        self.assertGreater(session["gathered"], 0)
        self.assertGreater(session["processed"], 0)
        self.assertFalse(
            any("Sacred clay" in item_name for item_name in data["inventory"])
        )

    def test_advanced_policy_uses_selected_gather_class_recipe_and_deposit(self):
        data = _entered()
        data, ok, _ = apply_stealing_creation_command_pure(
            data,
            "set_policy",
            {
                "automation_mode": "advanced",
                "selected_duty": "gather",
                "selected_gather_method": "mine",
                "selected_class": 3,
                "selected_recipe": "platebody",
            },
        )
        self.assertTrue(ok)
        data["stealing_creation"]["active_session"]["next_raid_review"] = 20
        data, ok, result = apply_stealing_creation_review_pure(data, lambda: 0.0)
        self.assertTrue(ok)
        self.assertEqual(result["tier"], 3)
        data, ok, _ = apply_stealing_creation_command_pure(
            data,
            "set_policy",
            {
                "automation_mode": "advanced",
                "selected_duty": "process",
                "selected_gather_method": "mine",
                "selected_class": 3,
                "selected_recipe": "platebody",
            },
        )
        self.assertTrue(ok)
        data, ok, result = apply_stealing_creation_review_pure(data, lambda: 0.0)
        self.assertTrue(ok)
        self.assertEqual(result["recipe_id"], "platebody")
        self.assertEqual(data["stealing_creation"]["active_session"]["equipment"]["armour"], 3)

    def test_casual_plan_uses_a_processable_class_instead_of_livelocking(self):
        data = _entered(
            mining_level=80,
            fishing_level=80,
            hunter_level=80,
            woodcutting_level=1,
            construction_level=80,
        )
        data["stealing_creation"]["active_session"]["next_raid_review"] = 20
        first, ok, result = apply_stealing_creation_review_pure(data, lambda: 0.0)
        self.assertTrue(ok)
        self.assertEqual(result["action"], "gather")
        self.assertEqual(result["tier"], 1)
        second, ok, result = apply_stealing_creation_review_pure(first, lambda: 0.0)
        self.assertTrue(ok)
        self.assertEqual(result["action"], "process")
        self.assertEqual(result["recipe_id"], "hatchet")
        self.assertEqual(
            second["stealing_creation"]["active_session"]["equipment"]["tool"],
            1,
        )

    def test_live_raid_uses_session_loadout_six_ticks_and_no_combat_xp(self):
        data = _entered(attack_exp=12.0)
        session = data["stealing_creation"]["active_session"]
        session["equipment"].update({"weapon": 4, "armour": 3, "barrier": 2})
        session["barrier_durability"] = 4
        session["next_raid_review"] = 1
        seen = {}

        def _apply(temp, _enemies, equipment, **kwargs):
            seen["equipment"] = dict(temp["equipment"])
            seen["ticks"] = kwargs["ticks"]
            self.assertIn("Sacred clay scimitar (class 4)", equipment)
            return _combat_result(killed=True)(temp, _enemies, equipment, **kwargs)

        with patch("stealing_creation_logic.apply_combat_burst_pure", side_effect=_apply):
            updated, ok, result = apply_stealing_creation_review_pure(data, lambda: 0.5)
        self.assertTrue(ok)
        self.assertTrue(result["killed"])
        self.assertEqual(seen["ticks"], 6)
        self.assertEqual(seen["equipment"]["weapon"], "Sacred clay scimitar (class 4)")
        self.assertEqual(updated["attack_exp"], 12.0)
        self.assertEqual(updated["stealing_creation"]["active_session"]["barrier_durability"], 3)

    def test_raid_actor_is_closed_and_terminal_flee_or_failure_reschedules(self):
        data = _entered(
            inventory={"Shark": 20},
            combat_auto_flee=True,
            combat_auto_flee_percent=50,
            combat_dream_thrift=True,
            combat_vengeance=True,
            combat_selected_prayers=["protect_from_melee"],
            combat_supply_loadout={"food": {"Shark": 10}},
        )
        data["stealing_creation"]["active_session"]["next_raid_review"] = 1

        def _flee(temp, _enemies, _equipment, **_kwargs):
            self.assertEqual(temp["inventory"], {})
            self.assertFalse(temp["combat_auto_flee"])
            self.assertEqual(temp["combat_auto_flee_percent"], 0)
            self.assertFalse(temp["combat_dream_thrift"])
            self.assertFalse(temp["combat_vengeance"])
            self.assertEqual(temp["combat_selected_prayers"], [])
            self.assertEqual(temp["combat_supply_loadout"]["food"], {})
            return copy.deepcopy(temp), True, {"fled": True}

        with patch("stealing_creation_logic.apply_combat_burst_pure", side_effect=_flee):
            fled, ok, result = apply_stealing_creation_review_pure(data, lambda: 0.0)
        self.assertTrue(ok)
        self.assertTrue(result["fled"])
        session = fled["stealing_creation"]["active_session"]
        self.assertFalse(session["raider"])
        self.assertGreater(session["next_raid_review"], session["review"])
        self.assertEqual(fled["inventory"]["Shark"], 20)

        session["next_raid_review"] = session["review"] + 1
        with patch(
            "stealing_creation_logic.apply_combat_burst_pure",
            return_value=(copy.deepcopy(fled), False, {"reason": "combat_locked"}),
        ):
            failed, ok, result = apply_stealing_creation_review_pure(fled, lambda: 0.0)
        self.assertTrue(ok)
        self.assertIn("disengaged", result["status"])
        failed_session = failed["stealing_creation"]["active_session"]
        self.assertGreater(
            failed_session["next_raid_review"],
            failed_session["review"],
        )

    def test_safe_death_transfers_carried_clay_and_clears_temporary_gear(self):
        data = _entered()
        session = data["stealing_creation"]["active_session"]
        session["clay"].update({"3": 2, "5": 1})
        session["equipment"].update({"weapon": 3, "armour": 2})
        session["next_raid_review"] = 1
        with patch(
            "stealing_creation_logic.apply_combat_burst_pure",
            side_effect=_combat_result(died=True),
        ):
            updated, ok, result = apply_stealing_creation_review_pure(data, lambda: 0.5)
        self.assertTrue(ok)
        self.assertTrue(result["died"])
        self.assertEqual(result["transferred_score"], 165)
        session = updated["stealing_creation"]["active_session"]
        self.assertEqual(sum(session["clay"].values()), 0)
        self.assertEqual(session["equipment"]["weapon"], 0)
        self.assertEqual(session["equipment"]["armour"], 0)
        self.assertEqual(session["opponent_score"], 165 + 225)

    def test_review_budget_finishes_race_clears_session_and_applies_win_bonus(self):
        data = _entered()
        session = data["stealing_creation"]["active_session"]
        session.update(
            {
                "review": 19,
                "player_score": 20_000,
                "opponent_score": 1_000,
                "next_raid_review": 20,
            }
        )
        with patch(
            "stealing_creation_logic.apply_combat_burst_pure",
            side_effect=_combat_result(killed=True),
        ):
            updated, ok, result = apply_stealing_creation_review_pure(data, lambda: 0.0)
        self.assertTrue(ok)
        self.assertTrue(result["complete"])
        self.assertEqual(result["outcome"], "win")
        self.assertEqual(result["reward_score"], 22_000)
        self.assertEqual(result["points"], 21)
        self.assertEqual(updated["activity_session"], {"active_id": ""})
        self.assertFalse(updated["stealing_creation"]["active_session"])


class StealingCreationRewardToolTests(unittest.TestCase):
    def test_morphic_tool_is_chosen_and_doubles_matching_skill_xp(self):
        data = _player()
        data["stealing_creation"]["points"] = 20
        bought, ok, _ = purchase_stealing_creation_tool_pure(
            data, "morphic", form_id="hammer"
        )
        self.assertTrue(ok)
        self.assertEqual(bought["inventory"]["Proto-tool"], 1)
        updated, bonus, info = apply_stealing_creation_xp_bonus_pure(
            bought, "smithing_exp", 100.0
        )
        self.assertEqual(bonus, 100.0)
        self.assertTrue(info["applied"])
        self.assertLess(updated["stealing_creation"]["reward_tools"]["morphic"]["charge"], 1.0)
        _unchanged, wrong_bonus, wrong_info = apply_stealing_creation_xp_bonus_pure(
            updated, "fishing_exp", 100.0
        )
        self.assertEqual(wrong_bonus, 0.0)
        self.assertFalse(wrong_info["applied"])

    def test_volatile_tool_adds_120_percent_bonus_and_randomizes_at_ten_percent_boundary(self):
        data = _player()
        data["stealing_creation"]["points"] = 20
        bought, ok, _ = purchase_stealing_creation_tool_pure(
            data, "volatile", rng=lambda: 0.0
        )
        self.assertTrue(ok)
        self.assertEqual(
            bought["stealing_creation"]["reward_tools"]["volatile"]["form_id"],
            "hammer",
        )
        bought["stealing_creation"]["reward_tools"]["volatile"]["charge"] = 0.95
        updated, bonus, info = apply_stealing_creation_xp_bonus_pure(
            bought, "smithing_exp", 2_000.0, rng=lambda: 0.999
        )
        self.assertEqual(bonus, 2_400.0)
        self.assertTrue(info["transformed"])
        self.assertEqual(info["next_form_id"], "butterfly_net")
        self.assertEqual(
            STEALING_CREATION_REWARD_FORM_BY_ID[info["next_form_id"]].display_name,
            "Butterfly net",
        )
        self.assertLess(updated["stealing_creation"]["reward_tools"]["volatile"]["charge"], 0.9)

    def test_volatile_form_obeys_the_period_level_40_gate(self):
        data = _player(smithing_level=39)
        data["stealing_creation"]["points"] = 20
        bought, ok, _ = purchase_stealing_creation_tool_pure(
            data, "volatile", rng=lambda: 0.0
        )
        self.assertTrue(ok)
        updated, bonus, info = apply_stealing_creation_xp_bonus_pure(
            bought, "smithing_exp", 100.0
        )
        self.assertEqual(bonus, 0.0)
        self.assertEqual(info["reason"], "volatile_level_40")
        self.assertEqual(
            updated["stealing_creation"]["reward_tools"]["volatile"]["charge"],
            1.0,
        )

    def test_matching_skill_side_xp_does_not_consume_tool_charge(self):
        data = _player()
        data["stealing_creation"]["points"] = 20
        bought, ok, _ = purchase_stealing_creation_tool_pure(
            data, "morphic", form_id="butterfly_net"
        )
        self.assertTrue(ok)
        updated, bonus, info = apply_stealing_creation_xp_bonus_pure(
            bought,
            "hunter_exp",
            30.0,
            action_skill_id="activities",
        )
        self.assertEqual(bonus, 0.0)
        self.assertEqual(info["reason"], "tool_not_used_by_action_family")
        self.assertEqual(
            updated["stealing_creation"]["reward_tools"]["morphic"]["charge"],
            1.0,
        )
        self.assertFalse(
            stealing_creation_tool_can_apply_pure(
                bought, "hunter_exp", "activities"
            )
        )
        self.assertTrue(
            stealing_creation_tool_can_apply_pure(
                bought, "hunter_exp", "hunter"
            )
        )


class StealingCreationMigrationAndRuntimeTests(unittest.TestCase):
    def test_migration_repairs_session_and_rejects_wall_clock_fields(self):
        raw = {
            "active_session": {
                "active": True,
                "review": 4,
                "wall_clock_started": 123,
                "clay": {"5": 2},
            }
        }
        sanitized = sanitize_stealing_creation_state_pure(raw)
        self.assertNotIn("wall_clock_started", sanitized["active_session"])
        migrated = migrate_loaded_data({"stealing_creation": raw}, {}, ())
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["activity_session"], {"active_id": "stealing_creation"})

        malformed = sanitize_stealing_creation_state_pure(
            {"active_session": {"active": True, "raider": {"broken": True}}}
        )
        self.assertEqual(malformed["active_session"]["raider"], {})
        self.assertEqual(malformed["active_session"]["combat_encounter"], {})

    def test_runtime_dispatch_persists_one_duty_review(self):
        player = _entered()
        player["current_utility"] = "stealing_creation"
        player["stealing_creation"]["active_session"]["next_raid_review"] = 20
        saved = []
        gains = []
        ctx = RuntimeActionContext(
            player_data=player,
            random_random=lambda: 0.0,
            show_error_message=lambda *_args: self.fail("unexpected runtime error"),
            deactivate_current_skill=lambda: self.fail("session should remain active"),
            award_skill_exp=lambda *_args: self.fail("Stealing Creation gives no skill XP"),
            award_hidden_skill_exp=lambda *_args: None,
            level_up_check=lambda *_args: None,
            check_achievements=lambda *_args: None,
            save_player_data=lambda: saved.append(True),
            refresh_skill_availability=lambda: None,
            refresh_skill_availability_partial=lambda *_args: None,
            can_smith_any=lambda: True,
            show_exp=lambda *_args: None,
            show_activity_gain=lambda message: gains.append(str(message)),
            implemented_exp_keys_snapshot=lambda: {},
            show_quest_exp_delta=lambda *_args: None,
        )
        self.assertTrue(handle_utility_answer(ctx))
        self.assertEqual(saved, [True])
        self.assertEqual(player["stealing_creation"]["active_session"]["review"], 1)
        self.assertTrue(any("sacred clay" in message for message in gains))
        view = stealing_creation_view_pure(player)
        self.assertEqual(view["reviews_remaining"], 19)


if __name__ == "__main__":
    unittest.main()
