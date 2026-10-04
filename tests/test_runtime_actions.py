import copy
import dataclasses
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from tests.quest_action_proof_helpers import quest_action_proofs_for_quest
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.brawling_gloves_data import BRAWLING_GLOVE_DATA
from ankiscape.data.dungeoneering_data import DUNGEONEERING_ACTIVITY_ID
from ankiscape.logic.brawling_gloves_logic import brawling_glove_state_pure
from ankiscape.logic.dungeoneering_logic import (
    apply_dungeoneering_command_pure,
    record_dungeon_drop_pure,
)
from ankiscape.logic_pure.logic_pure import can_start_quest_pure
from ankiscape.runtime import runtime_actions

# Patch targets live on the module that defines the name: a caller resolves it
# from its own globals, not from runtime_actions' re-export.
from ankiscape.runtime import runtime_actions_activities
from ankiscape.runtime import runtime_actions_carried_overlay
from ankiscape.runtime import runtime_actions_combat
from ankiscape.runtime import runtime_actions_production

from ankiscape.runtime.runtime_actions import (
    RuntimeActionContext,
    answer_handler_for_key,
    can_start_action,
    handle_cooking_answer,
    handle_combat_answer,
    handle_crafting_answer,
    handle_firemaking_answer,
    handle_fishing_answer,
    handle_fletching_answer,
    handle_hunter_answer,
    handle_agility_answer,
    handle_herblore_answer,
    handle_mining_answer,
    handle_quest_answer,
    handle_runecrafting_answer,
    handle_smithing_answer,
    handle_summoning_answer,
    handle_utility_answer,
    handle_woodcutting_answer,
    run_answer_with_carried_overlay,
)


def _context(
    player_data,
    calls=None,
    random_values=None,
    review_action_multiplier=1,
    prompt_slayer_completion=None,
):
    calls = calls if calls is not None else {"xp": [], "saves": 0, "errors": []}
    random_iter = iter(random_values or ())

    def award_skill_exp(exp_key, base_exp):
        player_data[exp_key] = player_data.get(exp_key, 0) + base_exp
        return base_exp

    def random_random():
        try:
            return next(random_iter)
        except StopIteration:
            return 0.0

    def deactivate_current_skill(reason=None):
        calls["deactivated"] = True
        if reason:
            calls.setdefault("deactivation_reasons", []).append(str(reason))

    return RuntimeActionContext(
        player_data=player_data,
        random_random=random_random,
        show_error_message=lambda title, message: calls["errors"].append((title, message)),
        deactivate_current_skill=deactivate_current_skill,
        award_skill_exp=award_skill_exp,
        award_hidden_skill_exp=lambda exp_key, _level_key, base_exp: player_data.__setitem__(
            exp_key,
            player_data.get(exp_key, 0) + base_exp,
        ),
        level_up_check=lambda _skill, _data: calls.setdefault("level_checks", []).append(_skill),
        check_achievements=lambda _data: calls.setdefault("achievement_checks", 0),
        save_player_data=lambda: calls.__setitem__("saves", calls.get("saves", 0) + 1),
        refresh_skill_availability=lambda: calls.setdefault("refreshes", 0),
        show_exp=lambda exp: calls["xp"].append(exp),
        show_activity_gain=lambda text: calls.setdefault("activity", []).append(text),
        implemented_exp_keys_snapshot=lambda: {},
        show_quest_exp_delta=lambda _before: None,
        review_action_multiplier=review_action_multiplier,
        prompt_slayer_completion=prompt_slayer_completion,
    )


def _bankstanding_context(player_data, calls=None, **kwargs):
    calls = calls if calls is not None else {"xp": [], "saves": 0, "errors": []}
    ctx = _context(player_data, calls, **kwargs)

    def switch_to_bankstanding(reason=None):
        player_data["current_utility"] = "bankstanding"
        calls["bankstanding"] = calls.get("bankstanding", 0) + 1
        if reason:
            calls.setdefault("bankstanding_reasons", []).append(str(reason))

    ctx.switch_to_bankstanding = switch_to_bankstanding
    return ctx


def _quest_combat_mid_rolls(repeats=1000):
    return (0.5,) * repeats


class TestRuntimeActions(unittest.TestCase):
    def test_invalid_runtime_targets_switch_to_bankstanding_without_default_actions(self):
        cases = (
            (runtime_actions.handle_utility_answer, "current_utility"),
            (runtime_actions.handle_fishing_answer, "current_fishing"),
            (runtime_actions.handle_hunter_answer, "current_hunter"),
            (runtime_actions.handle_woodcutting_answer, "current_tree"),
            (runtime_actions.handle_mining_answer, "current_ore"),
            (runtime_actions.handle_magic_answer, "current_magic"),
            (runtime_actions.handle_combat_answer, "current_combat_target"),
            (runtime_actions.handle_thieving_answer, "current_thieving"),
            (runtime_actions.handle_fletching_answer, "current_fletch"),
            (runtime_actions.handle_herblore_answer, "current_herblore"),
            (runtime_actions.handle_summoning_answer, "current_summoning"),
            (runtime_actions.handle_prayer_answer, "current_prayer"),
            (runtime_actions.handle_construction_answer, "current_construction"),
            (runtime_actions.handle_firemaking_answer, "current_firemaking"),
            (runtime_actions.handle_cooking_answer, "current_cooking"),
            (runtime_actions.handle_runecrafting_answer, "current_runecrafting"),
            (runtime_actions.handle_quest_answer, "current_quest"),
            (runtime_actions.handle_smithing_answer, "current_smith"),
            (runtime_actions.handle_agility_answer, "current_agility"),
        )
        for handler, selection_key in cases:
            with self.subTest(handler=handler.__name__):
                player_data = {selection_key: "removed_target"}
                calls = {"xp": [], "saves": 0, "errors": []}

                self.assertFalse(
                    handler(_bankstanding_context(player_data, calls))
                )

                self.assertEqual(player_data["current_utility"], "bankstanding")
                if selection_key != "current_utility":
                    self.assertEqual(player_data[selection_key], "removed_target")
                self.assertEqual(calls["bankstanding"], 1)
                self.assertEqual(calls["saves"], 0)

    def test_named_activity_refusals_switch_to_bankstanding(self):
        handlers = (
            runtime_actions_activities.handle_dungeoneering_answer,
            runtime_actions_activities.handle_temple_trekking_answer,
            runtime_actions_activities.handle_gnome_restaurant_answer,
            runtime_actions_activities.handle_dominion_tower_answer,
        )
        for handler in handlers:
            with self.subTest(handler=handler.__name__):
                player_data = {}
                calls = {"xp": [], "saves": 0, "errors": []}

                self.assertFalse(
                    handler(_bankstanding_context(player_data, calls))
                )

                self.assertEqual(player_data["current_utility"], "bankstanding")
                self.assertEqual(calls["bankstanding"], 1)
                self.assertEqual(len(calls["errors"]), 1)

    def test_dungeoneering_bind_prompt_keeps_the_current_surface(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["dungeoneering_level"] = 11
        player_data, ok, info = apply_dungeoneering_command_pure(
            player_data,
            "enter",
            {
                "floor": 6,
                "size": "small",
                "complexity": 6,
                "automation_mode": "casual",
            },
        )
        self.assertTrue(ok, info)
        player_data, ok, info = record_dungeon_drop_pure(
            player_data,
            "Novite arrows",
            50,
            ammo=True,
        )
        self.assertTrue(ok, info)
        player_data["current_utility"] = DUNGEONEERING_ACTIVITY_ID
        calls = {"xp": [], "saves": 0, "errors": []}

        self.assertFalse(
            runtime_actions_activities.handle_dungeoneering_answer(
                _bankstanding_context(player_data, calls)
            )
        )

        self.assertEqual(player_data["current_utility"], DUNGEONEERING_ACTIVITY_ID)
        self.assertTrue(player_data["dungeoneering"]["pending_bind_offer"])
        self.assertEqual(calls.get("bankstanding", 0), 0)
        self.assertEqual(
            calls["errors"],
            [
                (
                    "Dungeoneering unavailable",
                    "Resolve the Bind / Replace / Skip offer first.",
                )
            ],
        )

    def test_active_activity_prompts_keep_the_current_surface(self):
        cases = (
            (
                "apply_temple_trekking_review_pure",
                runtime_actions_activities.handle_temple_trekking_answer,
                runtime_actions_activities.TEMPLE_TREKKING_ACTIVITY_ID,
                "temple_trekking",
                {"session": {"nodes": ["ghasts"]}},
                "The current event still needs input.",
            ),
            (
                "apply_gnome_restaurant_review_pure",
                runtime_actions_activities.handle_gnome_restaurant_answer,
                runtime_actions_activities.GNOME_RESTAURANT_ACTIVITY_ID,
                "gnome_restaurant",
                {"order": {"item": "Gnomebowl"}},
                "Cook or bank 1 Gnomebowl for this delivery.",
            ),
            (
                "apply_dominion_tower_review_pure",
                runtime_actions_activities.handle_dominion_tower_answer,
                runtime_actions_activities.DOMINION_TOWER_ACTIVITY_ID,
                "dominion_tower",
                {"mode": "climber", "roster": [{"instance_id": 1}]},
                "Take the handicap on the spinner before the doors open.",
            ),
        )
        for pure_name, handler, activity_id, state_key, state, reason in cases:
            with self.subTest(handler=handler.__name__):
                player_data = {
                    "current_utility": activity_id,
                    "activity_session": {"active_id": activity_id},
                    state_key: state,
                }
                calls = {"xp": [], "saves": 0, "errors": []}
                with patch.object(
                    runtime_actions_activities,
                    pure_name,
                    return_value=(copy.deepcopy(player_data), False, {"reason": reason}),
                ):
                    self.assertFalse(
                        handler(_bankstanding_context(player_data, calls))
                    )

                self.assertEqual(player_data["current_utility"], activity_id)
                self.assertEqual(calls.get("bankstanding", 0), 0)
                self.assertEqual(len(calls["errors"]), 1)
                self.assertEqual(calls["errors"][0][1], reason)

    def test_flash_powder_factory_completion_switches_to_bankstanding(self):
        from ankiscape.data.flash_powder_factory_data import (
            FLASH_POWDER_FACTORY_ACTIVITY_ID,
        )
        from ankiscape.logic.agility_logic import default_agility_state_pure
        from ankiscape.logic.flash_powder_factory_logic import (
            enter_flash_powder_factory_pure,
        )

        player_data = default_agility_state_pure()
        player_data.update(
            {
                "agility_level": 99,
                "thieving_level": 99,
                "herblore_level": 99,
                "inventory": {},
                "equipment": {},
                "activity_session": {"active_id": ""},
                "summoning_state": {"active_follower": {}},
                "completed_achievements": [],
            }
        )
        player_data, ok, _info = enter_flash_powder_factory_pure(player_data)
        self.assertTrue(ok)
        player_data["current_agility"] = FLASH_POWDER_FACTORY_ACTIVITY_ID
        player_data["agility_activity_state"][FLASH_POWDER_FACTORY_ACTIVITY_ID].update(
            {"slots_used": 7, "batches": 7, "score": 800, "residue": 7}
        )
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}

        self.assertTrue(
            handle_agility_answer(
                _bankstanding_context(
                    player_data,
                    calls,
                    random_values=(0.99, 0.99, 0.99, 0.99),
                )
            )
        )

        self.assertEqual(player_data["current_utility"], "bankstanding")
        self.assertEqual(
            player_data["current_agility"], FLASH_POWDER_FACTORY_ACTIVITY_ID
        )
        self.assertEqual(player_data["activity_session"], {"active_id": ""})
        self.assertEqual(calls["bankstanding"], 1)

    def test_mining_review_applies_one_brawling_charge_and_multiplier(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data.update(
            {
                "current_ore": "copper",
                "mining_level": 99,
                "mining_exp": 0.0,
            }
        )
        item_name = BRAWLING_GLOVE_DATA["mining"]["item_name"]
        player_data["equipment"]["hands"] = item_name
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}

        self.assertTrue(
            handle_mining_answer(
                _context(player_data, calls, random_values=(0.0,) * 12)
            )
        )

        self.assertEqual(player_data["mining_exp"], 26.25)
        self.assertEqual(calls["xp"], [26.25])
        self.assertEqual(
            brawling_glove_state_pure(player_data, "mining")[
                "remaining_actions"
            ],
            BRAWLING_GLOVE_DATA["mining"]["max_actions"] - 1,
        )
        self.assertTrue(
            any("1.5× Brawling gloves" in text for text in calls["activity"])
        )

    def test_living_rock_remains_records_the_full_mineral_bundle(self):
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = {
            "current_ore": "living_rock_remains",
            "inventory": {},
            "toolbelt": {"mining": ["rune_pickaxe"]},
            "equipment": {},
            "mining_level": 73,
            "mining_exp": 0.0,
            "completed_achievements": [],
        }

        self.assertTrue(
            handle_mining_answer(
                _context(player_data, calls, random_values=(0.0, 0.5, 1.0, 0.0))
            )
        )

        self.assertEqual(player_data["inventory"]["Living minerals"], 15)
        self.assertEqual(player_data["mining_exp"], 25.0)
        telemetry = player_data["action_telemetry"]["actions"][
            "mining:living_rock_remains"
        ]
        self.assertEqual(telemetry["outputs"], {"Living minerals": 15})

    def test_tzhaar_fight_pit_routes_review_and_terminal_state_through_utility(self):
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = {
            "current_utility": "tzhaar_fight_pit",
            "activity_session": {"active_id": "tzhaar_fight_pit"},
            "tzhaar_fight_pit": {"roster": [{}]},
            "completed_achievements": [],
        }
        updated = {
            **player_data,
            "tzhaar_fight_pit": {},
            "activity_session": {"active_id": ""},
            "tzhaar_fight_pit_wins": 1,
        }
        result = {
            "terminal": True,
            "outcome": "win",
            "message": "Fight Pit champion · +100 TokKul",
            "combat": {"xp_rewards": {"attack_exp": 4.0}},
        }
        with patch(
            "ankiscape.runtime.runtime_actions_activities.apply_tzhaar_fight_pit_review_pure",
            return_value=(updated, True, result),
        ):
            self.assertTrue(handle_utility_answer(_context(player_data, calls)))
        self.assertEqual(player_data["tzhaar_fight_pit_wins"], 1)
        self.assertEqual(calls["saves"], 1)
        self.assertTrue(calls["deactivated"])
        self.assertIn(
            "utility:tzhaar_fight_pit",
            player_data["action_telemetry"]["actions"],
        )

    def test_shades_of_mortton_routes_repair_xp_through_utility(self):
        from ankiscape.logic.shades_of_mortton_logic import enter_shades_of_mortton_pure

        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data, ok, info = enter_shades_of_mortton_pure(
            {
                "current_utility": "shades_of_mortton",
                "activity_session": {"active_id": ""},
                "combat_encounter": {},
                "current_combat_target": "chicken",
                "quests": {"shades_of_mortton": {"completed": True}},
                "inventory": {
                    "Hammer": 1,
                    "Timber beam": 1,
                    "Limestone brick": 1,
                    "Swamp paste": 5,
                },
                "equipment": {},
                "crafting_exp": 0.0,
                "completed_achievements": [],
            },
            {"automation_mode": "advanced", "duty": "repair"},
        )
        self.assertTrue(ok, info)

        self.assertTrue(
            handle_utility_answer(
                _context(player_data, calls, random_values=(0.0, 0.0))
            )
        )

        self.assertEqual(player_data["crafting_exp"], 20.0)
        self.assertEqual(calls["xp"], [20.0])
        self.assertEqual(calls["saves"], 1)
        self.assertIn(
            "utility:shades_of_mortton",
            player_data["action_telemetry"]["actions"],
        )

    def test_barbarian_assault_routes_full_run_through_utility(self):
        from ankiscape.logic.barbarian_assault_logic import (
            complete_barbarian_assault_tutorial_pure,
            enter_barbarian_assault_pure,
        )

        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data, ok, info = complete_barbarian_assault_tutorial_pure(
            {
                "current_utility": "barbarian_assault",
                "activity_session": {"active_id": ""},
                "combat_encounter": {},
                "combat_supply_loadout": {},
                "current_combat_target": "chicken",
                "inventory": {},
                "equipment": {},
                "completed_achievements": [],
            }
        )
        self.assertTrue(ok, info)
        player_data, ok, info = enter_barbarian_assault_pure(
            player_data,
            {"automation_mode": "advanced", "role": "defender"},
        )
        self.assertTrue(ok, info)

        for _ in range(18):
            self.assertTrue(handle_utility_answer(_context(player_data, calls)))
            if not player_data["barbarian_assault"]:
                break

        self.assertEqual(player_data["barbarian_assault"], {})
        self.assertEqual(player_data["barbarian_assault_queen_kills"], 1)
        self.assertTrue(player_data["barbarian_assault_queen_credit"])
        self.assertTrue(calls.get("deactivated"))
        self.assertIn(
            "utility:barbarian_assault",
            player_data["action_telemetry"]["actions"],
        )

    def test_stronghold_player_safety_routes_three_landmarks_through_utility(self):
        from ankiscape.logic.stronghold_player_safety_logic import (
            default_stronghold_player_safety_state_pure,
        )

        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = {
            "current_utility": "stronghold_player_safety",
            "inventory": {},
            "equipment": {},
            "completed_achievements": [],
            "stronghold_player_safety": (
                default_stronghold_player_safety_state_pure()
            ),
        }

        for _ in range(3):
            self.assertTrue(handle_utility_answer(_context(player_data, calls)))

        self.assertEqual(player_data["stronghold_player_safety"]["stage"], 3)
        self.assertTrue(calls.get("deactivated"))
        self.assertEqual(calls["saves"], 3)
        self.assertIn(
            "utility:stronghold_player_safety",
            player_data["action_telemetry"]["actions"],
        )

    def test_varrock_museum_routes_one_landmark_through_utility(self):
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = {
            "current_utility": "varrock_museum",
            "inventory": {},
            "equipment": {},
            "quests": {},
            "completed_achievements": [],
        }

        self.assertTrue(handle_utility_answer(_context(player_data, calls)))

        self.assertEqual(player_data["varrock_museum"]["quiz_completed"], ["Lizard"])
        self.assertEqual(calls["saves"], 1)
        self.assertIn("+2 Kudos", calls["activity"][-1])
        self.assertIn(
            "utility:varrock_museum",
            player_data["action_telemetry"]["actions"],
        )

    def test_pest_control_routes_through_utility_and_settles_period_rewards(self):
        from ankiscape.logic.pest_control_logic import enter_pest_control_pure

        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data, ok, info = enter_pest_control_pure(
            {
                "current_utility": "pest_control",
                "activity_session": {"active_id": ""},
                "combat_encounter": {},
                "combat_supply_loadout": {},
                "current_combat_target": "chicken",
                "inventory": {},
                "equipment": {},
                "attack_level": 40,
                "strength_level": 40,
                "defense_level": 40,
                "constitution_level": 40,
                "ranged_level": 40,
                "magic_level": 40,
                "prayer_level": 40,
                "summoning_level": 1,
                "completed_achievements": [],
            },
            {"automation_mode": "advanced", "lander_id": "novice", "duty": "defend"},
        )
        self.assertTrue(ok, info)

        for _ in range(12):
            self.assertTrue(
                handle_utility_answer(
                    _context(player_data, calls, random_values=(0.5,))
                )
            )
            if not player_data["pest_control"]:
                break

        self.assertEqual(player_data["pest_control"], {})
        self.assertEqual(player_data["pest_control_commendations"], 2)
        self.assertEqual(player_data["coins"], 510)
        self.assertTrue(calls.get("deactivated"))
        self.assertIn(
            "utility:pest_control",
            player_data["action_telemetry"]["actions"],
        )

    def test_castle_wars_match_routes_through_utility_and_settles_tickets(self):
        from ankiscape.logic.castle_wars_logic import enter_castle_wars_pure

        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data, ok, info = enter_castle_wars_pure(
            {
                "current_utility": "castle_wars",
                "activity_session": {"active_id": ""},
                "combat_encounter": {},
                "combat_supply_loadout": {},
                "current_combat_target": "chicken",
                "inventory": {},
                "equipment": {},
                "completed_achievements": [],
            },
            {"automation_mode": "advanced", "duty": "capture"},
        )
        self.assertTrue(ok, info)

        for _ in range(10):
            self.assertTrue(
                handle_utility_answer(
                    _context(player_data, calls, random_values=(0.9,))
                )
            )

        self.assertEqual(player_data["castle_wars"], {})
        self.assertEqual(player_data["castle_wars_tickets"], 2)
        self.assertEqual(player_data["castle_wars_games_played"], 1)
        self.assertEqual(calls["saves"], 10)
        self.assertTrue(calls.get("deactivated"))
        self.assertIn(
            "utility:castle_wars",
            player_data["action_telemetry"]["actions"],
        )

    def test_soul_wars_match_routes_through_utility_and_settles_zeal(self):
        from ankiscape.logic.soul_wars_logic import enter_soul_wars_pure

        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data, ok, info = enter_soul_wars_pure(
            {
                "current_utility": "soul_wars",
                "activity_session": {"active_id": ""},
                "combat_encounter": {},
                "combat_supply_loadout": {"food": {}},
                "current_combat_target": "chicken",
                "inventory": {},
                "equipment": {},
                "attack_level": 40,
                "strength_level": 40,
                "defense_level": 40,
                "constitution_level": 40,
                "ranged_level": 40,
                "magic_level": 40,
                "prayer_level": 40,
                "slayer_level": 40,
                "summoning_level": 1,
                "completed_achievements": [],
            },
            {"automation_mode": "advanced", "duty": "defend", "team": "creation"},
        )
        self.assertTrue(ok, info)

        for _ in range(12):
            self.assertTrue(
                handle_utility_answer(
                    _context(player_data, calls, random_values=(0.9,) * 32)
                )
            )

        self.assertEqual(player_data["soul_wars"], {})
        self.assertEqual(player_data["soul_wars_games_played"], 1)
        self.assertIn(player_data["soul_wars_zeal"], {1, 2, 3})
        self.assertEqual(calls["saves"], 12)
        self.assertTrue(calls.get("deactivated"))
        self.assertIn(
            "utility:soul_wars",
            player_data["action_telemetry"]["actions"],
        )

    def test_soul_wars_again_is_an_idle_match_beat(self):
        from ankiscape.logic.soul_wars_logic import enter_soul_wars_pure

        player_data, ok, info = enter_soul_wars_pure(
            {
                "current_utility": "soul_wars",
                "activity_session": {"active_id": ""},
                "combat_encounter": {},
                "combat_supply_loadout": {"food": {}},
                "current_combat_target": "chicken",
                "inventory": {},
                "equipment": {},
                "completed_achievements": [],
            }
        )
        self.assertTrue(ok, info)
        self.assertTrue(
            runtime_actions.handle_soul_wars_answer(
                _context(player_data, random_values=(0.9,) * 16),
                productive=False,
            )
        )
        self.assertEqual(player_data["soul_wars"]["review"], 1)
        self.assertEqual(player_data["soul_wars"]["activity"], 2)

    def test_castle_wars_runtime_keeps_settled_combat_xp_and_again_can_idle(self):
        from ankiscape.logic.castle_wars_logic import enter_castle_wars_pure

        player_data, ok, info = enter_castle_wars_pure(
            {
                "current_utility": "castle_wars",
                "activity_session": {"active_id": ""},
                "combat_encounter": {},
                "combat_supply_loadout": {},
                "current_combat_target": "chicken",
                "inventory": {},
                "equipment": {},
                "attack_level": 1,
                "attack_exp": 0.0,
                "completed_achievements": [],
            },
            {"automation_mode": "advanced", "duty": "defend"},
        )
        self.assertTrue(ok, info)
        advanced = dict(player_data["castle_wars"])
        advanced["review"] = 1
        expected = dict(player_data, attack_exp=12.0)
        expected["castle_wars"] = advanced
        with patch(
            "ankiscape.runtime.runtime_actions_activities.apply_castle_wars_review_pure",
            return_value=(
                expected,
                True,
                {
                    "terminal": False,
                    "status": "Defended the standard",
                    "xp_rewards": {"attack_exp": 12.0},
                },
            ),
        ):
            self.assertTrue(
                runtime_actions.handle_castle_wars_answer(_context(player_data))
            )
        self.assertEqual(player_data["attack_exp"], 12.0)

        self.assertTrue(
            runtime_actions.handle_castle_wars_answer(
                _context(player_data, random_values=(0.9,)),
                productive=False,
            )
        )
        self.assertEqual(player_data["castle_wars"]["review"], 2)

    def test_castle_wars_casual_runtime_leaves_duty_to_the_bottleneck_selector(self):
        from ankiscape.logic.castle_wars_logic import enter_castle_wars_pure

        player_data, ok, info = enter_castle_wars_pure(
            {
                "current_utility": "castle_wars",
                "activity_session": {"active_id": ""},
                "combat_encounter": {},
                "combat_supply_loadout": {},
                "current_combat_target": "chicken",
                "inventory": {},
                "equipment": {},
                "completed_achievements": [],
            },
            {"automation_mode": "casual", "duty": "capture"},
        )
        self.assertTrue(ok, info)
        expected = dict(player_data)
        expected["castle_wars"] = dict(player_data["castle_wars"], review=1)
        with patch(
            "ankiscape.runtime.runtime_actions_activities.apply_castle_wars_review_pure",
            return_value=(
                expected,
                True,
                {"terminal": False, "status": "Resolved", "xp_rewards": {}},
            ),
        ) as apply_review:
            self.assertTrue(runtime_actions.handle_castle_wars_answer(_context(player_data)))
        self.assertIsNone(apply_review.call_args.kwargs["duty"])

    def test_trouble_brewing_review_race_awards_terminal_multi_skill_xp(self):
        from ankiscape.logic.trouble_brewing_logic import enter_trouble_brewing_pure

        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data, ok, info = enter_trouble_brewing_pure(
            {
                "current_utility": "trouble_brewing",
                "cooking_level": 40,
                "quests": {"cabin_fever": {"completed": True}},
                "activity_session": {"active_id": ""},
                "inventory": {},
                "completed_achievements": [],
            }
        )
        self.assertTrue(ok, info)

        for _ in range(16):
            self.assertTrue(
                handle_utility_answer(
                    _context(player_data, calls, random_values=(0.9, 0.9))
                )
            )

        self.assertEqual(player_data["trouble_brewing"], {})
        self.assertEqual(player_data["activity_session"], {"active_id": ""})
        self.assertEqual(player_data["trouble_brewing_pieces_of_eight"], 69)
        self.assertEqual(player_data["cooking_exp"], 810.0)
        self.assertEqual(player_data["crafting_exp"], 100.0)
        self.assertEqual(player_data["firemaking_exp"], 1950.0)
        self.assertEqual(calls["saves"], 16)
        self.assertTrue(calls.get("deactivated"))
        self.assertIn(
            "utility:trouble_brewing",
            player_data["action_telemetry"]["actions"],
        )

    def test_trouble_brewing_again_advances_without_player_duty(self):
        from ankiscape.logic.trouble_brewing_logic import enter_trouble_brewing_pure

        player_data, ok, info = enter_trouble_brewing_pure(
            {
                "current_utility": "trouble_brewing",
                "cooking_level": 40,
                "quests": {"cabin_fever": {"completed": True}},
                "activity_session": {"active_id": ""},
                "inventory": {},
                "completed_achievements": [],
            }
        )
        self.assertTrue(ok, info)
        self.assertTrue(
            runtime_actions.handle_trouble_brewing_answer(
                _context(player_data, random_values=(0.0, 0.9)),
                productive=False,
            )
        )
        self.assertEqual(player_data["trouble_brewing"]["review"], 1)
        self.assertEqual(
            player_data["trouble_brewing"]["stores"],
            {
                "water": 0,
                "coloured_water": 0,
                "sweetgrubs": 0,
                "scrapey_bark": 0,
                "bitternut": 0,
            },
        )
        self.assertEqual(player_data["trouble_brewing"]["opponent_progress"], 2)

    def test_circus_review_resolves_one_trick_per_answered_card(self):
        from ankiscape.logic.circus_logic import default_circus_state_pure

        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = {
            "current_utility": "big_top_bonanza",
            "circus": default_circus_state_pure(),
            "inventory": {},
            "quests": {},
            "shop_market_clock": {"answered_cards": 0},
            "agility_level": 99,
            "agility_exp": 0.0,
            "completed_achievements": [],
        }

        for _ in range(10):
            self.assertTrue(
                handle_utility_answer(
                    _context(player_data, calls, random_values=(0.0,))
                )
            )

        self.assertGreater(player_data["agility_exp"], 0.0)
        self.assertEqual(
            player_data["circus"]["used_week_by_performance"],
            {"agility": 0},
        )
        self.assertEqual(player_data["inventory"], {"Clown hat": 1})
        self.assertEqual(calls["saves"], 10)
        self.assertTrue(calls.get("deactivated"))
        self.assertIn("utility:big_top_bonanza", player_data["action_telemetry"]["actions"])
        self.assertEqual(
            len([row for row in player_data["review_event_log"] if row["kind"] == "activity"]),
            11,
        )

    def test_combat_level_refresh_leaves_the_old_level_for_the_level_up_gate(self):
        from ankiscape.runtime.runtime_actions_shared import _refresh_combat_levels

        player_data = {
            "constitution_level": 10,
            "constitution_exp": 1358.0,
        }
        ctx = _context(player_data)
        observed = []
        ctx.level_up_check = lambda skill, data: observed.append(
            (skill, data["constitution_level"])
        )

        _refresh_combat_levels(ctx, {"constitution_exp": 0.133})

        self.assertEqual(observed, [("Constitution", 10)])

    def test_circus_firemaking_performance_consumes_exactly_six_rolls(self):
        from ankiscape.logic.circus_logic import default_circus_state_pure

        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        state = default_circus_state_pure()
        state["selected_performance"] = "fire_breathing"
        state["performance_queue"] = {
            "executing": ["fire_breathing"],
            "non_executing": ["agility", "magic", "ranged", "flaming_poi", "thieving"],
        }
        player_data = {
            "current_utility": "big_top_bonanza",
            "circus": state,
            "inventory": {},
            "quests": {"the_firemakers_curse": {"completed": True}},
            "shop_market_clock": {"answered_cards": 0},
            "firemaking_level": 99,
            "firemaking_exp": 0.0,
            "completed_achievements": [],
        }
        rolls = []
        ctx = _context(player_data, calls)
        ctx = dataclasses.replace(
            ctx,
            random_random=lambda: rolls.append(0.0) or 0.0,
        )

        for _ in range(6):
            self.assertTrue(handle_utility_answer(ctx))

        self.assertEqual(len(rolls), 6)
        self.assertGreater(player_data["firemaking_exp"], 0.0)

    def test_circus_advanced_routine_consumes_only_its_saved_rolls(self):
        from ankiscape.logic.circus_logic import default_circus_state_pure

        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        state = default_circus_state_pure()
        state["automation_mode"] = "advanced"
        state["advanced_routines"] = {
            "agility": ["tightrope_99", "juggle_90"]
        }
        player_data = {
            "current_utility": "big_top_bonanza",
            "circus": state,
            "inventory": {},
            "quests": {},
            "shop_market_clock": {"answered_cards": 0},
            "agility_level": 99,
            "agility_exp": 0.0,
            "completed_achievements": [],
        }
        rolls = []
        ctx = dataclasses.replace(
            _context(player_data, calls),
            random_random=lambda: rolls.append(0.0) or 0.0,
        )

        for _ in range(2):
            self.assertTrue(handle_utility_answer(ctx))

        self.assertEqual(len(rolls), 2)
        self.assertGreater(player_data["agility_exp"], 0.0)

    def test_managing_miscellania_review_raises_approval_and_woodcutting_xp(self):
        from ankiscape.logic.managing_miscellania_logic import default_managing_miscellania_state_pure

        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = {
            "current_utility": "managing_miscellania",
            "quests": {"throne_of_miscellania": {"completed": True}},
            "shop_market_clock": {"answered_cards": 0},
            "woodcutting_level": 45,
            "woodcutting_exp": 0.0,
            "completed_achievements": [],
        }
        player_data.update(default_managing_miscellania_state_pure())
        player_data["managing_miscellania"]["approval_basis_points"] = 9_900

        self.assertTrue(handle_utility_answer(_context(player_data, calls)))

        self.assertEqual(
            player_data["managing_miscellania"]["approval_basis_points"], 10_000
        )
        self.assertEqual(player_data["woodcutting_exp"], 100.0)
        self.assertEqual(calls["xp"], [100.0])
        self.assertEqual(calls["saves"], 1)
        self.assertTrue(calls.get("deactivated"))
        telemetry = player_data["action_telemetry"]["actions"]
        self.assertIn("utility:managing_miscellania", telemetry)

    def test_fist_of_guthix_runtime_persists_one_six_tick_review(self):
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = {
            "current_utility": "fist_of_guthix",
            "attack_exp": 0.0,
            "attack_level": 1,
            "completed_achievements": [],
        }
        updated = dict(player_data)
        updated["attack_exp"] = 5.0
        updated["fist_of_guthix"] = {"active_match": {"round_ticks": 6}}
        result = {
            "ticks_elapsed": 6,
            "player_role": "hunter",
            "charge_gained": 18,
            "charge_total": 18,
            "xp_rewards": {"attack_exp": 5.0},
        }
        with patch.object(
            runtime_actions_activities,
            "apply_fist_of_guthix_review_pure",
            return_value=(updated, True, result),
        ) as apply_review:
            self.assertTrue(handle_utility_answer(_context(player_data, calls)))

        apply_review.assert_called_once()
        self.assertEqual(player_data["attack_exp"], 5.0)
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["xp"], [5.0])
        self.assertIn("+18 charges", calls["activity"][-1])
        self.assertIn(
            "utility:fist_of_guthix",
            player_data["action_telemetry"]["actions"],
        )

    def test_shooting_star_runtime_mines_one_dust_and_awards_layer_xp(self):
        from ankiscape.logic.shooting_star_logic import (
            advance_shooting_star_world_clock_pure,
            default_shooting_star_state_pure,
        )

        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = {
            "current_utility": "shooting_stars",
            "inventory": {},
            "toolbelt": {"mining": ["bronze_pickaxe"]},
            "equipment": {},
            "shop_market_clock": {"answered_cards": 20},
            "mining_level": 99,
            "mining_exp": 0.0,
            "completed_achievements": [],
            "world_population_profile": "normal",
            "shooting_star": default_shooting_star_state_pure(),
        }
        player_data, _ = advance_shooting_star_world_clock_pure(
            player_data
        )
        size = player_data["shooting_star"]["active_event"][
            "current_size"
        ]

        self.assertTrue(
            handle_utility_answer(
                _context(player_data, calls, random_values=(1.0, 0.0))
            )
        )

        self.assertEqual(player_data["inventory"]["Stardust"], 1)
        self.assertGreater(player_data["mining_exp"], 0)
        self.assertIn(f"Mined size {size} stardust", calls["activity"][-1])
        telemetry = player_data["action_telemetry"]["actions"][
            "mining:shooting_stars"
        ]
        self.assertEqual(telemetry["successes"], 1)
        self.assertEqual(telemetry["outputs"]["Stardust"], 1)

    def test_shooting_star_runtime_exits_unminable_layer_without_popup(self):
        from ankiscape.logic.shooting_star_logic import (
            advance_shooting_star_world_clock_pure,
            default_shooting_star_state_pure,
        )

        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = {
            "current_utility": "shooting_stars",
            "inventory": {},
            "toolbelt": {"mining": ["bronze_pickaxe"]},
            "equipment": {},
            "shop_market_clock": {"answered_cards": 20},
            "mining_level": 10,
            "mining_exp": 0.0,
            "completed_achievements": [],
            "shooting_star": default_shooting_star_state_pure(),
        }
        player_data, _ = advance_shooting_star_world_clock_pure(player_data)
        player_data["shooting_star"]["active_event"].update(
            {
                "starting_size": 9,
                "current_size": 9,
                "layer_remaining": 15,
                "tag_candidate": True,
                "crowd_dust_removed": 0,
            }
        )

        self.assertTrue(handle_utility_answer(_context(player_data, calls)))

        self.assertEqual(player_data["current_utility"], "bankstanding")
        self.assertTrue(calls["deactivated"])
        self.assertEqual(calls["activity"], [])
        self.assertEqual(calls["xp"], [750.0])
        self.assertEqual(player_data["mining_exp"], 750.0)
        self.assertEqual(player_data.get("review_event_log", []), [])
        self.assertEqual(len(calls["deactivation_reasons"]), 1)
        self.assertIn(
            "Star unminable at your level",
            calls["deactivation_reasons"][0],
        )

    def test_treasure_trail_routes_a_step_and_its_terminal_casket_through_utility(self):
        from ankiscape.logic.treasure_trails_logic import read_clue_scroll_pure

        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data, ok, _info = read_clue_scroll_pure(
            {
                "current_utility": "treasure_trail",
                "inventory": {"Clue scroll (easy)": 1},
                "equipment": {},
                "activity_session": {"active_id": ""},
                "completed_achievements": [],
            },
            "easy",
            lambda: 0.0,
        )
        self.assertTrue(ok)
        steps = len(player_data["treasure_trail"]["steps"])

        for _review in range(steps):
            self.assertTrue(handle_utility_answer(_context(player_data, calls)))

        self.assertEqual(player_data["inventory"]["Casket (easy)"], 1)
        self.assertNotIn("Clue scroll (easy)", player_data["inventory"])
        self.assertTrue(calls["deactivated"])
        self.assertIn(
            "utility:treasure_trail",
            player_data["action_telemetry"]["actions"],
        )

    def test_a_blocked_emote_step_is_recorded_as_a_failure_not_progress(self):
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = {
            "current_utility": "treasure_trail",
            "inventory": {"Clue scroll (easy)": 1},
            "equipment": {},
            "activity_session": {"active_id": "treasure_trail"},
            "completed_achievements": [],
            "treasure_trail": {
                "version": 1,
                "tier": "easy",
                "steps": ["emote_duel_arena_bow"],
                "index": 0,
            },
        }

        self.assertTrue(handle_utility_answer(_context(player_data, calls)))

        self.assertEqual(player_data["treasure_trail"]["index"], 0)
        self.assertNotIn("Casket (easy)", player_data["inventory"])
        telemetry = player_data["action_telemetry"]["actions"]["utility:treasure_trail"]
        self.assertEqual(telemetry["successes"], 0)

    def test_mining_a_real_ore_advances_the_matching_daily_challenge(self):
        """Daily Challenges accrue from ordinary gameplay, not their own rows."""
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = {
            "current_ore": "copper",
            "inventory": {},
            "toolbelt": {"mining": ["bronze_pickaxe"]},
            "equipment": {},
            "mining_level": 99,
            "mining_exp": 0.0,
            "completed_achievements": [],
            "daily_challenges": [
                {
                    "instance_id": "mining_copper_ore-1",
                    "challenge_id": "mining_copper_ore",
                    "day": 1,
                    "progress": 0,
                    "credited": {},
                }
            ],
        }

        self.assertTrue(
            handle_mining_answer(_context(player_data, calls, random_values=(0.0,) * 5))
        )

        instance = player_data["daily_challenges"][0]
        mined = player_data["inventory"]["Copper ore"]
        self.assertGreaterEqual(mined, 1, "the review must actually have mined something")
        self.assertEqual(instance["progress"], mined)
        self.assertEqual(instance["credited"], {"Copper ore": mined})

    def test_a_combat_kill_advances_a_rampage_challenge_at_the_named_level(self):
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = {
            "inventory": {},
            "equipment": {},
            "current_combat_target": "cow",
            "combat_lifepoints": 990,
            "constitution_level": 99,
            "completed_achievements": [],
            "daily_challenges": [
                {
                    "instance_id": "rampage_mk_i-1",
                    "challenge_id": "rampage_mk_i",
                    "day": 1,
                    "progress": 0,
                    "credited": {},
                }
            ],
        }
        result = {
            "target_id": "cow",
            "display_name": "Cow",
            "kills": 2,
            "died": False,
            "fled": False,
            "player_damage": 200,
            "enemy_lifepoints": 0,
            "drops": {},
            "xp_rewards": {},
        }

        with patch.object(
            runtime_actions_combat,
            "apply_combat_burst_pure",
            return_value=(dict(player_data), True, result),
        ):
            self.assertTrue(handle_combat_answer(_context(player_data, calls)))

        from ankiscape.data.combat_data import COMBAT_ENEMY_DATA

        self.assertGreaterEqual(COMBAT_ENEMY_DATA["cow"]["level"], 2)
        self.assertEqual(player_data["daily_challenges"][0]["progress"], 2)

    def test_combat_food_use_reports_eaten_quantity_and_remaining_pack(self):
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = {
            "inventory": {},
            "equipment": {},
            "current_combat_target": "cow",
            "combat_supply_loadout": {"food": {"Shrimps": 2}},
            "completed_achievements": [],
        }
        result = {
            "target_id": "cow",
            "display_name": "Cow",
            "kills": 0,
            "died": False,
            "fled": False,
            "player_damage": 0,
            "enemy_damage": 0,
            "enemy_lifepoints": 10,
            "drops": {},
            "xp_rewards": {},
            "food_used": (
                {"item": "Shrimps", "healed_by": 30},
                {"item": "Shrimps", "healed_by": 30},
            ),
        }

        with patch.object(
            runtime_actions_combat,
            "apply_combat_burst_pure",
            return_value=(dict(player_data), True, result),
        ):
            self.assertTrue(handle_combat_answer(_context(player_data, calls)))

        self.assertIn("Ate 2 × Shrimps · 2 left", calls["activity"])

    def test_star_sprite_bonus_adds_one_ore_and_stacks_with_mining(self):
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = {
            "current_ore": "copper",
            "inventory": {},
            "toolbelt": {"mining": ["bronze_pickaxe"]},
            "equipment": {},
            "mining_level": 99,
            "mining_exp": 0.0,
            "completed_achievements": [],
            "shooting_star": {"ore_bonus_ticks_remaining": 1_500},
        }

        self.assertTrue(
            handle_mining_answer(
                _context(
                    player_data,
                    calls,
                    random_values=(0.0, 0.0, 1.0, 0.0, 0.0),
                )
            )
        )

        self.assertEqual(player_data["inventory"]["Copper ore"], 2)
        self.assertIn(
            "Star sprite bonus: +1 Copper ore",
            calls["activity"][-1],
        )

    def test_big_chinchompa_runtime_groups_multiplier_into_whole_jars(self):
        from ankiscape.logic.big_chinchompa_logic import (
            advance_big_chinchompa_world_clock_pure,
            default_big_chinchompa_state_pure,
        )

        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = {
            "current_utility": "big_chinchompa",
            "inventory": {},
            "shop_market_clock": {"answered_cards": 60},
            "hunter_level": 1,
            "hunter_exp": 0.0,
            "completed_achievements": [],
            "world_population_profile": "quiet",
            "big_chinchompa": default_big_chinchompa_state_pure(),
        }
        player_data, _ = advance_big_chinchompa_world_clock_pure(player_data)

        self.assertTrue(
            handle_utility_answer(
                _context(
                    player_data,
                    calls,
                    review_action_multiplier=2,
                )
            )
        )

        event = player_data["big_chinchompa"]["active_event"]
        self.assertEqual(event["circuits_completed"], 2)
        self.assertEqual(event["event_points"], 30)
        self.assertAlmostEqual(player_data["hunter_exp"], 450.0)
        self.assertEqual(calls["xp"], [450.0])
        self.assertIn("Released 30 red soporith moths", calls["activity"][-1])
        telemetry = player_data["action_telemetry"]["actions"][
            "utility:big_chinchompa"
        ]
        self.assertEqual(telemetry["successes"], 1)

    def test_evil_tree_runtime_completes_three_review_phases(self):
        from ankiscape.logic.evil_tree_logic import (
            advance_evil_tree_world_clock_pure,
            default_evil_tree_state_pure,
        )

        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = {
            "current_utility": "evil_tree",
            "inventory": {},
            "toolbelt": {"woodcutting": ["bronze_hatchet"]},
            "shop_market_clock": {"answered_cards": 20},
            "woodcutting_level": 99,
            "farming_level": 99,
            "firemaking_level": 99,
            "woodcutting_exp": 0.0,
            "farming_exp": 0.0,
            "firemaking_exp": 0.0,
            "evil_tree": default_evil_tree_state_pure(),
        }
        player_data, _ = advance_evil_tree_world_clock_pure(player_data)

        self.assertTrue(handle_utility_answer(_context(player_data, calls)))
        self.assertEqual(player_data["evil_tree"]["session"]["phase"], "prepare")
        self.assertTrue(handle_utility_answer(_context(player_data, calls)))
        self.assertEqual(player_data["evil_tree"]["session"]["phase"], "fell")
        self.assertTrue(
            handle_utility_answer(
                _bankstanding_context(
                    player_data,
                    calls,
                    random_values=(0.0, 0.0, 0.0, 0.0),
                )
            )
        )

        self.assertEqual(player_data["current_utility"], "bankstanding")
        self.assertEqual(player_data["inventory"]["Logs"], 6)
        self.assertEqual(player_data["inventory"]["Coins"], 92)
        self.assertEqual(player_data["evil_tree"]["active_event"], {})
        self.assertEqual(calls["saves"], 3)
        self.assertEqual(calls["bankstanding"], 1)
        self.assertIn("Felled Normal evil tree", calls["activity"][-1])
        self.assertEqual(
            player_data["action_telemetry"]["actions"][
                "woodcutting:evil_tree_fell"
            ]["successes"],
            1,
        )

    def test_evil_tree_blessing_doubles_nest_roll_and_adds_one_continuation(self):
        from ankiscape.core.constants import BIRD_NEST_DROP_CHANCE

        player_data = {
            "inventory": {},
            "toolbelt": {"woodcutting": ["bronze_hatchet"]},
            "current_tree": "tree",
            "woodcutting_level": 99,
            "woodcutting_exp": 0.0,
            "evil_tree": {
                "blessing_reviews_remaining": 1,
                "blessing_tier": "normal",
            },
            "completed_achievements": [],
        }
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}

        self.assertTrue(
            handle_woodcutting_answer(
                _context(
                    player_data,
                    calls,
                    random_values=(
                        0.0,
                        BIRD_NEST_DROP_CHANCE * 1.5,
                        0.0,
                        0.0,
                        1.0,
                        0.0,
                    ),
                )
            )
        )

        self.assertEqual(player_data["inventory"]["Logs"], 2)
        self.assertEqual(player_data["inventory"]["Bird's nest (seeds)"], 1)
        self.assertIn("continuation chop succeeded", calls["activity"][-1])

    def test_evil_tree_full_pack_banks_overflow_without_starting_a_trip(self):
        player_data = {
            "inventory": {"Logs": 100},
            "current_tree": "tree",
            "woodcutting_level": 99,
            "agility_level": 1,
            "carried_inventory": {"tree": {"Logs": 28}},
            "carried_churn": {"tree": 28},
            "carried_keep_drop": {},
            "skilling_bank_run": {},
            "evil_tree": {"blessing_reviews_remaining": 2},
        }
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}

        def handler(ctx):
            ctx.player_data["inventory"]["Logs"] += 2
            return True

        with patch.object(
            runtime_actions_carried_overlay,
            "_admit_live_cadence",
            side_effect=lambda ctx, _handler_key, _target_id: (ctx, True),
        ):
            self.assertTrue(
                run_answer_with_carried_overlay(
                    _context(player_data, calls),
                    "woodcutting",
                    handler,
                )
            )

        self.assertEqual(player_data["carried_inventory"]["tree"], {"Logs": 28})
        self.assertEqual(player_data["carried_churn"]["tree"], 28)
        self.assertFalse(player_data["skilling_bank_run"])
        self.assertIn(
            "full-pack gains sent directly to the Bank",
            calls["activity"][-1],
        )

    def test_livid_farm_runtime_awards_all_cycle_skills_and_reports_progress(self):
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = {
            "current_utility": "livid_farm",
            "inventory": {
                "Astral rune": 1000,
                "Nature rune": 1000,
                "Law rune": 1000,
                "Earth rune": 1000,
                "Water rune": 1000,
            },
            "equipment": {},
            "quests": {"lunar_diplomacy": {"completed": True}},
            "magic_level": 99,
            "agility_level": 60,
            "crafting_level": 60,
            "farming_level": 60,
            "construction_level": 50,
            "magic_exp": 0.0,
            "agility_exp": 0.0,
            "crafting_exp": 0.0,
            "farming_exp": 0.0,
            "construction_exp": 0.0,
            "completed_achievements": [],
        }

        self.assertTrue(handle_utility_answer(_context(player_data, calls)))

        self.assertEqual(player_data["livid_farm"]["cycles_completed"], 1)
        self.assertEqual(player_data["livid_farm"]["produce_points"], 1580)
        self.assertAlmostEqual(player_data["magic_exp"], 3737.0)
        self.assertAlmostEqual(player_data["farming_exp"], 2754.0)
        self.assertAlmostEqual(player_data["construction_exp"], 546.0)
        self.assertAlmostEqual(player_data["crafting_exp"], 1080.0)
        self.assertAlmostEqual(player_data["agility_exp"], 509.1)
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertIn("1 cycle · +1,580 Produce", calls["activity"][0])
        telemetry = player_data["action_telemetry"]["actions"][
            "utility:livid_farm"
        ]
        self.assertEqual(telemetry["successes"], 1)

    def test_livid_farm_runtime_rejects_underfunded_review_atomically(self):
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = {
            "current_utility": "livid_farm",
            "inventory": {"Astral rune": 1},
            "equipment": {},
            "quests": {"lunar_diplomacy": {"completed": True}},
            "magic_level": 99,
            "agility_level": 60,
            "crafting_level": 60,
            "farming_level": 60,
            "construction_level": 50,
        }

        self.assertFalse(handle_utility_answer(_bankstanding_context(player_data, calls)))
        self.assertEqual(player_data["inventory"], {"Astral rune": 1})
        self.assertEqual(calls["bankstanding"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertIn("Astral rune", calls["bankstanding_reasons"][0])
        self.assertEqual(calls["saves"], 0)

    def test_wilderness_combat_requires_current_session_risk_confirmation(self):
        from ankiscape.data.combat_data import COMBAT_ENEMY_DATA
        from ankiscape.logic.combat_session import (
            confirm_wilderness_combat_risk,
            reset_wilderness_combat_confirmations,
            wilderness_combat_risk_fingerprint,
        )

        reset_wilderness_combat_confirmations()
        player_data = {
            "current_combat_target": "earth_warrior",
            "constitution_level": 99,
            "combat_lifepoints": 990,
            "equipment": {
                "weapon": "Rune sword",
                "body": "Rune platebody",
                "head": "Rune full helm",
                "shield": "Iron kiteshield",
            },
        }
        calls = {"xp": [], "saves": 0, "errors": []}

        self.assertFalse(handle_combat_answer(_context(player_data, calls)))
        self.assertTrue(calls["deactivated"])
        self.assertEqual(calls["errors"][0][0], "Wilderness confirmation required")

        fingerprint = wilderness_combat_risk_fingerprint(
            player_data,
            "earth_warrior",
            COMBAT_ENEMY_DATA["earth_warrior"],
        )
        confirm_wilderness_combat_risk(fingerprint)
        player_data["equipment"]["cape"] = "Cape"
        changed_calls = {"xp": [], "saves": 0, "errors": []}

        self.assertFalse(
            handle_combat_answer(_context(player_data, changed_calls))
        )
        self.assertEqual(
            changed_calls["errors"][0][0],
            "Wilderness confirmation required",
        )

    def test_green_dragon_runtime_feedback_reports_breath_damage(self):
        from ankiscape.data.combat_data import COMBAT_ENEMY_DATA
        from ankiscape.logic.combat_session import (
            confirm_wilderness_combat_risk,
            reset_wilderness_combat_confirmations,
            wilderness_combat_risk_fingerprint,
        )

        reset_wilderness_combat_confirmations()
        player_data = {
            "inventory": {},
            "equipment": {"shield": "Anti-dragon shield"},
            "current_combat_target": "green_dragon",
            "combat_lifepoints": 990,
            "constitution_level": 99,
            "slayer_level": 99,
            "completed_achievements": [],
        }
        confirm_wilderness_combat_risk(
            wilderness_combat_risk_fingerprint(
                player_data,
                "green_dragon",
                COMBAT_ENEMY_DATA["green_dragon"],
            )
        )
        result = {
            "target_id": "green_dragon",
            "display_name": "Green dragon",
            "kills": 0,
            "died": False,
            "fled": False,
            "player_damage": 120,
            "enemy_lifepoints": 630,
            "dragonfire_attacks": 2,
            "dragonfire_damage": 37,
            "drops": {},
            "xp_rewards": {},
        }
        calls = {"xp": [], "saves": 0, "errors": []}

        with patch.object(
            runtime_actions_combat,
            "apply_combat_burst_pure",
            return_value=(dict(player_data), True, result),
        ):
            ok = handle_combat_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertEqual(
            calls["activity"],
            [
                "Green dragon: 120 damage dealt, 630 LP left"
                " · 37 dragonfire LP from 2 breaths"
            ],
        )

    def test_summoning_handler_processes_one_source_recipe(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "current_summoning": "infuse_spiritwolf",
            "summoning_level": 99,
            "summoning_exp": 0.0,
            "inventory": {
                "Pouch": 1,
                "Spirit shards": 7,
                "Gold charm": 1,
                "Wolf bones": 1,
            },
            "completed_achievements": [],
        }

        self.assertTrue(handle_summoning_answer(_context(player_data, calls)))

        self.assertEqual(player_data["inventory"]["Spirit wolf pouch"], 1)
        self.assertEqual(player_data["summoning_exp"], 4.8)
        self.assertEqual(calls["xp"], [4.8])
        self.assertEqual(calls["saves"], 1)

    def test_brimhaven_ticket_is_cumulative_credit_without_double_adding_inventory(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "current_agility": "brimhaven_arena",
            "agility_level": 99,
            "agility_exp": 0.0,
            "inventory": {},
            "equipment": {},
            "completed_achievements": [],
            "agility_activity_state": {
                "brimhaven": {
                    "stint_active": True,
                    "activated": True,
                    "needs_chase": False,
                    "crossings_remaining": 1,
                    "attempts_remaining": 8,
                    "obstacle_id": "low_wall",
                    "obstacle_label": "Low wall",
                    "obstacle_xp": 8.0,
                    "obstacle_fail": 0.0,
                    "temporary_drain": 0,
                }
            },
        }

        self.assertTrue(
            handle_agility_answer(
                _context(player_data, calls, random_values=(0.0, 0.0, 0.5, 0.5))
            )
        )

        self.assertEqual(player_data["inventory"]["Agility arena ticket"], 1)
        self.assertEqual(
            player_data["achievement_progress"]["skills"]["agility"]["outputs"],
            {"Agility arena ticket": 1},
        )
        self.assertEqual(
            player_data["action_telemetry"]["actions"]["agility:low_wall"]["outputs"],
            {},
        )

    def test_fatal_agility_failure_deactivates_and_reports_shared_grave_death(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "current_agility": "wilderness_course",
            "agility_level": 53,
            "agility_exp": 0.0,
            "combat_lifepoints": 10,
            "hitpoints_level": 10,
            "inventory": {},
            "equipment": {"weapon": "Bronze sword"},
            "completed_achievements": [],
        }

        self.assertTrue(handle_agility_answer(_context(player_data, calls, random_values=(0.0, 0.5, 0.5, 0.5))))

        self.assertTrue(calls["deactivated"])
        self.assertEqual(player_data["combat_grave"]["items"], ["Bronze sword"])
        self.assertEqual(player_data["combat_grave"]["source"], "agility_failure")
        self.assertTrue(any("YOU DIED" in text for text in calls["activity"]))

    def test_brimhaven_death_click_walks_back_on_travel_clock_and_restores_loadout(self):
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data.update({
            "current_agility": "brimhaven_arena",
            "agility_level": 99,
            "combat_lifepoints": 20,
            "inventory": {"Shark": 1},
            "equipment": {"weapon": "Bronze sword", "shield": "Wooden shield"},
            "carried_inventory": {"brimhaven_arena": {"Shark": 1}},
            "agility_activity_state": {
                "brimhaven": {
                    "stint_active": True,
                    "activated": True,
                    "needs_chase": False,
                    "crossings_remaining": 1,
                    "attempts_remaining": 8,
                    "obstacle_id": "low_wall",
                    "obstacle_label": "Low wall",
                    "obstacle_xp": 8.0,
                    "obstacle_fail": 1.0,
                    "temporary_drain": 0,
                }
            },
        })

        self.assertTrue(
            handle_agility_answer(
                _context(player_data, calls, random_values=(0.0, 0.0, 0.0, 0.0))
            )
        )
        self.assertTrue(any("YOU DIED" in text for text in calls["activity"]))
        self.assertTrue(any("Training stopped" in text and "Gravestone banner" in text for text in calls["activity"]))
        self.assertCountEqual(
            player_data["combat_grave"]["items"],
            ["Bronze sword", "Wooden shield", "Shark"],
        )

        from ankiscape.logic_pure.logic_pure import (
            combat_grave_banner_view_pure,
            start_combat_grave_walk_pure,
        )

        player_data["combat_encounter"] = {
            "target_id": "giant_rat",
            "enemy_lifepoints": 50,
        }
        before_expiry = player_data["combat_grave"]["reviews_remaining"]
        runtime_actions.advance_shared_review_state_for_review(
            _context(player_data, calls, random_values=(0.5,))
        )
        self.assertEqual(
            player_data["combat_grave"]["reviews_remaining"],
            before_expiry - 1,
        )
        self.assertIn("expires after 1 more reviews", combat_grave_banner_view_pure(player_data)["text"])

        started, ok = start_combat_grave_walk_pure(player_data)
        self.assertTrue(ok)
        player_data.clear()
        player_data.update(started)
        runtime_actions.advance_shared_review_state_for_review(
            _context(player_data, calls, random_values=(0.5,))
        )

        self.assertEqual(player_data["combat_grave"], {})
        self.assertEqual(
            player_data["equipment"],
            {"weapon": "Bronze sword", "shield": "Wooden shield"},
        )
        self.assertEqual(player_data["inventory"]["Shark"], 1)

    def test_agility_danger_auto_stop_uses_target_maximum_and_toggle_disables_it(self):
        def brimhaven_player(enabled):
            player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
            player.update({
                "current_agility": "brimhaven_arena",
                "agility_level": 99,
                "combat_lifepoints": 70,
                "inventory": {},
                "equipment": {},
                "activity_auto_stop_on_danger": enabled,
                "agility_activity_state": {
                    "brimhaven": {
                        "stint_active": True,
                        "activated": True,
                        "needs_chase": False,
                        "crossings_remaining": 1,
                        "attempts_remaining": 8,
                        "obstacle_id": "low_wall",
                        "obstacle_label": "Low wall",
                        "obstacle_xp": 8.0,
                        "obstacle_fail": 1.0,
                        "temporary_drain": 0,
                    }
                },
            })
            return player

        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        protected = brimhaven_player(True)
        self.assertTrue(
            handle_agility_answer(
                _context(protected, calls, random_values=(0.0, 0.0, 0.0, 0.0))
            )
        )
        self.assertEqual(protected["combat_lifepoints"], 50)
        self.assertTrue(calls["deactivated"])
        self.assertTrue(any("Safety stop" in text and "60 LP" in text for text in calls["activity"]))

        disabled_calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        unprotected = brimhaven_player(False)
        self.assertTrue(
            handle_agility_answer(
                _context(unprotected, disabled_calls, random_values=(0.0, 0.0, 0.0, 0.0))
            )
        )
        self.assertEqual(unprotected["combat_lifepoints"], 50)
        self.assertNotIn("deactivated", disabled_calls)
        self.assertFalse(any("Safety stop" in text for text in disabled_calls["activity"]))

    def test_agility_auto_pack_carries_food_and_auto_eats_from_that_pack(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "current_agility": "wilderness_course",
            "agility_level": 53,
            "agility_exp": 0.0,
            "combat_lifepoints": 20,
            "hitpoints_level": 10,
            "combat_auto_eat_threshold_percent": 40,
            "combat_auto_eat_food": ["Shark"],
            "inventory": {"Shark": 2},
            "equipment": {},
            "completed_achievements": [],
        }

        self.assertTrue(
            run_answer_with_carried_overlay(
                _context(player_data, calls, random_values=(0.0, 0.5, 0.5, 0.5)),
                "agility",
                handle_agility_answer,
            )
        )

        self.assertEqual(player_data["inventory"], {"Shark": 1})
        self.assertEqual(player_data["carried_inventory"]["wilderness_course"], {"Shark": 1})
        self.assertEqual(player_data["combat_lifepoints"], 100)
        self.assertTrue(any("Auto-ate Shark" in text for text in calls["activity"]))

    def test_agility_auto_pack_does_not_refill_for_food_beyond_the_28_slot_projection(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "current_agility": "wilderness_course",
            "agility_level": 99,
            "agility_exp": 0.0,
            "combat_lifepoints": 1000,
            "combat_auto_eat_food": ["Shark", "Lobster"],
            "inventory": {"Shark": 100, "Lobster": 100},
            "equipment": {},
            "completed_achievements": [],
        }

        self.assertTrue(
            run_answer_with_carried_overlay(
                _context(player_data, calls, random_values=(0.99, 0.99, 0.99, 0.99)),
                "agility",
                handle_agility_answer,
            )
        )

        self.assertEqual(player_data["carried_inventory"]["wilderness_course"], {"Shark": 28})
        self.assertNotIn("agility_last_travel", player_data)
        self.assertEqual(player_data["agility_exp"], 15.0)

    def test_depleted_agility_food_costs_a_review_to_repack_from_the_bank(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "current_agility": "wilderness_course",
            "agility_level": 53,
            "agility_exp": 0.0,
            "combat_lifepoints": 1000,
            "combat_auto_eat_food": ["Shark"],
            "inventory": {"Shark": 72},
            "equipment": {},
            "completed_achievements": [],
            "carried_primed_targets": {"wilderness_course": True},
            "carried_inventory": {},
        }

        self.assertTrue(
            run_answer_with_carried_overlay(
                _context(player_data, calls, random_values=(0.5,)),
                "agility",
                handle_agility_answer,
            )
        )

        self.assertEqual(player_data["agility_exp"], 0.0)
        self.assertEqual(player_data["carried_inventory"]["wilderness_course"], {"Shark": 28})
        self.assertTrue(any("arrived and restocked" in text for text in calls["activity"]))

    def test_agility_custom_pack_does_not_fall_back_to_bank_for_course_requirements(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "current_agility": "werewolf_course",
            "agility_level": 99,
            "strength_level": 99,
            "agility_exp": 0.0,
            "inventory": {"Ring of charos": 1, "Shark": 27},
            "equipment": {},
            "quests": {"creature_of_fenkenstrain": {"completed": True}},
            "completed_achievements": [],
            "carried_advanced_targets": {"werewolf_course": True},
            "carried_layout": {"werewolf_course": {"Shark": 27}},
        }

        self.assertFalse(
            run_answer_with_carried_overlay(
                _context(player_data, calls, random_values=(0.99, 0.5, 0.5, 0.5)),
                "agility",
                handle_agility_answer,
            )
        )

        self.assertTrue(calls["deactivated"])
        self.assertIn("Ring of charos", calls["errors"][0][1])
        self.assertEqual(player_data["agility_exp"], 0.0)

    def test_fatal_agility_failure_graves_only_the_active_pack_and_equipment(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "current_agility": "wilderness_course",
            "agility_level": 53,
            "agility_exp": 0.0,
            "combat_lifepoints": 10,
            "hitpoints_level": 10,
            "combat_auto_eat_threshold_percent": 40,
            "combat_auto_eat_food": ["Shark"],
            "inventory": {"Shark": 1, "Logs": 4},
            "equipment": {"weapon": "Bronze sword"},
            "completed_achievements": [],
            "carried_inventory": {"logs": {"Logs": 4}},
        }

        self.assertTrue(
            run_answer_with_carried_overlay(
                _context(player_data, calls, random_values=(0.0, 0.5, 0.5, 0.5)),
                "agility",
                handle_agility_answer,
            )
        )

        self.assertCountEqual(player_data["combat_grave"]["items"], ["Bronze sword", "Shark"])
        self.assertEqual(player_data["combat_grave"]["source"], "agility_failure")
        self.assertEqual(player_data["carried_inventory"], {"logs": {"Logs": 4}})
        self.assertEqual(player_data["inventory"], {"Shark": 0, "Logs": 4})
        self.assertEqual(player_data["equipment"], {})

    def test_fatal_wilderness_lap_ambush_forfeits_uncommitted_lap_reward(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "current_agility": "wilderness_course",
            "agility_level": 99,
            "agility_exp": 0.0,
            "combat_lifepoints": 100,
            "hitpoints_level": 10,
            "combat_auto_eat_food": ["Shark"],
            "inventory": {},
            "equipment": {"weapon": "Bronze sword"},
            "completed_achievements": [],
            "agility_lap_counts": {
                "total": 0,
                "flawless": 0,
                "gnome_advanced_flawless": 0,
                "barbarian_advanced_flawless": 0,
                "agile_legs_unlocked": False,
                "agile_top_unlocked": False,
            },
            "agility_course_state": {
                "target": "wilderness_course",
                "stage": 5,
                "checkpoint": "start",
                "flawless": True,
                "lap_xp_valid": True,
                "requested_item_valid": True,
                "status": "",
            },
            "agility_pit_offer": False,
        }

        self.assertTrue(
            run_answer_with_carried_overlay(
                _context(player_data, calls, random_values=(0.99, 0.0, 0.005, 0.90)),
                "agility",
                handle_agility_answer,
            )
        )

        self.assertEqual(player_data["agility_exp"], 0.0)
        self.assertEqual(player_data["agility_lap_counts"]["total"], 0)
        self.assertFalse(player_data["agility_pit_offer"])
        self.assertEqual(player_data["agility_course_state"]["stage"], 0)
        self.assertEqual(player_data["combat_grave"]["source"], "agility_wilderness_pker")
        self.assertEqual(player_data["combat_grave"]["items"], ["Bronze sword"])
        self.assertNotIn("Bronze sword", player_data["inventory"])
        self.assertEqual(player_data["current_agility"], "wilderness_course")
        self.assertEqual(calls["xp"], [])
        self.assertIn("died before the lap reward", calls["activity"][0])

    def test_barehanded_butterfly_awards_atomic_hunter_and_agility_xp_without_an_item(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "hunter_level": 80,
            "hunter_exp": 0.0,
            "agility_level": 75,
            "agility_exp": 0.0,
            "current_hunter": "barehand_ruby_harvest",
            "completed_achievements": [],
        }

        self.assertTrue(handle_hunter_answer(_context(player_data, calls, random_values=(0.0,))))

        self.assertEqual(player_data["inventory"], {})
        self.assertEqual(player_data["hunter_exp"], 300.0)
        self.assertEqual(player_data["agility_exp"], 50.0)
        self.assertEqual(calls["xp"], [300.0])

    def test_agility_double_catch_adds_one_shark_without_extra_fishing_xp(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "fishing_level": 99,
            "fishing_exp": 0.0,
            "agility_level": 76,
            "current_fishing": "catch_sharks",
            "completed_achievements": [],
        }

        self.assertTrue(handle_fishing_answer(_context(player_data, calls, random_values=(0.0, 0.0))))

        self.assertEqual(player_data["inventory"], {"Raw shark": 2})
        self.assertEqual(player_data["fishing_exp"], 110.0)
        self.assertEqual(calls["xp"], [110.0])
        telemetry = player_data["action_telemetry"]["actions"]["fishing:catch_sharks"]
        self.assertEqual(telemetry["outputs"], {"Raw shark": 2})

    def test_full_fishing_outfit_applies_its_source_five_percent_xp_bonus(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "equipment": {
                "head": "Fishing hat",
                "body": "Fishing jacket",
                "legs": "Fishing waders",
                "feet": "Fishing boots",
            },
            "fishing_level": 99,
            "fishing_exp": 0.0,
            "agility_level": 1,
            "current_fishing": "catch_sharks",
            "completed_achievements": [],
        }

        self.assertTrue(
            handle_fishing_answer(
                _context(player_data, calls, random_values=(0.0,))
            )
        )

        self.assertAlmostEqual(player_data["fishing_exp"], 115.5)
        self.assertEqual(calls["xp"], [115.5])

    def test_cave_eel_review_consumes_bait_and_awards_period_xp(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Fishing bait": 1},
            "fishing_level": 38,
            "fishing_exp": 0.0,
            "agility_level": 1,
            "current_fishing": "catch_cave_eel",
            "completed_achievements": [],
        }

        self.assertTrue(
            handle_fishing_answer(
                _context(player_data, calls, random_values=(1.0, 0.0))
            )
        )

        self.assertEqual(player_data["inventory"]["Fishing bait"], 0)
        self.assertEqual(player_data["inventory"]["Raw cave eel"], 1)
        self.assertEqual(player_data["fishing_exp"], 80.0)
        self.assertEqual(calls["xp"], [80.0])

    def test_level_one_player_can_clean_guam_without_druidic_ritual(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Grimy guam": 1},
            "herblore_level": 1,
            "herblore_exp": 0.0,
            "current_herblore": "clean_guam",
            "quests": {"druidic_ritual": {"started": False, "progress": 0, "completed": False}},
            "completed_achievements": [],
        }

        self.assertTrue(handle_herblore_answer(_context(player_data, calls)))

        self.assertEqual(player_data["inventory"], {"Grimy guam": 0, "Clean guam": 1})
        self.assertEqual(player_data["herblore_exp"], 2.5)
        self.assertEqual(calls["xp"], [2.5])

    def test_overload_handler_records_primary_output_and_four_vials(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        inputs = {
            "Extreme attack (3)": 1,
            "Extreme strength (3)": 1,
            "Extreme defence (3)": 1,
            "Extreme magic (3)": 1,
            "Extreme ranging (3)": 1,
            "Clean torstol": 1,
        }
        player_data = {
            "inventory": inputs,
            "herblore_level": 96,
            "herblore_exp": 0.0,
            "current_herblore": "finished_overload",
            "completed_achievements": [],
        }

        self.assertTrue(handle_herblore_answer(_context(player_data, calls)))

        self.assertEqual(player_data["inventory"]["Overload (3)"], 1)
        self.assertEqual(player_data["inventory"]["Vial"], 4)
        self.assertEqual(player_data["herblore_exp"], 1000.0)
        telemetry = player_data["action_telemetry"]["actions"]["herblore:finished_overload"]
        self.assertEqual(telemetry["outputs"], {"Overload (3)": 1, "Vial": 4})
        self.assertEqual(calls["xp"], [1000.0])

    def test_super_prayer_recipe_consumes_only_wyvern_bonemeal(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {
                "Prayer potion (3)": 1,
                "Wyvern bonemeal": 1,
                "Bonemeal": 7,
            },
            "herblore_level": 94,
            "herblore_exp": 0.0,
            "current_herblore": "finished_super_prayer",
            "completed_achievements": [],
        }

        self.assertTrue(handle_herblore_answer(_context(player_data, calls)))

        self.assertEqual(player_data["inventory"]["Prayer potion (3)"], 0)
        self.assertEqual(player_data["inventory"]["Wyvern bonemeal"], 0)
        self.assertEqual(player_data["inventory"]["Bonemeal"], 7)
        self.assertEqual(player_data["inventory"]["Super prayer (3)"], 1)
        self.assertEqual(player_data["herblore_exp"], 270.0)
        telemetry = player_data["action_telemetry"]["actions"]["herblore:finished_super_prayer"]
        self.assertEqual(telemetry["outputs"], {"Super prayer (3)": 1})
        self.assertEqual(calls["xp"], [270.0])

    def test_shrink_me_quick_handler_consumes_period_recipe_and_records_output(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {
                "Tarromin potion (unf)": 1,
                "Shrunk ogleroot": 1,
            },
            "herblore_level": 52,
            "herblore_exp": 0.0,
            "current_herblore": "finished_shrink_me_quick",
            "completed_achievements": [],
        }

        self.assertTrue(handle_herblore_answer(_context(player_data, calls)))

        self.assertEqual(
            player_data["inventory"],
            {
                "Tarromin potion (unf)": 0,
                "Shrunk ogleroot": 0,
                "Shrink-me-quick": 1,
            },
        )
        self.assertEqual(player_data["herblore_exp"], 6.0)
        telemetry = player_data["action_telemetry"]["actions"][
            "herblore:finished_shrink_me_quick"
        ]
        self.assertEqual(telemetry["outputs"], {"Shrink-me-quick": 1})
        self.assertEqual(calls["xp"], [6.0])

    def test_woodcutting_inferno_adze_incinerates_logs_for_firemaking_xp(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "toolbelt": {"woodcutting": ["inferno_adze"]},
            "woodcutting_level": 99,
            "woodcutting_exp": 0.0,
            "firemaking_exp": 0.0,
            "current_tree": "tree",
            "completed_achievements": [],
        }

        ok = handle_woodcutting_answer(_context(player_data, calls, random_values=(0.0, 1.0, 0.0, 0.0)))

        self.assertTrue(ok)
        self.assertNotIn("Logs", player_data["inventory"])
        self.assertEqual(player_data["woodcutting_exp"], 25.0)
        self.assertEqual(player_data["firemaking_exp"], 25.0)
        self.assertEqual(calls["level_checks"], ["Woodcutting", "Firemaking"])

    def test_woodcutting_incineration_credits_every_declared_output_unit(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "toolbelt": {"woodcutting": ["inferno_adze"]},
            "woodcutting_level": 99,
            "woodcutting_exp": 0.0,
            "firemaking_exp": 0.0,
            "current_tree": "curly_jade_root",
            "completed_achievements": [],
        }

        self.assertTrue(
            handle_woodcutting_answer(
                _context(player_data, calls, random_values=(0.0, 1.0, 0.0, 0.0))
            )
        )
        self.assertNotIn("Curly root", player_data["inventory"])
        self.assertEqual(
            player_data["achievement_progress"]["skills"]["woodcutting"]["outputs"],
            {"Curly root": 4},
        )

    def test_arctic_pine_runtime_enforces_the_route_gate_then_awards_the_log(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "toolbelt": {"woodcutting": ["rune_hatchet"]},
            "woodcutting_level": 99,
            "woodcutting_exp": 0.0,
            "current_tree": "arctic_pine",
            "quests": {},
            "completed_achievements": [],
        }

        self.assertFalse(handle_woodcutting_answer(_context(player_data, calls)))
        self.assertTrue(calls["deactivated"])
        self.assertIn("Start The Fremennik Isles", calls["errors"][0][1])
        self.assertEqual(player_data["inventory"], {})

        player_data["quests"] = {"the_fremennik_isles": {"started": True}}
        calls = {"xp": [], "saves": 0, "errors": []}
        self.assertTrue(
            handle_woodcutting_answer(
                _context(player_data, calls, random_values=(0.0, 1.0, 0.0))
            )
        )
        self.assertEqual(player_data["inventory"], {"Arctic pine logs": 1})
        self.assertEqual(player_data["woodcutting_exp"], 140.2)
        self.assertEqual(calls["xp"], [140.2])

    def test_eucalyptus_runtime_uses_the_safe_ungated_target(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "toolbelt": {"woodcutting": ["rune_hatchet"]},
            "woodcutting_level": 99,
            "woodcutting_exp": 0.0,
            "current_tree": "eucalyptus",
            "completed_achievements": [],
        }

        self.assertTrue(
            handle_woodcutting_answer(
                _context(player_data, calls, random_values=(0.0, 1.0, 0.0))
            )
        )
        self.assertEqual(player_data["inventory"], {"Eucalyptus logs": 1})
        self.assertEqual(player_data["woodcutting_exp"], 165.0)
        self.assertEqual(calls["errors"], [])

    def test_curly_root_route_mutates_real_woodcutting_and_firemaking_kernels(self):
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data.update(
            {
                "toolbelt": {"woodcutting": ["rune_hatchet"]},
                "woodcutting_level": 83,
                "woodcutting_exp": 0.0,
                "current_tree": "curly_jade_root",
                "firemaking_level": 75,
                "firemaking_exp": 0.0,
                "current_firemaking": "curly_root",
            }
        )

        self.assertTrue(
            handle_woodcutting_answer(
                _context(
                    player_data,
                    calls,
                    random_values=(0.0, 1.0, 0.0, 1.0),
                )
            )
        )
        self.assertEqual(player_data["inventory"]["Curly root"], 4)
        self.assertEqual(player_data["woodcutting_exp"], 161.6)
        woodcutting_telemetry = player_data["action_telemetry"]["actions"][
            "woodcutting:curly_jade_root"
        ]
        self.assertEqual(woodcutting_telemetry["outputs"], {"Curly root": 4})

        self.assertTrue(
            handle_firemaking_answer(
                _context(player_data, calls, random_values=(0.0, 1.0))
            )
        )
        self.assertEqual(player_data["inventory"]["Curly root"], 3)
        self.assertEqual(player_data["inventory"]["Ashes"], 1)
        self.assertEqual(player_data["firemaking_exp"], 161.6)
        self.assertEqual(calls["errors"], [])

    def test_fletching_handler_mutates_player_data_through_context(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Logs": 1},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
        }

        ok = handle_fletching_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"]["Logs"], 0)
        self.assertEqual(player_data["inventory"]["Arrow shafts"], 15)
        self.assertAlmostEqual(player_data["fletching_exp"], 5.0)
        telemetry = player_data["action_telemetry"]["actions"]["fletching:arrow_shafts"]
        self.assertEqual(telemetry["attempts"], 1)
        self.assertEqual(telemetry["successes"], 1)
        self.assertEqual(telemetry["outputs"], {"Arrow shafts": 15})
        self.assertAlmostEqual(telemetry["expected_successes"], 1.0)
        self.assertEqual(calls["xp"], [5.0])
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])

    def test_fletching_handler_makes_six_long_kebbit_bolts_and_keeps_chisel(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Long kebbit spike": 1, "Chisel": 1},
            "fletching_level": 42,
            "fletching_exp": 0,
            "current_fletch": "fletch_long_kebbit_bolts",
            "completed_achievements": [],
        }

        ok = handle_fletching_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"]["Long kebbit spike"], 0)
        self.assertEqual(player_data["inventory"]["Chisel"], 1)
        self.assertEqual(player_data["inventory"]["Long kebbit bolts"], 6)
        self.assertAlmostEqual(player_data["fletching_exp"], 7.98)
        self.assertEqual(calls["xp"], [7.98])
        self.assertEqual(calls["errors"], [])

    def test_fletching_handler_and_carried_overlay_consume_selected_coloured_feathers(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Arrow shafts": 30, "Feather": 30, "Blue feather": 30},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "headless_arrows",
            "completed_achievements": [],
            "carried_advanced_targets": {"headless_arrows": True},
            "carried_layout": {"headless_arrows": {"Arrow shafts": 15, "Blue feather": 15}},
        }

        ok = run_answer_with_carried_overlay(
            _context(player_data, calls),
            "fletching",
            handle_fletching_answer,
        )

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"]["Arrow shafts"], 15)
        self.assertEqual(player_data["inventory"]["Feather"], 30)
        self.assertEqual(player_data["inventory"]["Blue feather"], 15)
        self.assertEqual(player_data["inventory"]["Headless arrows"], 15)
        self.assertNotIn("headless_arrows", player_data["carried_inventory"])
        self.assertAlmostEqual(player_data["fletching_exp"], 15.0)
        self.assertNotIn("activity", calls)
        self.assertEqual(player_data["skilling_bank_run"], {})

    def test_crafting_handler_and_carried_overlay_reconcile_thread_consumption(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Leather": 1, "Thread": 1},
            "crafting_level": 1,
            "crafting_exp": 0,
            "current_craft": "leather_leather_gloves",
            "completed_achievements": [],
            "carried_advanced_targets": {"leather_leather_gloves": True},
            "carried_layout": {"leather_leather_gloves": {"Leather": 1, "Thread": 1}},
        }

        ok = run_answer_with_carried_overlay(
            _context(player_data, calls, random_values=(0.0,)),
            "crafting",
            handle_crafting_answer,
        )

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"], {"Leather": 0, "Thread": 0, "Leather gloves": 1})
        self.assertNotIn("leather_leather_gloves", player_data["carried_inventory"])
        self.assertAlmostEqual(player_data["crafting_exp"], 13.8)
        self.assertEqual(calls["errors"], [])

    def test_runecrafting_tablet_skips_only_the_outbound_runecrafting_phase(self):
        from ankiscape.core import constants
        from ankiscape.logic.great_orb_project_logic import (
            use_great_orb_project_teleport_tablet_pure,
        )

        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Rune essence": 56, "Air altar teleport": 1},
            "equipment": {"head": "Master runecrafter hat"},
            "current_runecrafting": "craft_air_runes",
            "runecrafting_level": 1,
            "agility_level": 1,
            "carried_inventory": {"craft_air_runes": {"Rune essence": 28}},
            "carried_churn": {"craft_air_runes": 28},
            "carried_primed_targets": {"craft_air_runes": True},
            "skilling_bank_run": {},
            "shop_market_clock": {"answered_cards": 0},
        }
        player_data, used, info = use_great_orb_project_teleport_tablet_pure(
            player_data,
            "Air altar teleport",
            constants.EQUIPMENT_DATA,
            constants.QUEST_UNLOCK_RULES,
        )
        self.assertTrue(used, info)
        self.assertNotIn("Air altar teleport", player_data["inventory"])
        acted = []

        self.assertTrue(
            run_answer_with_carried_overlay(
                _context(player_data, calls),
                "runecrafting",
                lambda _ctx: acted.append(True) or True,
            )
        )

        self.assertEqual(acted, [])
        self.assertEqual(player_data["wicked_hood"]["pending_altar_teleport"], "")
        run = player_data["skilling_bank_run"]
        self.assertEqual(run["reviews_total"], 10)
        self.assertEqual(run["reviews_remaining"], 9)
        self.assertEqual(
            [phase["id"] for phase in run["route_phases"]],
            ["return", "bank"],
        )
        self.assertTrue(run["outbound_teleport_used"])
        travel = player_data["agility_last_travel"]
        self.assertEqual(travel["scheduled_reviews"], 20)
        self.assertEqual(travel["charged_reviews"], 10)
        self.assertTrue(travel["outbound_teleport_used"])

    def test_wicked_hood_teleport_finishes_an_already_outbound_route(self):
        from ankiscape.logic.wicked_hood_logic import (
            default_wicked_hood_state_pure,
            runecrafting_route_phases_pure,
        )

        calls = {"xp": [], "saves": 0, "errors": []}
        hood = default_wicked_hood_state_pure()
        hood["fed_altars"] = ["air"]
        hood["pending_altar_teleport"] = "air"
        player_data = {
            "inventory": {"Rune essence": 56},
            "equipment": {"head": "Wicked hood"},
            "current_runecrafting": "craft_air_runes",
            "runecrafting_level": 1,
            "agility_level": 1,
            "carried_inventory": {"craft_air_runes": {}},
            "carried_churn": {"craft_air_runes": 28},
            "carried_primed_targets": {"craft_air_runes": True},
            "skilling_bank_run": {
                "target_id": "craft_air_runes",
                "reviews_total": 20,
                "reviews_remaining": 5,
                "route_label": "Running to the Air altar",
                "route_phases": list(runecrafting_route_phases_pure(20)),
            },
            "wicked_hood": hood,
            "shop_market_clock": {"answered_cards": 0},
        }
        acted = []

        self.assertTrue(
            run_answer_with_carried_overlay(
                _context(player_data, calls),
                "runecrafting",
                lambda _ctx: acted.append(True) or True,
            )
        )

        self.assertEqual(acted, [True])
        self.assertEqual(player_data["wicked_hood"]["pending_altar_teleport"], "")
        self.assertEqual(player_data["skilling_bank_run"], {})
        self.assertEqual(
            player_data["carried_inventory"]["craft_air_runes"]["Rune essence"],
            28,
        )

    def test_crafting_carried_overlay_requires_and_retains_mould(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Gold bar": 1, "Ring mould": 1},
            "crafting_level": 5,
            "crafting_exp": 0,
            "current_craft": "jewellery_gold_ring",
            "completed_achievements": [],
            "carried_advanced_targets": {"jewellery_gold_ring": True},
            "carried_layout": {"jewellery_gold_ring": {"Gold bar": 1, "Ring mould": 1}},
        }
        self.assertTrue(run_answer_with_carried_overlay(
            _context(player_data, calls), "crafting", handle_crafting_answer
        ))
        self.assertEqual(player_data["inventory"], {"Gold bar": 0, "Ring mould": 1, "Gold ring": 1})
        self.assertEqual(player_data["carried_inventory"]["jewellery_gold_ring"], {"Ring mould": 1})
        self.assertAlmostEqual(player_data["crafting_exp"], 15.0)

    def test_cannonball_advanced_pack_carries_and_retains_ammo_mould(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Steel bar": 1, "Ammo mould": 1},
            "smithing_level": 35,
            "smithing_exp": 0.0,
            "crafting_level": 1,
            "current_smith": "forge_cannonballs",
            "quests": {"dwarf_cannon": {"completed": True}},
            "completed_achievements": [],
            "carried_advanced_targets": {"forge_cannonballs": True},
            "carried_layout": {"forge_cannonballs": {"Steel bar": 1, "Ammo mould": 1}},
        }
        ctx = _context(player_data, calls)

        self.assertTrue(run_answer_with_carried_overlay(ctx, "smithing", handle_smithing_answer))

        self.assertEqual(player_data["inventory"], {"Steel bar": 0, "Ammo mould": 1, "Cannonball": 4})
        self.assertEqual(player_data["carried_inventory"]["forge_cannonballs"], {"Ammo mould": 1})
        self.assertAlmostEqual(player_data["smithing_exp"], 25.6)
        self.assertEqual(calls["errors"], [])

    def test_unfired_clay_ring_carried_overlay_reconciles_and_retains_mould(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Soft clay": 1, "Ring mould": 1},
            "crafting_level": 4,
            "crafting_exp": 0,
            "current_craft": "form_clay_ring_unfired",
            "completed_achievements": [],
            "carried_advanced_targets": {"form_clay_ring_unfired": True},
            "carried_layout": {"form_clay_ring_unfired": {"Soft clay": 1, "Ring mould": 1}},
        }

        self.assertTrue(run_answer_with_carried_overlay(
            _context(player_data, calls), "crafting", handle_crafting_answer
        ))
        self.assertEqual(
            player_data["inventory"], {"Soft clay": 0, "Ring mould": 1, "Clay ring (unfired)": 1}
        )
        self.assertEqual(player_data["carried_inventory"]["form_clay_ring_unfired"], {"Ring mould": 1})
        self.assertAlmostEqual(player_data["crafting_exp"], 11.3)
        self.assertEqual(calls["errors"], [])

    def test_crafting_carried_overlay_retains_one_thread_across_leather_actions(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Leather": 27, "Thread": 1},
            "crafting_level": 1,
            "crafting_exp": 0,
            "current_craft": "leather_leather_gloves",
            "completed_achievements": [],
            "carried_advanced_targets": {"leather_leather_gloves": True},
            "carried_layout": {"leather_leather_gloves": {"Leather": 27, "Thread": 1}},
        }
        ctx = _context(player_data, calls, random_values=(0.2, 0.2))

        self.assertTrue(run_answer_with_carried_overlay(ctx, "crafting", handle_crafting_answer))
        self.assertEqual(player_data["carried_inventory"]["leather_leather_gloves"], {"Leather": 26, "Thread": 1})
        self.assertTrue(run_answer_with_carried_overlay(ctx, "crafting", handle_crafting_answer))

        self.assertEqual(player_data["inventory"], {"Leather": 25, "Thread": 1, "Leather gloves": 2})
        self.assertEqual(player_data["carried_inventory"]["leather_leather_gloves"], {"Leather": 25, "Thread": 1})
        self.assertNotIn("activity", calls)
        self.assertEqual(calls["errors"], [])

    def test_crafting_advanced_layout_refills_consumed_thread_from_bank_before_resuming(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Leather": 27, "Thread": 5},
            "crafting_level": 1,
            "crafting_exp": 0,
            "current_craft": "leather_leather_gloves",
            "completed_achievements": [],
            "carried_advanced_targets": {"leather_leather_gloves": True},
            "carried_layout": {"leather_leather_gloves": {"Leather": 27, "Thread": 1}},
        }
        ctx = _context(player_data, calls, random_values=(0.0, 0.2))

        # The first source roll consumes the carried Thread. Crafting is a
        # stationary bank method, so the next review repacks and crafts in one
        # atomic action instead of inventing a movement review.
        self.assertTrue(run_answer_with_carried_overlay(ctx, "crafting", handle_crafting_answer))
        self.assertEqual(player_data["inventory"], {"Leather": 26, "Thread": 4, "Leather gloves": 1})
        self.assertEqual(player_data["carried_inventory"]["leather_leather_gloves"], {"Leather": 26})
        self.assertTrue(run_answer_with_carried_overlay(ctx, "crafting", handle_crafting_answer))
        self.assertEqual(player_data["inventory"], {"Leather": 25, "Thread": 4, "Leather gloves": 2})
        self.assertEqual(player_data["carried_inventory"]["leather_leather_gloves"], {"Leather": 25, "Thread": 1})
        self.assertAlmostEqual(player_data["crafting_exp"], 27.6)
        self.assertEqual(calls["xp"], [13.8, 13.8])
        self.assertNotIn("activity", calls)
        self.assertNotIn("deactivated", calls)
        self.assertEqual(calls["errors"], [])

    def test_combat_full_loot_pack_forces_a_bank_run_that_deposits_it(self):
        # A full carried loot pack (28 slots) forces a bank run: the answer banks
        # instead of fighting, the loot is deposited (view cleared, but the items
        # stay in the flat inventory), and no kill happens this answer.
        full_loot = {f"Trophy {i}": 1 for i in range(28)}
        player_data = {
            "inventory": dict(full_loot),
            "equipment": {},
            "current_combat_target": "chicken",
            "combat_attack_style": "accurate",
            "combat_lifepoints": 100,
            "combat_auto_eat_food": ["Shrimps"],
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 10,
            "attack_exp": 0.0,
            "constitution_exp": 0.0,
            "carried_inventory": {"chicken": dict(full_loot)},
            "completed_achievements": [],
        }
        calls = {"xp": [], "saves": 0, "errors": []}
        # The combat bank run costs two review answers; the loot deposits on
        # completion, and no kill happens while banking.
        handle_combat_answer(_context(player_data, calls, [0.0, 0.999999, 0.0]))
        self.assertEqual(player_data.get("carried_inventory", {}).get("chicken"), dict(full_loot))
        handle_combat_answer(_context(player_data, calls, [0.0, 0.999999, 0.0]))

        # Loot deposited: view cleared, items still banked, no kill credited.
        self.assertIsNone(player_data.get("carried_inventory", {}).get("chicken"))
        self.assertEqual(player_data["inventory"]["Trophy 0"], 1)
        self.assertEqual(player_data.get("combat_kill_counts", {}).get("chicken", 0), 0)

    def test_stackable_loot_counts_as_one_slot_and_does_not_prematurely_bank(self):
        # A huge feather stack (stackable) occupies a single slot, so it must not
        # trigger a bank run the way 28 distinct unstackables would.
        player_data = {
            "inventory": {"Feather": 2_000_000},
            "equipment": {},
            "current_combat_target": "chicken",
            "combat_attack_style": "accurate",
            "combat_lifepoints": 100,
            "combat_auto_eat_food": ["Shrimps"],
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 10,
            "attack_exp": 0.0,
            "constitution_exp": 0.0,
            "carried_inventory": {"chicken": {"Feather": 2_000_000}},
            "completed_achievements": [],
        }
        calls = {"xp": [], "saves": 0, "errors": []}
        handle_combat_answer(_context(player_data, calls, [0.0, 0.999999, 0.0]))
        # No bank run: the fight happened this answer (a kill was credited).
        self.assertEqual(player_data.get("combat_kill_counts", {}).get("chicken", 0), 1)

    def test_combat_handler_runs_review_burst_and_records_drops(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "equipment": {},
            "current_combat_target": "chicken",
            "combat_attack_style": "accurate",
            "combat_lifepoints": 100,
            "combat_auto_eat_food": ["Shrimps"],
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 10,
            "attack_exp": 0.0,
            "strength_exp": 0.0,
            "defense_exp": 0.0,
            "constitution_exp": 0.0,
            "completed_achievements": [],
        }

        ok = handle_combat_answer(_context(player_data, calls, [0.0, 0.999999, 0.0]))

        self.assertTrue(ok)
        self.assertEqual(player_data["combat_kill_counts"], {"chicken": 1})
        self.assertGreater(player_data["attack_exp"], 0.0)
        self.assertGreater(player_data["constitution_exp"], 0.0)
        # Every first-seen drop is picked up and starts in Keep mode, even when it
        # falls below the coarse value threshold. The player can turn it off only
        # after the recorder has made it available in the per-drop control.
        self.assertEqual(player_data["inventory"]["Bones"], 1)
        self.assertEqual(player_data["inventory"]["Raw chicken"], 1)
        self.assertEqual(player_data["inventory"]["Feather"], 5)
        self.assertEqual(
            player_data["loot_overrides"],
            {"Bones": "keep", "Raw chicken": "keep", "Feather": "keep"},
        )
        # Kept loot also folds into the combat target's carried view (it competes
        # for slots and drops on death); coins would be excluded.
        self.assertEqual(
            player_data["carried_inventory"]["chicken"],
            {"Bones": 1, "Raw chicken": 1, "Feather": 5},
        )
        telemetry = player_data["action_telemetry"]["actions"]["combat:chicken"]
        self.assertEqual(telemetry["attempts"], 1)
        self.assertEqual(telemetry["successes"], 1)
        self.assertEqual(
            telemetry["outputs"], {"Bones": 1, "Raw chicken": 1, "Feather": 5}
        )
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Defeated Chicken"])
        self.assertEqual(len(calls["xp"]), 1)

        player_data["loot_overrides"]["Bones"] = "leave"
        ok = handle_combat_answer(
            _context(player_data, calls, [0.0, 0.999999, 0.0])
        )
        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"]["Bones"], 1)
        self.assertEqual(player_data["loot_overrides"]["Bones"], "leave")

    def test_combat_handler_refuses_and_reports_a_second_clue_drop(self):
        enemy_data = copy.deepcopy(runtime_actions_combat.COMBAT_ENEMY_DATA)
        enemy_data["chicken"]["drops"] = {
            "guaranteed": (("Clue scroll (medium)", 1),),
            "tables": (),
        }
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = {
            "inventory": {"Clue scroll (easy)": 1},
            "equipment": {},
            "current_combat_target": "chicken",
            "combat_attack_style": "accurate",
            "combat_lifepoints": 100,
            "combat_auto_eat_food": ["Shrimps"],
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 10,
            "attack_exp": 0.0,
            "strength_exp": 0.0,
            "defense_exp": 0.0,
            "constitution_exp": 0.0,
            "completed_achievements": [],
        }

        with patch.object(runtime_actions_combat, "COMBAT_ENEMY_DATA", enemy_data):
            self.assertTrue(
                handle_combat_answer(
                    _context(player_data, calls, [0.0, 0.999999, 0.0])
                )
            )

        self.assertEqual(player_data["inventory"]["Clue scroll (easy)"], 1)
        self.assertNotIn("Clue scroll (medium)", player_data["inventory"])
        self.assertTrue(
            any("already have a clue scroll" in message for message in calls["activity"]),
            calls["activity"],
        )
        telemetry = player_data["action_telemetry"]["actions"]["combat:chicken"]
        self.assertNotIn("Clue scroll (medium)", telemetry["outputs"])

    def test_combat_burst_grants_only_one_clue_across_multiple_kills(self):
        enemy_data = copy.deepcopy(runtime_actions_combat.COMBAT_ENEMY_DATA)
        enemy_data["chicken"]["drops"] = {
            "guaranteed": (("Clue scroll (medium)", 1),),
            "tables": (),
        }
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = {
            "inventory": {},
            "equipment": {},
            "current_combat_target": "chicken",
            "combat_attack_style": "accurate",
            "combat_lifepoints": 100,
            "combat_auto_eat_food": ["Shrimps"],
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 10,
            "attack_exp": 0.0,
            "strength_exp": 0.0,
            "defense_exp": 0.0,
            "constitution_exp": 0.0,
            "completed_achievements": [],
        }

        with patch.object(runtime_actions_combat, "COMBAT_ENEMY_DATA", enemy_data):
            self.assertTrue(
                handle_combat_answer(
                    _context(
                        player_data,
                        calls,
                        [0.0, 0.999999, 0.0] * 500,
                        review_action_multiplier=10,
                    )
                )
            )

        self.assertEqual(player_data["combat_kill_counts"], {"chicken": 2})
        self.assertEqual(player_data["inventory"]["Clue scroll (medium)"], 1)
        self.assertTrue(
            any("already have a clue scroll" in message for message in calls["activity"]),
            calls["activity"],
        )
        telemetry = player_data["action_telemetry"]["actions"]["combat:chicken"]
        self.assertEqual(telemetry["outputs"]["Clue scroll (medium)"], 1)

    def test_combat_handler_finisher_refuses_and_reports_a_second_clue(self):
        enemy_data = copy.deepcopy(runtime_actions_combat.COMBAT_ENEMY_DATA)
        enemy_data["desert_lizard"]["drops"] = {
            "guaranteed": (("Clue scroll (medium)", 1),),
            "tables": (),
        }
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = {
            "inventory": {"Clue scroll (easy)": 1},
            "equipment": {},
            "current_combat_target": "desert_lizard",
            "combat_action": "finisher",
            "combat_encounter": {
                "target_id": "desert_lizard",
                "enemy_lifepoints": 30,
            },
            "combat_supply_loadout": {
                "finishers": {"Ice cooler": 2},
                "hazards": {"Waterskin (0)": 1},
            },
            "combat_lifepoints": 100,
            "combat_auto_eat_food": ["Shrimps"],
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 10,
            "slayer_level": 99,
            "completed_achievements": [],
        }

        with patch.object(runtime_actions_combat, "COMBAT_ENEMY_DATA", enemy_data):
            ok = handle_combat_answer(
                _context(player_data, calls, [0.999999] * 40)
            )

        self.assertTrue(ok)
        self.assertEqual(player_data["combat_action"], "attack")
        self.assertEqual(player_data["combat_encounter"], {})
        self.assertEqual(player_data["combat_kill_counts"], {"desert_lizard": 1})
        self.assertEqual(
            player_data["combat_supply_loadout"]["finishers"],
            {"Ice cooler": 1},
        )
        self.assertEqual(player_data["inventory"], {"Clue scroll (easy)": 1})
        self.assertTrue(
            any("already have a clue scroll" in message for message in calls["activity"]),
            calls["activity"],
        )
        telemetry = player_data["action_telemetry"]["actions"][
            "combat:desert_lizard"
        ]
        self.assertEqual(telemetry["attempts"], 1)
        self.assertNotIn("Clue scroll (medium)", telemetry["outputs"])
        self.assertEqual(
            calls["activity"],
            [
                "Defeated Desert lizard",
                "You already have a clue scroll: Clue scroll (easy)",
            ],
        )
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["saves"], 1)

    def test_combat_handler_finisher_repairs_stale_runes_when_fight_ends(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "equipment": {},
            "current_combat_target": "desert_lizard",
            "combat_action": "finisher",
            "combat_encounter": {
                "target_id": "desert_lizard",
                "enemy_lifepoints": 30,
            },
            "combat_supply_loadout": {
                "runes": {"Air rune": 5, "Mind rune": 5},
                "finishers": {"Ice cooler": 1},
                "hazards": {"Waterskin (4)": 1},
            },
            "combat_lifepoints": 100,
            "combat_auto_eat_food": ["Shrimps"],
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 10,
            "slayer_level": 99,
            "completed_achievements": [],
        }

        ok = handle_combat_answer(
            _context(player_data, calls, [0.999999] * 40)
        )

        self.assertTrue(ok)
        self.assertEqual(player_data["combat_encounter"], {})
        self.assertEqual(player_data["combat_supply_loadout"]["runes"], {})
        self.assertEqual(player_data["inventory"]["Air rune"], 5)
        self.assertEqual(player_data["inventory"]["Mind rune"], 5)
        self.assertEqual(calls["saves"], 1)

    def test_combat_handler_routes_charged_zygomite_finisher_without_losing_remainder(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "equipment": {},
            "quests": {"lost_city": {"completed": True}},
            "current_combat_target": "mutated_zygomite_level_86",
            "combat_action": "finisher",
            "combat_encounter": {
                "target_id": "mutated_zygomite_level_86",
                "enemy_lifepoints": 19,
            },
            "combat_supply_loadout": {
                "finishers": {"Fungicide spray 4": 1},
            },
            "combat_lifepoints": 990,
            "combat_auto_eat_food": ["Shark"],
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "slayer_level": 57,
            "completed_achievements": [],
        }

        ok = handle_combat_answer(
            _context(player_data, calls, [0.999999] * 40)
        )

        self.assertTrue(ok)
        self.assertEqual(player_data["combat_action"], "attack")
        self.assertEqual(player_data["combat_encounter"], {})
        self.assertEqual(
            player_data["combat_kill_counts"],
            {"mutated_zygomite_level_86": 1},
        )
        self.assertEqual(
            player_data["combat_supply_loadout"]["finishers"],
            {"Fungicide spray 3": 1},
        )
        self.assertEqual(calls["activity"], ["Defeated Mutated zygomite"])
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["saves"], 1)

    def test_combat_handler_resets_a_stale_finisher_without_disabling_combat(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "equipment": {},
            "current_combat_target": "desert_lizard",
            "combat_action": "finisher",
            "combat_encounter": {
                "target_id": "desert_lizard",
                "enemy_lifepoints": 31,
            },
            "combat_supply_loadout": {
                "finishers": {"Ice cooler": 1},
                "hazards": {"Waterskin (4)": 1},
            },
            "combat_lifepoints": 100,
            "combat_auto_eat_food": ["Shrimps"],
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 10,
            "slayer_level": 99,
            "completed_achievements": [],
        }

        ok = handle_combat_answer(_context(player_data, calls))

        self.assertFalse(ok)
        self.assertEqual(player_data["combat_action"], "attack")
        self.assertNotIn("deactivated", calls)
        self.assertEqual(calls["errors"][0][0], "Finisher unavailable")
        self.assertEqual(calls["saves"], 1)

    def test_combat_handler_reports_target_regeneration(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "equipment": {},
            "current_combat_target": "gargoyle",
            "combat_encounter": {
                "target_id": "gargoyle",
                "enemy_lifepoints": 100,
            },
            "combat_lifepoints": 100,
            "combat_auto_eat_food": ["Shrimps"],
            "attack_level": 1,
            "strength_level": 1,
            "defense_level": 99,
            "constitution_level": 10,
            "slayer_level": 99,
            "completed_achievements": [],
        }

        ok = handle_combat_answer(
            _context(player_data, calls, [1.0] * 100)
        )

        self.assertTrue(ok)
        self.assertEqual(
            calls["activity"],
            ["Gargoyle: 0 damage dealt, 220 LP left, 120 LP regenerated"],
        )

    def test_combat_handler_reports_vampyre_bite_healing(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "equipment": {},
            "current_combat_target": "vampyre",
            "combat_lifepoints": 100,
            "combat_auto_eat_food": ["Shrimps"],
            "attack_level": 1,
            "strength_level": 1,
            "defense_level": 1,
            "constitution_level": 10,
            "slayer_level": 99,
            "quests": {"priest_in_peril": {"completed": True}},
            "completed_achievements": [],
        }
        result = {
            "target_id": "vampyre",
            "display_name": "Vampyre",
            "kills": 0,
            "died": False,
            "fled": False,
            "player_damage": 0,
            "enemy_lifepoints": 320,
            "enemy_healing": 20,
            "vampyre_bites": 1,
            "vampyre_bite_healing": 20,
            "drops": {},
            "xp_rewards": {},
        }

        with patch.object(
            runtime_actions_combat,
            "apply_combat_burst_pure",
            return_value=(dict(player_data), True, result),
        ):
            ok = handle_combat_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertEqual(
            calls["activity"],
            ["Vampyre: 0 damage dealt, 320 LP left, 20 LP healed by 1 bite"],
        )

    def test_a_near_death_review_with_no_food_anywhere_is_refused(self):
        """The owner's report: dying mid-activity with no warning. A review that
        would begin below the near-death line with nothing to eat and nothing
        bankable is refused outright rather than resolved."""
        player_data = {
            "inventory": {},
            "equipment": {},
            "current_combat_target": "cow",
            "combat_lifepoints": 15,   # 15% of 100
            "combat_auto_eat_food": [],
            "attack_level": 10,
            "strength_level": 10,
            "defense_level": 10,
            "constitution_level": 10,
            "completed_achievements": [],
        }
        calls = {"xp": [], "saves": 0, "errors": [], "deactivated": []}
        prompted = []
        ctx = _context(player_data, calls)
        ctx.prompt_near_death = lambda source: prompted.append(source)

        ok = handle_combat_answer(ctx)

        self.assertFalse(ok, "the review must not resolve")
        self.assertEqual(prompted, ["combat"], "the player must be asked")
        self.assertEqual(
            calls["deactivation_reasons"],
            ["Lifepoints are critical and there is no food left in your pack or bank."],
        )
        self.assertNotIn("combat_last_result", player_data)

    def test_near_death_with_food_in_the_bank_is_not_refused(self):
        """The recoverable case belongs to the bank run, not the prompt: with
        food still in the bank the engine fetches it instead of stopping."""
        player_data = {
            "inventory": {"Shark": 6},
            "equipment": {},
            "current_combat_target": "cow",
            "combat_lifepoints": 15,
            "combat_auto_eat_food": ["Shark"],
            "attack_level": 10,
            "strength_level": 10,
            "defense_level": 10,
            "constitution_level": 10,
            "completed_achievements": [],
        }
        prompted = []
        ctx = _context(player_data, {"xp": [], "saves": 0, "errors": []})
        ctx.prompt_near_death = lambda source: prompted.append(source)

        handle_combat_answer(ctx)

        self.assertEqual(prompted, [], "a fetchable bank must not raise the prompt")

    def test_fatal_combat_burst_graves_loot_earned_before_death(self):
        enemy = {
            "display_name": "Fatal looter",
            "level": 99,
            "group": "Test",
            "stats": {"attack": 99, "strength": 99, "defence": 1, "hitpoints": 1},
            "bonuses": {},
            "attack_speed": 1,
            "drops": {"guaranteed": (("Feather", 1),), "tables": ()},
            "source": "test",
        }
        player_data = {
            "inventory": {},
            "equipment": {},
            "current_combat_target": "fatal_looter",
            "combat_attack_style": "accurate",
            # Starts above the near-death guard (20% of 100 max LP) so the burst
            # is allowed to run; the level-99 attacker then kills outright. The
            # guard refuses reviews that begin below the line, not deaths.
            "combat_lifepoints": 100,
            "combat_auto_flee": False,
            "combat_auto_eat_food": [],
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 1,
            "constitution_level": 10,
            "attack_exp": 0.0,
            "constitution_exp": 0.0,
            "completed_achievements": [],
        }
        calls = {"xp": [], "saves": 0, "errors": []}

        with patch.dict(runtime_actions.COMBAT_ENEMY_DATA, {"fatal_looter": enemy}):
            ok = handle_combat_answer(_context(player_data, calls, [0.0, 0.999999, 0.0, 0.999999]))

        self.assertTrue(ok)
        self.assertTrue(player_data["combat_last_result"]["died"])
        self.assertEqual(player_data["combat_last_result"]["kills"], 1)
        self.assertIn("Feather", player_data["combat_grave"]["items"])
        self.assertEqual(player_data["inventory"].get("Feather", 0), 0)
        self.assertNotIn("fatal_looter", player_data.get("carried_inventory", {}))

    def test_combat_handler_runs_ranged_review_with_starter_bow_and_arrows(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "equipment": {"weapon": "Shortbow"},
            "current_combat_target": "chicken",
            "combat_attack_style": "ranged_accurate",
            "combat_lifepoints": 100,
            "combat_auto_eat_food": ["Shrimps"],
            "combat_supply_loadout": {"ammo": {"Bronze arrows": 2}},
            "attack_level": 1,
            "strength_level": 1,
            "defense_level": 1,
            "ranged_level": 99,
            "constitution_level": 10,
            "attack_exp": 0.0,
            "strength_exp": 0.0,
            "defense_exp": 0.0,
            "ranged_exp": 0.0,
            "constitution_exp": 0.0,
            "completed_achievements": [],
        }

        ok = handle_combat_answer(_context(player_data, calls, [0.0, 0.999999, 0.0]))

        self.assertTrue(ok)
        self.assertEqual(player_data["combat_kill_counts"], {"chicken": 1})
        self.assertEqual(player_data["inventory"].get("Bronze arrows", 0), 0)
        # Chain kills keep firing after the first kill within the tick budget, so
        # the second carried arrow is spent on the follow-up shot too.
        self.assertEqual(player_data["combat_supply_loadout"]["ammo"], {})
        self.assertEqual(player_data["attack_exp"], 0.0)
        self.assertGreater(player_data["ranged_exp"], 0.0)
        self.assertGreater(player_data["constitution_exp"], 0.0)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Defeated Chicken"])

    def test_combat_handler_runs_magic_review_with_wind_strike_runes(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "equipment": {"weapon": "Staff"},
            "current_combat_target": "chicken",
            "combat_attack_style": "magic_standard",
            "current_combat_spell": "wind_strike",
            "combat_lifepoints": 100,
            "combat_auto_eat_food": ["Shrimps"],
            "combat_supply_loadout": {"runes": {"Air rune": 1, "Mind rune": 1}},
            "attack_level": 1,
            "strength_level": 1,
            "defense_level": 1,
            "ranged_level": 1,
            "magic_level": 99,
            "constitution_level": 10,
            "attack_exp": 0.0,
            "strength_exp": 0.0,
            "defense_exp": 0.0,
            "ranged_exp": 0.0,
            "magic_exp": 0.0,
            "constitution_exp": 0.0,
            "completed_achievements": [],
        }

        ok = handle_combat_answer(_context(player_data, calls, [0.999999]))

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"].get("Air rune", 0), 0)
        self.assertEqual(player_data["inventory"].get("Mind rune", 0), 0)
        self.assertEqual(player_data["combat_supply_loadout"]["runes"], {})
        self.assertEqual(player_data["combat_last_result"]["combat_class"], "magic")
        self.assertEqual(player_data["combat_last_result"]["spell"], "Wind Strike")
        self.assertEqual(player_data["combat_last_result"]["stop_reason"], "out_of_runes")
        self.assertAlmostEqual(player_data["magic_exp"], 5.5)
        self.assertEqual(player_data["constitution_exp"], 0.0)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["xp"], [5.5])
        self.assertEqual(calls["activity"], ["Chicken: 0 damage dealt, 30 LP left"])

    def test_combat_handler_uses_staff_substitution_for_magic_runes(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "equipment": {"weapon": "Staff of air"},
            "current_combat_target": "chicken",
            "combat_attack_style": "magic_standard",
            "current_combat_spell": "wind_strike",
            "combat_lifepoints": 100,
            "combat_auto_eat_food": ["Shrimps"],
            "combat_supply_loadout": {"runes": {"Mind rune": 1}},
            "attack_level": 1,
            "strength_level": 1,
            "defense_level": 1,
            "ranged_level": 1,
            "magic_level": 99,
            "constitution_level": 10,
            "attack_exp": 0.0,
            "strength_exp": 0.0,
            "defense_exp": 0.0,
            "ranged_exp": 0.0,
            "magic_exp": 0.0,
            "constitution_exp": 0.0,
            "completed_achievements": [],
        }

        ok = handle_combat_answer(_context(player_data, calls, [0.999999]))

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"].get("Air rune", 0), 0)
        self.assertEqual(player_data["inventory"].get("Mind rune", 0), 0)
        self.assertEqual(player_data["combat_supply_loadout"]["runes"], {})
        self.assertEqual(player_data["combat_last_result"]["runes_used"], {"Mind rune": 1})
        self.assertAlmostEqual(player_data["magic_exp"], 5.5)
        self.assertEqual(calls["errors"], [])

    def test_combat_handler_bankstands_magic_without_runes(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "equipment": {"weapon": "Staff"},
            "current_combat_target": "chicken",
            "combat_attack_style": "magic_standard",
            "current_combat_spell": "wind_strike",
            "combat_lifepoints": 100,
            "magic_level": 99,
            "constitution_level": 10,
            "completed_achievements": [],
        }

        ok = handle_combat_answer(_bankstanding_context(player_data, calls))

        self.assertFalse(ok)
        self.assertEqual(player_data["current_utility"], "bankstanding")
        self.assertEqual(calls["bankstanding"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertIn("Air rune x1", calls["bankstanding_reasons"][0])
        self.assertIn("Mind rune x1", calls["bankstanding_reasons"][0])

    def test_handler_key_registry_and_readiness_share_runtime_module(self):
        self.assertIs(answer_handler_for_key("fletching"), handle_fletching_answer)
        self.assertIs(answer_handler_for_key("hunter"), handle_hunter_answer)
        self.assertIs(answer_handler_for_key("combat"), handle_combat_answer)

        player_data = {
            "inventory": {"Logs": 1},
            "fletching_level": 1,
            "current_fletch": "arrow_shafts",
        }
        self.assertTrue(can_start_action(_context(player_data), "fletching"))

        player_data["inventory"] = {}
        self.assertFalse(can_start_action(_context(player_data), "fletching"))

        combat_data = {
            "inventory": {},
            "equipment": {},
            "current_combat_target": "chicken",
            "combat_attack_style": "accurate",
            "combat_lifepoints": 100,
            "attack_level": 1,
            "strength_level": 1,
            "defense_level": 1,
            "constitution_level": 10,
        }
        self.assertTrue(can_start_action(_context(combat_data), "combat"))
        combat_data.update(
            {
                "inventory": {"Bronze arrows": 1},
                "equipment": {"weapon": "Shortbow"},
                "combat_attack_style": "ranged_accurate",
                "ranged_level": 1,
            }
        )
        self.assertTrue(can_start_action(_context(combat_data), "combat"))
        combat_data["inventory"] = {}
        self.assertFalse(can_start_action(_context(combat_data), "combat"))
        combat_data.update(
            {
                "combat_attack_style": "magic_standard",
                "equipment": {"weapon": "Staff"},
                "inventory": {"Air rune": 1, "Mind rune": 1},
                "magic_level": 1,
                "current_combat_spell": "wind_strike",
            }
        )
        self.assertTrue(can_start_action(_context(combat_data), "combat"))
        combat_data["inventory"] = {}
        self.assertFalse(can_start_action(_context(combat_data), "combat"))
        combat_data.update(
            {
                "equipment": {"weapon": "Staff of air"},
                "inventory": {"Mind rune": 1},
            }
        )
        self.assertTrue(can_start_action(_context(combat_data), "combat"))
        self.assertTrue(can_start_action(_context(player_data), "unknown"))

        hunter_data = {
            "inventory": {"Logs": 1},
            "hunter_level": 23,
            "current_hunter": "catch_wild_kebbit",
        }
        self.assertTrue(can_start_action(_context(hunter_data), "hunter"))

        hunter_data["inventory"] = {}
        self.assertFalse(can_start_action(_context(hunter_data), "hunter"))

    def test_what_lies_below_completion_grants_dagonhai_history(self):
        from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
        from ankiscape.core.storage_pure import default_player_data

        quest_id = "what_lies_below"
        quest = QUEST_DATA[quest_id]
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["current_quest"] = quest_id
        for requirement in quest["required_skills"]:
            player_data[f"{requirement['skill_id']}_level"] = requirement["level"]
        final_stage = int(quest["stages"]) - 1
        player_data["quests"][quest_id] = {
            "started": True,
            "progress": final_stage,
            "completed": False,
        }
        final_requirement = next(
            row for row in quest["stage_requirements"] if row["stage"] == final_stage
        )
        player_data["quest_action_proofs"] = list(
            final_requirement["required_actions"]
        )
        calls = {"xp": [], "saves": 0, "errors": []}

        self.assertTrue(handle_quest_answer(_context(player_data, calls)))

        self.assertTrue(player_data["quests"]["what_lies_below"]["completed"])
        self.assertEqual(player_data["inventory"]["Dagon'hai history"], 1)

    def test_do_no_evil_completion_refuses_and_reports_a_second_clue(self):
        from ankiscape.core.constants import QUEST_DATA

        quest_id = "do_no_evil"
        quest = QUEST_DATA[quest_id]
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["current_quest"] = quest_id
        player_data["inventory"]["Clue scroll (easy)"] = 1
        for requirement in quest["required_quests"]:
            player_data["quests"][requirement["quest_id"]] = {
                "started": True,
                "progress": 1,
                "completed": True,
            }
        for requirement in quest["required_skills"]:
            player_data[f"{requirement['skill_id']}_level"] = requirement["level"]
        final_stage = int(quest["stages"]) - 1
        player_data["quests"][quest_id] = {
            "started": True,
            "progress": final_stage,
            "completed": False,
        }
        final_requirement = next(
            row
            for row in quest["stage_requirements"]
            if row["stage"] == final_stage
        )
        player_data["quest_action_proofs"] = list(
            final_requirement["required_actions"]
        )
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}

        self.assertTrue(handle_quest_answer(_context(player_data, calls)))

        self.assertTrue(player_data["quests"][quest_id]["completed"])
        self.assertEqual(player_data["inventory"]["Clue scroll (easy)"], 1)
        self.assertEqual(player_data["inventory"].get("Clue scroll (elite)", 0), 0)
        self.assertEqual(player_data["inventory"]["Cramulet"], 1)
        self.assertTrue(
            any("already have a clue scroll" in message for message in calls["activity"]),
            calls["activity"],
        )

    def test_quest_completion_reports_a_clue_produced_by_its_final_stage(self):
        quest_id = "do_no_evil"
        quest_data = copy.deepcopy(runtime_actions_production.QUEST_DATA)
        quest = quest_data[quest_id]
        final_stage = int(quest["stages"]) - 1
        final_requirement = next(
            row
            for row in quest["stage_requirements"]
            if row["stage"] == final_stage
        )
        final_requirement["produced_inventory"] = {"Clue scroll (easy)": 1}

        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["current_quest"] = quest_id
        for requirement in quest["required_quests"]:
            player_data["quests"][requirement["quest_id"]] = {
                "started": True,
                "progress": 1,
                "completed": True,
            }
        for requirement in quest["required_skills"]:
            player_data[f"{requirement['skill_id']}_level"] = requirement["level"]
        player_data["quests"][quest_id] = {
            "started": True,
            "progress": final_stage,
            "completed": False,
        }
        player_data["quest_action_proofs"] = list(
            final_requirement["required_actions"]
        )
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}

        with patch.object(runtime_actions_production, "QUEST_DATA", quest_data):
            self.assertTrue(handle_quest_answer(_context(player_data, calls)))

        self.assertTrue(player_data["quests"][quest_id]["completed"])
        self.assertEqual(player_data["inventory"]["Clue scroll (easy)"], 1)
        self.assertEqual(player_data["inventory"].get("Clue scroll (elite)", 0), 0)
        self.assertEqual(player_data["inventory"]["Cramulet"], 1)
        self.assertEqual(
            calls["activity"],
            [
                "Do No Evil complete",
                "You can only carry one clue scroll at a time.",
            ],
        )

    def test_jungle_potion_real_handler_repeats_each_search_until_turn_in_and_unlocks_shilo(self):
        from ankiscape.core.constants import HERBLORE_DATA, QUEST_DATA

        quest_id = "jungle_potion"
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data.update(
            {
                "current_quest": quest_id,
                "herblore_level": 3,
                "herblore_exp": 250.0,
                "quest_points": 4,
            }
        )
        player_data["quests"]["druidic_ritual"] = {
            "started": True,
            "progress": 8,
            "completed": True,
        }
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        ctx = _context(player_data, calls, random_values=(0.0,) * 5)
        player_data["current_utility"] = "search_marshy_jungle_vines"
        self.assertFalse(handle_utility_answer(ctx))
        self.assertEqual(player_data["inventory"]["Grimy snake weed"], 0)

        route = (
            ("clean_snake_weed", "Grimy snake weed", "Clean snake weed"),
            ("clean_ardrigal", "Grimy ardrigal", "Clean ardrigal"),
            ("clean_sito_foil", "Grimy sito foil", "Clean sito foil"),
            ("clean_volencia_moss", "Grimy volencia moss", "Clean volencia moss"),
            ("clean_rogues_purse", "Grimy rogue's purse", "Clean rogue's purse"),
        )

        for stage, (clean_target, grimy_item, clean_item) in enumerate(route, start=1):
            self.assertTrue(handle_quest_answer(ctx))
            self.assertEqual(player_data["inventory"][grimy_item], 1)
            self.assertEqual(player_data["quests"][quest_id]["progress"], stage)
            self.assertFalse(player_data["quests"][quest_id]["completed"])

            player_data["inventory"][grimy_item] = 0
            self.assertTrue(handle_quest_answer(ctx))
            self.assertEqual(player_data["inventory"][grimy_item], 1)
            self.assertEqual(player_data["quests"][quest_id]["progress"], stage)

            player_data["current_herblore"] = clean_target
            self.assertTrue(handle_herblore_answer(ctx))
            self.assertEqual(player_data["inventory"][grimy_item], 0)
            self.assertEqual(HERBLORE_DATA[clean_target]["level"], 3)
            self.assertEqual(HERBLORE_DATA[clean_target]["exp"], 2.5)
            if stage == 1:
                self.assertEqual(player_data["inventory"][clean_item], 0)
                self.assertEqual(
                    player_data["inventory"]["Strange rock (Herblore 1)"], 1
                )
                self.assertEqual(
                    player_data["inventory"]["Strange rock (Herblore 2)"], 1
                )
                self.assertTrue(handle_quest_answer(ctx))
                self.assertEqual(player_data["inventory"][grimy_item], 1)
                self.assertEqual(player_data["quests"][quest_id]["progress"], stage)
                self.assertTrue(handle_herblore_answer(ctx))
                self.assertEqual(player_data["inventory"][grimy_item], 0)
            self.assertEqual(player_data["inventory"][clean_item], 1)

            self.assertTrue(handle_quest_answer(ctx))
            self.assertEqual(player_data["inventory"][clean_item], 0)
            self.assertEqual(player_data["quests"][quest_id]["progress"], stage + 1)
            self.assertEqual(
                player_data["quests"][quest_id]["completed"],
                stage == len(route),
            )

        self.assertTrue(player_data["quests"][quest_id]["completed"])
        self.assertEqual(player_data["quest_points"], 5)
        self.assertEqual(player_data["herblore_exp"], 1040.0)
        self.assertEqual(calls["saves"], 22)
        self.assertEqual(calls["activity"][-1], "Jungle Potion complete")
        self.assertIn("Found 2 Herblore strange rocks.", calls["activity"])
        self.assertEqual(player_data["inventory"]["Strange rock (Herblore 1)"], 1)
        self.assertEqual(player_data["inventory"]["Strange rock (Herblore 2)"], 1)
        self.assertEqual(calls["errors"][-1][0], "Quest complete")
        self.assertTrue(calls["deactivated"])
        for _clean_target, grimy_item, clean_item in route:
            self.assertEqual(player_data["inventory"][grimy_item], 0)
            self.assertEqual(player_data["inventory"][clean_item], 0)

        for activity_id, grimy_item in (
            ("search_marshy_jungle_vines", "Grimy snake weed"),
            ("search_jungle_palm_trees", "Grimy ardrigal"),
            ("search_scorched_earth", "Grimy sito foil"),
            ("search_jungle_mine_rocks", "Grimy volencia moss"),
            ("search_fungus_covered_wall", "Grimy rogue's purse"),
        ):
            player_data["current_utility"] = activity_id
            before = player_data["inventory"].get(grimy_item, 0)
            self.assertTrue(handle_utility_answer(ctx))
            self.assertTrue(handle_utility_answer(ctx))
            self.assertEqual(player_data["inventory"][grimy_item], before + 2)

        from ankiscape.logic.shattered_heart_logic import default_shattered_heart_state_pure

        player_data["inventory"].pop("Strange rock (Herblore 1)", None)
        player_data["inventory"].pop("Strange rock (Herblore 2)", None)
        player_data["shattered_heart"] = default_shattered_heart_state_pure()
        player_data["current_herblore"] = "clean_sito_foil"
        self.assertTrue(handle_herblore_answer(ctx))
        self.assertEqual(player_data["inventory"]["Clean sito foil"], 0)
        self.assertEqual(player_data["inventory"]["Strange rock (Herblore 1)"], 1)

        player_data.update({"smithing_level": 4, "crafting_level": 20, "agility_level": 32})
        self.assertTrue(can_start_quest_pure(player_data, "shilo_village", QUEST_DATA))

    def test_quest_completion_warns_and_switches_off(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Research notes": 1},
            "current_quest": "rune_mysteries",
            "quests": {"rune_mysteries": {"started": True, "progress": 5, "completed": False}},
            "quest_action_proofs": ["Return Aubury's research notes to Sedridor"],
            "quest_points": 0,
            "runecrafting_exp": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertTrue(player_data["quests"]["rune_mysteries"]["completed"])
        self.assertEqual(player_data["inventory"]["Air talisman"], 1)
        self.assertEqual(player_data["inventory"]["Research notes"], 0)
        self.assertEqual(calls["saves"], 1)
        self.assertTrue(calls["deactivated"])
        self.assertEqual(calls["activity"], ["Rune Mysteries complete"])
        self.assertEqual(calls["errors"][0][0], "Quest complete")
        self.assertIn("Rune Mysteries is complete", calls["errors"][0][1])
        self.assertIn("questing has been switched off", calls["errors"][0][1])

    def test_quest_answer_runs_the_final_tears_of_guthix_stage_before_completion(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Bullseye lantern (empty)": 1, "Sapphire": 1},
            "current_quest": "tears_of_guthix",
            "quests": {"tears_of_guthix": {"started": True, "progress": 2, "completed": False}},
            "quest_action_proofs": ["Complete Tears of Guthix stage 2 objective"],
            "quest_points": 0,
            "crafting_exp": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        self.assertTrue(handle_quest_answer(_context(player_data, calls)))
        self.assertEqual(player_data["quests"]["tears_of_guthix"]["progress"], 3)
        self.assertFalse(player_data["quests"]["tears_of_guthix"]["completed"])
        self.assertNotIn("deactivated", calls)
        self.assertEqual(calls["activity"], ["Tears of Guthix 3/4"])

        self.assertFalse(handle_quest_answer(_context(player_data, calls)))
        self.assertTrue(calls["deactivated"])
        self.assertEqual(player_data["quests"]["tears_of_guthix"]["progress"], 3)
        self.assertIn("Needs Sapphire lantern (lit) x1", calls["errors"][-1][1])

        player_data["inventory"]["Sapphire lantern (lit)"] = 1
        player_data["quest_action_proofs"].append(
            "Complete Tears of Guthix stage 3 objective"
        )
        self.assertTrue(handle_quest_answer(_context(player_data, calls)))
        self.assertTrue(player_data["quests"]["tears_of_guthix"]["completed"])
        self.assertEqual(player_data["quests"]["tears_of_guthix"]["progress"], 4)
        self.assertEqual(player_data["crafting_exp"], 1000.0)
        self.assertEqual(calls["activity"][-1], "Tears of Guthix complete")

    def test_quest_stage_blocker_deactivates_without_progress_or_reward(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "current_quest": "the_knights_sword",
            "quests": {"the_knights_sword": {"started": True, "progress": 2, "completed": False}},
            "quest_points": 0,
            "smithing_exp": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertFalse(ok)
        self.assertEqual(player_data["quests"]["the_knights_sword"]["progress"], 2)
        self.assertFalse(player_data["quests"]["the_knights_sword"]["completed"])
        self.assertEqual(player_data["quest_points"], 0)
        self.assertEqual(player_data["smithing_exp"], 0)
        self.assertEqual(calls["saves"], 0)
        self.assertTrue(calls["deactivated"])
        self.assertEqual(calls["errors"][0][0], "Quest blocked")
        self.assertIn("Needs Redberry pie x1", calls["errors"][0][1])

    def test_quest_choice_blocker_deactivates_without_progress_or_reward(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "current_quest": "shield_of_arrav",
            "quests": {"shield_of_arrav": {"started": True, "progress": 4, "completed": False}},
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertFalse(ok)
        self.assertEqual(player_data["quests"]["shield_of_arrav"]["progress"], 4)
        self.assertFalse(player_data["quests"]["shield_of_arrav"]["completed"])
        self.assertEqual(player_data["quest_points"], 0)
        self.assertNotIn("quest_route_states", player_data)
        self.assertEqual(calls["saves"], 0)
        self.assertTrue(calls["deactivated"])
        self.assertEqual(calls["errors"][0][0], "Quest blocked")
        self.assertIn("Choose path: Phoenix Gang or Black Arm Gang", calls["errors"][0][1])

    def test_quest_answer_blocks_witchs_house_mouse_puzzle_without_stage_item(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Magnet": 1},
            "current_quest": "witchs_house",
            "quests": {"witchs_house": {"started": True, "progress": 4, "completed": False}},
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertFalse(ok)
        self.assertEqual(player_data["quests"]["witchs_house"]["progress"], 4)
        self.assertFalse(player_data["quests"]["witchs_house"]["completed"])
        self.assertEqual(player_data["quest_points"], 0)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(calls["saves"], 0)
        self.assertTrue(calls["deactivated"])
        self.assertEqual(calls["errors"][0][0], "Quest blocked")
        self.assertIn("Needs Cheese x1", calls["errors"][0][1])
        self.assertNotIn("Use cheese on the mouse hole", calls["errors"][0][1])

    def test_quest_answer_blocks_biohazard_guidor_without_priest_gown(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {
                "Liquid honey": 1,
                "Ethenea": 1,
                "Sulphuric broline": 1,
                "Plague sample": 1,
                "Touch paper": 1,
            },
            "current_quest": "biohazard",
            "quests": {"biohazard": {"started": True, "progress": 11, "completed": False}},
            "quest_route_states": {
                "biohazard": ["Reach Guidor's house without Varrock guards confiscating the vials"]
            },
            "quest_action_proofs": [
                "Give sulphuric broline to Hops",
                "Give ethenea to Da Vinci",
                "Give liquid honey to Chancy",
                "Collect the sulphuric broline from Hops in Varrock",
                "Collect the ethenea from Da Vinci in Varrock",
                "Collect the liquid honey from Chancy in Varrock",
                "Enter Guidor's room wearing priest gowns",
                "Give Guidor the vials, plague sample, and touch paper",
            ],
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertFalse(ok)
        self.assertEqual(player_data["quests"]["biohazard"]["progress"], 11)
        self.assertFalse(player_data["quests"]["biohazard"]["completed"])
        self.assertEqual(player_data["inventory"]["Liquid honey"], 1)
        self.assertEqual(player_data["inventory"]["Touch paper"], 1)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(calls["saves"], 0)
        self.assertTrue(calls["deactivated"])
        self.assertEqual(calls["errors"][0][0], "Quest blocked")
        self.assertIn("Needs Priest gown x2", calls["errors"][0][1])

    def test_quest_answer_blocks_heroes_final_without_fire_feather(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Lava eel": 1, "Thieves' armband": 1},
            "current_quest": "heroes_quest",
            "quests": {"heroes_quest": {"started": True, "progress": 12, "completed": False}},
            "quest_action_proofs": ["Hand Achietties the Lava eel, Thieves' armband, and Fire feather"],
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertFalse(ok)
        self.assertEqual(player_data["quests"]["heroes_quest"]["progress"], 12)
        self.assertFalse(player_data["quests"]["heroes_quest"]["completed"])
        self.assertEqual(player_data["inventory"]["Lava eel"], 1)
        self.assertEqual(player_data["inventory"]["Thieves' armband"], 1)
        self.assertEqual(player_data["quest_points"], 0)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(calls["saves"], 0)
        self.assertTrue(calls["deactivated"])
        self.assertEqual(calls["errors"][0][0], "Quest blocked")
        self.assertIn("Needs Fire feather x1", calls["errors"][0][1])

    def test_quest_answer_blocks_family_crest_jewellery_without_two_rubies(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {
                "Perfect gold bar": 2,
                "Ruby": 1,
                "Ring mould": 1,
                "Necklace mould": 1,
            },
            "current_quest": "family_crest",
            "quests": {"family_crest": {"started": True, "progress": 10, "completed": False}},
            "quest_action_proofs": ["Craft the perfect ruby ring and perfect ruby necklace"],
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertFalse(ok)
        self.assertEqual(player_data["quests"]["family_crest"]["progress"], 10)
        self.assertFalse(player_data["quests"]["family_crest"]["completed"])
        self.assertEqual(player_data["inventory"]["Perfect gold bar"], 2)
        self.assertEqual(player_data["inventory"]["Ruby"], 1)
        self.assertEqual(player_data["inventory"].get("Perfect ruby ring", 0), 0)
        self.assertEqual(player_data["quest_points"], 0)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(calls["saves"], 0)
        self.assertTrue(calls["deactivated"])
        self.assertEqual(calls["errors"][0][0], "Quest blocked")
        self.assertIn("Needs Ruby x2", calls["errors"][0][1])

    def test_quest_answer_blocks_temple_of_ikov_fire_warrior_without_bow_option(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Ice arrows": 1},
            "current_quest": "temple_of_ikov",
            "quests": {"temple_of_ikov": {"started": True, "progress": 7, "completed": False}},
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertFalse(ok)
        self.assertEqual(player_data["quests"]["temple_of_ikov"]["progress"], 7)
        self.assertFalse(player_data["quests"]["temple_of_ikov"]["completed"])
        self.assertEqual(player_data["inventory"]["Ice arrows"], 1)
        self.assertEqual(player_data["quest_points"], 0)
        self.assertEqual(calls["saves"], 0)
        self.assertTrue(calls["deactivated"])
        self.assertEqual(calls["errors"][0][0], "Quest blocked")
        self.assertIn("Needs Yew shortbow x1 or Yew longbow x1", calls["errors"][0][1])

    def test_quest_stage_progress_accepts_required_tools_from_equipment(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "equipment": {"body": "Iron chainbody", "head": "Bronze med helm"},
            "current_quest": "black_knights_fortress",
            "quests": {"black_knights_fortress": {"started": True, "progress": 1, "completed": False}},
            "quest_action_proofs": ["Infiltrate the Black Knights' Fortress"],
            "quest_points": 12,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["black_knights_fortress"]["progress"], 2)
        self.assertFalse(player_data["quests"]["black_knights_fortress"]["completed"])
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Black Knights' Fortress 2/5"])

    def test_quest_answer_progresses_dwarf_cannon_repairs_without_goblin_gate(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Hammer": 1},
            "current_quest": "dwarf_cannon",
            "quests": {"dwarf_cannon": {"started": True, "progress": 1, "completed": False}},
            "quest_action_proofs": ["Accept replacement railings from Captain Lawgof"],
            "quest_points": 0,
            "crafting_exp": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["dwarf_cannon"]["progress"], 2)
        self.assertFalse(player_data["quests"]["dwarf_cannon"]["completed"])
        self.assertEqual(player_data["inventory"]["Railing"], 6)
        self.assertEqual(player_data["inventory"]["Hammer"], 1)
        self.assertEqual(player_data["quest_combat_encounters"], {})
        self.assertEqual(player_data["quest_combat_encounter_counts"], {})
        self.assertEqual(player_data["quest_points"], 0)
        self.assertEqual(player_data["crafting_exp"], 0)
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Dwarf Cannon 2/14"])

        calls = {"xp": [], "saves": 0, "errors": []}
        player_data["quest_action_proofs"] = []

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["dwarf_cannon"]["progress"], 3)
        self.assertEqual(player_data["inventory"]["Railing"], 0)
        self.assertEqual(player_data["inventory"]["Hammer"], 1)
        self.assertEqual(calls["activity"], ["Dwarf Cannon 3/14"])

    def test_quest_answer_progresses_fishing_contest_pass_emitter(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "current_quest": "fishing_contest",
            "quests": {"fishing_contest": {"started": True, "progress": 1, "completed": False}},
            "quest_points": 0,
            "fishing_exp": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertFalse(player_data["quests"]["fishing_contest"]["completed"])
        self.assertEqual(player_data["quests"]["fishing_contest"]["progress"], 2)
        self.assertEqual(player_data["inventory"]["Fishing pass"], 1)
        self.assertEqual(
            quest_action_proofs_for_quest(player_data, "fishing_contest", QUEST_DATA),
            ("Receive a fishing pass from Austri or Vestri",),
        )
        self.assertEqual(player_data["quest_points"], 0)
        self.assertEqual(player_data["fishing_exp"], 0)
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Fishing Contest 2/7"])

    def test_quest_answer_progresses_sheep_herder_feed_handoff(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "current_quest": "sheep_herder",
            "quests": {
                "sheep_herder": {
                    "started": True,
                    "progress": 1,
                    "completed": False,
                }
            },
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertFalse(player_data["quests"]["sheep_herder"]["completed"])
        self.assertEqual(player_data["quests"]["sheep_herder"]["progress"], 2)
        self.assertEqual(player_data["inventory"]["Sheep feed"], 1)
        self.assertEqual(
            quest_action_proofs_for_quest(player_data, "sheep_herder", QUEST_DATA),
            ("Accept poisoned sheep feed from Councillor Halgrive",),
        )
        self.assertEqual(player_data["quest_points"], 0)
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Sheep Herder 2/6"])

    def test_quest_answer_progresses_waterfall_book_gate(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "current_quest": "waterfall_quest",
            "quests": {"waterfall_quest": {"started": True, "progress": 2, "completed": False}},
            "quest_action_proofs": ["Search the Baxtorian bookcase", "Read the Book on Baxtorian"],
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertFalse(player_data["quests"]["waterfall_quest"]["completed"])
        self.assertEqual(player_data["quests"]["waterfall_quest"]["progress"], 3)
        self.assertEqual(player_data["inventory"]["Book on Baxtorian"], 1)
        self.assertEqual(player_data["quest_points"], 0)
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Waterfall Quest 3/6"])

    def test_quest_answer_completes_priest_in_peril_only_after_essence_gate(self):
        blocked_calls = {"xp": [], "saves": 0, "errors": []}
        blocked_data = {
            "inventory": {"Pure essence": 24},
            "current_quest": "priest_in_peril",
            "quests": {"priest_in_peril": {"started": True, "progress": 8, "completed": False}},
            "quest_points": 0,
            "prayer_exp": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(blocked_data, blocked_calls))

        self.assertFalse(ok)
        self.assertEqual(blocked_data["quests"]["priest_in_peril"]["progress"], 8)
        self.assertFalse(blocked_data["quests"]["priest_in_peril"]["completed"])
        self.assertEqual(blocked_data["inventory"].get("Wolfbane dagger", 0), 0)
        self.assertEqual(blocked_data["prayer_exp"], 0)
        self.assertEqual(blocked_calls["saves"], 0)
        self.assertIn("Needs Rune essence x50 or Pure essence x25", blocked_calls["errors"][0][1])

        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Pure essence": 25, "Rune essence": 2},
            "current_quest": "priest_in_peril",
            "quests": {"priest_in_peril": {"started": True, "progress": 8, "completed": False}},
            "quest_points": 0,
            "prayer_exp": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertTrue(player_data["quests"]["priest_in_peril"]["completed"])
        self.assertEqual(player_data["quests"]["priest_in_peril"]["progress"], 9)
        self.assertEqual(player_data["inventory"]["Pure essence"], 0)
        self.assertEqual(player_data["inventory"]["Rune essence"], 2)
        self.assertEqual(player_data["inventory"]["Wolfbane dagger"], 1)
        self.assertEqual(player_data["quest_points"], 1)
        self.assertEqual(player_data["prayer_exp"], 1406.0)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"][0][0], "Quest complete")

    def test_quest_answer_blocks_holy_grail_titan_stage_without_excalibur(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Magic whistle": 1},
            "current_quest": "holy_grail",
            "quests": {"holy_grail": {"started": True, "progress": 5, "completed": False}},
            "quest_route_states": {
                "holy_grail": ["Reach the Fisher Realm crossing at the six stone heads"]
            },
            "quest_action_proofs": ["Blow the Magic whistle at the six stone heads"],
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
            "attack_level": 120,
            "strength_level": 120,
            "defense_level": 120,
            "constitution_level": 120,
            "prayer_level": 1,
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertFalse(ok)
        self.assertEqual(player_data["quests"]["holy_grail"]["progress"], 5)
        self.assertFalse(player_data["quests"]["holy_grail"]["completed"])
        self.assertNotIn("quest_combat_encounters", player_data)
        self.assertEqual(player_data["inventory"].get("Grail bell", 0), 0)
        self.assertEqual(calls["saves"], 0)
        self.assertIn("Needs Excalibur", calls["errors"][0][1])

    def test_quest_answer_resolves_source_backed_combat_before_stage_progress(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Stake": 1, "Stake hammer": 1},
            "current_quest": "vampyre_slayer",
            "quests": {"vampyre_slayer": {"started": True, "progress": 3, "completed": False}},
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
            "attack_level": 40,
            "strength_level": 40,
            "defense_level": 35,
            "constitution_level": 40,
            "prayer_level": 20,
        }

        ok = handle_quest_answer(
            _context(player_data, calls, random_values=_quest_combat_mid_rolls(), review_action_multiplier=10)
        )

        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["vampyre_slayer"]["progress"], 3)
        self.assertFalse(player_data["quests"]["vampyre_slayer"]["completed"])
        self.assertEqual(player_data["quest_combat_encounters"], {"vampyre_slayer": ["vampyre_slayer_count_draynor_37"]})
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Defeated Count Draynor"])

    def test_quest_answer_resolves_style_aware_magic_combat_before_stage_progress(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "current_quest": "another_slice_of_h_a_m",
            "quests": {"another_slice_of_h_a_m": {"started": True, "progress": 4, "completed": False}},
            "quest_combat_encounters": {"another_slice_of_h_a_m": ["another_slice_of_h_a_m_sigmund_64"]},
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
            "attack_level": 40,
            "strength_level": 40,
            "defense_level": 40,
            "constitution_level": 40,
            "prayer_level": 1,
        }

        ok = handle_quest_answer(
            _context(player_data, calls, random_values=_quest_combat_mid_rolls(), review_action_multiplier=10)
        )

        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["another_slice_of_h_a_m"]["progress"], 4)
        self.assertFalse(player_data["quests"]["another_slice_of_h_a_m"]["completed"])
        self.assertEqual(
            player_data["quest_combat_encounters"],
            {
                "another_slice_of_h_a_m": [
                    "another_slice_of_h_a_m_h_a_m_mage_30",
                    "another_slice_of_h_a_m_sigmund_64",
                ]
            },
        )
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Defeated H.A.M. mage"])

    def test_quest_answer_resolves_beast_fallback_ranged_combat_before_stage_progress(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "current_quest": "toktz_ket_dill",
            "quests": {"toktz_ket_dill": {"started": True, "progress": 6, "completed": False}},
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
            "attack_level": 50,
            "strength_level": 50,
            "defense_level": 50,
            "constitution_level": 50,
            "prayer_level": 1,
        }

        ok = handle_quest_answer(
            _context(player_data, calls, random_values=_quest_combat_mid_rolls(), review_action_multiplier=10)
        )

        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["toktz_ket_dill"]["progress"], 6)
        self.assertFalse(player_data["quests"]["toktz_ket_dill"]["completed"])
        self.assertEqual(player_data["quest_combat_encounter_counts"], {"toktz_ket_dill": {"toktz_ket_dill_lava_monster_47": 1}})
        self.assertEqual(player_data["quest_combat_encounters"], {})
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Defeated Lava monster"])

        ok = handle_quest_answer(
            _context(player_data, calls, random_values=_quest_combat_mid_rolls(), review_action_multiplier=10)
        )

        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["toktz_ket_dill"]["progress"], 6)
        self.assertFalse(player_data["quests"]["toktz_ket_dill"]["completed"])
        self.assertEqual(player_data["quest_combat_encounter_counts"], {"toktz_ket_dill": {"toktz_ket_dill_lava_monster_47": 2}})
        self.assertEqual(player_data["quest_combat_encounters"], {"toktz_ket_dill": ["toktz_ket_dill_lava_monster_47"]})
        self.assertEqual(calls["saves"], 2)
        self.assertEqual(calls["activity"], ["Defeated Lava monster", "Defeated Lava monster"])

    def test_quest_answer_resolves_a_souls_bane_first_fear_reaper_before_stage_progress(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "current_quest": "a_souls_bane",
            "quests": {"a_souls_bane": {"started": True, "progress": 3, "completed": False}},
            "quest_action_proofs": ["Fill the rage meter with an anger weapon"],
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
            "attack_level": 100,
            "strength_level": 100,
            "defense_level": 100,
            "constitution_level": 100,
            "prayer_level": 1,
        }

        ok = handle_quest_answer(
            _context(player_data, calls, random_values=_quest_combat_mid_rolls(), review_action_multiplier=10)
        )

        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["a_souls_bane"]["progress"], 3)
        self.assertFalse(player_data["quests"]["a_souls_bane"]["completed"])
        self.assertEqual(player_data["quest_combat_encounter_counts"], {"a_souls_bane": {"a_souls_bane_fear_reaper_42": 1}})
        self.assertEqual(player_data["quest_combat_encounters"], {})
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Defeated Fear reaper"])

    def test_quest_answer_resolves_death_to_dorgeshuun_senior_guard_quantity(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Pickaxe": 1},
            "current_quest": "death_to_the_dorgeshuun",
            "quests": {"death_to_the_dorgeshuun": {"started": True, "progress": 5, "completed": False}},
            "quest_combat_encounters": {"death_to_the_dorgeshuun": ["death_to_the_dorgeshuun_sigmund_50"]},
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
            "attack_level": 100,
            "strength_level": 100,
            "defense_level": 100,
            "constitution_level": 100,
            "prayer_level": 1,
        }

        ok = handle_quest_answer(
            _context(player_data, calls, random_values=_quest_combat_mid_rolls(), review_action_multiplier=10)
        )

        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["death_to_the_dorgeshuun"]["progress"], 5)
        self.assertFalse(player_data["quests"]["death_to_the_dorgeshuun"]["completed"])
        self.assertEqual(
            player_data["quest_combat_encounter_counts"],
            {"death_to_the_dorgeshuun": {"death_to_the_dorgeshuun_senior_ham_guard_22": 1}},
        )
        self.assertEqual(
            player_data["quest_combat_encounters"],
            {"death_to_the_dorgeshuun": ["death_to_the_dorgeshuun_sigmund_50"]},
        )
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Defeated Senior H.A.M. guard"])

    def test_quest_answer_resolves_conflict_overridden_dad_before_stage_progress(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Coins": 12},
            "current_quest": "troll_stronghold",
            "quests": {"troll_stronghold": {"started": True, "progress": 2, "completed": False}},
            "quest_combat_encounters": {
                "troll_stronghold": ["troll_stronghold_twig_troll_71", "troll_stronghold_troll_general_171"]
            },
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
            "attack_level": 100,
            "strength_level": 100,
            "defense_level": 100,
            "constitution_level": 100,
            "prayer_level": 1,
        }

        ok = handle_quest_answer(
            _context(player_data, calls, random_values=_quest_combat_mid_rolls(), review_action_multiplier=10)
        )

        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["troll_stronghold"]["progress"], 2)
        self.assertFalse(player_data["quests"]["troll_stronghold"]["completed"])
        self.assertEqual(
            player_data["quest_combat_encounters"],
            {
                "troll_stronghold": [
                    "troll_stronghold_dad_101",
                    "troll_stronghold_troll_general_171",
                    "troll_stronghold_twig_troll_71",
                ]
            },
        )
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Defeated Dad"])

    def test_broad_fletching_requires_ability_before_review_reward(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Headless arrows": 15, "Broad arrow heads": 15},
            "fletching_level": 99,
            "fletching_exp": 0,
            "current_fletch": "broad_arrows",
            "completed_achievements": [],
            "unlocked_abilities": [],
        }

        ok = handle_fletching_answer(_context(player_data, calls))

        self.assertFalse(ok)
        self.assertEqual(player_data["inventory"]["Broad arrow heads"], 15)
        self.assertEqual(player_data["fletching_exp"], 0)
        self.assertEqual(calls["errors"][0][0], "Fletching target locked")
        self.assertIn("Broad Fletching", calls["errors"][0][1])
        self.assertTrue(calls["deactivated"])

        player_data["unlocked_abilities"] = ["broad_fletching"]
        calls = {"xp": [], "saves": 0, "errors": []}
        ok = handle_fletching_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"]["Headless arrows"], 0)
        self.assertEqual(player_data["inventory"]["Broad arrows"], 15)
        self.assertAlmostEqual(player_data["fletching_exp"], 150.0)
        self.assertEqual(calls["xp"], [150.0])

    def test_hunter_handler_consumes_materials_and_awards_outputs_on_success(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Logs": 1},
            "hunter_level": 23,
            "hunter_exp": 0,
            "current_hunter": "catch_wild_kebbit",
            "hunter_success_count": 0,
            "completed_achievements": [],
        }

        ok = handle_hunter_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"]["Logs"], 0)
        self.assertEqual(player_data["inventory"]["Bones"], 1)
        self.assertEqual(player_data["inventory"]["Kebbit claws"], 1)
        self.assertAlmostEqual(player_data["hunter_exp"], 128.0)
        self.assertEqual(player_data["hunter_success_count"], 1)
        self.assertEqual(calls["xp"], [128.0])
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])

    def test_hunter_handler_awards_carrion_jadinko_vine_and_selected_seed(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Marasamaw plant": 1},
            "hunter_level": 78,
            "hunter_exp": 0,
            "current_hunter": "catch_carrion_jadinko",
            "hunter_success_count": 0,
            "completed_achievements": [],
        }

        ok = handle_hunter_answer(
            _context(player_data, calls, random_values=(0.0, 0.0, 0.99))
        )

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"]["Marasamaw plant"], 1)
        self.assertEqual(player_data["inventory"]["Pungent vine"], 1)
        self.assertEqual(player_data["inventory"]["Samaden seed"], 1)
        telemetry = player_data["action_telemetry"]["actions"][
            "hunter:catch_carrion_jadinko"
        ]
        self.assertEqual(
            telemetry["outputs"],
            {"Pungent vine": 1, "Samaden seed": 1},
        )
        self.assertEqual(player_data["hunter_exp"], 505.0)
        self.assertEqual(player_data["hunter_success_count"], 1)
        self.assertEqual(calls["xp"], [505.0])
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])

    def test_hunter_handler_runs_the_collapsed_razor_backed_tracking_route(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Noose wand": 1},
            "hunter_level": 49,
            "hunter_exp": 0,
            "current_hunter": "track_razor_backed_kebbit",
            "hunter_success_count": 0,
            "completed_achievements": [],
        }

        ok = handle_hunter_answer(
            _context(player_data, calls, random_values=(0.0,))
        )

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"]["Noose wand"], 1)
        self.assertEqual(player_data["inventory"]["Raw beast meat"], 1)
        self.assertEqual(player_data["inventory"]["Long kebbit spike"], 1)
        self.assertEqual(player_data["hunter_exp"], 348.0)
        self.assertEqual(calls["xp"], [348.0])

    def test_hunter_handler_rolls_source_ordered_jadinko_tables_independently(self):
        cases = {
            "track_shadow_jadinko": (
                71,
                "Noose wand",
                "Shadow vine",
                ("Kalferberry seed", "Samaden seed", "Green blossom seed"),
                475.0,
            ),
            "track_diseased_jadinko": (
                78,
                "Noose wand",
                "Corrupt vine",
                ("Kalferberry seed", "Samaden seed", "Green blossom seed"),
                580.5,
            ),
            "catch_common_jadinko": (
                70,
                "Marasamaw plant",
                "Withered vine",
                ("Kalferberry seed", "Samaden seed", "Green blossom seed"),
                350.0,
            ),
            "catch_guthix_jadinko": (
                81,
                "Marasamaw plant",
                "Guthix vine",
                ("Kalferberry seed", "Samaden seed", "Green blossom seed"),
                600.0,
            ),
            "catch_saradomin_jadinko": (
                81,
                "Marasamaw plant",
                "Saradomin vine",
                ("Kalferberry seed", "Samaden seed", "Green blossom seed"),
                600.0,
            ),
            "catch_zamorak_jadinko": (
                81,
                "Marasamaw plant",
                "Zamorak vine",
                ("Kalferberry seed", "Samaden seed", "Green blossom seed"),
                600.0,
            ),
        }
        for target, (level, tool, output, secondaries, expected_xp) in cases.items():
            with self.subTest(target=target):
                calls = {"xp": [], "saves": 0, "errors": []}
                player_data = {
                    "inventory": {tool: 1},
                    "hunter_level": level,
                    "hunter_exp": 0,
                    "current_hunter": target,
                    "hunter_success_count": 0,
                    "completed_achievements": [],
                }
                table_rolls = (0.0, 0.999999) * len(secondaries)
                ok = handle_hunter_answer(
                    _context(
                        player_data,
                        calls,
                        random_values=(0.0,) + table_rolls,
                    )
                )
                self.assertTrue(ok)
                expected_inventory = {tool: 1, output: 1}
                expected_inventory.update({item: 1 for item in secondaries})
                self.assertEqual(player_data["inventory"], expected_inventory)
                self.assertEqual(
                    player_data["action_telemetry"]["actions"][f"hunter:{target}"]["outputs"],
                    {output: 1, **{item: 1 for item in secondaries}},
                )
                self.assertEqual(player_data["hunter_exp"], expected_xp)
                self.assertEqual(player_data["hunter_success_count"], 1)
                self.assertEqual(calls["xp"], [expected_xp])
                self.assertEqual(calls["saves"], 1)
                self.assertEqual(calls["errors"], [])

    def test_hunter_handler_records_the_actual_kalferberry_secondary_drop(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Marasamaw plant": 1},
            "hunter_level": 75,
            "hunter_exp": 0,
            "current_hunter": "catch_cannibal_jadinko",
            "hunter_success_count": 0,
            "completed_achievements": [],
        }

        ok = handle_hunter_answer(
            _context(player_data, calls, random_values=(0.0, 0.0, 0.5))
        )

        self.assertTrue(ok)
        self.assertEqual(
            player_data["inventory"],
            {
                "Marasamaw plant": 1,
                "Plant teeth": 1,
                "Kalferberry seed": 1,
            },
        )
        self.assertEqual(player_data["hunter_exp"], 475.0)
        self.assertEqual(calls["xp"], [475.0])

    def test_hunter_rocks_do_not_replace_bonecrusher_consumed_bones(self):
        from ankiscape.data.shattered_heart_data import SHATTERED_HEART_SKILLS_BY_ID
        from ankiscape.logic.shattered_heart_logic import default_shattered_heart_state_pure

        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = {
            "inventory": {"Bird snare": 1, "Bonecrusher": 1, "Bones": 100},
            "carried_inventory": {"catch_crimson_swift": {"Bonecrusher": 1}},
            "hunter_level": 99,
            "hunter_exp": 0,
            "current_hunter": "catch_crimson_swift",
            "hunter_success_count": 0,
            "completed_achievements": [],
            "shattered_heart": default_shattered_heart_state_pure(),
        }

        self.assertTrue(
            handle_hunter_answer(
                _context(player_data, calls, random_values=(0.0, 0.0, 0.0))
            )
        )

        inventory = player_data["inventory"]
        self.assertEqual(inventory["Bones"], 100)
        for rock in SHATTERED_HEART_SKILLS_BY_ID["hunter"].rock_items:
            self.assertEqual(inventory[rock], 1)
        self.assertEqual(
            player_data["action_telemetry"]["actions"][
                "hunter:catch_crimson_swift"
            ]["outputs"],
            {
                item_name: inventory.get(item_name, 0)
                for item_name in ("Raw bird meat", "Red feather")
                if inventory.get(item_name, 0) > 0
            },
        )

    def test_common_jadinko_bonus_seed_is_recorded_for_review_undo(self):
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = {
            "inventory": {"Marasamaw plant": 1},
            "hunter_level": 70,
            "hunter_exp": 0,
            "current_hunter": "catch_common_jadinko",
            "hunter_success_count": 0,
            "completed_achievements": [],
        }

        self.assertTrue(
            handle_hunter_answer(
                _context(
                    player_data,
                    calls,
                    random_values=(0.0, 1.0, 0.0, 0.0, 0.4, 1.0, 0.0),
                )
            )
        )

        self.assertEqual(player_data["inventory"]["Marasamaw plant"], 1)
        self.assertEqual(player_data["inventory"]["Withered vine"], 1)
        self.assertEqual(player_data["inventory"]["Argway seed"], 1)
        self.assertEqual(player_data["hunter_exp"], 350.0)
        telemetry = player_data["action_telemetry"]["actions"][
            "hunter:catch_common_jadinko"
        ]
        self.assertEqual(
            telemetry["outputs"],
            {"Withered vine": 1, "Argway seed": 1},
        )

    def test_common_jadinko_rare_seed_survives_loose_strange_rocks(self):
        from ankiscape.data.shattered_heart_data import SHATTERED_HEART_SKILLS_BY_ID
        from ankiscape.logic.shattered_heart_logic import default_shattered_heart_state_pure

        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = {
            "inventory": {"Marasamaw plant": 1},
            "hunter_level": 70,
            "hunter_exp": 0,
            "current_hunter": "catch_common_jadinko",
            "hunter_success_count": 0,
            "completed_achievements": [],
            "shattered_heart": default_shattered_heart_state_pure(),
        }

        self.assertTrue(
            handle_hunter_answer(
                _context(
                    player_data,
                    calls,
                    random_values=(
                        0.0,
                        1.0,
                        0.0,
                        0.0,
                        0.9,
                        1.0,
                        0.0,
                        0.0,
                        0.0,
                    ),
                )
            )
        )

        inventory = player_data["inventory"]
        self.assertEqual(inventory["Samaden seed"], 1)
        self.assertEqual(inventory["Withered vine"], 1)
        for rock in SHATTERED_HEART_SKILLS_BY_ID["hunter"].rock_items:
            self.assertEqual(inventory[rock], 1)
        self.assertEqual(
            player_data["action_telemetry"]["actions"][
                "hunter:catch_common_jadinko"
            ]["outputs"],
            {"Withered vine": 1, "Samaden seed": 1},
        )

    def test_jadinko_potion_inputs_survive_loose_strange_rocks(self):
        from ankiscape.data.shattered_heart_data import SHATTERED_HEART_SKILLS_BY_ID
        from ankiscape.logic.shattered_heart_logic import default_shattered_heart_state_pure

        routes = (
            ("track_shadow_jadinko", "Noose wand", "Shadow vine", 71, "Ugune seed"),
            ("track_diseased_jadinko", "Noose wand", "Corrupt vine", 78, "Ugune seed"),
            ("catch_cannibal_jadinko", "Marasamaw plant", "Plant teeth", 75, None),
            ("catch_guthix_jadinko", "Marasamaw plant", "Guthix vine", 81, "Ugune seed"),
        )
        for target, tool, output, level, secondary_output in routes:
            with self.subTest(target=target):
                calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
                player_data = {
                    "inventory": {tool: 1},
                    "hunter_level": level,
                    "hunter_exp": 0,
                    "current_hunter": target,
                    "hunter_success_count": 0,
                    "completed_achievements": [],
                    "shattered_heart": default_shattered_heart_state_pure(),
                }
                random_values = (
                    (0.0, 1.0, 0.5, 0.0, 0.0)
                    if target == "catch_cannibal_jadinko"
                    else (0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0)
                )

                self.assertTrue(
                    handle_hunter_answer(
                        _context(player_data, calls, random_values=random_values)
                    )
                )

                inventory = player_data["inventory"]
                self.assertEqual(inventory[output], 1)
                expected_outputs = {output: 1}
                if secondary_output is not None:
                    self.assertEqual(inventory[secondary_output], 1)
                    expected_outputs[secondary_output] = 1
                for rock in SHATTERED_HEART_SKILLS_BY_ID["hunter"].rock_items:
                    self.assertEqual(inventory[rock], 1)
                self.assertEqual(
                    player_data["action_telemetry"]["actions"][
                        f"hunter:{target}"
                    ]["outputs"],
                    expected_outputs,
                )

    def test_source_enumerated_jadinko_vines_survive_loose_strange_rocks(self):
        from ankiscape.core.constants import HUNTER_EXTRA_ITEM_DATA
        from ankiscape.data.shattered_heart_data import SHATTERED_HEART_SKILLS_BY_ID
        from ankiscape.logic.shattered_heart_logic import default_shattered_heart_state_pure

        routes = (
            ("catch_igneous_jadinko", "Marble vine", 74),
            ("catch_aquatic_jadinko", "Aquatic vine", 76),
            ("catch_amphibious_jadinko", "Oily vine", 77),
            ("catch_carrion_jadinko", "Pungent vine", 78),
            ("catch_draconic_jadinko", "Draconic vine", 80),
            ("catch_saradomin_jadinko", "Saradomin vine", 81),
            ("catch_zamorak_jadinko", "Zamorak vine", 81),
        )
        for target, output, level in routes:
            with self.subTest(target=target):
                calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
                player_data = {
                    "inventory": {"Marasamaw plant": 1},
                    "hunter_level": level,
                    "hunter_exp": 0,
                    "current_hunter": target,
                    "hunter_success_count": 0,
                    "completed_achievements": [],
                    "shattered_heart": default_shattered_heart_state_pure(),
                }

                random_values = (
                    (0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0)
                    if target in {"catch_saradomin_jadinko", "catch_zamorak_jadinko"}
                    else (0.0, 1.0, 0.0, 0.0, 0.0)
                )
                self.assertTrue(
                    handle_hunter_answer(
                        _context(
                            player_data,
                            calls,
                            random_values=random_values,
                        )
                    )
                )

                inventory = player_data["inventory"]
                self.assertEqual(inventory[output], 1)
                for rock in SHATTERED_HEART_SKILLS_BY_ID["hunter"].rock_items:
                    self.assertEqual(inventory[rock], 1)
                self.assertEqual(
                    player_data["action_telemetry"]["actions"][
                        f"hunter:{target}"
                    ]["outputs"],
                    {output: 1},
                )
                item_spec = HUNTER_EXTRA_ITEM_DATA[output]
                self.assertFalse(item_spec["tradeable"])
                self.assertEqual(item_spec["category"], "material")

    def test_cannibal_jadinko_rocks_replace_only_the_tradeable_seed(self):
        from ankiscape.data.shattered_heart_data import SHATTERED_HEART_SKILLS_BY_ID
        from ankiscape.logic.shattered_heart_logic import default_shattered_heart_state_pure

        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = {
            "inventory": {"Marasamaw plant": 1},
            "hunter_level": 99,
            "hunter_exp": 0,
            "current_hunter": "catch_cannibal_jadinko",
            "hunter_success_count": 0,
            "completed_achievements": [],
            "shattered_heart": default_shattered_heart_state_pure(),
        }

        self.assertTrue(
            handle_hunter_answer(
                _context(
                    player_data,
                    calls,
                    random_values=(0.0, 0.0, 0.5, 0.0, 0.0),
                )
            )
        )

        inventory = player_data["inventory"]
        self.assertEqual(inventory["Plant teeth"], 1)
        self.assertEqual(inventory["Kalferberry seed"], 0)
        for rock in SHATTERED_HEART_SKILLS_BY_ID["hunter"].rock_items:
            self.assertEqual(inventory[rock], 1)
        self.assertEqual(
            player_data["action_telemetry"]["actions"][
                "hunter:catch_cannibal_jadinko"
            ]["outputs"],
            {"Plant teeth": 1},
        )

    def test_hunter_quota_ticket_is_consumed_only_after_success(self):
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        ticket = "Swamp lizard quota ticket"
        player_data = {
            "inventory": {
                ticket: 2,
                "Small fishing net": 1,
                "Rope": 1,
            },
            "carried_inventory": {"catch_swamp_lizard": {ticket: 2}},
            "hunter_private_ground_targets": ["catch_swamp_lizard"],
            "hunter_level": 99,
            "hunter_exp": 0,
            "current_hunter": "catch_swamp_lizard",
            "hunter_success_count": 0,
            "quests": {"priest_in_peril": {"completed": True}},
            "completed_achievements": [],
        }

        self.assertTrue(
            handle_hunter_answer(
                _context(player_data, calls, random_values=(1.0,))
            )
        )
        self.assertEqual(player_data["inventory"][ticket], 2)
        self.assertEqual(
            player_data["carried_inventory"]["catch_swamp_lizard"][ticket],
            2,
        )

        self.assertTrue(
            handle_hunter_answer(
                _context(player_data, calls, random_values=(0.0,))
            )
        )
        self.assertEqual(player_data["inventory"][ticket], 1)
        self.assertEqual(
            player_data["carried_inventory"]["catch_swamp_lizard"][ticket],
            1,
        )
        self.assertIn("Private ground catch", calls["activity"][-1])

    def test_hunter_quest_lock_deactivates_review_target(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "hunter_level": 99,
            "hunter_exp": 0,
            "current_hunter": "catch_ferret",
            "hunter_success_count": 0,
            "quests": {},
            "completed_achievements": [],
        }

        ok = handle_hunter_answer(_context(player_data, calls))

        self.assertFalse(ok)
        self.assertEqual(player_data["hunter_exp"], 0)
        self.assertEqual(player_data["hunter_success_count"], 0)
        self.assertEqual(calls["errors"][0][0], "Hunter target locked")
        self.assertIn("Eagles' Peak", calls["errors"][0][1])
        self.assertTrue(calls["deactivated"])

    def test_fishing_dry_attempt_records_telemetry_and_saves(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "fishing_level": 18,
            "fishing_exp": 0,
            "current_fishing": "catch_mackerel_cod_bass",
            "completed_achievements": [],
        }

        ok = handle_fishing_answer(_context(player_data, calls, random_values=[1.0]))

        self.assertTrue(ok)
        self.assertEqual(player_data["fishing_exp"], 0)
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["saves"], 1)
        telemetry = player_data["action_telemetry"]["actions"]["fishing:catch_mackerel_cod_bass"]
        self.assertEqual(telemetry["attempts"], 1)
        self.assertEqual(telemetry["failures"], 1)
        self.assertEqual(telemetry["failure_kinds"], {"dry": 1})
        self.assertGreater(telemetry["expected_successes"], 0.35)
        self.assertEqual(telemetry["current_dry_streak"], 1)

    def test_cooking_burn_records_failed_attempt_with_output(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Raw shrimps": 1},
            "cooking_level": 1,
            "cooking_exp": 0,
            "current_cooking": "cook_shrimps",
            "cooking_success_count": 0,
            "cooking_burn_count": 0,
            "completed_achievements": [],
        }

        ok = handle_cooking_answer(_context(player_data, calls, random_values=[1.0]))

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"]["Raw shrimps"], 0)
        self.assertEqual(player_data["inventory"]["Burnt shrimp"], 1)
        self.assertEqual(player_data["cooking_success_count"], 0)
        self.assertEqual(player_data["cooking_burn_count"], 1)
        self.assertEqual(calls["saves"], 1)
        telemetry = player_data["action_telemetry"]["actions"]["cooking:cook_shrimps"]
        self.assertEqual(telemetry["attempts"], 1)
        self.assertEqual(telemetry["failures"], 1)
        self.assertEqual(telemetry["failure_kinds"], {"burn": 1})
        self.assertEqual(telemetry["outputs"], {"Burnt shrimp": 1})

    def test_cooking_runtime_auto_equips_gauntlets_and_applies_no_burn_level(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Raw shark": 1, "Cooking gauntlets": 1},
            "equipment": {"hands": "Leather gloves"},
            "cooking_level": 94,
            "cooking_exp": 0,
            "current_cooking": "cook_shark",
            "cooking_success_count": 0,
            "cooking_burn_count": 0,
            "completed_achievements": [],
        }

        ok = handle_cooking_answer(
            _context(player_data, calls, random_values=[0.999])
        )

        self.assertTrue(ok)
        self.assertEqual(player_data["equipment"]["hands"], "Cooking gauntlets")
        self.assertEqual(player_data["inventory"]["Leather gloves"], 1)
        self.assertEqual(player_data["inventory"]["Shark"], 1)
        self.assertEqual(player_data["cooking_burn_count"], 0)
        self.assertEqual(player_data["cooking_success_count"], 1)
        self.assertEqual(calls["xp"], [210.0])

    def test_lava_eel_cooking_always_succeeds_with_source_xp(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Raw lava eel": 1},
            "cooking_level": 53,
            "cooking_exp": 0,
            "current_cooking": "cook_lava_eel",
            "cooking_success_count": 0,
            "cooking_burn_count": 0,
            "completed_achievements": [],
        }

        ok = handle_cooking_answer(_context(player_data, calls, random_values=[1.0]))

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"], {"Raw lava eel": 0, "Lava eel": 1})
        self.assertEqual(player_data["cooking_exp"], 30.0)
        self.assertEqual(player_data["cooking_success_count"], 1)
        self.assertEqual(player_data["cooking_burn_count"], 0)
        self.assertEqual(calls["xp"], [30.0])
        self.assertEqual(calls["saves"], 1)

    def test_poison_karambwan_burns_during_the_started_quest(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Raw karambwan": 1},
            "cooking_level": 1,
            "cooking_exp": 0.0,
            "current_cooking": "cook_poison_karambwan",
            "cooking_success_count": 0,
            "cooking_burn_count": 0,
            "completed_achievements": [],
            "quests": {
                "tai_bwo_wannai_trio": {
                    "started": True,
                    "progress": 1,
                    "completed": False,
                }
            },
        }

        self.assertTrue(
            handle_cooking_answer(_context(player_data, calls, random_values=[1.0]))
        )
        self.assertEqual(
            player_data["inventory"],
            {"Raw karambwan": 0, "Burnt karambwan": 1},
        )
        self.assertEqual(player_data["cooking_exp"], 0.0)
        self.assertEqual(player_data["cooking_burn_count"], 1)
        self.assertEqual(calls["xp"], [])

    def test_thorough_karambwan_requires_completion_and_never_burns(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Raw karambwan": 1},
            "cooking_level": 30,
            "cooking_exp": 0.0,
            "current_cooking": "cook_karambwan_thoroughly",
            "completed_achievements": [],
            "quests": {
                "tai_bwo_wannai_trio": {
                    "started": True,
                    "progress": 6,
                    "completed": True,
                }
            },
        }

        self.assertTrue(
            handle_cooking_answer(_context(player_data, calls, random_values=[1.0]))
        )
        self.assertEqual(
            player_data["inventory"],
            {"Raw karambwan": 0, "Cooked karambwan": 1},
        )
        self.assertEqual(player_data["cooking_exp"], 190.0)
        self.assertEqual(calls["xp"], [190.0])

    def test_wine_bad_outcome_consumes_inputs_without_xp(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Grapes": 1, "Jug of water": 1},
            "cooking_level": 35,
            "cooking_exp": 0.0,
            "current_cooking": "make_wine",
            "cooking_success_count": 0,
            "cooking_burn_count": 0,
            "completed_achievements": [],
        }

        self.assertTrue(
            handle_cooking_answer(
                _context(player_data, calls, random_values=[0.61])
            )
        )

        self.assertEqual(
            player_data["inventory"],
            {"Grapes": 0, "Jug of water": 0, "Jug of bad wine": 1},
        )
        self.assertEqual(player_data["cooking_exp"], 0.0)
        self.assertEqual(player_data["cooking_success_count"], 0)
        self.assertEqual(player_data["cooking_burn_count"], 0)
        self.assertEqual(calls["xp"], [])
        telemetry = player_data["action_telemetry"]["actions"]["cooking:make_wine"]
        self.assertEqual(telemetry["failures"], 1)
        self.assertEqual(telemetry["failure_kinds"], {"bad_wine": 1})
        self.assertEqual(telemetry["outputs"], {"Jug of bad wine": 1})

    def test_dwarven_stout_runtime_records_both_full_vat_outcomes_as_completed(self):
        materials = {
            "Ale yeast": 2,
            "Bucket of water": 4,
            "Barley malt": 4,
            "Hammerstone hops": 8,
            "Beer glass": 16,
        }
        mature_calls = {"xp": [], "saves": 0, "errors": []}
        mature_data = {
            "inventory": {**materials, "The stuff": 1},
            "cooking_level": 19,
            "cooking_exp": 0.0,
            "current_cooking": "brew_dwarven_stout_with_the_stuff",
            "completed_achievements": [],
        }
        self.assertTrue(
            handle_cooking_answer(
                _context(mature_data, mature_calls, random_values=[0.50])
            )
        )
        self.assertEqual(mature_data["inventory"]["Dwarven stout (m)"], 8)
        self.assertEqual(mature_data["inventory"]["Bucket"], 2)
        self.assertEqual(mature_data["inventory"]["The stuff"], 0)
        self.assertEqual(mature_data["cooking_exp"], 215.0)
        self.assertEqual(mature_calls["activity"], ["+8 Dwarven stout (m) · +2 Bucket"])

        ordinary_calls = {"xp": [], "saves": 0, "errors": []}
        ordinary_data = {
            "inventory": dict(materials),
            "cooking_level": 19,
            "cooking_exp": 0.0,
            "current_cooking": "brew_dwarven_stout",
            "completed_achievements": [],
        }
        self.assertTrue(
            handle_cooking_answer(
                _context(ordinary_data, ordinary_calls, random_values=[0.50])
            )
        )
        self.assertEqual(ordinary_data["inventory"]["Dwarven stout"], 8)
        self.assertEqual(ordinary_data["inventory"]["Bucket"], 2)
        self.assertEqual(ordinary_data["cooking_exp"], 215.0)
        telemetry = ordinary_data["action_telemetry"]["actions"][
            "cooking:brew_dwarven_stout"
        ]
        self.assertEqual(telemetry["successes"], 1)
        self.assertEqual(telemetry["failures"], 0)
        self.assertEqual(telemetry["expected_successes"], 1.0)
        self.assertEqual(
            telemetry["outputs"], {"Dwarven stout": 8, "Bucket": 2}
        )

    def test_malting_barley_uses_the_shared_runtime_without_awarding_xp(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Barley": 1},
            "cooking_level": 1,
            "cooking_exp": 0.0,
            "current_cooking": "malt_barley",
            "cooking_success_count": 0,
            "cooking_burn_count": 0,
            "completed_achievements": [],
        }

        self.assertTrue(handle_cooking_answer(_context(player_data, calls)))
        self.assertEqual(player_data["inventory"], {"Barley": 0, "Barley malt": 1})
        self.assertEqual(player_data["cooking_exp"], 0.0)
        self.assertEqual(player_data["cooking_success_count"], 1)
        self.assertEqual(player_data["cooking_burn_count"], 0)
        self.assertEqual(calls["xp"], [])
        telemetry = player_data["action_telemetry"]["actions"]["cooking:malt_barley"]
        self.assertEqual(telemetry["successes"], 1)
        self.assertEqual(telemetry["outputs"], {"Barley malt": 1})

    def test_cooking_runtime_extra_gutting_uses_source_rolls(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Leaping sturgeon": 1},
            "cooking_level": 80,
            "cooking_exp": 0,
            "current_cooking": "gut_leaping_sturgeon",
            "cooking_success_count": 0,
            "cooking_burn_count": 0,
            "completed_achievements": [],
        }

        ok = handle_cooking_answer(_context(player_data, calls, random_values=[1.0, 5.0 / 6.0]))

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"], {"Leaping sturgeon": 0, "Caviar": 1, "Fish offcuts": 1})
        self.assertEqual(player_data["cooking_exp"], 15.0)
        self.assertEqual(player_data["cooking_success_count"], 1)
        self.assertEqual(calls["xp"], [15.0])
        self.assertEqual(calls["saves"], 1)
        telemetry = player_data["action_telemetry"]["actions"]["cooking:gut_leaping_sturgeon"]
        self.assertEqual(telemetry["successes"], 1)
        self.assertEqual(telemetry["outputs"], {"Caviar": 1})

        failed_data = {
            "inventory": {"Leaping trout": 1},
            "cooking_level": 1,
            "cooking_exp": 0,
            "current_cooking": "gut_leaping_trout",
            "cooking_success_count": 0,
            "cooking_burn_count": 0,
            "completed_achievements": [],
        }
        self.assertTrue(handle_cooking_answer(_context(failed_data, calls, random_values=[1.0])))
        self.assertEqual(failed_data["inventory"], {"Leaping trout": 0})
        self.assertEqual(failed_data["cooking_burn_count"], 0)
        failed_telemetry = failed_data["action_telemetry"]["actions"]["cooking:gut_leaping_trout"]
        self.assertEqual(failed_telemetry["failure_kinds"], {"gut": 1})

    def test_cooking_runtime_extra_honors_source_no_level_requirement(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Leaping trout": 1},
            "cooking_level": 0,
            "cooking_exp": 0,
            "current_cooking": "gut_leaping_trout",
            "cooking_success_count": 0,
            "cooking_burn_count": 0,
            "completed_achievements": [],
        }

        self.assertTrue(handle_cooking_answer(_context(player_data, calls, random_values=[0.0, 0.0])))
        self.assertEqual(player_data["inventory"], {"Leaping trout": 0, "Roe": 1, "Fish offcuts": 1})
        self.assertEqual(player_data["cooking_exp"], 10.0)
        self.assertEqual(calls["errors"], [])

        ordinary_calls = {"xp": [], "saves": 0, "errors": []}
        ordinary_data = {
            "inventory": {"Raw shrimps": 1},
            "cooking_level": 0,
            "current_cooking": "cook_shrimps",
        }
        self.assertFalse(handle_cooking_answer(_context(ordinary_data, ordinary_calls)))
        self.assertEqual(ordinary_calls["errors"], [("Insufficient level", "You need level 1 Cooking to cook raw shrimps.")])

    def test_cheese_wheel_actions_report_real_outputs_and_do_not_charge_urns(self):
        churn_calls = {"xp": [], "saves": 0, "errors": []}
        churn_data = {
            "inventory": {
                "Bucket of milk": 1,
                "Cracked cooking urn (r)": 1,
            },
            "cooking_level": 48,
            "cooking_exp": 0.0,
            "current_cooking": "churn_milk_cheese_wheel",
            "completed_achievements": [],
        }

        self.assertTrue(
            handle_cooking_answer(
                _context(churn_data, churn_calls, random_values=[1.0])
            )
        )
        self.assertEqual(
            churn_data["inventory"],
            {
                "Bucket of milk": 0,
                "Cracked cooking urn (r)": 1,
                "Cheese wheel": 1,
                "Bucket": 1,
            },
        )
        self.assertEqual(churn_data["cooking_exp"], 40.5)
        self.assertEqual(churn_data.get("urn_progress_cooking", 0.0), 0.0)
        self.assertEqual(churn_calls["xp"], [40.5])
        self.assertEqual(
            churn_calls["activity"],
            ["+1 Cheese wheel · +1 Bucket"],
        )
        churn_telemetry = churn_data["action_telemetry"]["actions"][
            "cooking:churn_milk_cheese_wheel"
        ]
        self.assertEqual(
            churn_telemetry["outputs"],
            {"Cheese wheel": 1, "Bucket": 1},
        )

        slice_calls = {"xp": [], "saves": 0, "errors": []}
        slice_data = {
            "inventory": {"Cheese wheel": 1},
            "cooking_level": 48,
            "cooking_exp": 0.0,
            "current_cooking": "slice_cheese_wheel",
            "completed_achievements": [],
        }
        self.assertTrue(
            handle_cooking_answer(
                _context(slice_data, slice_calls, random_values=[0.0])
            )
        )
        self.assertEqual(
            slice_data["inventory"],
            {"Cheese wheel": 0, "Cheese": 5},
        )
        self.assertEqual(slice_data["cooking_exp"], 20.0)
        self.assertEqual(slice_calls["xp"], [20.0])
        self.assertEqual(slice_calls["activity"], ["+5 Cheese"])
        slice_telemetry = slice_data["action_telemetry"]["actions"][
            "cooking:slice_cheese_wheel"
        ]
        self.assertEqual(slice_telemetry["outputs"], {"Cheese": 5})

    def test_smithing_iron_failure_consumes_ore_and_records_telemetry(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Iron ore": 1},
            "smithing_level": 15,
            "smithing_exp": 0,
            "crafting_level": 1,
            "current_smith": "smelt_iron_bar",
            "completed_achievements": [],
        }

        ok = handle_smithing_answer(_context(player_data, calls, random_values=[0.99]))

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"]["Iron ore"], 0)
        self.assertNotIn("Iron bar", player_data["inventory"])
        self.assertEqual(player_data["smithing_exp"], 0)
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["The ore was too impure"])
        telemetry = player_data["action_telemetry"]["actions"]["smithing:smelt_iron_bar"]
        self.assertEqual(telemetry["attempts"], 1)
        self.assertEqual(telemetry["failures"], 1)
        self.assertEqual(telemetry["failure_kinds"], {"smelt_fail": 1})
        self.assertAlmostEqual(telemetry["expected_successes"], 0.51)

    def test_smithing_dragon_sq_shield_assembly_consumes_both_halves(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Shield left half": 1, "Shield right half": 1},
            "smithing_level": 60,
            "smithing_exp": 0,
            "crafting_level": 1,
            "current_smith": "repair_dragon_sq_shield",
            "quests": {"dorics_quest": {"completed": False}},
            "completed_achievements": [],
        }

        ok = handle_smithing_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"], {"Shield left half": 0, "Shield right half": 0, "Dragon sq shield": 1})
        self.assertAlmostEqual(player_data["smithing_exp"], 70.0)
        self.assertEqual(calls["xp"], [70.0])
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        telemetry = player_data["action_telemetry"]["actions"]["smithing:repair_dragon_sq_shield"]
        self.assertEqual(telemetry["attempts"], 1)
        self.assertEqual(telemetry["successes"], 1)

    def test_smithing_cannonballs_requires_quest_and_preserves_ammo_mould(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Steel bar": 1, "Ammo mould": 1},
            "smithing_level": 35,
            "smithing_exp": 0,
            "crafting_level": 1,
            "current_smith": "forge_cannonballs",
            "quests": {"dwarf_cannon": {"completed": False}},
            "completed_achievements": [],
        }

        self.assertFalse(handle_smithing_answer(_context(player_data, calls)))
        self.assertTrue(calls.get("deactivated"))
        self.assertIn("Dwarf Cannon", calls["errors"][0][1])

        calls = {"xp": [], "saves": 0, "errors": []}
        player_data["quests"]["dwarf_cannon"]["completed"] = True
        self.assertTrue(handle_smithing_answer(_context(player_data, calls)))
        self.assertEqual(player_data["inventory"], {"Steel bar": 0, "Ammo mould": 1, "Cannonball": 4})
        self.assertEqual(player_data["smithing_exp"], 25.6)
        telemetry = player_data["action_telemetry"]["actions"]["smithing:forge_cannonballs"]
        self.assertEqual(telemetry["outputs"], {"Cannonball": 4})

    def test_smithing_consumes_owned_coal_bag_before_loose_coal(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Iron ore": 1, "Coal": 2},
            "smithing_level": 30,
            "smithing_exp": 0,
            "crafting_level": 1,
            "current_smith": "smelt_steel_bar",
            "completed_achievements": [],
            "dungeoneering": {
                "coal_bag_owned": True,
                "coal_bag_coal": 1,
            },
        }

        ok = handle_smithing_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"]["Iron ore"], 0)
        self.assertEqual(player_data["inventory"]["Coal"], 1)
        self.assertEqual(player_data["inventory"]["Steel bar"], 1)
        self.assertEqual(player_data["dungeoneering"]["coal_bag_coal"], 0)
        self.assertEqual(calls["errors"], [])


class TestCarriedOverlayWrapper(unittest.TestCase):
    """The overlay wrapper that runs a skilling tick through the 28-slot pack."""

    def _mining_ctx(self, player_data):
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        ctx = _context(player_data, calls)
        return ctx, calls

    def _fake_gather(self, ctx):
        # Stand-in gathering handler: one Coal per acting tick.
        inv = ctx.player_data.setdefault("inventory", {})
        inv["Coal"] = inv.get("Coal", 0) + 1
        return True

    def test_gathering_banks_on_the_29th_answer_with_no_xp(self):
        player_data = {"inventory": {}, "current_ore": "copper_ore"}
        for _ in range(28):
            ctx, calls = self._mining_ctx(player_data)
            result = run_answer_with_carried_overlay(ctx, "mining", self._fake_gather)
            self.assertTrue(result)
        self.assertEqual(player_data["inventory"]["Coal"], 28)
        self.assertEqual(player_data["carried_inventory"]["copper_ore"], {"Coal": 28})
        self.assertEqual(player_data["carried_churn"]["copper_ore"], 28)

        # 29th answer buys the bank-run: handler is not called (Coal stays 28),
        # a bank-run toast fires, and the pack + churn reset.
        ctx, calls = self._mining_ctx(player_data)
        inventory_refreshes = []
        ctx.refresh_carried_inventory = lambda: inventory_refreshes.append(True)
        result = run_answer_with_carried_overlay(ctx, "mining", self._fake_gather)
        self.assertTrue(result)
        self.assertEqual(player_data["inventory"]["Coal"], 28)
        self.assertTrue(any("Bank run" in msg for msg in calls["activity"]))
        self.assertEqual(inventory_refreshes, [True])
        self.assertNotIn("copper_ore", player_data.get("carried_inventory", {}))
        self.assertNotIn("copper_ore", player_data.get("carried_churn", {}))

        # 30th gathers again from a fresh pack.
        ctx, calls = self._mining_ctx(player_data)
        run_answer_with_carried_overlay(ctx, "mining", self._fake_gather)
        self.assertEqual(player_data["inventory"]["Coal"], 29)
        self.assertEqual(player_data["carried_inventory"]["copper_ore"], {"Coal": 1})

    def test_manual_request_enters_the_same_review_paced_bank_run(self):
        player_data = {
            "inventory": {"Coal": 3},
            "current_ore": "copper_ore",
            "review_bank_run_requested_target": "copper_ore",
        }
        ctx, calls = self._mining_ctx(player_data)
        acted = []

        self.assertTrue(
            run_answer_with_carried_overlay(
                ctx,
                "mining",
                lambda _ctx: acted.append(True) or True,
            )
        )

        self.assertEqual(acted, [])
        self.assertNotIn("review_bank_run_requested_target", player_data)
        self.assertTrue(any("Bank run" in msg for msg in calls["activity"]))
        self.assertTrue(
            player_data.get("skilling_bank_run") == {}
            or int(player_data["skilling_bank_run"]["reviews_remaining"]) > 0
        )

    def test_full_run_energy_credit_waives_and_consumes_the_next_moving_trip(self):
        player_data = {
            "inventory": {"Coal": 28},
            "current_ore": "copper_ore",
            "carried_inventory": {"copper_ore": {"Coal": 28}},
            "carried_churn": {"copper_ore": 28},
            "agility_run_energy_credit_pct": 100,
        }
        ctx, calls = self._mining_ctx(player_data)

        self.assertTrue(
            run_answer_with_carried_overlay(
                ctx,
                "mining",
                self._fake_gather,
            )
        )

        self.assertEqual(player_data["inventory"]["Coal"], 29)
        self.assertEqual(
            player_data["carried_inventory"]["copper_ore"],
            {"Coal": 1},
        )
        self.assertEqual(player_data["agility_run_energy_credit_pct"], 0)
        self.assertEqual(
            player_data["agility_last_travel"][
                "run_energy_credit_used_pct"
            ],
            100,
        )
        self.assertEqual(
            player_data["agility_last_travel"]["adjusted_reviews"],
            0.0,
        )
        self.assertEqual(calls["activity"], [])

    def test_drop_mode_destroys_the_product_never_banks_and_keeps_nothing(self):
        # Drop is power-gathering: XP is kept, the product is destroyed. Previously
        # Drop kept every gathered item AND paid no bank-run review, so it strictly
        # dominated Keep and the whole Keep/Drop tradeoff was meaningless.
        player_data = {
            "inventory": {},
            "current_ore": "copper_ore",
            "carried_keep_drop": {"copper_ore": "drop"},
        }
        for _ in range(40):
            ctx, calls = self._mining_ctx(player_data)
            result = run_answer_with_carried_overlay(ctx, "mining", self._fake_gather)
            self.assertTrue(result)
            self.assertEqual(calls["activity"], [])  # never a bank-run toast
        # 40 gathers, XP awarded by the handler, but zero materials kept.
        self.assertEqual(player_data["inventory"].get("Coal", 0), 0)
        self.assertEqual(player_data.get("carried_inventory", {}), {})
        self.assertEqual(player_data.get("carried_churn", {}), {})

    def test_drop_mode_still_consumes_real_inputs_only_the_product_is_dropped(self):
        # A consumed input (fishing bait) is a real cost and must not be refunded;
        # only the produced item is destroyed.
        def bait_fish(ctx):
            inv = ctx.player_data.setdefault("inventory", {})
            if inv.get("Fishing bait", 0) < 1:
                return False
            inv["Fishing bait"] -= 1
            inv["Raw fish"] = inv.get("Raw fish", 0) + 1
            return True

        player_data = {
            "inventory": {"Fishing bait": 5},
            "current_fishing": "x",
            "carried_keep_drop": {"x": "drop"},
        }
        ctx, _calls = self._mining_ctx(player_data)
        run_answer_with_carried_overlay(ctx, "fishing", bait_fish)
        self.assertEqual(player_data["inventory"]["Fishing bait"], 4)  # consumed, not refunded
        self.assertEqual(player_data["inventory"].get("Raw fish", 0), 0)  # dropped

    def test_coal_bag_defers_the_bank_run(self):
        # Owning a Coal bag raises coal capacity to 55, so 40 gathers do not bank
        # (they would without the bag, which banks at 28).
        player_data = {"inventory": {"Coal bag": 1}, "current_ore": "coal_rock"}
        for _ in range(40):
            ctx, calls = self._mining_ctx(player_data)
            run_answer_with_carried_overlay(ctx, "mining", self._fake_gather)
            self.assertEqual(calls["activity"], [])  # no bank-run yet
        self.assertEqual(player_data["carried_churn"]["coal_rock"], 40)
        self.assertEqual(player_data["inventory"]["Coal"], 40)

    def test_a_dry_gather_produces_no_churn_and_folds_nothing(self):
        # A gather can succeed as a review but roll no product (a dry action). It
        # must not churn or fold, or an unlucky streak would rack up phantom slots
        # and force bank runs with nothing to deposit.
        def dry_gather(ctx):
            return True  # counted as an action, but produced nothing

        player_data = {"inventory": {}, "current_ore": "copper"}
        for _ in range(50):
            ctx, _calls = self._mining_ctx(player_data)
            run_answer_with_carried_overlay(ctx, "mining", dry_gather)
        self.assertEqual(player_data.get("carried_churn", {}), {})
        self.assertEqual(player_data.get("carried_inventory", {}), {})

    def test_untracked_handler_key_runs_untouched(self):
        player_data = {"inventory": {}}
        marker = {"called": False}

        def handler(ctx):
            marker["called"] = True
            return True

        ctx, calls = self._mining_ctx(player_data)
        result = run_answer_with_carried_overlay(ctx, "quest", handler)
        self.assertTrue(result)
        self.assertTrue(marker["called"])
        self.assertNotIn("carried_inventory", player_data)

    def test_manual_bank_run_for_an_untracked_handler_spends_the_review(self):
        player_data = {
            "inventory": {},
            "review_bank_run_requested_handler": "utility",
        }
        marker = {"called": False}
        ctx, calls = self._mining_ctx(player_data)

        result = run_answer_with_carried_overlay(
            ctx,
            "utility",
            lambda _ctx: marker.__setitem__("called", True),
        )

        self.assertTrue(result)
        self.assertFalse(marker["called"])
        self.assertNotIn("review_bank_run_requested_handler", player_data)
        self.assertEqual(calls["activity"], ["Bank run — arrived at the bank"])
        self.assertEqual(calls["saves"], 1)

    def test_non_carried_bank_requests_complete_without_stealing_review_progress(self):
        for handler_key, target_key, target_id in (
            ("utility", "current_utility", "shooting_stars"),
            ("quest", "current_quest", "rune_mysteries"),
        ):
            with self.subTest(handler_key=handler_key):
                player_data = {
                    "inventory": {},
                    target_key: target_id,
                    "skilling_bank_run_requested": target_id,
                }
                marker = {"called": False}

                def handler(_ctx):
                    marker["called"] = True
                    return True

                ctx, calls = self._mining_ctx(player_data)
                result = run_answer_with_carried_overlay(ctx, handler_key, handler)
                self.assertTrue(result)
                self.assertTrue(marker["called"])
                self.assertNotIn("skilling_bank_run_requested", player_data)
                self.assertEqual(calls["activity"], ["Bank run — arrived and ready"])
                self.assertEqual(calls["saves"], 1)


class TestProcessingPackOverlay(unittest.TestCase):
    """Processing skills draw recipe inputs from the carried pack, not the bank."""

    def _firemaking_ctx(self, player_data):
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        return _context(player_data, calls, random_values=[0.0] * 200), calls

    def _base_player_data(self, logs):
        return {
            "inventory": {"Logs": logs},
            "firemaking_level": 1,
            "firemaking_exp": 0,
            "current_firemaking": "logs",
            "completed_achievements": [],
        }

    def test_runecrafting_consumes_hood_withdrawn_essence_from_the_carried_pack(self):
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = {
            "inventory": {"Rune essence": 27, "Air talisman": 1},
            "equipment": {
                "head": "Master runecrafter hat",
                "body": "Master runecrafter body",
                "legs": "Master runecrafter skirt",
                "feet": "Master runecrafter boots",
            },
            "quests": {
                "rune_mysteries": {
                    "started": True,
                    "progress": 6,
                    "completed": True,
                }
            },
            "wicked_hood": {"fed_altars": ["air"]},
            "current_runecrafting": "craft_air_runes",
            "runecrafting_level": 1,
            "runecrafting_exp": 0.0,
            "completed_achievements": [],
            "carried_inventory": {
                "craft_air_runes": {"Rune essence": 27, "Air talisman": 1}
            },
            "carried_primed_targets": {"craft_air_runes": True},
            "carried_churn": {"craft_air_runes": 0},
            "skilling_bank_run": {},
        }

        result = run_answer_with_carried_overlay(
            _context(player_data, calls, random_values=[0.0] * 64),
            "runecrafting",
            handle_runecrafting_answer,
        )

        self.assertTrue(result)
        self.assertEqual(player_data["inventory"]["Rune essence"], 0)
        self.assertEqual(player_data["inventory"]["Air rune"], 54)
        self.assertAlmostEqual(player_data["runecrafting_exp"], 141.75)
        self.assertEqual(
            player_data["carried_inventory"]["craft_air_runes"],
            {"Air talisman": 1},
        )
        self.assertEqual(calls["errors"], [])

    def test_talisman_staff_binding_consumes_the_carried_recipe_not_the_bank(self):
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        player_data = {
            "inventory": {"Runecrafting staff": 2, "Air talisman": 2},
            "equipment": {},
            "quests": {
                "rune_mysteries": {
                    "started": True,
                    "progress": 6,
                    "completed": True,
                }
            },
            "current_runecrafting": "bind_air_talisman_staff",
            "runecrafting_level": 1,
            "runecrafting_exp": 0.0,
            "completed_achievements": [],
            "carried_advanced_targets": {"bind_air_talisman_staff": True},
            "carried_layout": {
                "bind_air_talisman_staff": {
                    "Runecrafting staff": 1,
                    "Air talisman": 1,
                }
            },
        }

        result = run_answer_with_carried_overlay(
            _context(player_data, calls, random_values=[0.0] * 64),
            "runecrafting",
            handle_runecrafting_answer,
        )

        self.assertTrue(result)
        self.assertEqual(player_data["inventory"]["Runecrafting staff"], 1)
        self.assertEqual(player_data["inventory"]["Air talisman"], 1)
        self.assertEqual(player_data["inventory"]["Air talisman staff"], 1)
        self.assertNotIn(
            "bind_air_talisman_staff", player_data["carried_inventory"]
        )
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["errors"], [])

    def test_first_engagement_primes_the_pack_for_free_and_acts(self):
        player_data = self._base_player_data(5)
        ctx, calls = self._firemaking_ctx(player_data)
        result = run_answer_with_carried_overlay(ctx, "firemaking", handle_firemaking_answer)

        self.assertTrue(result)
        self.assertEqual(calls["activity"], [])  # no bank-run toast on priming
        self.assertEqual(player_data["inventory"]["Logs"], 4)
        self.assertEqual(player_data["inventory"]["Ashes"], 1)
        # The pack was seeded with all 5 logs, then one was consumed.
        self.assertEqual(player_data["carried_inventory"]["logs"], {"Logs": 4})
        self.assertIn("logs", player_data["carried_primed_targets"])

    def test_manual_bank_run_request_uses_the_real_route_before_acting(self):
        player_data = self._base_player_data(5)
        player_data.update(
            {
                "carried_inventory": {"logs": {"Logs": 5}},
                "carried_primed_targets": {"logs": True},
                "carried_churn": {"logs": 0},
                "skilling_bank_run_requested": "logs",
            }
        )
        ctx, calls = self._firemaking_ctx(player_data)

        result = run_answer_with_carried_overlay(
            ctx, "firemaking", handle_firemaking_answer
        )

        self.assertTrue(result)
        self.assertEqual(player_data["inventory"], {"Logs": 5})
        self.assertNotIn("skilling_bank_run_requested", player_data)
        self.assertEqual(player_data["firemaking_exp"], 0)
        self.assertIn("Bank run", calls["activity"][-1])

    def test_smithing_pack_uses_bag_coal_first_through_the_real_handler(self):
        player_data = {
            "inventory": {"Iron ore": 3, "Coal": 3},
            "smithing_level": 30,
            "smithing_exp": 0,
            "crafting_level": 1,
            "current_smith": "smelt_steel_bar",
            "completed_achievements": [],
            "dungeoneering": {
                "coal_bag_owned": True,
                "coal_bag_coal": 2,
            },
        }
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}

        result = run_answer_with_carried_overlay(
            _context(player_data, calls, random_values=[0.0] * 20),
            "smithing",
            handle_smithing_answer,
        )

        self.assertTrue(result)
        self.assertEqual(player_data["inventory"]["Iron ore"], 2)
        self.assertEqual(player_data["inventory"]["Coal"], 3)
        self.assertEqual(player_data["inventory"]["Steel bar"], 1)
        self.assertEqual(player_data["dungeoneering"]["coal_bag_coal"], 0)
        self.assertEqual(
            player_data["carried_inventory"]["smelt_steel_bar"],
            {"Iron ore": 2},
        )
        self.assertEqual(calls["errors"], [])

        player_data["dungeoneering"]["coal_bag_coal"] = 1
        for _review in range(10):
            result = run_answer_with_carried_overlay(
                _context(player_data, calls, random_values=[0.0] * 20),
                "smithing",
                handle_smithing_answer,
            )
            self.assertTrue(result)
            if player_data["inventory"].get("Steel bar") == 2:
                break

        self.assertEqual(player_data["inventory"]["Steel bar"], 2)
        self.assertEqual(player_data["inventory"]["Iron ore"], 1)
        self.assertEqual(player_data["inventory"]["Coal"], 2)
        self.assertEqual(player_data["dungeoneering"]["coal_bag_coal"], 0)
        self.assertEqual(
            player_data["carried_inventory"]["smelt_steel_bar"],
            {"Iron ore": 1, "Coal": 1},
        )

    def test_pack_depletes_then_forces_a_bank_run_leaving_bank_remainder(self):
        # 30 logs but a 28-slot pack: the pack primes to 28, 28 actions drain it,
        # and 2 logs never left the bank.
        player_data = self._base_player_data(30)
        for _ in range(28):
            ctx, calls = self._firemaking_ctx(player_data)
            result = run_answer_with_carried_overlay(ctx, "firemaking", handle_firemaking_answer)
            self.assertTrue(result)
            self.assertEqual(calls["activity"], [])
        self.assertEqual(player_data["inventory"]["Ashes"], 28)
        self.assertEqual(player_data["inventory"]["Logs"], 2)
        self.assertEqual(player_data["carried_inventory"].get("logs", {}), {})

        # The pack is dry but the bank has 2 more: this answer is spent banking,
        # not firemaking (no XP tick, a bank-run toast, no additional Ashes).
        ctx, calls = self._firemaking_ctx(player_data)
        result = run_answer_with_carried_overlay(ctx, "firemaking", handle_firemaking_answer)
        self.assertTrue(result)
        self.assertTrue(any("Bank run" in msg for msg in calls["activity"]))
        self.assertEqual(player_data["inventory"]["Ashes"], 28)
        self.assertEqual(player_data["carried_inventory"]["logs"], {"Logs": 2})

        # And firemaking resumes from the repacked (now 2-log) pack.
        ctx, calls = self._firemaking_ctx(player_data)
        result = run_answer_with_carried_overlay(ctx, "firemaking", handle_firemaking_answer)
        self.assertTrue(result)
        self.assertEqual(player_data["inventory"]["Ashes"], 29)
        self.assertEqual(player_data["inventory"]["Logs"], 1)

    def test_out_of_materials_in_both_pack_and_bank_fails_normally_no_forced_loop(self):
        player_data = self._base_player_data(0)
        ctx, calls = self._firemaking_ctx(player_data)
        result = run_answer_with_carried_overlay(ctx, "firemaking", handle_firemaking_answer)
        # The handler's own "out of materials" path fires; no bank-run is forced
        # since the bank cannot supply it either.
        self.assertFalse(result)
        self.assertEqual(calls["activity"], [])
        self.assertTrue(calls.get("deactivated"))

    def test_scoped_inventory_never_leaks_the_capped_bank_to_saves_or_achievements(self):
        # While a processing tick runs, player_data["inventory"] is temporarily
        # capped to what the pack holds. The handler must not persist that or
        # evaluate achievements against it: a save would write a truncated bank to
        # disk, and a "own N logs" achievement would see only the pack's 28.
        observed = {"saves": [], "achievements": []}
        player_data = {
            "inventory": {"Logs": 100},
            "firemaking_level": 1,
            "firemaking_exp": 0,
            "current_firemaking": "logs",
            "completed_achievements": [],
        }
        calls = {"xp": [], "errors": [], "activity": []}
        ctx = _context(player_data, calls, random_values=[0.0] * 20)
        ctx = dataclasses.replace(
            ctx,
            save_player_data=lambda: observed["saves"].append(player_data["inventory"].get("Logs")),
            check_achievements=lambda data: observed["achievements"].append(data["inventory"].get("Logs")),
        )

        run_answer_with_carried_overlay(ctx, "firemaking", handle_firemaking_answer)

        # Bank truly went 100 -> 99 (one log burned), even though the pack held 28.
        self.assertEqual(player_data["inventory"]["Logs"], 99)
        self.assertEqual(observed["achievements"], [99])
        self.assertNotIn(27, observed["saves"])
        self.assertEqual(observed["saves"], [99])

    def test_skill_availability_is_computed_from_the_bank_not_the_capped_pack(self):
        # Same leak class: the availability UI must reflect the real bank, or a
        # skill/recipe can look unavailable while the bank is full of materials.
        from ankiscape.runtime.runtime_actions import handle_crafting_answer

        observed = {"refresh": []}
        player_data = {
            "inventory": {"Uncut opal": 100},
            "crafting_level": 99,
            "crafting_exp": 0,
            "current_craft": "cut_opal",
            "completed_achievements": [],
        }
        calls = {"xp": [], "errors": [], "activity": []}
        ctx = _context(player_data, calls, random_values=[0.0] * 20)
        ctx = dataclasses.replace(
            ctx,
            refresh_skill_availability=lambda: observed["refresh"].append(
                player_data["inventory"].get("Uncut opal")
            ),
        )

        run_answer_with_carried_overlay(ctx, "crafting", handle_crafting_answer)

        self.assertEqual(player_data["inventory"]["Uncut opal"], 99)
        # One full refresh, after reconciliation, seeing the true bank (not 27).
        self.assertEqual(observed["refresh"], [99])

    def test_churn_per_action_matches_real_runescape_trip_lengths(self):
        # Balance guard for the invented churn=28 knob. Cross-checked against RS:
        # smelting bronze carries 14 tin + 14 copper, so 14 smelts per trip; fletching
        # 28 logs into *stacking* arrow shafts is 28 actions per trip. Regression here
        # means slot accounting has drifted (e.g. a stackable read as unstackable,
        # which once made Fletching bank every other action).
        from ankiscape.runtime import runtime_actions as RA

        cases = [
            ("fletching", "current_fletch", "arrow_shafts", {"Logs": 500}, "fletching_level", 1),
            ("firemaking", "current_firemaking", "logs", {"Logs": 500}, "firemaking_level", 1),
            ("cooking", "current_cooking", "cook_shrimps", {"Raw shrimps": 500}, "cooking_level", 1),
            ("smithing", "current_smith", "smelt_bronze_bar",
             {"Tin ore": 500, "Copper ore": 500}, "smithing_level", 2),
        ]
        for key, target_key, target, inventory, level_key, expected_churn in cases:
            with self.subTest(skill=key):
                player_data = {
                    "inventory": dict(inventory), target_key: target,
                    level_key: 99, f"{key}_exp": 0, "completed_achievements": [],
                }
                calls = {"xp": [], "errors": [], "activity": []}
                ctx = _context(player_data, calls, random_values=[0.0] * 40)
                run_answer_with_carried_overlay(ctx, key, RA.answer_handler_for_key(key))
                self.assertEqual(player_data["carried_churn"][target], expected_churn)

    def test_advanced_layout_seeds_the_pack_instead_of_the_casual_full_fill(self):
        player_data = self._base_player_data(100)
        player_data["carried_advanced_targets"] = {"logs": True}
        player_data["carried_layout"] = {"logs": {"Logs": 6}}
        ctx, calls = self._firemaking_ctx(player_data)
        result = run_answer_with_carried_overlay(ctx, "firemaking", handle_firemaking_answer)

        self.assertTrue(result)
        # Seeded to the saved layout's 6, not a casual full-capacity fill of 28;
        # only the 1 log actually consumed leaves the real bank (99 stay banked).
        self.assertEqual(player_data["inventory"]["Logs"], 99)
        self.assertEqual(player_data["carried_inventory"]["logs"], {"Logs": 5})

    def test_advanced_fletching_pack_carries_and_preserves_reusable_chisel(self):
        player_data = {
            "inventory": {"Long kebbit spike": 2, "Chisel": 1},
            "fletching_level": 42,
            "fletching_exp": 0,
            "current_fletch": "fletch_long_kebbit_bolts",
            "completed_achievements": [],
            "carried_advanced_targets": {"fletch_long_kebbit_bolts": True},
            "carried_layout": {
                "fletch_long_kebbit_bolts": {
                    "Long kebbit spike": 2,
                    "Chisel": 1,
                }
            },
        }
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}

        result = run_answer_with_carried_overlay(
            _context(player_data, calls),
            "fletching",
            handle_fletching_answer,
        )

        self.assertTrue(result)
        self.assertEqual(player_data["inventory"]["Long kebbit spike"], 1)
        self.assertEqual(player_data["inventory"]["Chisel"], 1)
        self.assertEqual(player_data["inventory"]["Long kebbit bolts"], 6)
        self.assertEqual(player_data["carried_inventory"]["fletch_long_kebbit_bolts"],
                         {"Long kebbit spike": 1, "Chisel": 1})


if __name__ == "__main__":
    unittest.main()
