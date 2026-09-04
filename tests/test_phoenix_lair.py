from __future__ import annotations

import copy
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import EQUIPMENT_DATA, ITEM_DEFINITIONS, ORE_DATA
from ankiscape.logic.pet_logic import hatch_phoenix_egg_pure
from ankiscape.data.phoenix_lair_data import (
    PHOENIX_LAIR_ACTIVITY_ID,
    PHOENIX_LAIR_GUARDIAN_COUNT,
    PHOENIX_LAIR_GUARDIANS,
)
from ankiscape.logic.phoenix_lair_logic import (
    apply_phoenix_lair_command_pure,
    apply_phoenix_lair_review_pure,
    default_phoenix_lair_state_pure,
    phoenix_lair_view_pure,
    resolve_phoenix_egg_choice_pure,
    sanitize_phoenix_lair_state_pure,
)
from ankiscape.core.review_context import (
    ignored_review_context_choice_pure,
    review_context_projection_pure,
)
from ankiscape.runtime.runtime_actions import RuntimeActionContext, handle_utility_answer
from ankiscape.core.storage_pure import CURRENT_CONFIG_VERSION, default_player_data, migrate_loaded_data


def _player(**overrides):
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data["quests"]["in_pyre_need"] = {
        "started": True,
        "progress": 1,
        "completed": True,
    }
    data.update(
        {
            "slayer_level": 99,
            "summoning_level": 99,
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "magic_level": 99,
            "ranged_level": 99,
            "combat_lifepoints": 990,
        }
    )
    data["inventory"].update({"Knife": 1, "Secateurs": 1, "Tinderbox": 1})
    data.update(overrides)
    return data


def _entered(**overrides):
    data = _player(**overrides)
    entered, ok, info = apply_phoenix_lair_command_pure(
        data,
        "enter",
        rng=lambda: 0.5,
        equipment_data=EQUIPMENT_DATA,
    )
    if not ok:
        raise AssertionError(info)
    return entered


def _combat_result(*, killed=False, died=False, lifepoints=1000, grave=False):
    def _apply(data, *_args, **_kwargs):
        updated = copy.deepcopy(data)
        updated["combat_encounter"] = (
            {} if killed or died else {"target_id": data["current_combat_target"], "enemy_lifepoints": lifepoints}
        )
        if grave:
            updated["combat_grave"] = {"active": True, "location": "Phoenix Lair entrance"}
        return updated, True, {
            "reason": "combat_burst",
            "killed": killed,
            "died": died,
            "fled": False,
            "enemy_lifepoints": 0 if killed else lifepoints,
            "xp_rewards": {},
            "drops": {},
        }

    return _apply


class PhoenixLairRequirementsTests(unittest.TestCase):
    def test_entry_checks_quest_slayer_tools_daily_and_shared_combat_readiness(self):
        data = _player()
        data["quests"]["in_pyre_need"]["completed"] = False
        blocked, ok, info = apply_phoenix_lair_command_pure(data, "enter")
        self.assertFalse(ok)
        self.assertIn("In Pyre Need", info["reason"])
        self.assertEqual(blocked["phoenix_lair"], default_phoenix_lair_state_pure())

        data = _player(slayer_level=50)
        _blocked, ok, info = apply_phoenix_lair_command_pure(data, "enter")
        self.assertFalse(ok)
        self.assertIn("Slayer level 51", info["reason"])

        data = _player()
        data["carried_advanced_targets"][PHOENIX_LAIR_ACTIVITY_ID] = True
        data["carried_layout"][PHOENIX_LAIR_ACTIVITY_ID] = {
            "Knife": 1,
            "Secateurs": 1,
        }
        view = phoenix_lair_view_pure(data)
        self.assertFalse(view["requirements_met"])
        self.assertIn(
            "Tinderbox in carried pack or toolbelt",
            view["missing_requirements"],
        )
        _blocked, ok, info = apply_phoenix_lair_command_pure(data, "enter")
        self.assertFalse(ok)
        self.assertIn("carried pack or toolbelt", info["reason"])
        self.assertIn("Tinderbox", info["reason"])

        data["toolbelt"]["utility"] = ["Tinderbox"]
        entered, ok, info = apply_phoenix_lair_command_pure(
            data, "enter", rng=lambda: 0.0, equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok, info)
        self.assertEqual(
            entered["carried_inventory"][PHOENIX_LAIR_ACTIVITY_ID],
            {"Knife": 1, "Secateurs": 1},
        )
        self.assertEqual(entered["activity_session"], {"active_id": PHOENIX_LAIR_ACTIVITY_ID})
        self.assertEqual(len(entered["phoenix_lair"]["guardian_roster"]), 5)
        self.assertEqual(
            entered["phoenix_lair"]["guardian_max_lifepoints"],
            PHOENIX_LAIR_GUARDIAN_COUNT
            * PHOENIX_LAIR_GUARDIANS["lesser_reborn_warrior"]["stats"]["hitpoints"],
        )

    def test_competing_session_and_same_day_completion_block_entry(self):
        data = _player(activity_session={"active_id": "fight_caves"})
        _blocked, ok, info = apply_phoenix_lair_command_pure(data, "enter")
        self.assertFalse(ok)
        self.assertIn("persistent activity", info["reason"])

        data = _player()
        data["phoenix_lair"]["last_completed_world_day"] = 0
        _blocked, ok, info = apply_phoenix_lair_command_pure(data, "enter")
        self.assertFalse(ok)
        self.assertIn("world day", info["reason"])


class PhoenixLairMechanicsTests(unittest.TestCase):
    def test_guardian_front_prepare_and_phoenix_completion_are_atomic(self):
        data = _entered()
        with patch(
            "ankiscape.logic.phoenix_lair_logic.apply_combat_burst_pure",
            side_effect=_combat_result(killed=True),
        ):
            cleared, ok, result = apply_phoenix_lair_review_pure(
                data, lambda: 0.5, equipment_data=EQUIPMENT_DATA
            )
        self.assertTrue(ok, result)
        self.assertEqual(cleared["phoenix_lair"]["phase"], "prepare")
        self.assertEqual(cleared["inventory"]["Ashes"], 5)

        prepared, ok, result = apply_phoenix_lair_review_pure(
            cleared, lambda: 0.5, equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok, result)
        self.assertEqual(prepared["phoenix_lair"]["phase"], "phoenix")
        self.assertEqual(prepared["phoenix_lair"]["phoenix_lifepoints"], 2550)

        before = {
            key: float(prepared.get(key, 0.0) or 0.0)
            for key in ("firemaking_exp", "fletching_exp", "crafting_exp", "slayer_exp")
        }
        with patch(
            "ankiscape.logic.phoenix_lair_logic.apply_combat_burst_pure",
            side_effect=_combat_result(killed=True),
        ):
            won, ok, result = apply_phoenix_lair_review_pure(
                prepared, lambda: 0.5, equipment_data=EQUIPMENT_DATA
            )
        self.assertTrue(ok, result)
        self.assertFalse(won["phoenix_lair"]["active"])
        self.assertEqual(won["current_combat_target"], "chicken")
        self.assertEqual(won["inventory"]["Phoenix quill"], 5)
        self.assertEqual(won["firemaking_exp"] - before["firemaking_exp"], 7500.0)
        self.assertEqual(won["fletching_exp"] - before["fletching_exp"], 3000.0)
        self.assertEqual(won["crafting_exp"] - before["crafting_exp"], 1000.0)
        self.assertEqual(won["slayer_exp"] - before["slayer_exp"], 5000.0)
        self.assertEqual(won["phoenix_lair"]["last_completed_world_day"], 0)
        _blocked, can_enter, _ = apply_phoenix_lair_command_pure(won, "enter")
        self.assertFalse(can_enter)

        won["shop_market_clock"]["answered_cards"] = 240
        repeat, ok, info = apply_phoenix_lair_command_pure(
            won, "enter", rng=lambda: 0.5, equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok, info)
        repeat["phoenix_lair"]["phase"] = "phoenix"
        repeat["phoenix_lair"]["phoenix_lifepoints"] = 1
        repeat["phoenix_lair"]["encounter"] = {
            "target_id": "phoenix_lair_phoenix",
            "enemy_lifepoints": 1,
        }
        prior_slayer = repeat["slayer_exp"]
        with patch(
            "ankiscape.logic.phoenix_lair_logic.apply_combat_burst_pure",
            side_effect=_combat_result(killed=True),
        ):
            repeated, ok, result = apply_phoenix_lair_review_pure(
                repeat, lambda: 0.5, equipment_data=EQUIPMENT_DATA
            )
        self.assertTrue(ok, result)
        self.assertEqual(repeated["slayer_exp"] - prior_slayer, 500.0)

    def test_death_and_abandon_clear_only_unfinished_session_state(self):
        data = _entered()
        data["inventory"]["Ashes"] = 7
        with patch(
            "ankiscape.logic.phoenix_lair_logic.apply_combat_burst_pure",
            side_effect=_combat_result(died=True, grave=True),
        ):
            defeated, ok, result = apply_phoenix_lair_review_pure(
                data, lambda: 0.5, equipment_data=EQUIPMENT_DATA
            )
        self.assertTrue(ok, result)
        self.assertFalse(defeated["phoenix_lair"]["active"])
        self.assertEqual(defeated["phoenix_lair"]["last_completed_world_day"], -1)
        self.assertEqual(defeated["inventory"]["Ashes"], 7)
        self.assertTrue(defeated["combat_grave"]["active"])

        data = _entered(current_combat_target="")
        data["inventory"]["Ashes"] = 5
        left, ok, info = apply_phoenix_lair_command_pure(data, "leave")
        self.assertTrue(ok, info)
        self.assertFalse(left["phoenix_lair"]["active"])
        self.assertEqual(left["inventory"]["Ashes"], 5)
        self.assertEqual(left["phoenix_lair"]["last_completed_world_day"], -1)
        self.assertEqual(left["current_combat_target"], "")

    def test_fifth_phoenix_review_applies_review_native_dust_drain(self):
        data = _entered()
        state = data["phoenix_lair"]
        state["phase"] = "phoenix"
        state["phoenix_lifepoints"] = 2000
        state["phoenix_review_count"] = 4
        state["encounter"] = {
            "target_id": "phoenix_lair_phoenix",
            "enemy_lifepoints": 2000,
        }
        with patch(
            "ankiscape.logic.phoenix_lair_logic.apply_combat_burst_pure",
            side_effect=_combat_result(lifepoints=1900),
        ):
            drained, ok, result = apply_phoenix_lair_review_pure(
                data, lambda: 0.5, equipment_data=EQUIPMENT_DATA
            )
        self.assertTrue(ok, result)
        self.assertTrue(result["dust_attack"])
        self.assertEqual(
            drained["combat_current_levels"],
            {"attack": 49, "magic": 49, "ranged": 49},
        )

        data["combat_current_levels"] = {"attack": 60, "magic": 40, "ranged": 20}
        data["phoenix_lair"]["phoenix_review_count"] = 4
        with patch(
            "ankiscape.logic.phoenix_lair_logic.apply_combat_burst_pure",
            side_effect=_combat_result(lifepoints=1800),
        ):
            drained, ok, result = apply_phoenix_lair_review_pure(
                data, lambda: 0.5, equipment_data=EQUIPMENT_DATA
            )
        self.assertTrue(ok, result)
        self.assertEqual(
            drained["combat_current_levels"],
            {"attack": 30, "magic": 20, "ranged": 10},
        )


class PhoenixEggTests(unittest.TestCase):
    def test_context_default_remembering_low_level_item_and_late_hatch(self):
        data = _player(summoning_level=71)
        data["phoenix_lair"]["pending_egg"] = True
        projection = review_context_projection_pure(data)
        self.assertEqual(projection["active"]["family_id"], "phoenix_egg")
        self.assertEqual(ignored_review_context_choice_pure(data), ("phoenix_egg", "clap"))

        item, ok, info = resolve_phoenix_egg_choice_pure(
            data, "kick", remember_choice=True
        )
        self.assertTrue(ok, info)
        self.assertEqual(item["inventory"]["Cracked phoenix egg"], 1)
        self.assertEqual(item["review_context_preferences"]["phoenix_egg"], "kick")
        self.assertFalse(item["phoenix_lair"]["pending_egg"])

        blocked, ok, reason = hatch_phoenix_egg_pure(item, "Cracked phoenix egg")
        self.assertFalse(ok)
        self.assertEqual(reason, "summoning_level")
        item["summoning_level"] = 72
        hatched, ok, instance_id = hatch_phoenix_egg_pure(
            item, "Cracked phoenix egg"
        )
        self.assertTrue(ok, instance_id)
        self.assertEqual(hatched["inventory"]["Cracked phoenix egg"], 0)
        self.assertEqual(
            hatched["summoning_state"]["pet_instances"][instance_id]["pet_id"],
            "mean_phoenix_eggling",
        )

    def test_level_72_choice_acquires_either_temperament_without_exclusion(self):
        data = _player(summoning_level=72)
        data["phoenix_lair"]["pending_egg"] = True
        cute, ok, info = resolve_phoenix_egg_choice_pure(data, "clap")
        self.assertTrue(ok, info)
        cute["phoenix_lair"]["pending_egg"] = True
        both, ok, info = resolve_phoenix_egg_choice_pure(cute, "kick")
        self.assertTrue(ok, info)
        pets = {
            row["pet_id"]
            for row in both["summoning_state"]["pet_instances"].values()
        }
        self.assertEqual(
            pets, {"cute_phoenix_eggling", "mean_phoenix_eggling"}
        )


class PhoenixLairPersistenceAndRuntimeTests(unittest.TestCase):
    def test_sanitizer_and_migration_repair_active_session_without_timers(self):
        raw = {
            "active": True,
            "phase": "guardians",
            "guardian_roster": ["lesser_reborn_mage"] * 5,
            "guardian_lifepoints": 2000,
            "timer": 600,
        }
        clean = sanitize_phoenix_lair_state_pure(raw)
        self.assertNotIn("timer", clean)
        migrated = migrate_loaded_data({"phoenix_lair": raw}, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["activity_session"], {"active_id": "phoenix_lair"})

    def test_runtime_routes_only_selected_active_phoenix_lair_reviews(self):
        player = _entered()
        saved = []
        gains = []
        ctx = RuntimeActionContext(
            player_data=player,
            random_random=lambda: 0.5,
            show_error_message=lambda *_args: self.fail("unexpected runtime error"),
            deactivate_current_skill=lambda _reason=None: None,
            award_skill_exp=lambda *_args: self.fail("pure activity owns XP"),
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
        with patch(
            "ankiscape.logic.phoenix_lair_logic.apply_combat_burst_pure",
            side_effect=_combat_result(lifepoints=4000),
        ):
            self.assertTrue(handle_utility_answer(ctx))
        self.assertEqual(saved, [True])
        self.assertEqual(player["phoenix_lair"]["guardian_lifepoints"], 4000)
        self.assertTrue(any("Guardian front" in str(value) for value in gains))

    def test_view_exposes_daily_and_phase_state_without_wall_clock_fields(self):
        data = _entered()
        view = phoenix_lair_view_pure(data)
        self.assertTrue(view["active"])
        self.assertEqual(view["phase"], "guardians")
        self.assertNotIn("timestamp", view)
        self.assertNotIn("timer", view)


if __name__ == "__main__":
    unittest.main()
