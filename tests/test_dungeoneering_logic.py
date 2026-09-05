import copy
import sys
import types
import unittest
from dataclasses import replace

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import (
    DUNGEONEERING_EXP_TABLE,
    EQUIPMENT_DATA,
    EXP_TABLE,
    ITEM_DEFINITIONS,
    ORE_DATA,
    exp_table_for_skill,
)
from ankiscape.core.storage_pure import (
    CURRENT_CONFIG_VERSION,
    default_player_data,
    migrate_loaded_data,
)
from ankiscape.data.dungeoneering_data import (
    COAL_BAG_CAPACITY,
    DUNGEONEERING_STATE_VERSION,
    FROZEN_BOSSES,
    FROZEN_BOSS_COMBAT_LEVEL_LADDERS,
    KINSHIP_TIER_COSTS,
    STARTER_SKILL_DOOR_REQUIREMENT,
    STARTER_SMALL_GRAPH_ROOM_COUNT,
    STARTER_SMALL_REVIEW_BUDGET,
)
from ankiscape.logic.dungeoneering_logic import (
    _automate_herblore_chain_pure,
    active_bind_slots_for_level_pure,
    ammo_bind_capacity_pure,
    apply_dungeoneering_command_pure,
    apply_dungeoneering_review_pure,
    begin_starter_session_pure,
    build_starter_floor_graph_pure,
    calculate_completion_payout_pure,
    death_xp_penalty_pure,
    default_dungeoneering_state_pure,
    dungeoneering_view_pure,
    eligible_frozen_bosses_pure,
    floor_theme_for_floor_pure,
    frozen_boss_combat_level_pure,
    frozen_boss_enemy_pure,
    maximum_floor_for_level_pure,
    prestige_value_pure,
    record_dungeon_drop_pure,
    record_starter_death_pure,
    required_level_for_floor_pure,
    resolve_floor_replay_pure,
    resolve_starter_room_pure,
    sanitize_dungeoneering_state_pure,
    starter_completion_modifier_pure,
    starter_floor_xp_pure,
)
from ankiscape.logic_pure.logic_pure import calculate_new_level, compute_level_progress
from ankiscape.runtime.runtime_actions import (
    RuntimeActionContext,
    answer_handler_for_key,
    can_start_action,
)


class DungeoneeringLogicTests(unittest.TestCase):
    def test_level_120_curve_is_dungeoneering_only(self):
        self.assertEqual(len(EXP_TABLE), 99)
        self.assertEqual(len(DUNGEONEERING_EXP_TABLE), 120)
        self.assertIs(exp_table_for_skill("Mining"), EXP_TABLE)
        self.assertIs(
            exp_table_for_skill("Dungeoneering"),
            DUNGEONEERING_EXP_TABLE,
        )
        self.assertEqual(DUNGEONEERING_EXP_TABLE[99], 14_391_160)
        self.assertEqual(DUNGEONEERING_EXP_TABLE[-1], 104_273_167)
        self.assertEqual(
            calculate_new_level(10**9, 1, EXP_TABLE),
            99,
        )
        self.assertEqual(
            calculate_new_level(10**9, 1, DUNGEONEERING_EXP_TABLE),
            120,
        )

    def test_level_100_to_120_progress_uses_the_extended_curve(self):
        midpoint = (
            DUNGEONEERING_EXP_TABLE[99] + DUNGEONEERING_EXP_TABLE[100]
        ) / 2
        percent, remaining, target = compute_level_progress(
            100,
            midpoint,
            DUNGEONEERING_EXP_TABLE,
        )
        self.assertEqual(percent, 50)
        self.assertEqual(target, 101)
        self.assertAlmostEqual(
            remaining,
            DUNGEONEERING_EXP_TABLE[100] - midpoint,
        )
        self.assertEqual(
            compute_level_progress(
                120,
                DUNGEONEERING_EXP_TABLE[-1],
                DUNGEONEERING_EXP_TABLE,
            ),
            (100, 0.0, 120),
        )

    def test_floor_access_theme_and_bind_boundaries(self):
        scenarios = (
            (1, 1, "frozen", 1),
            (11, 21, "frozen", 2),
            (12, 23, "abandoned_i", 2),
            (30, 59, "abandoned_ii", 3),
            (48, 95, "warped", 4),
            (60, 119, "warped", 4),
        )
        for floor, level, theme_id, bind_slots in scenarios:
            with self.subTest(floor=floor):
                self.assertEqual(required_level_for_floor_pure(floor), level)
                self.assertEqual(maximum_floor_for_level_pure(level), floor)
                self.assertEqual(floor_theme_for_floor_pure(floor).id, theme_id)
                self.assertEqual(active_bind_slots_for_level_pure(level), bind_slots)
        self.assertEqual(maximum_floor_for_level_pure(120), 60)
        self.assertEqual(active_bind_slots_for_level_pure(120), 5)
        self.assertEqual(ammo_bind_capacity_pure(), 125)
        self.assertEqual(ammo_bind_capacity_pure(salt_in_the_wound_complete=True), 225)

    def test_prestige_replay_prefers_lower_then_higher_inside_the_theme(self):
        self.assertEqual(prestige_value_pure(9, 11), 11)
        self.assertEqual(
            resolve_floor_replay_pure(5, {1, 2, 3, 4}),
            resolve_floor_replay_pure(5, (1, 2, 3, 4)),
        )
        fresh = resolve_floor_replay_pure(5, {1, 2, 3, 4})
        self.assertEqual((fresh.credited_floor, fresh.xp_floor), (5, 5))

        lower = resolve_floor_replay_pure(5, {1, 2, 3, 5})
        self.assertEqual((lower.credited_floor, lower.xp_floor), (4, 4))
        lowest_lower = resolve_floor_replay_pure(5, {2, 4, 5})
        self.assertEqual(
            (lowest_lower.credited_floor, lowest_lower.xp_floor),
            (1, 1),
        )

        higher = resolve_floor_replay_pure(5, {1, 2, 3, 4, 5})
        self.assertEqual((higher.credited_floor, higher.xp_floor), (6, 5))

        exhausted = resolve_floor_replay_pure(5, set(range(1, 12)))
        self.assertIsNone(exhausted.credited_floor)
        self.assertTrue(exhausted.repeated_without_credit)

    def test_completion_formula_combines_modifiers_additively(self):
        payout = calculate_completion_payout_pure(
            active_floor_xp=1000,
            prestige_floor_xp=600,
            complexity=1,
            death_penalty=0.10,
            completion_modifier=0.25,
        )
        self.assertEqual(payout.base_xp, 800)
        self.assertEqual(payout.adjusted_xp, 400)
        self.assertEqual(payout.final_xp, 520)
        self.assertEqual(payout.tokens, 52)
        self.assertEqual(payout.total_modifier, 0.65)
        with self.assertRaisesRegex(ValueError, "death_penalty"):
            calculate_completion_payout_pure(
                active_floor_xp=100,
                prestige_floor_xp=100,
                complexity=6,
                death_penalty=1.1,
            )

    def test_registered_floor_death_and_completion_candidates_stay_bounded(self):
        self.assertEqual(
            starter_floor_xp_pure(floor=1, size="small", opened_rooms=16),
            177,
        )
        self.assertEqual(death_xp_penalty_pure(0), 0.0)
        self.assertEqual(death_xp_penalty_pure(1), 0.04)
        self.assertAlmostEqual(death_xp_penalty_pure(15), 0.70)
        self.assertAlmostEqual(death_xp_penalty_pure(99), 0.70)
        session = begin_starter_session_pure(
            floor=1,
            dungeoneering_level=1,
            complexity=1,
            seed=1,
        )
        modifier = starter_completion_modifier_pure(session)
        self.assertGreaterEqual(modifier, -0.151)
        self.assertLessEqual(modifier, 0.2267)

    def test_frozen_boss_roster_unlocks_by_floor_and_level(self):
        self.assertEqual(
            {boss.id for boss in eligible_frozen_bosses_pure(1, 1)},
            {"gluttonous_behemoth", "astea_frostweb", "icy_bones"},
        )
        self.assertEqual(
            {boss.id for boss in eligible_frozen_bosses_pure(6, 11)},
            {
                "gluttonous_behemoth",
                "astea_frostweb",
                "icy_bones",
                "luminescent_icefiend",
                "plane_freezer_lakhrahnaz",
            },
        )
        self.assertEqual(eligible_frozen_bosses_pure(12, 99), ())

    def test_registered_boss_scaling_builds_live_enemy_definitions_with_empty_drops(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player.update(
            {
                "attack_level": 1,
                "strength_level": 1,
                "defence_level": 1,
                "constitution_level": 10,
                "prayer_level": 1,
                "ranged_level": 1,
                "magic_level": 1,
            }
        )
        level = frozen_boss_combat_level_pure("gluttonous_behemoth", player)
        self.assertEqual(level, 5)
        enemy = frozen_boss_enemy_pure("gluttonous_behemoth", level)
        self.assertEqual(enemy["stats"]["hitpoints"], 126)
        self.assertEqual(enemy["max_hit"], 5)
        self.assertTrue(all(0 <= enemy["stats"][skill] <= 120 for skill in ("attack", "strength", "defence", "magic", "ranged")))
        self.assertEqual(enemy["drops"], {"guaranteed": (), "tables": ()})

    def test_seeded_graph_is_deterministic_connected_and_complexity_shaped(self):
        skill_levels = {
            "runecrafting": 11,
            "strength": 12,
            "mining": 13,
            "firemaking": 14,
            "magic": 15,
            "prayer": 16,
            "woodcutting": 17,
            "smithing": 18,
            "crafting": 19,
        }
        first = build_starter_floor_graph_pure(
            seed=4107,
            complexity=6,
            skill_levels=skill_levels,
        )
        second = build_starter_floor_graph_pure(
            seed=4107,
            complexity=6,
            skill_levels=skill_levels,
        )
        maxed = build_starter_floor_graph_pure(
            seed=4107,
            complexity=6,
            skill_levels={skill_id: 99 for skill_id in skill_levels},
        )
        simple = build_starter_floor_graph_pure(seed=4107, complexity=1)
        self.assertEqual(first, second)
        self.assertEqual(first, maxed)
        self.assertEqual(len(first), STARTER_SMALL_GRAPH_ROOM_COUNT)
        self.assertEqual(
            sum(room.critical_path for room in first),
            STARTER_SMALL_REVIEW_BUDGET + 1,
        )
        self.assertEqual(first[0].family, "start")
        self.assertEqual(sum(room.family == "boss" for room in first), 1)
        self.assertIn("skill", {room.family for room in first})
        self.assertIn("resource", {room.family for room in first})
        self.assertIn(
            "skill",
            {room.family for room in first if room.critical_path},
        )
        self.assertIn(
            "resource",
            {room.family for room in first if room.critical_path},
        )
        self.assertTrue(
            all(
                room.required_level == STARTER_SKILL_DOOR_REQUIREMENT
                for room in first
                if room.family == "skill"
            )
        )
        self.assertTrue({room.family for room in simple}.isdisjoint({"skill", "resource"}))
        for room in first:
            for neighbor in room.connected_room_ids:
                with self.subTest(room=room.id, neighbor=neighbor):
                    self.assertIn(room.id, first[neighbor].connected_room_ids)
        with self.assertRaisesRegex(ValueError, "complexity 1 or 6"):
            build_starter_floor_graph_pure(seed=1, complexity=5)

    def test_session_resolves_one_room_and_death_respawns_without_erasing_the_floor(self):
        session = begin_starter_session_pure(
            floor=6,
            dungeoneering_level=11,
            complexity=6,
            seed=99,
        )
        self.assertEqual(session.resolved_room_ids, (0,))
        first_room = session.frontier_room_ids[0]
        advanced = resolve_starter_room_pure(session, first_room)
        self.assertIn(first_room, advanced.resolved_room_ids)
        self.assertEqual(session.resolved_room_ids, (0,))
        with self.assertRaisesRegex(ValueError, "revealed frontier"):
            resolve_starter_room_pure(advanced, first_room)

        restarted = record_starter_death_pure(advanced)
        self.assertEqual(restarted.death_count, 1)
        self.assertEqual(restarted.current_room_id, 0)
        self.assertEqual(restarted.resolved_room_ids, advanced.resolved_room_ids)
        self.assertEqual(restarted.frontier_room_ids, advanced.frontier_room_ids)
        self.assertFalse(restarted.completed)

        current = restarted
        resolved_reviews = 1
        while not current.completed:
            critical_frontier = [
                room_id
                for room_id in current.frontier_room_ids
                if current.rooms[room_id].critical_path
            ]
            current = resolve_starter_room_pure(current, critical_frontier[0])
            resolved_reviews += 1
        self.assertEqual(resolved_reviews, STARTER_SMALL_REVIEW_BUDGET)
        self.assertEqual(current.rooms[current.current_room_id].family, "boss")

    def test_invalid_floor_and_level_gates_fail_before_state_creation(self):
        for invalid_floor in (0, 61, "bad"):
            with self.subTest(invalid_floor=invalid_floor):
                with self.assertRaises(ValueError):
                    required_level_for_floor_pure(invalid_floor)
        with self.assertRaisesRegex(ValueError, "too low"):
            begin_starter_session_pure(
                floor=6,
                dungeoneering_level=10,
                complexity=6,
                seed=1,
            )
        with self.assertRaisesRegex(ValueError, "Frozen"):
            begin_starter_session_pure(
                floor=12,
                dungeoneering_level=23,
                complexity=6,
                seed=1,
            )


class DungeoneeringFloorRuntimeTests(unittest.TestCase):
    def _player(self, **overrides):
        data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        data.update(
            {
                "dungeoneering_level": 11,
                "dungeoneering_exp": 0.0,
            }
        )
        data.update(overrides)
        return data

    def _enter(self, data=None, **payload):
        data = self._player() if data is None else data
        if "next_seed" in payload:
            data["dungeoneering"]["next_seed"] = payload.pop("next_seed")
        data, ok, info = apply_dungeoneering_command_pure(
            data,
            "enter",
            {
                "floor": 6,
                "size": "small",
                "complexity": 6,
                "automation_mode": "casual",
                **payload,
            },
        )
        self.assertTrue(ok, info)
        data.update(
            {
                "attack_level": 99,
                "strength_level": 99,
                "constitution_level": 99,
                "combat_lifepoints": 990,
            }
        )
        return data

    def _review_recommended_route(self, player):
        view = dungeoneering_view_pure(player, selected_skill="Dungeoneering")
        route = next(row for row in view["frontier_rows"] if row["casual_recommended"])
        if player["dungeoneering"]["automation_mode"] == "advanced":
            player, ok, info = apply_dungeoneering_command_pure(
                player,
                "select_route",
                {"room_id": route["room_id"]},
            )
            self.assertTrue(ok, info)
        player, ok, result = apply_dungeoneering_review_pure(
            player,
            lambda: 0.5,
            equipment_data=EQUIPMENT_DATA,
        )
        self.assertTrue(ok, result)
        return player, route, result

    def test_entry_advanced_routing_abandon_and_resume_are_persistent(self):
        original = self._player()
        entered, ok, info = apply_dungeoneering_command_pure(
            original,
            "enter",
            {
                "floor": 6,
                "size": "small",
                "complexity": 6,
                "automation_mode": "advanced",
            },
        )
        self.assertTrue(ok, info)
        self.assertEqual(original["activity_session"], {"active_id": ""})
        self.assertEqual(
            entered["activity_session"],
            {"active_id": "dungeoneering"},
        )
        blocked_view = dungeoneering_view_pure(
            entered,
            selected_skill="Dungeoneering",
        )
        self.assertFalse(blocked_view["can_review"])
        self.assertTrue(blocked_view["route_choice_visible"])
        room_id = blocked_view["frontier_rows"][0]["room_id"]
        selected, ok, info = apply_dungeoneering_command_pure(
            entered,
            "select_route",
            {"room_id": room_id},
        )
        self.assertTrue(ok, info)
        self.assertTrue(
            dungeoneering_view_pure(
                selected,
                selected_skill="Dungeoneering",
            )["can_review"]
        )

        selected, ok, info = record_dungeon_drop_pure(
            selected,
            "Raw heim crab",
            2,
        )
        self.assertTrue(ok, info)
        selected["dungeoneering"]["session_coins"] = 60
        restarted = migrate_loaded_data(selected, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(restarted["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(
            restarted["dungeoneering"]["version"],
            DUNGEONEERING_STATE_VERSION,
        )
        self.assertEqual(
            restarted["activity_session"],
            {"active_id": "dungeoneering"},
        )
        self.assertEqual(
            restarted["dungeoneering"]["session"],
            selected["dungeoneering"]["session"],
        )
        self.assertEqual(
            restarted["dungeoneering"]["session_inventory"],
            {"Raw heim crab": 2},
        )
        self.assertEqual(restarted["dungeoneering"]["session_coins"], 60)
        abandoned, ok, info = apply_dungeoneering_command_pure(
            restarted,
            "abandon",
        )
        self.assertTrue(ok, info)
        self.assertFalse(abandoned["dungeoneering"]["active"])
        self.assertEqual(abandoned["activity_session"], {"active_id": ""})

    def test_death_respawns_preserves_rooms_and_reduces_projection(self):
        entered = self._enter()
        before_review = copy.deepcopy(entered)
        advanced, ok, info = apply_dungeoneering_review_pure(entered)
        self.assertTrue(ok, info)
        self.assertEqual(entered, before_review)
        before_state = copy.deepcopy(advanced["dungeoneering"]["session"])
        before_projection = dungeoneering_view_pure(
            advanced,
            selected_skill="Dungeoneering",
        )["projected_xp"]
        defeated, ok, result = apply_dungeoneering_review_pure(
            advanced,
            player_died=True,
        )
        self.assertTrue(ok, result)
        self.assertTrue(result["death"])
        after_session = defeated["dungeoneering"]["session"]
        self.assertEqual(
            after_session["resolved_room_ids"],
            before_state["resolved_room_ids"],
        )
        self.assertEqual(after_session["current_room_id"], 0)
        self.assertEqual(after_session["death_count"], 1)
        self.assertLess(
            dungeoneering_view_pure(
                defeated,
                selected_skill="Dungeoneering",
            )["projected_xp"],
            before_projection,
        )

    def test_skill_door_failure_and_success_drive_the_real_room_reducer(self):
        player = self._enter()
        while True:
            view = dungeoneering_view_pure(player, selected_skill="Dungeoneering")
            route = next(row for row in view["frontier_rows"] if row["casual_recommended"])
            if route["family"] == "skill":
                room_id = route["room_id"]
                break
            player, ok, result = apply_dungeoneering_review_pure(
                player,
                lambda: 0.5,
                equipment_data=EQUIPMENT_DATA,
            )
            self.assertTrue(ok, result)

        before_rooms = list(player["dungeoneering"]["session"]["resolved_room_ids"])
        before_lp = player["combat_lifepoints"]
        failed, ok, result = apply_dungeoneering_review_pure(
            player,
            lambda: 0.0,
            equipment_data=EQUIPMENT_DATA,
        )
        self.assertTrue(ok, result)
        self.assertTrue(result["skill_door_failed"])
        self.assertFalse(result["room_resolved"])
        self.assertEqual(
            failed["dungeoneering"]["session"]["resolved_room_ids"],
            before_rooms,
        )
        self.assertLess(failed["combat_lifepoints"], before_lp)

        opened, ok, result = apply_dungeoneering_review_pure(
            failed,
            lambda: 0.5,
            equipment_data=EQUIPMENT_DATA,
        )
        self.assertTrue(ok, result)
        self.assertTrue(result["room_resolved"])
        self.assertIn(room_id, opened["dungeoneering"]["session"]["resolved_room_ids"])
        self.assertEqual(sum(result["xp_rewards"].values()), 5.0)

    def test_daemonheim_herblore_chain_requires_complexity_five_and_druidic_ritual(self):
        for complexity, quest_complete in ((4, True), (5, False)):
            with self.subTest(
                complexity=complexity,
                quest_complete=quest_complete,
            ):
                state = {
                    "complexity": complexity,
                    "session_inventory": {"Vial": 1},
                }
                player = self._player(herblore_level=5)
                if quest_complete:
                    player["quests"]["druidic_ritual"] = {"completed": True}

                rewards, reports = _automate_herblore_chain_pure(
                    state,
                    player,
                    None,
                )

                self.assertEqual(rewards, {})
                self.assertEqual(reports, ())
                self.assertEqual(state["session_inventory"], {"Vial": 1})

    def test_natural_c6_floor_brews_the_starter_weak_ranged_potion(self):
        player = self._player(herblore_level=5)
        player["quests"]["druidic_ritual"] = {"completed": True}
        player["dungeoneering"]["next_seed"] = 7
        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "enter",
            {
                "floor": 6,
                "size": "small",
                "complexity": 6,
                "automation_mode": "casual",
            },
        )
        self.assertTrue(ok, info)
        player.update(
            {
                "attack_level": 99,
                "strength_level": 99,
                "constitution_level": 99,
                "combat_lifepoints": 990,
            }
        )
        bank_before = copy.deepcopy(player["inventory"])
        bought_secondaries = False
        brewed = False
        resource_rooms_resolved = 0
        guardian_coin_drops = []
        final_result = {}

        for _review in range(100):
            if not player["dungeoneering"]["active"]:
                break
            view = dungeoneering_view_pure(player, selected_skill="Dungeoneering")
            route = next(row for row in view["frontier_rows"] if row["casual_recommended"])
            coins_before_review = player["dungeoneering"]["session_coins"]
            player, ok, final_result = apply_dungeoneering_review_pure(
                player,
                lambda: 0.5,
                equipment_data=EQUIPMENT_DATA,
            )
            self.assertTrue(ok, final_result)
            if route["family"] == "guardian":
                guardian_coin_drops.append(
                    player["dungeoneering"]["session_coins"] - coins_before_review
                )
            if route["family"] == "resource":
                resource_rooms_resolved += 1
                if resource_rooms_resolved == 1:
                    self.assertEqual(
                        final_result["xp_rewards"],
                        {"fishing": 9.0, "cooking": 22.0, "herblore": 3.2},
                    )
                    self.assertEqual(
                        player["dungeoneering"]["session_inventory"]["Clean valerian"],
                        1,
                    )
            if (
                not bought_secondaries
                and player["dungeoneering"]["session_coins"] >= 1_010
            ):
                self.assertEqual(resource_rooms_resolved, 2)
                self.assertTrue(all(drop > 0 for drop in guardian_coin_drops))
                self.assertEqual(sum(guardian_coin_drops), 1_010)
                player, ok, info = apply_dungeoneering_command_pure(
                    player,
                    "smuggler_buy",
                    {"item_id": "vial"},
                )
                self.assertTrue(ok, info)
                player, ok, info = apply_dungeoneering_command_pure(
                    player,
                    "smuggler_buy",
                    {"item_id": "void_dust"},
                )
                self.assertTrue(ok, info)
                self.assertEqual(player["dungeoneering"]["session_coins"], 0)
                bought_secondaries = True
            if final_result.get("xp_rewards", {}).get("herblore") == 34.0:
                brewed = True

        self.assertTrue(bought_secondaries)
        self.assertTrue(brewed)
        self.assertIn(
            "mix weak ranged potion",
            player["dungeoneering"]["last_automation"],
        )
        self.assertTrue(final_result["complete"])
        self.assertEqual(player["inventory"], bank_before)
        self.assertEqual(player["dungeoneering"]["session_inventory"], {})
        self.assertEqual(player["dungeoneering"]["session_coins"], 0)

    def test_advanced_critical_route_funds_the_pinned_smuggler_purchase(self):
        for seed in range(1, 61):
            with self.subTest(seed=seed):
                eligible = self._player(herblore_level=5)
                eligible["quests"]["druidic_ritual"] = {"completed": True}
                player = self._enter(
                    eligible,
                    next_seed=seed,
                    automation_mode="advanced",
                )
                guardian_drops = []

                for _review in range(20):
                    coins_before = player["dungeoneering"]["session_coins"]
                    player, route, _result = self._review_recommended_route(player)
                    if route["family"] == "guardian":
                        guardian_drops.append(
                            player["dungeoneering"]["session_coins"] - coins_before
                        )
                    if player["dungeoneering"]["session_coins"] >= 1_010:
                        break

                self.assertTrue(all(drop > 0 for drop in guardian_drops))
                self.assertEqual(sum(guardian_drops), 1_010)
                for item_id in ("vial", "void_dust"):
                    player, ok, info = apply_dungeoneering_command_pure(
                        player,
                        "smuggler_buy",
                        {"item_id": item_id},
                    )
                    self.assertTrue(ok, info)
                self.assertEqual(player["dungeoneering"]["session_coins"], 0)
                if seed == 7:
                    for _review in range(20):
                        player, _route, result = self._review_recommended_route(player)
                        if result.get("xp_rewards", {}).get("herblore") == 34.0:
                            break
                    self.assertEqual(result["xp_rewards"].get("herblore"), 34.0)

    def test_optional_guardian_room_does_not_dilute_or_extend_coin_total(self):
        eligible = self._player(herblore_level=5)
        eligible["quests"]["druidic_ritual"] = {"completed": True}
        player = self._enter(
            eligible,
            next_seed=7,
            automation_mode="advanced",
        )
        guardian_drops = []

        for room_id in (1, 2, 3, 9, 4, 5, 6, 7):
            room = player["dungeoneering"]["session"]["rooms"][room_id]
            coins_before = player["dungeoneering"]["session_coins"]
            player, ok, info = apply_dungeoneering_command_pure(
                player,
                "select_route",
                {"room_id": room_id},
            )
            self.assertTrue(ok, info)
            player, ok, result = apply_dungeoneering_review_pure(
                player,
                lambda: 0.5,
                equipment_data=EQUIPMENT_DATA,
            )
            self.assertTrue(ok, result)
            if room["family"] == "guardian":
                guardian_drops.append(
                    (
                        room["critical_path"],
                        player["dungeoneering"]["session_coins"] - coins_before,
                    )
                )

        self.assertEqual(len(guardian_drops), 3)
        self.assertEqual(
            [drop for critical, drop in guardian_drops if not critical],
            [0],
        )
        self.assertTrue(
            all(drop > 0 for critical, drop in guardian_drops if critical)
        )
        self.assertEqual(sum(drop for _critical, drop in guardian_drops), 1_010)

    def test_route_policy_can_change_after_a_guardian_room_resolves(self):
        player = self._enter(next_seed=7)
        while True:
            player, route, _result = self._review_recommended_route(player)
            if route["family"] == "guardian":
                break

        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "set_policy",
            {"automation_mode": "advanced"},
        )

        self.assertTrue(ok, info)
        self.assertEqual(player["dungeoneering"]["automation_mode"], "advanced")
        self.assertTrue(
            dungeoneering_view_pure(
                player,
                selected_skill="Dungeoneering",
            )["policy_control_enabled"]
        )

    def test_complexity_one_guardians_do_not_emit_unspendable_coins(self):
        player = self._enter(next_seed=7, complexity=1)
        guardian_ids = {
            room["id"]
            for room in player["dungeoneering"]["session"]["rooms"]
            if room["family"] == "guardian" and room["critical_path"]
        }
        resolved_guardians = set()

        for _review in range(20):
            coins_before = player["dungeoneering"]["session_coins"]
            player, route, result = self._review_recommended_route(player)
            if route["room_id"] in guardian_ids:
                resolved_guardians.add(route["room_id"])
                self.assertEqual(player["dungeoneering"]["session_coins"], coins_before)
                self.assertNotIn("guardian enemies dropped", result.get("status", ""))
                self.assertNotIn(
                    "guardian enemies dropped",
                    player["dungeoneering"]["last_automation"],
                )
            if resolved_guardians == guardian_ids:
                break

        self.assertEqual(resolved_guardians, guardian_ids)
        self.assertEqual(player["dungeoneering"]["session_coins"], 0)

    def test_guardian_funding_keeps_the_retired_cache_eligibility_gate(self):
        for quest_complete, herblore_level in ((False, 5), (True, 1)):
            with self.subTest(
                quest_complete=quest_complete,
                herblore_level=herblore_level,
            ):
                player = self._player(herblore_level=herblore_level)
                if quest_complete:
                    player["quests"]["druidic_ritual"] = {"completed": True}
                player = self._enter(player, next_seed=7)
                guardian_ids = {
                    room["id"]
                    for room in player["dungeoneering"]["session"]["rooms"]
                    if room["family"] == "guardian" and room["critical_path"]
                }

                for _review in range(20):
                    player, _route, result = self._review_recommended_route(player)
                    if guardian_ids.issubset(
                        player["dungeoneering"]["session"]["resolved_room_ids"]
                    ):
                        break

                self.assertEqual(player["dungeoneering"]["session_coins"], 0)
                self.assertNotIn("guardian enemies dropped", result.get("status", ""))
                view = dungeoneering_view_pure(
                    player,
                    selected_skill="Dungeoneering",
                )
                self.assertNotIn(
                    "novite_rapier",
                    {row["item_id"] for row in view["smuggler_rows"]},
                )
                _unchanged, ok, info = apply_dungeoneering_command_pure(
                    player,
                    "smuggler_buy",
                    {"item_id": "novite_rapier"},
                )
                self.assertFalse(ok)
                self.assertIn("Need 875", info["reason"])

    def test_pre_guardian_drop_save_resumes_with_the_full_funding_total(self):
        for seed in (1, 5, 7):
            with self.subTest(seed=seed):
                eligible = self._player(herblore_level=5)
                eligible["quests"]["druidic_ritual"] = {"completed": True}
                player = self._enter(
                    eligible,
                    next_seed=seed,
                    automation_mode="advanced",
                )
                while True:
                    player, route, _result = self._review_recommended_route(player)
                    if route["family"] == "guardian":
                        break

                saved_state = copy.deepcopy(player["dungeoneering"])
                resolved_ids = set(saved_state["session"]["resolved_room_ids"])
                resource_cache_granted = any(
                    room["id"] in resolved_ids and room["family"] == "resource"
                    for room in saved_state["session"]["rooms"]
                )
                saved_state["session_coins"] = (
                    1_010 if resource_cache_granted else 0
                )
                saved_state.pop("guardian_coin_room_ids")
                player["dungeoneering"] = sanitize_dungeoneering_state_pure(
                    saved_state,
                    player,
                )

                for _review in range(20):
                    if player["dungeoneering"]["session_coins"] >= 1_010:
                        break
                    player, _route, _result = self._review_recommended_route(player)

                self.assertEqual(player["dungeoneering"]["session_coins"], 1_010)
                for item_id in ("vial", "void_dust"):
                    player, ok, info = apply_dungeoneering_command_pure(
                        player,
                        "smuggler_buy",
                        {"item_id": item_id},
                    )
                    self.assertTrue(ok, info)
                if seed == 7:
                    for _review in range(20):
                        player, _route, result = self._review_recommended_route(player)
                        if result.get("xp_rewards", {}).get("herblore") == 34.0:
                            break
                    self.assertEqual(result["xp_rewards"].get("herblore"), 34.0)

    def test_legacy_cache_money_is_not_granted_again_during_sanitization(self):
        eligible = self._player(herblore_level=5)
        eligible["quests"]["druidic_ritual"] = {"completed": True}
        player = self._enter(
            eligible,
            next_seed=7,
            automation_mode="advanced",
        )
        guardian_ids = {
            room["id"]
            for room in player["dungeoneering"]["session"]["rooms"]
            if room["family"] == "guardian" and room["critical_path"]
        }

        for _review in range(20):
            player, _route, _result = self._review_recommended_route(player)
            resolved_ids = set(
                player["dungeoneering"]["session"]["resolved_room_ids"]
            )
            resource_resolved = any(
                room["id"] in resolved_ids and room["family"] == "resource"
                for room in player["dungeoneering"]["session"]["rooms"]
            )
            if guardian_ids.issubset(resolved_ids) and resource_resolved:
                break

        self.assertTrue(guardian_ids.issubset(resolved_ids))
        self.assertTrue(resource_resolved)
        saved_state = copy.deepcopy(player["dungeoneering"])
        saved_state["session_coins"] = 1_010
        saved_state.pop("guardian_coin_room_ids")

        player["dungeoneering"] = saved_state
        migrated = migrate_loaded_data(player, ORE_DATA, ITEM_DEFINITIONS)

        self.assertEqual(migrated["dungeoneering"]["session_coins"], 1_010)
        self.assertEqual(migrated["dungeoneering"]["guardian_coin_room_ids"], [])

    def test_live_resource_sale_and_smuggler_purchase_produce_an_ammo_bind_offer(self):
        player = self._enter()
        bank_before = copy.deepcopy(player["inventory"])
        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "set_resource_policy",
            {"resource_policy": "gather_only"},
        )
        self.assertTrue(ok, info)
        while True:
            view = dungeoneering_view_pure(player, selected_skill="Dungeoneering")
            route = next(row for row in view["frontier_rows"] if row["casual_recommended"])
            player, ok, result = apply_dungeoneering_review_pure(
                player,
                lambda: 0.5,
                equipment_data=EQUIPMENT_DATA,
            )
            self.assertTrue(ok, result)
            if route["family"] == "resource":
                break
        self.assertEqual(player["dungeoneering"]["session_inventory"]["Raw heim crab"], 1)
        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "smuggler_sell",
            {"item_id": "raw_heim_crab"},
        )
        self.assertTrue(ok, info)
        self.assertEqual(player["dungeoneering"]["session_coins"], 60)
        self.assertEqual(player["inventory"], bank_before)
        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "smuggler_buy",
            {"item_id": "novite_arrows"},
        )
        self.assertTrue(ok, info)
        self.assertEqual(
            player["dungeoneering"]["pending_bind_offer"]["kind"],
            "ammo",
        )
        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "resolve_bind_offer",
            {"choice": "bind"},
        )
        self.assertTrue(ok, info)
        self.assertEqual(player["dungeoneering"]["ammo_bind"]["item_name"], "Novite arrows")

    def test_selling_the_offered_arrows_cannot_materialize_an_ammo_bind(self):
        player = self._player(dungeoneering_level=13)
        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "enter",
            {
                "floor": 6,
                "size": "small",
                "complexity": 6,
                "automation_mode": "casual",
            },
        )
        self.assertTrue(ok, info)
        player.update(
            {
                "attack_level": 99,
                "strength_level": 99,
                "constitution_level": 99,
                "combat_lifepoints": 990,
            }
        )
        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "set_resource_policy",
            {"resource_policy": "gather_only"},
        )
        self.assertTrue(ok, info)
        while True:
            view = dungeoneering_view_pure(player, selected_skill="Dungeoneering")
            route = next(row for row in view["frontier_rows"] if row["casual_recommended"])
            player, ok, result = apply_dungeoneering_review_pure(
                player,
                lambda: 0.5,
                equipment_data=EQUIPMENT_DATA,
            )
            self.assertTrue(ok, result)
            if route["family"] == "resource":
                break

        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "smuggler_sell",
            {"item_id": "raw_heim_crab"},
        )
        self.assertTrue(ok, info)
        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "smuggler_buy",
            {"item_id": "novite_arrows"},
        )
        self.assertTrue(ok, info)
        self.assertTrue(player["dungeoneering"]["pending_bind_offer"])
        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "smuggler_sell",
            {"item_id": "novite_arrows"},
        )
        self.assertTrue(ok, info)
        self.assertNotIn(
            "Novite arrows",
            player["dungeoneering"]["session_inventory"],
        )
        self.assertEqual(player["dungeoneering"]["pending_bind_offer"], {})

        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "resolve_bind_offer",
            {"choice": "bind"},
        )
        self.assertFalse(ok)
        self.assertIn("No eligible", info["reason"])
        self.assertEqual(player["dungeoneering"]["ammo_bind"], {})
        player, ok, info = apply_dungeoneering_command_pure(player, "abandon")
        self.assertTrue(ok, info)
        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "enter",
            {
                "floor": 7,
                "size": "small",
                "complexity": 6,
                "automation_mode": "casual",
            },
        )
        self.assertTrue(ok, info)
        self.assertEqual(player["dungeoneering"]["ammo_bind"], {})
        self.assertNotIn(
            "Novite arrows",
            player["dungeoneering"]["session_inventory"],
        )

    def test_smuggler_hides_stock_above_the_live_floor_economy(self):
        player = self._enter(automation_mode="advanced")
        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "set_resource_policy",
            {"resource_policy": "gather_only"},
        )
        self.assertTrue(ok, info)

        while True:
            view = dungeoneering_view_pure(player, selected_skill="Dungeoneering")
            route = next(
                (
                    row
                    for row in view["frontier_rows"]
                    if row["family"] != "boss"
                ),
                None,
            )
            if route is None:
                break
            player, ok, info = apply_dungeoneering_command_pure(
                player,
                "select_route",
                {"room_id": route["room_id"]},
            )
            self.assertTrue(ok, info)
            player, ok, result = apply_dungeoneering_review_pure(
                player,
                lambda: 0.5,
                equipment_data=EQUIPMENT_DATA,
            )
            self.assertTrue(ok, result)

        raw_crabs = player["dungeoneering"]["session_inventory"].get(
            "Raw heim crab",
            0,
        )
        self.assertGreater(raw_crabs, 0)
        for _ in range(raw_crabs):
            player, ok, info = apply_dungeoneering_command_pure(
                player,
                "smuggler_sell",
                {"item_id": "raw_heim_crab"},
            )
            self.assertTrue(ok, info)

        view = dungeoneering_view_pure(player, selected_skill="Dungeoneering")
        self.assertEqual(player["dungeoneering"]["session_coins"], raw_crabs * 60)
        self.assertEqual(
            view["smuggler_reachable_coins"],
            player["dungeoneering"]["session_coins"],
        )
        self.assertEqual(view["smuggler_source_row_count"], 86)
        self.assertTrue(
            all(
                row["buy_price"] <= view["smuggler_reachable_coins"]
                for row in view["smuggler_rows"]
            )
        )
        self.assertNotIn(
            "novite_rapier",
            {row["item_id"] for row in view["smuggler_rows"]},
        )
        _unchanged, ok, info = apply_dungeoneering_command_pure(
            player,
            "smuggler_buy",
            {"item_id": "novite_rapier"},
        )
        self.assertFalse(ok)
        self.assertIn("Need 875", info["reason"])

    def test_bind_replace_skip_and_ammo_bind_persist_across_floor_evaporation(self):
        player = self._enter()
        bank_before = copy.deepcopy(player["inventory"])
        player, ok, info = record_dungeon_drop_pure(
            player,
            "Eligible blade",
            equipment_slot="weapon",
        )
        self.assertTrue(ok, info)
        self.assertTrue(player["dungeoneering"]["pending_bind_offer"])
        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "resolve_bind_offer",
            {"choice": "bind"},
        )
        self.assertTrue(ok, info)
        self.assertEqual(player["dungeoneering"]["session_equipment"]["weapon"], "Eligible blade")

        player, ok, info = record_dungeon_drop_pure(
            player,
            "Replacement blade",
            equipment_slot="weapon",
        )
        self.assertTrue(ok, info)
        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "resolve_bind_offer",
            {"choice": "replace"},
        )
        self.assertTrue(ok, info)
        self.assertNotIn("Eligible blade", player["dungeoneering"]["session_inventory"])
        self.assertEqual(player["dungeoneering"]["bound_items"][0]["item_name"], "Replacement blade")

        player, ok, info = record_dungeon_drop_pure(
            player,
            "Bound arrows",
            500,
            ammo=True,
        )
        self.assertTrue(ok, info)
        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "resolve_bind_offer",
            {"choice": "bind"},
        )
        self.assertTrue(ok, info)
        self.assertEqual(player["dungeoneering"]["ammo_bind"]["quantity"], 125)

        player, ok, info = record_dungeon_drop_pure(
            player,
            "Skipped blade",
            equipment_slot="weapon",
        )
        self.assertTrue(ok, info)
        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "resolve_bind_offer",
            {"choice": "skip"},
        )
        self.assertTrue(ok, info)
        self.assertEqual(player["dungeoneering"]["remembered_bind_choice"], "skip")
        self.assertEqual(player["dungeoneering"]["bound_items"][0]["item_name"], "Replacement blade")

        player, ok, info = apply_dungeoneering_command_pure(player, "abandon")
        self.assertTrue(ok, info)
        self.assertEqual(player["inventory"], bank_before)
        self.assertEqual(player["dungeoneering"]["session_inventory"], {})
        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "enter",
            {
                "floor": 6,
                "size": "small",
                "complexity": 6,
                "automation_mode": "casual",
            },
        )
        self.assertTrue(ok, info)
        self.assertEqual(player["dungeoneering"]["session_equipment"]["weapon"], "Replacement blade")
        self.assertEqual(player["dungeoneering"]["session_inventory"]["Bound arrows"], 125)
        self.assertEqual(player["inventory"], bank_before)

    def test_ten_item_collection_and_three_selectable_loadouts_are_separate_from_active_slots(self):
        player = self._player(dungeoneering_level=120)
        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "enter",
            {
                "floor": 6,
                "size": "small",
                "complexity": 6,
                "automation_mode": "casual",
            },
        )
        self.assertTrue(ok, info)
        for item_number in range(1, 7):
            player, ok, info = record_dungeon_drop_pure(
                player,
                f"Collected blade {item_number}",
                equipment_slot="weapon",
            )
            self.assertTrue(ok, info)
            player, ok, info = apply_dungeoneering_command_pure(
                player,
                "resolve_bind_offer",
                {"choice": "bind"},
            )
            self.assertTrue(ok, info)
        self.assertEqual(len(player["dungeoneering"]["bound_items"]), 6)
        self.assertEqual(len(player["dungeoneering"]["bind_loadouts"][0]), 5)
        view = dungeoneering_view_pure(player, selected_skill="Dungeoneering")
        self.assertEqual((view["bind_slots_used"], view["bind_slots"]), (5, 5))

        player, ok, info = apply_dungeoneering_command_pure(player, "abandon")
        self.assertTrue(ok, info)
        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "set_bind_loadout",
            {"loadout_index": 1, "item_names": ["Collected blade 6"]},
        )
        self.assertTrue(ok, info)
        self.assertEqual(player["dungeoneering"]["active_bind_loadout"], 1)
        self.assertEqual(len(player["dungeoneering"]["bind_loadouts"]), 3)
        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "enter",
            {
                "floor": 6,
                "size": "small",
                "complexity": 6,
                "automation_mode": "casual",
            },
        )
        self.assertTrue(ok, info)
        self.assertEqual(
            player["dungeoneering"]["session_equipment"],
            {"weapon": "Collected blade 6"},
        )

    def test_real_boss_burst_auto_eats_and_evaporates_the_closed_session_inventory(self):
        player = self._enter()
        bank_before = copy.deepcopy(player["inventory"])
        player["dungeoneering"]["session_inventory"] = {
            "Heim crab": 1,
            "Raw heim crab": 1,
        }
        player["combat_lifepoints"] = 100
        while True:
            view = dungeoneering_view_pure(player, selected_skill="Dungeoneering")
            route = next(row for row in view["frontier_rows"] if row["casual_recommended"])
            if route["family"] == "boss":
                break
            player, ok, result = apply_dungeoneering_review_pure(
                player,
                lambda: 0.5,
                equipment_data=EQUIPMENT_DATA,
            )
            self.assertTrue(ok, result)
        player["dungeoneering"]["boss"]["lifepoints"] = 1
        player["dungeoneering"]["boss"]["encounter"]["enemy_lifepoints"] = 1
        completed, ok, result = apply_dungeoneering_review_pure(
            player,
            lambda: 0.1,
            equipment_data=EQUIPMENT_DATA,
        )
        self.assertTrue(ok, result)
        self.assertTrue(result["complete"])
        self.assertTrue(result["boss_killed"])
        self.assertEqual(result["healed"], 20)
        self.assertTrue(result["combat_xp_rewards"])
        self.assertEqual(completed["inventory"], bank_before)
        self.assertEqual(completed["dungeoneering"]["session_inventory"], {})
        self.assertEqual(completed["dungeoneering"]["session_equipment"], {})
        self.assertEqual(completed["dungeoneering"]["boss"], {})

    def test_all_six_frozen_bosses_run_through_the_shared_six_tick_reducer(self):
        player = self._player(dungeoneering_level=21)
        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "enter",
            {
                "floor": 11,
                "size": "small",
                "complexity": 6,
                "automation_mode": "casual",
            },
        )
        self.assertTrue(ok, info)
        player.update(
            {
                "attack_level": 99,
                "strength_level": 99,
                "constitution_level": 99,
                "combat_lifepoints": 990,
            }
        )
        while True:
            view = dungeoneering_view_pure(player, selected_skill="Dungeoneering")
            route = next(row for row in view["frontier_rows"] if row["casual_recommended"])
            if route["family"] == "boss":
                break
            player, ok, result = apply_dungeoneering_review_pure(
                player,
                lambda: 0.5,
                equipment_data=EQUIPMENT_DATA,
            )
            self.assertTrue(ok, result)
        pre_boss = copy.deepcopy(player)

        for boss in FROZEN_BOSSES:
            with self.subTest(boss=boss.id):
                candidate = copy.deepcopy(pre_boss)
                combat_level = FROZEN_BOSS_COMBAT_LEVEL_LADDERS[boss.id][0]
                candidate["dungeoneering"]["boss"] = {
                    "boss_id": boss.id,
                    "combat_level": combat_level,
                    "lifepoints": 1,
                    "encounter": {
                        "target_id": "dungeoneering_boss",
                        "enemy_lifepoints": 1,
                    },
                }
                completed, ok, result = apply_dungeoneering_review_pure(
                    candidate,
                    lambda: 0.1,
                    equipment_data=EQUIPMENT_DATA,
                )
                self.assertTrue(ok, result)
                self.assertTrue(result["boss_killed"])
                self.assertTrue(result["complete"])
                self.assertEqual(completed["dungeoneering"]["boss"], {})

    def test_real_review_reducer_completes_floor_and_runtime_awards_xp_tokens(self):
        player = self._enter()
        before_exp = player["dungeoneering_exp"]
        saved = []
        gains = []
        deactivated = []

        def award_skill_exp(exp_key, amount):
            player[exp_key] = float(player.get(exp_key, 0.0)) + float(amount)
            return float(amount)

        ctx = RuntimeActionContext(
            player_data=player,
            random_random=lambda: 0.5,
            show_error_message=lambda *_args: self.fail("unexpected runtime error"),
            deactivate_current_skill=lambda _reason=None: deactivated.append(True),
            award_skill_exp=award_skill_exp,
            award_hidden_skill_exp=lambda *_args: None,
            level_up_check=lambda *_args: None,
            check_achievements=lambda *_args: None,
            save_player_data=lambda: saved.append(copy.deepcopy(player)),
            refresh_skill_availability=lambda: None,
            show_exp=lambda amount: gains.append(float(amount)),
            show_activity_gain=lambda message: gains.append(str(message)),
            implemented_exp_keys_snapshot=lambda: {},
            show_quest_exp_delta=lambda *_args: None,
        )
        handler = answer_handler_for_key("dungeoneering")
        self.assertIsNotNone(handler)
        player["combat_lifepoints"] = 0
        self.assertTrue(handler(ctx))
        death_session = player["dungeoneering"]["session"]
        self.assertEqual(death_session["death_count"], 1)
        self.assertEqual(death_session["current_room_id"], 0)
        self.assertEqual(death_session["resolved_room_ids"], [0])
        self.assertGreater(player["combat_lifepoints"], 0)

        answered_reviews = 0
        while player["dungeoneering"]["active"]:
            self.assertLess(answered_reviews, 100)
            self.assertTrue(can_start_action(ctx, "dungeoneering"))
            self.assertTrue(handler(ctx))
            answered_reviews += 1
        self.assertGreaterEqual(answered_reviews, STARTER_SMALL_REVIEW_BUDGET)
        self.assertGreater(player["dungeoneering_exp"], before_exp)
        self.assertGreater(player["dungeoneering"]["tokens"], 0)
        self.assertFalse(player["dungeoneering"]["active"])
        self.assertEqual(player["activity_session"], {"active_id": ""})
        self.assertEqual(len(saved), answered_reviews + 1)
        self.assertEqual(deactivated, [True])
        self.assertTrue(any("Dungeoneering XP" in str(value) for value in gains))
        telemetry = player["action_telemetry"]["actions"]
        self.assertIn("dungeoneering:starter_floor", telemetry)

    def test_floor_one_completion_resets_at_the_accessible_prestige_boundary(self):
        player = self._player(dungeoneering_level=1)
        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "enter",
            {
                "floor": 1,
                "size": "small",
                "complexity": 1,
                "automation_mode": "casual",
            },
        )
        self.assertTrue(ok, info)
        player.update(
            {
                "attack_level": 99,
                "strength_level": 99,
                "constitution_level": 99,
                "combat_lifepoints": 990,
            }
        )
        player["dungeoneering"]["boss"]["lifepoints"] = 1
        player["dungeoneering"]["boss"]["encounter"]["enemy_lifepoints"] = 1
        final_result = {}
        while player["dungeoneering"]["active"]:
            player, ok, final_result = apply_dungeoneering_review_pure(
                player,
                lambda: 0.1,
                equipment_data=EQUIPMENT_DATA,
            )
            self.assertTrue(ok, final_result)
        self.assertTrue(final_result["complete"])
        self.assertEqual(player["dungeoneering"]["checked_floors"]["frozen"], [])
        self.assertEqual(player["dungeoneering"]["previous_progress"]["frozen"], 1)
        self.assertTrue(final_result["payout"]["prestige_reset"])

    def test_legacy_bind_collection_migrates_into_the_first_of_three_loadouts(self):
        raw = default_dungeoneering_state_pure()
        raw.pop("bind_loadouts")
        raw.pop("active_bind_loadout")
        raw["bound_items"] = [
            {"item_name": "Legacy blade", "quantity": 1, "slot": "weapon"},
            {"item_name": "Legacy shield", "quantity": 1, "slot": "shield"},
        ]
        cleaned = sanitize_dungeoneering_state_pure(raw)
        self.assertEqual(
            cleaned["bind_loadouts"],
            [["Legacy blade", "Legacy shield"], [], []],
        )
        self.assertEqual(cleaned["active_bind_loadout"], 0)

    def test_storage_repair_rebuilds_frontier_from_the_seeded_graph(self):
        entered = self._enter()
        raw = copy.deepcopy(entered["dungeoneering"])
        raw["session"]["resolved_room_ids"] = [0, 1, 999]
        raw["session"]["frontier_room_ids"] = [999]
        raw["session"]["current_room_id"] = 999
        cleaned = sanitize_dungeoneering_state_pure(raw)
        session = cleaned["session"]
        self.assertNotIn(999, session["resolved_room_ids"])
        self.assertNotIn(999, session["frontier_room_ids"])
        self.assertEqual(session["current_room_id"], 0)
        self.assertTrue(session["frontier_room_ids"])
        self.assertEqual(
            set(cleaned),
            set(default_dungeoneering_state_pure()),
        )


class DungeoneeringPhaseCTests(unittest.TestCase):
    def _player(self, **overrides):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player.update(overrides)
        return player

    def test_v100_sanitizer_adds_and_clamps_phase_c_state(self):
        old_state = default_dungeoneering_state_pure()
        for key in (
            "kinship_active_class",
            "kinship_tiers",
            "tokens_earned",
            "tokens_spent",
            "coal_bag_owned",
            "coal_bag_coal",
        ):
            old_state.pop(key)
        old_state["tokens"] = 50

        cleaned = sanitize_dungeoneering_state_pure(old_state)

        self.assertEqual(cleaned["kinship_active_class"], "tank")
        self.assertEqual(len(cleaned["kinship_tiers"]), 12)
        self.assertEqual(cleaned["tokens_earned"], 50)
        self.assertEqual(cleaned["tokens_spent"], 0)
        self.assertFalse(cleaned["coal_bag_owned"])
        self.assertEqual(cleaned["coal_bag_coal"], 0)

        cleaned = sanitize_dungeoneering_state_pure(
            {
                **cleaned,
                "kinship_active_class": "not-a-class",
                "kinship_tiers": {"gatherer": 99, "artisan": -2},
                "coal_bag_owned": True,
                "coal_bag_coal": 999,
            }
        )
        self.assertEqual(cleaned["kinship_active_class"], "tank")
        self.assertEqual(cleaned["kinship_tiers"]["gatherer"], 10)
        self.assertEqual(cleaned["kinship_tiers"]["artisan"], 0)
        self.assertEqual(cleaned["coal_bag_coal"], COAL_BAG_CAPACITY)

    def test_v100_save_receives_phase_c_defaults_without_a_schema_bump(self):
        player = self._player()
        player["config_version"] = 100
        for key in (
            "kinship_active_class",
            "kinship_tiers",
            "tokens_earned",
            "tokens_spent",
            "coal_bag_owned",
            "coal_bag_coal",
        ):
            player["dungeoneering"].pop(key)

        migrated = migrate_loaded_data(player, ORE_DATA, ITEM_DEFINITIONS)

        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["dungeoneering"]["kinship_active_class"], "tank")
        self.assertEqual(len(migrated["dungeoneering"]["kinship_tiers"]), 12)
        self.assertFalse(migrated["dungeoneering"]["coal_bag_owned"])
        self.assertEqual(migrated["dungeoneering"]["coal_bag_coal"], 0)

    def test_kinship_selection_and_exact_tier_upgrades_use_the_command_reducer(self):
        player = self._player()
        player["dungeoneering"]["tokens"] = sum(KINSHIP_TIER_COSTS)

        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "select_kinship_class",
            {"class_id": "gatherer"},
        )
        self.assertTrue(ok, info)
        self.assertEqual(player["dungeoneering"]["kinship_active_class"], "gatherer")

        balance = sum(KINSHIP_TIER_COSTS)
        for tier, exact_cost in enumerate(KINSHIP_TIER_COSTS, start=1):
            player, ok, info = apply_dungeoneering_command_pure(
                player,
                "upgrade_kinship_class",
                {"class_id": "gatherer"},
            )
            self.assertTrue(ok, info)
            balance -= exact_cost
            self.assertEqual(
                player["dungeoneering"]["kinship_tiers"]["gatherer"],
                tier,
            )
            self.assertEqual(player["dungeoneering"]["tokens"], balance)
        self.assertEqual(
            player["dungeoneering"]["tokens_spent"],
            sum(KINSHIP_TIER_COSTS),
        )

        unchanged, ok, info = apply_dungeoneering_command_pure(
            player,
            "upgrade_kinship_class",
            {"class_id": "gatherer"},
        )
        self.assertFalse(ok)
        self.assertIn("tier 10", info["reason"])
        self.assertEqual(unchanged["dungeoneering"], player["dungeoneering"])

    def test_kinship_changes_are_refused_during_a_floor(self):
        player = self._player(dungeoneering_level=1)
        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "enter",
            {
                "floor": 1,
                "size": "small",
                "complexity": 1,
                "automation_mode": "casual",
            },
        )
        self.assertTrue(ok, info)

        for action_id in ("select_kinship_class", "upgrade_kinship_class"):
            with self.subTest(action_id=action_id):
                _unchanged, ok, info = apply_dungeoneering_command_pure(
                    player,
                    action_id,
                    {"class_id": "artisan"},
                )
                self.assertFalse(ok)
                self.assertIn("between floors", info["reason"])

    def test_trader_renders_42_rows_but_only_functional_coal_bag_can_open(self):
        player = self._player(
            dungeoneering_level=99,
            mining_level=99,
            magic_level=99,
            runecrafting_level=99,
        )
        player["dungeoneering"]["tokens"] = 500_000

        view = dungeoneering_view_pure(player)

        self.assertEqual(view["reward_catalog_count"], 42)
        self.assertEqual(view["reward_purchase_count"], 1)
        purchasable = [row["reward_id"] for row in view["reward_rows"] if row["can_purchase"]]
        self.assertEqual(purchasable, ["coal_bag"])
        for row in view["reward_rows"]:
            if row["reward_id"] == "coal_bag":
                self.assertEqual(row["status_text"], "Available")
            else:
                self.assertFalse(row["fully_functional"])
                self.assertEqual(
                    row["status_text"],
                    "Catalogued — not purchasable yet",
                )

    def test_trader_enforces_level_token_functionality_and_one_owned_gates(self):
        player = self._player()
        player["dungeoneering"]["tokens"] = 500_000
        _unchanged, ok, info = apply_dungeoneering_command_pure(
            player,
            "purchase_reward",
            {"reward_id": "coal_bag"},
        )
        self.assertFalse(ok)
        self.assertIn("Dungeoneering 35", info["reason"])

        player["dungeoneering_level"] = 35
        _unchanged, ok, info = apply_dungeoneering_command_pure(
            player,
            "purchase_reward",
            {"reward_id": "coal_bag"},
        )
        self.assertFalse(ok)
        self.assertIn("Mining 35", info["reason"])

        player["mining_level"] = 35
        player["dungeoneering"]["tokens"] = 3_999
        _unchanged, ok, info = apply_dungeoneering_command_pure(
            player,
            "purchase_reward",
            {"reward_id": "coal_bag"},
        )
        self.assertFalse(ok)
        self.assertIn("4,000 tokens", info["reason"])

        player["dungeoneering"]["tokens"] = 4_000
        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "purchase_reward",
            {"reward_id": "coal_bag"},
        )
        self.assertTrue(ok, info)
        self.assertTrue(player["dungeoneering"]["coal_bag_owned"])
        self.assertEqual(player["dungeoneering"]["tokens"], 0)
        self.assertEqual(player["dungeoneering"]["tokens_spent"], 4_000)

        _unchanged, ok, info = apply_dungeoneering_command_pure(
            player,
            "purchase_reward",
            {"reward_id": "coal_bag"},
        )
        self.assertFalse(ok)
        self.assertIn("Only one", info["reason"])

        player["dungeoneering"]["tokens"] = 500_000
        _unchanged, ok, info = apply_dungeoneering_command_pure(
            player,
            "purchase_reward",
            {"reward_id": "chaotic_rapier"},
        )
        self.assertFalse(ok)
        self.assertIn("not purchasable yet", info["reason"])

    def test_coal_bag_fill_moves_bank_or_carried_coal_and_stops_at_27(self):
        player = self._player(
            dungeoneering_level=35,
            mining_level=35,
            current_smith="smelt_steel_bar",
        )
        player["dungeoneering"].update(
            {"coal_bag_owned": True, "coal_bag_coal": 0}
        )
        player["inventory"]["Coal"] = 40
        player["carried_inventory"] = {"smelt_steel_bar": {"Coal": 10}}

        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "fill_coal_bag",
            {"source": "bank"},
        )
        self.assertTrue(ok, info)
        self.assertEqual(player["dungeoneering"]["coal_bag_coal"], 27)
        self.assertEqual(player["inventory"]["Coal"], 13)
        self.assertEqual(
            player["carried_inventory"]["smelt_steel_bar"]["Coal"],
            10,
        )

        _unchanged, ok, info = apply_dungeoneering_command_pure(
            player,
            "fill_coal_bag",
            {"source": "bank"},
        )
        self.assertFalse(ok)
        self.assertIn("already holds 27", info["reason"])

        player["dungeoneering"]["coal_bag_coal"] = 0
        player, ok, info = apply_dungeoneering_command_pure(
            player,
            "fill_coal_bag",
            {"source": "carried"},
        )
        self.assertTrue(ok, info)
        self.assertEqual(player["dungeoneering"]["coal_bag_coal"], 10)
        self.assertEqual(player["inventory"]["Coal"], 3)
        self.assertNotIn("smelt_steel_bar", player["carried_inventory"])


class DungeoneeringReviewUndoIntegrationTests(unittest.TestCase):
    def setUp(self):
        from tests.test_integration_smoke import _install_runtime_fakes

        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_global_review_multiplier_does_not_shorten_starter_floor(self):
        from tests.test_integration_smoke import _load_addon_as_package

        addon = _load_addon_as_package("ankiscape_dungeoneering_multiplier")
        logic = sys.modules[f"{addon.__name__}.logic.dungeoneering_logic"]
        storage = sys.modules[f"{addon.__name__}.core.storage_pure"]
        constants = sys.modules[f"{addon.__name__}.core.constants"]
        player = storage.default_player_data(
            constants.ORE_DATA,
            constants.ITEM_DEFINITIONS,
        )
        player["dungeoneering_level"] = 11
        player, ok, info = logic.apply_dungeoneering_command_pure(
            player,
            "enter",
            {
                "floor": 6,
                "size": "small",
                "complexity": 6,
                "automation_mode": "casual",
            },
        )
        self.assertTrue(ok, info)
        player.update(
            {
                "attack_level": 99,
                "strength_level": 99,
                "constitution_level": 99,
                "combat_lifepoints": 990,
            }
        )
        player["dungeoneering"]["boss"]["lifepoints"] = 1
        player["dungeoneering"]["boss"]["encounter"]["enemy_lifepoints"] = 1

        addon._state.player_data = player
        addon._state.current_skill = "Dungeoneering"
        addon._review_action_multiplier = lambda: 2
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _message: None
        addon._show_exp = lambda _amount: None
        addon._advance_world_events_after_review = lambda: None
        addon._save_player_data_if_anki_ready = lambda: None

        original_random = addon.random.random
        addon.random.random = lambda: 0.5
        try:
            for answered_reviews in range(1, STARTER_SMALL_REVIEW_BUDGET + 1):
                addon._state.exp_awarded = False
                addon.on_good_answer(copy.deepcopy(addon._state.player_data))
                active = addon._state.player_data["dungeoneering"]["active"]
                self.assertEqual(
                    active,
                    answered_reviews < STARTER_SMALL_REVIEW_BUDGET,
                )
                if active:
                    self.assertEqual(
                        len(
                            addon._state.player_data["dungeoneering"]["session"][
                                "resolved_room_ids"
                            ]
                        ),
                        answered_reviews + 1,
                    )
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["dungeoneering"]["floors_completed"], 1)

    def test_answer_undo_restores_resource_automation_inventory_and_skill_xp_atomically(self):
        from tests.test_integration_smoke import _load_addon_as_package

        addon = _load_addon_as_package("ankiscape_dungeoneering_resource_undo")
        logic = sys.modules[f"{addon.__name__}.logic.dungeoneering_logic"]
        storage = sys.modules[f"{addon.__name__}.core.storage_pure"]
        constants = sys.modules[f"{addon.__name__}.core.constants"]
        player = storage.default_player_data(
            constants.ORE_DATA,
            constants.ITEM_DEFINITIONS,
        )
        player["dungeoneering_level"] = 11
        player, ok, info = logic.apply_dungeoneering_command_pure(
            player,
            "enter",
            {
                "floor": 6,
                "size": "small",
                "complexity": 6,
                "automation_mode": "casual",
            },
        )
        self.assertTrue(ok, info)
        while True:
            view = logic.dungeoneering_view_pure(
                player,
                selected_skill="Dungeoneering",
            )
            route = next(
                row for row in view["frontier_rows"] if row["casual_recommended"]
            )
            if route["family"] == "resource":
                break
            player, ok, info = logic.apply_dungeoneering_review_pure(
                player,
                lambda: 0.5,
                equipment_data=constants.EQUIPMENT_DATA,
            )
            self.assertTrue(ok, info)

        addon._state.player_data = player
        addon._state.current_skill = "Dungeoneering"
        addon._state.exp_awarded = False
        addon._review_action_multiplier = lambda: 1
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _message: None
        addon._show_exp = lambda _amount: None
        addon._advance_world_events_after_review = lambda: None
        addon._save_player_data_if_anki_ready = lambda: None
        before = copy.deepcopy(addon._state.player_data)
        original_random = addon.random.random
        addon.random.random = lambda: 0.5
        try:
            addon.on_good_answer(before)
        finally:
            addon.random.random = original_random
        self.assertEqual(addon._state.player_data["dungeoneering"]["session_inventory"]["Heim crab"], 1)
        self.assertEqual(
            addon._state.player_data["fishing_exp"],
            before["fishing_exp"] + 9.0,
        )
        self.assertEqual(
            addon._state.player_data["cooking_exp"],
            before["cooking_exp"] + 22.0,
        )

        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
        self.assertEqual(addon._state.player_data, before)

    def test_answer_undo_restores_the_exact_pre_boss_session_and_save(self):
        from tests.test_integration_smoke import _load_addon_as_package

        addon = _load_addon_as_package("ankiscape_dungeoneering_hook")
        logic = sys.modules[f"{addon.__name__}.logic.dungeoneering_logic"]
        storage = sys.modules[f"{addon.__name__}.core.storage_pure"]
        constants = sys.modules[f"{addon.__name__}.core.constants"]
        player = storage.default_player_data(
            constants.ORE_DATA,
            constants.ITEM_DEFINITIONS,
        )
        player["dungeoneering_level"] = 11
        player, ok, info = logic.apply_dungeoneering_command_pure(
            player,
            "enter",
            {
                "floor": 6,
                "size": "small",
                "complexity": 6,
                "automation_mode": "casual",
            },
        )
        self.assertTrue(ok, info)
        while True:
            session = player["dungeoneering"]["session"]
            rooms = {row["id"]: row for row in session["rooms"]}
            if any(
                rooms[room_id]["family"] == "boss"
                for room_id in session["frontier_room_ids"]
            ):
                break
            player, ok, info = logic.apply_dungeoneering_review_pure(player)
            self.assertTrue(ok, info)
        player.update(
            {
                "attack_level": 99,
                "strength_level": 99,
                "constitution_level": 99,
                "combat_lifepoints": 990,
            }
        )
        player["dungeoneering"]["boss"]["lifepoints"] = 1
        player["dungeoneering"]["boss"]["encounter"]["enemy_lifepoints"] = 1

        addon._state.player_data = player
        addon._state.current_skill = "Dungeoneering"
        addon._state.exp_awarded = False
        addon._review_action_multiplier = lambda: 1
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _message: None
        addon._show_exp = lambda _amount: None
        addon._advance_world_events_after_review = lambda: None
        addon._save_player_data_if_anki_ready = lambda: None
        before = copy.deepcopy(addon._state.player_data)

        addon.on_good_answer(before)
        self.assertFalse(addon._state.player_data["dungeoneering"]["active"])
        self.assertGreater(addon._state.player_data["dungeoneering_exp"], before["dungeoneering_exp"])
        self.assertGreater(addon._state.player_data["dungeoneering"]["tokens"], 0)

        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
        self.assertEqual(addon._state.player_data, before)


if __name__ == "__main__":
    unittest.main()
