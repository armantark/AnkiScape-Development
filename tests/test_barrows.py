from __future__ import annotations

import copy
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.barrows_data import (
    BARROWS_BROTHER_DATA,
    BARROWS_MAX_REWARD_POTENTIAL,
)
from ankiscape.logic.barrows_logic import (
    apply_barrows_command_pure,
    apply_barrows_review_pure,
    barrows_reward_potential_pure,
    barrows_view_pure,
    default_barrows_state_pure,
    sanitize_barrows_state_pure,
)
from ankiscape.core.constants import EQUIPMENT_DATA, ITEM_DEFINITIONS, ORE_DATA, UTILITY_ACTIVITY_DATA
from ankiscape.data.equipment_condition_data import EQUIPMENT_CONDITION_DATA
from ankiscape.logic.equipment_instance_logic import advance_equipped_condition_pure
from ankiscape.data.item_values import ITEM_VALUES
from ankiscape.runtime.runtime_actions import RuntimeActionContext, handle_utility_answer
from ankiscape.core.storage_pure import CURRENT_CONFIG_VERSION, default_player_data, migrate_loaded_data


def _player(**overrides):
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data.update(
        {
            "attack_level": 80,
            "strength_level": 80,
            "defense_level": 80,
            "ranged_level": 80,
            "magic_level": 80,
            "prayer_level": 80,
            "constitution_level": 80,
            "agility_level": 80,
            "combat_lifepoints": 800,
            "combat_prayer_points": 800,
            "combat_auto_eat_food": [],
            "combat_auto_flee_percent": 0,
            "inventory": {"Shark": 8, "Coins": 500_000},
            "equipment": {},
            "current_combat_target": "chicken",
        }
    )
    data.update(overrides)
    return data


def _combat_result(
    *,
    killed=False,
    died=False,
    lifepoints=None,
    player_damage=50,
    enemy_damage=10,
    ticks_elapsed=6,
):
    def _apply(data, _enemies, _equipment, **_kwargs):
        updated = copy.deepcopy(data)
        before = int(updated["combat_encounter"]["enemy_lifepoints"])
        after = 0 if killed else int(lifepoints if lifepoints is not None else before)
        updated["combat_encounter"]["enemy_lifepoints"] = max(0, after)
        if died:
            updated["combat_encounter"] = {}
        return updated, True, {
            "killed": killed,
            "died": died,
            "enemy_lifepoints": after,
            "player_damage": player_damage,
            "enemy_damage": enemy_damage,
            "ticks_elapsed": ticks_elapsed,
            "xp_rewards": {"attack_exp": 4.0} if player_damage else {},
        }

    return _apply


def _active_brother(player, brother_id, *, lifepoints=500, protected_class="melee"):
    state = default_barrows_state_pure()
    state.update(
        {
            "active": True,
            "phase": "mounds",
            "available_brothers": list(BARROWS_BROTHER_DATA),
            "surface_queue": [brother_id],
            "active_encounter": {
                "kind": "brother",
                "enemy_id": brother_id,
                "lifepoints": lifepoints,
                "encounter": {
                    "target_id": "barrows",
                    "enemy_lifepoints": lifepoints,
                },
                "protected_class": protected_class,
                "protection_damage": 0,
            },
        }
    )
    player["barrows"] = state
    player["activity_session"] = {"active_id": "barrows"}
    return player


class BarrowsDataTests(unittest.TestCase):
    def test_horizontal_catalog_registers_activity_brothers_and_conditioned_weapons(self):
        activity = UTILITY_ACTIVITY_DATA["barrows"]
        self.assertEqual(activity["group"], "minigames")
        self.assertEqual(len(activity["outputs"]), 7)
        self.assertEqual(BARROWS_BROTHER_DATA["dharok"]["max_hit"], 300)
        self.assertEqual(BARROWS_BROTHER_DATA["akrisae"]["quest_gate"], "ritual_of_the_mahjarrat")

        item_names = {definition.storage_key for definition in ITEM_DEFINITIONS}
        for item_name in ("Ahrim's staff", "Dharok's greataxe 0", "Akrisae's war mace 75"):
            self.assertIn(item_name, item_names)
            self.assertIn(item_name, EQUIPMENT_DATA)
        self.assertEqual(EQUIPMENT_DATA["Akrisae's war mace"].skill_requirements[-1], ("prayer", 70))
        self.assertEqual(
            ITEM_VALUES["Dharok's greataxe 100"],
            ITEM_VALUES["Dharok's greataxe (deg)"],
        )

    def test_condition_families_use_full_then_25_percent_identities(self):
        family = "barrows_dharok"
        spec = EQUIPMENT_CONDITION_DATA[family]
        self.assertEqual(spec["full_name"], "Dharok's greataxe")
        player = {
            "inventory": {},
            "equipment": {"weapon": "Dharok's greataxe"},
            "equipment_instances": {
                "equipment-1": {
                    "family_id": family,
                    "item_name": "Dharok's greataxe",
                    "condition": 90_000,
                    "location": "equipped:weapon",
                }
            },
            "equipment_instance_next_id": 2,
        }
        degraded, events = advance_equipped_condition_pure(player, 1, EQUIPMENT_CONDITION_DATA)
        self.assertEqual(degraded["equipment"]["weapon"], "Dharok's greataxe 100")
        self.assertEqual(events[0]["after_name"], "Dharok's greataxe 100")


class BarrowsStateAndCommandTests(unittest.TestCase):
    def test_entry_builds_reachable_nine_room_run_and_rotm_adds_akrisae(self):
        player = _player()
        player["quests"]["ritual_of_the_mahjarrat"]["completed"] = True
        entered, ok, info = apply_barrows_command_pure(player, "enter", rng=lambda: 0.0)
        self.assertTrue(ok, info)
        view = barrows_view_pure(entered)
        self.assertTrue(view["active"])
        self.assertEqual(entered["activity_session"], {"active_id": "barrows"})
        self.assertEqual(len(view["usable_edges"]), 8)
        self.assertEqual(view["start_room"], 0)
        self.assertEqual(view["hidden_brother"], "ahrim")
        self.assertIn("akrisae", view["available_brothers"])
        self.assertTrue(view["route_to_center"])
        self.assertEqual(view["route_to_center"][-1], 4)

    def test_every_generated_topology_is_one_open_perimeter_path_plus_one_central_door(self):
        perimeter = {"0-1", "1-2", "2-5", "5-8", "7-8", "6-7", "3-6", "0-3"}
        center = {"1-4", "3-4", "4-5", "4-7"}
        for start_index in range(4):
            for locked_index in range(8):
                for center_index in range(4):
                    with self.subTest(start=start_index, locked=locked_index, center=center_index):
                        rolls = iter(
                            (
                                (start_index + 0.25) / 4,
                                (locked_index + 0.25) / 8,
                                (center_index + 0.25) / 4,
                            )
                        )
                        entered, ok, info = apply_barrows_command_pure(
                            _player(), "enter", rng=lambda: next(rolls)
                        )
                        self.assertTrue(ok, info)
                        view = barrows_view_pure(entered)
                        edges = set(view["usable_edges"])
                        self.assertEqual(len(edges), 8)
                        self.assertEqual(len(edges & perimeter), 7)
                        self.assertEqual(len(edges & center), 1)
                        self.assertEqual(view["route_to_center"][-1], 4)

    def test_leave_preserves_run_but_resets_an_interrupted_brother(self):
        entered, ok, _ = apply_barrows_command_pure(_player(), "enter", rng=lambda: 0.0)
        self.assertTrue(ok)
        state = entered["barrows"]
        state["active_encounter"] = {
            "kind": "brother",
            "enemy_id": "dharok",
            "lifepoints": 123,
            "encounter": {"target_id": "barrows", "enemy_lifepoints": 123},
            "protected_class": "melee",
            "protection_damage": 0,
        }
        left, ok, info = apply_barrows_command_pure(entered, "leave")
        self.assertTrue(ok, info)
        self.assertTrue(left["barrows"]["suspended"])
        self.assertFalse(left["barrows"]["active"])
        self.assertEqual(left["barrows"]["active_encounter"]["lifepoints"], 1000)
        resumed, ok, _ = apply_barrows_command_pure(left, "enter")
        self.assertTrue(ok)
        self.assertEqual(resumed["barrows"]["active_encounter"]["lifepoints"], 1000)

    def test_leave_preserves_an_interrupted_crypt_creature_lifepoints(self):
        entered, ok, _ = apply_barrows_command_pure(_player(), "enter", rng=lambda: 0.0)
        self.assertTrue(ok)
        state = entered["barrows"]
        state["phase"] = "tunnels"
        state["active_encounter"] = {
            "kind": "creature",
            "enemy_id": "crypt_rat",
            "lifepoints": 123,
            "encounter": {"target_id": "barrows", "enemy_lifepoints": 123},
            "protected_class": "melee",
            "protection_damage": 0,
        }
        left, ok, info = apply_barrows_command_pure(entered, "leave")
        self.assertTrue(ok, info)
        resumed, ok, info = apply_barrows_command_pure(left, "enter")
        self.assertTrue(ok, info)
        self.assertEqual(resumed["barrows"]["active_encounter"]["lifepoints"], 123)

    def test_advanced_selection_is_atomic_and_casual_has_a_route(self):
        entered, ok, _ = apply_barrows_command_pure(_player(), "enter", rng=lambda: 0.0)
        self.assertTrue(ok)
        advanced, ok, _ = apply_barrows_command_pure(
            entered, "set_mode", {"automation_mode": "advanced"}
        )
        self.assertTrue(ok)
        self.assertFalse(barrows_view_pure(advanced)["can_review"])
        selected, ok, _ = apply_barrows_command_pure(
            advanced,
            "select_brother",
            {"brother_id": advanced["barrows"]["surface_queue"][0]},
        )
        self.assertTrue(ok)
        self.assertTrue(barrows_view_pure(selected)["can_review"])

    def test_advanced_chest_pauses_reviews_until_manual_claim(self):
        player = _player(current_utility="barrows")
        player["barrows"] = default_barrows_state_pure()
        player["barrows"].update(
            {"active": True, "phase": "chest", "automation_mode": "advanced"}
        )
        player["activity_session"] = {"active_id": "barrows"}
        self.assertFalse(barrows_view_pure(player)["can_review"])

    def test_bob_repair_is_instant_prorated_and_preserves_the_instance(self):
        player = _player()
        player.update(
            {
                "inventory": {"Coins": 500_000, "Verac's flail 50": 1},
                "equipment_instances": {
                    "equipment-7": {
                        "family_id": "barrows_verac",
                        "item_name": "Verac's flail 50",
                        "condition": 45_000,
                        "location": "bank",
                    }
                },
                "equipment_instance_next_id": 8,
            }
        )
        repaired, ok, info = apply_barrows_command_pure(
            player, "repair", {"instance_id": "equipment-7"}
        )
        self.assertTrue(ok, info)
        self.assertEqual(info["cost"], 50_000)
        self.assertEqual(repaired["inventory"]["Coins"], 450_000)
        self.assertEqual(repaired["inventory"]["Verac's flail"], 1)
        self.assertEqual(repaired["equipment_instances"]["equipment-7"]["condition"], 90_000)

    def test_sanitizer_and_migration_preserve_consequential_state(self):
        raw = default_barrows_state_pure()
        raw.update({"active": True, "phase": "tunnels", "current_room": 3, "start_room": 0, "usable_edges": ["0-1", "0-3", "3-4"], "revealed_rooms": [0, 3, 4], "tunnel_kill_count": 5})
        clean = sanitize_barrows_state_pure(raw)
        self.assertEqual(clean["current_room"], 3)
        self.assertEqual(clean["tunnel_kill_count"], 5)
        migrated = migrate_loaded_data({"barrows": raw}, {}, ())
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["activity_session"], {"active_id": "barrows"})


class BarrowsReviewAndRewardTests(unittest.TestCase):
    def test_combat_review_uses_six_ticks_and_drains_prayer_with_residual(self):
        entered, ok, _ = apply_barrows_command_pure(_player(), "enter", rng=lambda: 0.0)
        self.assertTrue(ok)
        with patch("ankiscape.logic.barrows_logic.apply_combat_burst_pure") as combat:
            combat.side_effect = _combat_result(lifepoints=500)
            advanced, ok, result = apply_barrows_review_pure(entered, lambda: 0.5, equipment_data=EQUIPMENT_DATA)
        self.assertTrue(ok, result)
        self.assertEqual(combat.call_args.kwargs["ticks"], 6)
        self.assertTrue(combat.call_args.kwargs["live_cadence"])
        self.assertFalse(combat.call_args.kwargs["safe_death"])
        self.assertGreater(result["prayer_drained"], 0)
        self.assertEqual(advanced["barrows"]["active_encounter"]["lifepoints"], 500)

    def test_prayer_drain_uses_actual_ticks_and_slain_brother_term(self):
        entered, ok, _ = apply_barrows_command_pure(_player(), "enter", rng=lambda: 0.0)
        self.assertTrue(ok)
        entered["barrows"]["slain_brothers"] = ["ahrim", "guthan", "karil"]
        with patch(
            "ankiscape.logic.barrows_logic.apply_combat_burst_pure",
            _combat_result(killed=True, ticks_elapsed=1),
        ):
            advanced, ok, result = apply_barrows_review_pure(
                entered, lambda: 0.5, equipment_data=EQUIPMENT_DATA
            )
        self.assertTrue(ok, result)
        self.assertEqual(result["prayer_drained"], 6)
        self.assertEqual(advanced["barrows"]["prayer_drain_residual"], 60)

    def test_dharok_missing_lifepoints_raise_the_enemy_max_hit(self):
        player = _active_brother(_player(), "dharok", lifepoints=100)
        with patch("ankiscape.logic.barrows_logic.apply_combat_burst_pure") as combat:
            combat.side_effect = _combat_result(lifepoints=100, player_damage=0)
            _advanced, ok, result = apply_barrows_review_pure(
                player, lambda: 0.5, equipment_data=EQUIPMENT_DATA
            )
        self.assertTrue(ok, result)
        self.assertEqual(combat.call_args.args[1]["barrows"]["max_hit"], 642)

    def test_guthan_heals_from_damage_dealt(self):
        player = _active_brother(_player(), "guthan", lifepoints=500)
        with patch(
            "ankiscape.logic.barrows_logic.apply_combat_burst_pure",
            _combat_result(lifepoints=400, enemy_damage=100),
        ):
            advanced, ok, result = apply_barrows_review_pure(
                player, lambda: 0.0, equipment_data=EQUIPMENT_DATA
            )
        self.assertTrue(ok, result)
        self.assertEqual(advanced["barrows"]["active_encounter"]["lifepoints"], 500)
        self.assertIn("Guthan healed 100 LP", result["status"])

    def test_ahrim_karil_and_torag_apply_their_period_drains(self):
        cases = (
            ("ahrim", "strength", 75, {}),
            ("karil", "agility", 64, {}),
            ("torag", None, None, {"agility_run_energy_credit_pct": 10}),
        )
        for brother_id, level_key, expected_level, overrides in cases:
            with self.subTest(brother_id=brother_id):
                player = _active_brother(_player(**overrides), brother_id)
                with patch(
                    "ankiscape.logic.barrows_logic.apply_combat_burst_pure",
                    _combat_result(lifepoints=450, enemy_damage=10),
                ):
                    advanced, ok, result = apply_barrows_review_pure(
                        player, lambda: 0.0, equipment_data=EQUIPMENT_DATA
                    )
                self.assertTrue(ok, result)
                if level_key:
                    self.assertEqual(
                        advanced["combat_current_levels"][level_key], expected_level
                    )
                else:
                    self.assertEqual(advanced["agility_run_energy_credit_pct"], 6)

        empty_credit = _active_brother(_player(agility_run_energy_credit_pct=0), "torag")
        with patch(
            "ankiscape.logic.barrows_logic.apply_combat_burst_pure",
            _combat_result(lifepoints=450, enemy_damage=10),
        ):
            unchanged, ok, result = apply_barrows_review_pure(
                empty_credit, lambda: 0.0, equipment_data=EQUIPMENT_DATA
            )
        self.assertTrue(ok, result)
        self.assertEqual(unchanged["agility_run_energy_credit_pct"], 0)
        self.assertIn("no remaining credit", result["status"])

    def test_verac_defiler_temporarily_ignores_prayer_and_armour(self):
        player = _active_brother(
            _player(combat_selected_prayers=["protect_from_melee"]), "verac"
        )
        with patch("ankiscape.logic.barrows_logic.apply_combat_burst_pure") as combat:
            combat.side_effect = _combat_result(lifepoints=450)
            advanced, ok, result = apply_barrows_review_pure(
                player, lambda: 0.0, equipment_data=EQUIPMENT_DATA
            )
        self.assertTrue(ok, result)
        combat_player = combat.call_args.args[0]
        combat_enemy = combat.call_args.args[1]["barrows"]
        self.assertEqual(combat_player["combat_selected_prayers"], [])
        self.assertEqual(combat_enemy["stats"]["attack"], 100_000)
        self.assertEqual(advanced["combat_selected_prayers"], ["protect_from_melee"])
        self.assertIn("Defiler ignored armour and prayer", result["status"])

    def test_akrisae_protection_is_passed_to_combat_and_rotates_at_150_damage(self):
        player = _active_brother(_player(), "akrisae", protected_class="melee")
        with patch("ankiscape.logic.barrows_logic.apply_combat_burst_pure") as combat:
            combat.side_effect = _combat_result(lifepoints=340, player_damage=160)
            advanced, ok, result = apply_barrows_review_pure(
                player, lambda: 0.5, equipment_data=EQUIPMENT_DATA
            )
        self.assertTrue(ok, result)
        self.assertEqual(
            combat.call_args.args[1]["barrows"]["protect_from_player_class"],
            "melee",
        )
        encounter = advanced["barrows"]["active_encounter"]
        self.assertEqual(encounter["protected_class"], "ranged")
        self.assertEqual(encounter["protection_damage"], 10)
        self.assertIn("protects from ranged", result["status"])

    def test_surface_kills_transition_to_tunnels_then_move_and_attach_creature(self):
        entered, ok, _ = apply_barrows_command_pure(_player(), "enter", rng=lambda: 0.0)
        self.assertTrue(ok)
        with patch("ankiscape.logic.barrows_logic.apply_combat_burst_pure", _combat_result(killed=True)):
            for _ in range(len(entered["barrows"]["surface_queue"])):
                entered, ok, result = apply_barrows_review_pure(entered, lambda: 0.5, equipment_data=EQUIPMENT_DATA)
                self.assertTrue(ok, result)
        self.assertEqual(entered["barrows"]["phase"], "tunnels")
        moved, ok, result = apply_barrows_review_pure(entered, lambda: 0.5, equipment_data=EQUIPMENT_DATA)
        self.assertTrue(ok, result)
        self.assertNotEqual(moved["barrows"]["current_room"], moved["barrows"]["start_room"])
        self.assertEqual(moved["barrows"]["active_encounter"]["kind"], "creature")

    def test_central_door_attaches_the_living_hidden_brother_to_the_same_review(self):
        player = _player()
        state = default_barrows_state_pure()
        state.update(
            {
                "active": True,
                "phase": "tunnels",
                "automation_mode": "advanced",
                "hidden_brother": "dharok",
                "current_room": 3,
                "start_room": 0,
                "usable_edges": ["3-4"],
                "revealed_rooms": [3, 4],
                "selected_room": 4,
            }
        )
        player["barrows"] = state
        player["activity_session"] = {"active_id": "barrows"}
        with patch(
            "ankiscape.logic.barrows_logic.apply_combat_burst_pure",
            _combat_result(lifepoints=500),
        ):
            advanced, ok, result = apply_barrows_review_pure(
                player, lambda: 0.5, equipment_data=EQUIPMENT_DATA
            )
        self.assertTrue(ok, result)
        self.assertEqual(advanced["barrows"]["phase"], "chest")
        self.assertEqual(advanced["barrows"]["active_encounter"]["enemy_id"], "dharok")
        self.assertEqual(advanced["barrows"]["active_encounter"]["lifepoints"], 500)

    def test_reward_formula_and_chest_add_full_condition_instances(self):
        player = _player()
        state = default_barrows_state_pure()
        state.update({
            "active": True,
            "phase": "chest",
            "slain_brothers": ["ahrim", "dharok", "guthan", "karil", "torag", "verac"],
            "tunnel_kill_count": 6,
            "available_brothers": ["ahrim", "dharok", "guthan", "karil", "torag", "verac"],
        })
        player["barrows"] = state
        player["activity_session"] = {"active_id": "barrows"}
        self.assertEqual(barrows_reward_potential_pure(state), BARROWS_MAX_REWARD_POTENTIAL)
        looted, ok, info = apply_barrows_command_pure(player, "claim_chest", rng=lambda: 0.0)
        self.assertTrue(ok, info)
        self.assertTrue(info["complete"])
        self.assertGreaterEqual(info["rewards"]["Ahrim's staff"], 1)
        self.assertTrue(any(record["family_id"] == "barrows_ahrim" for record in looted["equipment_instances"].values()))
        self.assertEqual(looted["inventory"]["Ahrim's staff"], info["rewards"]["Ahrim's staff"])
        self.assertFalse(looted["barrows"]["active"])

    def test_early_chest_equipment_rolls_do_not_depend_on_brother_order(self):
        player = _player()
        state = default_barrows_state_pure()
        state.update({
            "active": True,
            "phase": "chest",
            "automation_mode": "advanced",
            "slain_brothers": ["verac"],
            "available_brothers": ["ahrim", "dharok", "guthan", "karil", "torag", "verac"],
        })
        player["barrows"] = state
        player["activity_session"] = {"active_id": "barrows"}
        looted, ok, info = apply_barrows_command_pure(
            player, "claim_chest", rng=lambda: 0.0
        )
        self.assertTrue(ok, info)
        self.assertEqual(info["rewards"]["Verac's flail"], 1)
        self.assertTrue(
            any(
                record["family_id"] == "barrows_verac"
                for record in looted["equipment_instances"].values()
            )
        )

    def test_exit_paths_clear_synthetic_target_when_no_target_was_saved(self):
        player = _player(current_combat_target="")
        entered, ok, _ = apply_barrows_command_pure(player, "enter", rng=lambda: 0.0)
        self.assertTrue(ok)
        with patch("ankiscape.logic.barrows_logic.apply_combat_burst_pure", _combat_result(lifepoints=500)):
            advanced, ok, _ = apply_barrows_review_pure(
                entered, lambda: 0.5, equipment_data=EQUIPMENT_DATA
            )
        self.assertTrue(ok)
        self.assertEqual(advanced["current_combat_target"], "barrows")
        left, ok, info = apply_barrows_command_pure(advanced, "leave")
        self.assertTrue(ok, info)
        self.assertEqual(left["current_combat_target"], "")

    def test_dangerous_death_ends_the_run(self):
        entered, ok, _ = apply_barrows_command_pure(
            _player(current_combat_target=""), "enter", rng=lambda: 0.0
        )
        self.assertTrue(ok)
        with patch("ankiscape.logic.barrows_logic.apply_combat_burst_pure", _combat_result(died=True)):
            defeated, ok, result = apply_barrows_review_pure(entered, lambda: 0.5, equipment_data=EQUIPMENT_DATA)
        self.assertTrue(ok, result)
        self.assertEqual(result["outcome"], "death")
        self.assertFalse(defeated["barrows"]["active"])
        self.assertFalse(defeated["barrows"]["suspended"])
        self.assertEqual(defeated["current_combat_target"], "")


class BarrowsRuntimeIntegrationTests(unittest.TestCase):
    def test_utility_dispatch_records_review_and_deactivates_on_chest(self):
        player = _player(current_utility="barrows")
        player["barrows"] = default_barrows_state_pure()
        player["barrows"].update({"active": True, "phase": "chest"})
        player["activity_session"] = {"active_id": "barrows"}
        events = {"saved": 0, "deactivated": 0, "gains": []}
        ctx = RuntimeActionContext(
            player_data=player,
            random_random=lambda: 0.5,
            show_error_message=lambda *_args: self.fail("unexpected runtime error"),
            save_player_data=lambda: events.__setitem__("saved", events["saved"] + 1),
            deactivate_current_skill=lambda: events.__setitem__("deactivated", events["deactivated"] + 1),
            award_skill_exp=lambda *_args: self.fail("combat reducer owns its XP"),
            award_hidden_skill_exp=lambda *_args: None,
            level_up_check=lambda *_args: None,
            check_achievements=lambda *_args: None,
            refresh_skill_availability=lambda: None,
            refresh_skill_availability_partial=lambda *_args: None,
            can_smith_any=lambda: True,
            show_exp=lambda *_args: None,
            show_activity_gain=lambda text: events["gains"].append(text),
            implemented_exp_keys_snapshot=lambda: {},
            show_quest_exp_delta=lambda *_args: None,
        )
        self.assertTrue(handle_utility_answer(ctx))
        self.assertEqual(events["saved"], 1)
        self.assertEqual(events["deactivated"], 1)
        self.assertTrue(events["gains"])


if __name__ == "__main__":
    unittest.main()
