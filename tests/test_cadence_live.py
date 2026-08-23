import copy
import random
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.runtime import runtime_actions

# Patch targets live on the module that defines the name: a caller resolves it
# from its own globals, not from runtime_actions' re-export.
from ankiscape.runtime import runtime_actions_production

from ankiscape.logic.cadence_coverage import (
    cadence_coverage_rows_pure,
    validate_cadence_coverage_pure,
)
from ankiscape.logic.cadence_kernel import (
    CADENCE_WAIT,
    EMBEDDED_PROBABILITY,
    RATE_LIMITED,
    default_cadence_profile_state_pure,
)
from ankiscape.logic.cadence_live import (
    LIVE_COMBAT_TICKS_PER_REVIEW,
    advance_live_cadence_route_pure,
    resolve_live_cadence_route_pure,
)
from ankiscape.core.constants import (
    COOKING_DATA,
    EQUIPMENT_DATA,
    ITEM_DEFINITIONS,
    ORE_DATA,
    QUEST_DATA,
    TREE_DATA,
)
from ankiscape.logic_pure.logic_pure import (
    apply_combat_burst_pure,
    apply_cooking_action_pure,
    apply_quest_combat_encounter_pure,
    cooking_source_roll_chance_pure,
    record_cadence_wait_telemetry_pure,
)
from ankiscape.runtime.runtime_actions import (
    ANSWER_HANDLERS,
    handle_magic_answer,
    handle_quest_answer,
    handle_thieving_answer,
    handle_woodcutting_answer,
    run_answer_with_carried_overlay,
)
from ankiscape.logic.summoning_logic import advance_summoning_world_tick_pure
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from tests.test_combat_logic import _player
from tests.test_runtime_actions import _context


class TestCadenceLiveCoverage(unittest.TestCase):
    def test_every_runtime_handler_and_selectable_route_is_declared(self):
        summary = validate_cadence_coverage_pure(ANSWER_HANDLERS)
        self.assertEqual(summary["handlers"], 21)
        self.assertGreaterEqual(summary["foreground_routes"], 2_190)
        self.assertGreaterEqual(summary["modes"]["combat_ticks"], 130)
        self.assertTrue(
            any(
                row["action_id"] == "attached:winter_storage"
                for row in cadence_coverage_rows_pure()
            )
        )
        dungeoneering = next(
            row
            for row in cadence_coverage_rows_pure()
            if row["handler_key"] == "dungeoneering"
            and row["action_id"] == "starter_floor"
        )
        self.assertEqual(dungeoneering["mode"], "passthrough")
        self.assertEqual(
            dungeoneering["undo_boundary"],
            "one answered-card transaction",
        )

    def test_new_handler_fails_closed_until_it_has_a_declaration(self):
        with self.assertRaisesRegex(ValueError, "missing=.*slayer_live"):
            validate_cadence_coverage_pure({*ANSWER_HANDLERS, "slayer_live"})

    def test_livid_farm_declares_its_exact_activity_owned_residual(self):
        row = next(
            row
            for row in cadence_coverage_rows_pure()
            if row["handler_key"] == "utility"
            and row["action_id"] == "livid_farm"
        )

        self.assertEqual(row["mode"], "rate_limited")
        self.assertEqual(row["source_status"], "sourced")
        self.assertEqual(row["profile"]["increment_numerator"], 6)
        self.assertEqual(row["profile"]["threshold_denominator"], 5)

    def test_big_chinchompa_declares_grouped_jar_and_world_boundary(self):
        row = next(
            row
            for row in cadence_coverage_rows_pure()
            if row["handler_key"] == "utility"
            and row["action_id"] == "big_chinchompa"
        )

        self.assertEqual(row["mode"], "activity_group")
        self.assertEqual(row["source_status"], "sourced")
        self.assertEqual(
            row["includes"],
            ("fifteen-moth jar circuit", "world boundary"),
        )
        self.assertIn("up to M whole circuits", row["multiplier_behavior"])

    def test_shooting_star_declares_one_attempt_and_crowd_boundary(self):
        row = next(
            row
            for row in cadence_coverage_rows_pure()
            if row["handler_key"] == "utility"
            and row["action_id"] == "shooting_stars"
        )

        self.assertEqual(row["mode"], "activity_group")
        self.assertEqual(
            row["includes"],
            ("one stardust attempt", "one public-crowd boundary"),
        )
        self.assertIn(
            "Never foreground-multiplied",
            row["multiplier_behavior"],
        )

    def test_fight_caves_declares_one_live_combat_and_roster_pressure_boundary(self):
        row = next(
            row
            for row in cadence_coverage_rows_pure()
            if row["handler_key"] == "utility"
            and row["action_id"] == "fight_caves"
        )
        self.assertEqual(row["mode"], "activity_group")
        self.assertEqual(row["source_status"], "sourced")
        self.assertEqual(
            row["includes"],
            (
                "one engaged six-tick Combat slice",
                "one unengaged-roster pressure boundary",
                "one atomic wave-state transaction",
            ),
        )

    def test_barbarian_assault_declares_one_duty_or_persistent_queen_beat(self):
        row = next(
            row
            for row in cadence_coverage_rows_pure()
            if row["handler_key"] == "utility"
            and row["action_id"] == "barbarian_assault"
        )

        self.assertEqual(row["mode"], "activity_group")
        self.assertEqual(row["source_status"], "sourced_with_disclosed_translation")
        self.assertEqual(
            row["includes"],
            (
                "one productive duty or explicit Again idle/Queen-pressure beat",
                "wave points, safe restart, and terminal Queen settlement",
            ),
        )
        self.assertIn("Never foreground-multiplied", row["multiplier_behavior"])

    def test_declared_multiplier_behavior_matches_single_step_exemptions(self):
        thieving = resolve_live_cadence_route_pure(
            "thieving", "stall_silver", {}
        )
        agility = resolve_live_cadence_route_pure(
            "agility", "burthorpe_course", {}
        )
        self.assertIn("never foreground-multiplied", thieving.multiplier_behavior)
        self.assertIn("never foreground-multiplied", agility.multiplier_behavior)

    def test_exact_seed_profiles_and_range_policy_are_auditable(self):
        maple = resolve_live_cadence_route_pure("woodcutting", "maple", {})
        shark = resolve_live_cadence_route_pure("fishing", "catch_sharks", {})
        altar = resolve_live_cadence_route_pure(
            "prayer", "gilded_altar_dragon_bones", {}
        )
        iron = resolve_live_cadence_route_pure(
            "mining",
            "iron",
            {"carried_keep_drop": {"iron": "drop"}},
        )
        self.assertEqual(
            (maple.profile.increment_numerator, maple.profile.threshold_denominator),
            (3, 10),
        )
        self.assertEqual(
            (shark.profile.increment_numerator, shark.profile.threshold_denominator),
            (2, 11),
        )
        self.assertEqual(
            (altar.profile.increment_numerator, altar.profile.threshold_denominator),
            (115, 126),
        )
        self.assertEqual(
            (iron.profile.increment_numerator, iron.profile.threshold_denominator),
            (1, 1),
        )
        self.assertNotIn("urns", iron.includes)
        self.assertIn("lower_source_endpoint", iron.source_reason)

    def test_only_unimplemented_modifier_routes_remain_source_blocked(self):
        kept_iron = resolve_live_cadence_route_pure("mining", "iron", {})
        shark = resolve_live_cadence_route_pure("cooking", "cook_shark", {})
        alchemy_without_staff = resolve_live_cadence_route_pure(
            "magic", "high_alchemy", {}
        )
        self.assertEqual(kept_iron.mode, "source_blocked")
        self.assertEqual(shark.mode, "embedded_probability")
        self.assertEqual(alchemy_without_staff.mode, "source_blocked")

    def test_runtime_xp_incompatible_source_rows_remain_blocked(self):
        for skill_id, target_id in (
            ("fishing", "catch_trout_salmon"),
            ("hunter", "catch_chinchompa"),
            ("hunter", "catch_black_salamander"),
            ("hunter", "catch_spotted_kebbit"),
            ("hunter", "catch_dark_kebbit"),
        ):
            with self.subTest(skill_id=skill_id, target_id=target_id):
                declaration = resolve_live_cadence_route_pure(
                    skill_id, target_id, {}
                )
                self.assertEqual(declaration.mode, "source_blocked")
                self.assertTrue(declaration.source_row)
                self.assertTrue(declaration.source_reason)

    def test_barehand_black_warlock_uses_its_exact_source_row(self):
        declaration = resolve_live_cadence_route_pure(
            "hunter", "barehand_black_warlock", {}
        )
        self.assertEqual(declaration.mode, RATE_LIMITED)
        self.assertEqual(declaration.source_row, "barehand_black_warlock")
        self.assertEqual(
            (
                declaration.profile.increment_numerator,
                declaration.profile.threshold_denominator,
            ),
            (14, 65),
        )
        self.assertIn("attached 125 Agility XP", declaration.includes)

    def test_cheese_wheel_churning_uses_eight_tick_period_cadence(self):
        for target_id in (
            "churn_milk_cheese_wheel",
            "churn_butter_cheese_wheel",
        ):
            with self.subTest(target_id=target_id):
                declaration = resolve_live_cadence_route_pure(
                    "cooking",
                    target_id,
                    {},
                )
                self.assertEqual(declaration.mode, RATE_LIMITED)
                self.assertEqual(declaration.source_status, "sourced")
                self.assertEqual(
                    (
                        declaration.profile.increment_numerator,
                        declaration.profile.threshold_denominator,
                    ),
                    (3, 4),
                )
                self.assertIn("8 game ticks", declaration.source_row)

    def test_loaded_credit_clamps_to_the_profile_residual_boundary(self):
        for saved_credit in (10_000, 9):
            with self.subTest(saved_credit=saved_credit):
                player = migrate_loaded_data(
                    {
                        "inventory": {},
                        "cadence_profiles": {
                            "woodcutting:maple": {
                                "credit": saved_credit,
                                "opening_ready": True,
                                "assigned_reviews": 0,
                                "opportunities_emitted": 0,
                                "cadence_version": 1,
                            }
                        },
                    },
                    ORE_DATA,
                )

                _route, emitted = advance_live_cadence_route_pure(
                    player, "woodcutting", "maple"
                )

                self.assertTrue(emitted)
                state = player["cadence_profiles"]["woodcutting:maple"]
                self.assertEqual(state["credit"], 9)
                self.assertFalse(state["opening_ready"])
                self.assertEqual(state["assigned_reviews"], 1)
                self.assertEqual(state["opportunities_emitted"], 1)

    def test_waits_advance_only_live_residual_and_wait_telemetry(self):
        data = {"cadence_profiles": {}}
        _route, first = advance_live_cadence_route_pure(
            data, "woodcutting", "maple"
        )
        _route, second = advance_live_cadence_route_pure(
            data, "woodcutting", "maple"
        )
        self.assertTrue(first)
        self.assertFalse(second)
        record = record_cadence_wait_telemetry_pure(
            data, "woodcutting", "maple"
        )
        self.assertEqual(record["cadence_waits"], 1)
        self.assertEqual(record["attempts"], 0)
        self.assertEqual(record["failures"], 0)
        self.assertEqual(record["current_dry_streak"], 0)

    def test_forced_gathering_opportunity_does_not_draw_primary_success_roll(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player = {
            "inventory": {},
            "woodcutting_level": 99,
            "woodcutting_exp": 0.0,
            "current_tree": "maple",
            "toolbelt": {"woodcutting": ["bronze_hatchet"]},
            "equipment": {},
            "completed_achievements": [],
        }
        draws = 0

        def rng():
            nonlocal draws
            draws += 1
            return 0.999

        ctx = _context(player, calls)
        ctx.random_random = rng
        ctx.cadence_forced_opportunity = True
        self.assertTrue(handle_woodcutting_answer(ctx))
        self.assertEqual(player["inventory"].get("Maple logs"), 1)
        self.assertEqual(draws, 2)

    def test_embedded_cooking_uses_one_authentic_roll(self):
        route = resolve_live_cadence_route_pure(
            "cooking", "cook_tuna", {}
        )
        self.assertEqual(route.mode, EMBEDDED_PROBABILITY)
        spec = COOKING_DATA["cook_tuna"]
        source_chance = cooking_source_roll_chance_pure(30, spec)
        inventory = {"Raw tuna": 1}
        _legacy, _xp, legacy_ok, _out, legacy_burned = apply_cooking_action_pure(
            "cook_tuna",
            inventory,
            COOKING_DATA,
            30,
            source_chance + 0.01,
        )
        _live, _xp, live_ok, _out, live_burned = apply_cooking_action_pure(
            "cook_tuna",
            inventory,
            COOKING_DATA,
            30,
            source_chance + 0.01,
            use_source_probability=True,
        )
        self.assertTrue(legacy_ok)
        self.assertTrue(live_ok)
        self.assertFalse(legacy_burned)
        self.assertTrue(live_burned)

    def test_magic_owned_admission_is_not_applied_twice_by_carried_overlay(self):
        player = {
            "inventory": {"Nature rune": 1, "Rune platebody": 1},
            "equipment": {"weapon": "Staff of fire"},
            "magic_level": 99,
            "magic_exp": 0.0,
            "current_magic": "high_alchemy",
            "magic_alchemy_item": "Rune platebody",
            "completed_achievements": [],
        }
        ctx = _context(player)
        ctx.cadence_live_enabled = True

        self.assertTrue(
            run_answer_with_carried_overlay(
                ctx,
                "magic",
                handle_magic_answer,
            )
        )

        profile = player["cadence_profiles"]["magic:high_alchemy"]
        self.assertEqual(profile["assigned_reviews"], 1)
        self.assertEqual(profile["opportunities_emitted"], 1)
        self.assertEqual(player["inventory"]["Rune platebody"], 0)

    def test_cadence_wait_does_not_start_bank_trip_or_consume_full_pack(self):
        player = {
            "inventory": {"Maple logs": 28},
            "woodcutting_level": 99,
            "current_tree": "maple",
            "carried_inventory": {"maple": {"Maple logs": 28}},
            "carried_churn": {"maple": 28},
            "carried_keep_drop": {"maple": "keep"},
            "cadence_profiles": {
                "woodcutting:maple": default_cadence_profile_state_pure(
                    opening_ready=False
                )
            },
        }
        called = False

        def handler(_ctx):
            nonlocal called
            called = True
            return True

        calls = {"xp": [], "saves": 0, "errors": []}
        ctx = _context(player, calls)
        ctx.cadence_live_enabled = True

        self.assertTrue(
            run_answer_with_carried_overlay(ctx, "woodcutting", handler)
        )
        self.assertFalse(called)
        self.assertNotIn("skilling_bank_run", player)
        self.assertEqual(player["inventory"]["Maple logs"], 28)
        self.assertEqual(
            player["cadence_profiles"]["woodcutting:maple"]["credit"],
            3,
        )
        self.assertEqual(
            player["action_telemetry"]["actions"]["woodcutting:maple"][
                "cadence_waits"
            ],
            1,
        )
        self.assertFalse(
            any("Bank run" in message for message in calls.get("activity", ()))
        )
        # A rate-limited route withholding an opportunity is the kernel's
        # normal tick, so the review is silent: no XP and no activity line.
        # It fired on the majority of reviews for every capped route before.
        self.assertEqual(calls.get("activity", []), [])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["errors"], [])

    def test_rejected_first_action_restores_live_cadence_residual(self):
        initial = default_cadence_profile_state_pure(opening_ready=True)
        player = {
            "inventory": {},
            "woodcutting_level": 99,
            "woodcutting_exp": 0.0,
            "current_tree": "maple",
            "toolbelt": {"woodcutting": []},
            "equipment": {},
            "cadence_profiles": {
                "woodcutting:maple": copy.deepcopy(initial)
            },
            "completed_achievements": [],
        }
        ctx = _context(player)
        ctx.cadence_live_enabled = True

        self.assertFalse(
            run_answer_with_carried_overlay(
                ctx,
                "woodcutting",
                handle_woodcutting_answer,
            )
        )
        self.assertEqual(
            player["cadence_profiles"]["woodcutting:maple"],
            initial,
        )

    def test_thieving_canary_wait_does_not_count_as_attempt_or_failure(self):
        player = {
            "inventory": {},
            "thieving_level": 99,
            "thieving_exp": 0.0,
            "current_thieving": "stall_silver",
            "thieving_stunned": False,
            "cadence_profiles": {
                "thieving:stall_silver": default_cadence_profile_state_pure(
                    opening_ready=False
                )
            },
            "completed_achievements": [],
        }

        self.assertTrue(handle_thieving_answer(_context(player)))

        telemetry = player["action_telemetry"]["actions"][
            "thieving:stall_silver"
        ]
        self.assertEqual(telemetry["cadence_waits"], 1)
        self.assertEqual(telemetry["attempts"], 0)
        self.assertEqual(telemetry["failures"], 0)
        self.assertEqual(telemetry["current_dry_streak"], 0)


class TestLiveCombatContinuity(unittest.TestCase):
    ENEMIES = {
        "continuity_target": {
            "display_name": "Continuity target",
            "level": 1,
            "group": "Test",
            "stats": {
                "attack": 40,
                "strength": 40,
                "defence": 40,
                "hitpoints": 100_000,
            },
            "bonuses": {},
            "attack_speed": 5,
            "drops": {"guaranteed": (), "tables": ()},
            "source": "test",
        }
    }

    def _run(self, chunks, *, prayers=False):
        player = _player(
            current_combat_target="continuity_target",
            attack_level=80,
            strength_level=80,
            defense_level=80,
            constitution_level=99,
            combat_lifepoints=990,
            combat_special_attack_energy=0,
        )
        if prayers:
            player.update(
                {
                    "prayer_level": 99,
                    "combat_prayer_points": 990,
                    "combat_prayer_book": "curses",
                    "combat_selected_prayers": [
                        "leech_attack",
                        "leech_strength",
                        "leech_defence",
                    ],
                    "combat_prayer_uptime": "100",
                    "quests": {
                        "the_temple_at_senntisten": {"completed": True}
                    },
                }
            )
        rng = random.Random(20260717)
        calls = 0

        def draw():
            nonlocal calls
            calls += 1
            return rng.random()

        result = copy.deepcopy(player)
        for ticks in chunks:
            result, ok, _info = apply_combat_burst_pure(
                result,
                self.ENEMIES,
                EQUIPMENT_DATA,
                ticks=ticks,
                rng=draw,
                live_cadence=True,
            )
            self.assertTrue(ok)
        return result, rng.getstate(), calls

    def test_runtime_tick_budget_is_six_times_multiplier_with_exact_rollback(self):
        live = _context({}, review_action_multiplier=3)
        live.cadence_live_enabled = True
        legacy = _context({}, review_action_multiplier=3)
        legacy.cadence_live_enabled = False

        self.assertEqual(runtime_actions._combat_review_ticks(live), 18)
        self.assertEqual(runtime_actions._combat_review_ticks(legacy), 150)

    def test_special_regen_residual_exists_only_on_live_path(self):
        player = _player(
            current_combat_target="continuity_target",
            combat_special_attack_energy=0,
            constitution_level=99,
            combat_lifepoints=990,
        )
        legacy, ok, _info = apply_combat_burst_pure(
            player,
            self.ENEMIES,
            EQUIPMENT_DATA,
            ticks=6,
            rng=lambda: 0.999,
            live_cadence=False,
        )
        self.assertTrue(ok)
        self.assertNotIn("combat_special_attack_regen_residual", legacy)

        live, ok, _info = apply_combat_burst_pure(
            player,
            self.ENEMIES,
            EQUIPMENT_DATA,
            ticks=6,
            rng=lambda: 0.999,
            live_cadence=True,
        )
        self.assertTrue(ok)
        self.assertEqual(live["combat_special_attack_regen_residual"], 10)

    def test_six_slices_equal_one_continuous_simulation_with_prayer_and_curses(self):
        sliced, sliced_rng, sliced_calls = self._run(
            [LIVE_COMBAT_TICKS_PER_REVIEW] * 6, prayers=True
        )
        whole, whole_rng, whole_calls = self._run([36], prayers=True)
        sliced.pop("combat_last_result", None)
        whole.pop("combat_last_result", None)
        self.assertEqual(sliced, whole)
        self.assertEqual(sliced_rng, whole_rng)
        self.assertEqual(sliced_calls, whole_calls)
        self.assertEqual(
            sliced["combat_special_attack_regen_residual"], 10
        )
        self.assertEqual(sliced["combat_special_attack_energy"], 7)

    def test_prayer_depletion_is_identical_across_tick_chunks(self):
        enemy = copy.deepcopy(self.ENEMIES["continuity_target"])
        enemy["attack_speed"] = 1
        enemies = {"continuity_target": enemy}
        player = _player(
            current_combat_target="continuity_target",
            constitution_level=99,
            combat_lifepoints=80,
            combat_auto_flee=False,
            prayer_level=99,
            combat_prayer_points=1,
            combat_prayer_drain_counter=31.0,
            combat_selected_prayers=["redemption"],
            combat_prayer_uptime="100",
            combat_encounter={
                "target_id": "continuity_target",
                "enemy_lifepoints": 100_000,
                "player_attack_ticks_remaining": 99,
                "enemy_attack_ticks_remaining": 1,
            },
        )

        def run(chunks):
            current = copy.deepcopy(player)
            rng = random.Random(101)
            for ticks in chunks:
                current, ok, _info = apply_combat_burst_pure(
                    current,
                    enemies,
                    EQUIPMENT_DATA,
                    ticks=ticks,
                    rng=rng.random,
                    live_cadence=True,
                )
                self.assertTrue(ok)
            current.pop("combat_last_result", None)
            return current, rng.getstate()

        sliced = run([1, 1])
        whole = run([2])
        self.assertEqual(sliced, whole)
        self.assertEqual(sliced[0]["combat_prayer_points"], 0)
        self.assertEqual(sliced[0]["combat_selected_prayers"], [])

    def test_live_combat_ages_charge_by_elapsed_ticks_only(self):
        player = _player(
            current_combat_target="continuity_target",
            constitution_level=99,
            combat_lifepoints=990,
            magic_charge_active=True,
            magic_charge_ticks_remaining=100,
        )
        result, ok, info = apply_combat_burst_pure(
            player,
            self.ENEMIES,
            EQUIPMENT_DATA,
            ticks=6,
            rng=lambda: 0.999,
            live_cadence=True,
        )
        self.assertTrue(ok)
        self.assertEqual(info["ticks_elapsed"], 6)
        self.assertEqual(result["magic_charge_ticks_remaining"], 94)

    def test_flat_magic_defence_drain_persists_across_review_slices(self):
        player = _player(
            current_combat_target="continuity_target",
            combat_attack_style="magic_standard",
            current_combat_spell="storm_of_armadyl",
            equipment={"weapon": "Staff"},
            combat_supply_loadout={"runes": {"Armadyl rune": 100}},
            quests={"ritual_of_the_mahjarrat": {"completed": True}},
            constitution_level=99,
            combat_lifepoints=990,
        )

        def run(chunks):
            current = copy.deepcopy(player)
            rng = random.Random(88)
            calls = 0

            def draw():
                nonlocal calls
                calls += 1
                return rng.random()

            for ticks in chunks:
                current, ok, _info = apply_combat_burst_pure(
                    current,
                    self.ENEMIES,
                    EQUIPMENT_DATA,
                    ticks=ticks,
                    rng=draw,
                    live_cadence=True,
                )
                self.assertTrue(ok)
            current.pop("combat_last_result", None)
            return current, rng.getstate(), calls

        sliced = run([LIVE_COMBAT_TICKS_PER_REVIEW] * 6)
        whole = run([36])
        self.assertEqual(sliced, whole)
        encounter = sliced[0]["combat_encounter"]
        self.assertEqual(encounter["magic_effects_applied"], ("defence_flat",))
        self.assertEqual(encounter["spell_enemy_defence_factor"], 0.99)

    def test_again_disengaged_encounter_resumes_with_identical_combat_phase(self):
        phase = {
            "target_id": "continuity_target",
            "enemy_lifepoints": 100_000,
            "player_attack_ticks_remaining": 3,
            "enemy_attack_ticks_remaining": 2,
            "curse_attack_count": 4,
        }

        def run(disengaged):
            encounter = copy.deepcopy(phase)
            if disengaged:
                encounter["disengaged"] = True
            player = _player(
                current_combat_target="continuity_target",
                constitution_level=99,
                combat_lifepoints=990,
                combat_encounter=encounter,
            )
            rng = random.Random(20260717)
            result, ok, _info = apply_combat_burst_pure(
                player,
                self.ENEMIES,
                EQUIPMENT_DATA,
                ticks=LIVE_COMBAT_TICKS_PER_REVIEW,
                rng=rng.random,
                live_cadence=True,
            )
            self.assertTrue(ok)
            result.pop("combat_last_result", None)
            return result, rng.getstate()

        resumed, resumed_rng = run(True)
        uninterrupted, uninterrupted_rng = run(False)
        self.assertEqual(resumed, uninterrupted)
        self.assertEqual(resumed_rng, uninterrupted_rng)
        self.assertNotIn("disengaged", resumed["combat_encounter"])

    def test_live_kill_is_terminal_and_never_chains_a_second_spawn(self):
        enemies = {
            "one_hit": {
                "display_name": "One hit",
                "level": 1,
                "group": "Test",
                "stats": {
                    "attack": 1,
                    "strength": 1,
                    "defence": 1,
                    "hitpoints": 1,
                },
                "bonuses": {},
                "attack_speed": 4,
                "drops": {"guaranteed": (("Bones", 1),), "tables": ()},
                "source": "test",
            }
        }
        player = _player(
            current_combat_target="one_hit",
            magic_charge_active=True,
            magic_charge_ticks_remaining=100,
        )
        result, ok, info = apply_combat_burst_pure(
            player,
            enemies,
            EQUIPMENT_DATA,
            ticks=36,
            rng=lambda: 0.0,
            live_cadence=True,
        )
        self.assertTrue(ok)
        self.assertEqual(info["kills"], 1)
        self.assertEqual(info["ticks_elapsed"], 1)
        self.assertEqual(result["inventory"]["Bones"], 1)
        self.assertEqual(result["combat_encounter"], {})
        self.assertEqual(result["magic_charge_ticks_remaining"], 99)

    def test_reflected_live_kill_is_terminal_and_never_chains_a_second_spawn(self):
        enemies = {
            "reflection_target": {
                "display_name": "Reflection target",
                "level": 99,
                "group": "Test",
                "stats": {
                    "attack": 99,
                    "strength": 99,
                    "defence": 99,
                    "hitpoints": 100,
                },
                "bonuses": {},
                "attack_speed": 1,
                "drops": {"guaranteed": (("Bones", 1),), "tables": ()},
                "source": "test",
            }
        }
        player = _player(
            current_combat_target="reflection_target",
            combat_attack_style="magic_standard",
            equipment={"weapon": "Staff of air"},
            combat_supply_loadout={"runes": {"Mind rune": 1}},
            combat_lifepoints=990,
            combat_auto_flee=False,
            combat_encounter={
                "target_id": "reflection_target",
                "enemy_lifepoints": 1,
                "player_attack_ticks_remaining": 99,
                "enemy_attack_ticks_remaining": 0,
                "vengeance_pending": True,
            },
        )
        draws = iter((0.0, 0.99, 0.0, 0.0))
        result, ok, info = apply_combat_burst_pure(
            player,
            enemies,
            EQUIPMENT_DATA,
            ticks=36,
            rng=lambda: next(draws, 0.0),
            live_cadence=True,
        )
        self.assertTrue(ok)
        self.assertEqual(info["kills"], 1)
        self.assertEqual(info["ticks_elapsed"], 1)
        self.assertEqual(result["inventory"]["Bones"], 1)
        self.assertEqual(result["combat_encounter"], {})

    def test_redemption_consumption_survives_an_early_reflected_kill(self):
        enemies = {
            "reflection_target": {
                "display_name": "Reflection target",
                "level": 99,
                "group": "Test",
                "stats": {
                    "attack": 99,
                    "strength": 99,
                    "defence": 99,
                    "hitpoints": 100,
                },
                "bonuses": {},
                "attack_speed": 1,
                "drops": {"guaranteed": (), "tables": ()},
                "source": "test",
            }
        }
        player = _player(
            current_combat_target="reflection_target",
            combat_attack_style="magic_standard",
            equipment={"weapon": "Staff of air"},
            combat_supply_loadout={"runes": {"Mind rune": 1}},
            constitution_level=99,
            combat_lifepoints=50,
            combat_auto_flee=False,
            prayer_level=99,
            combat_prayer_points=99,
            combat_selected_prayers=["redemption"],
            combat_prayer_uptime="100",
            combat_encounter={
                "target_id": "reflection_target",
                "enemy_lifepoints": 1,
                "player_attack_ticks_remaining": 99,
                "enemy_attack_ticks_remaining": 0,
                "vengeance_pending": True,
            },
        )
        draws = iter((0.0, 0.1, 0.0, 0.0))

        result, ok, info = apply_combat_burst_pure(
            player,
            enemies,
            EQUIPMENT_DATA,
            ticks=36,
            rng=lambda: next(draws, 0.0),
            live_cadence=True,
        )

        self.assertTrue(ok)
        self.assertTrue(info["killed"])
        self.assertEqual(info["ticks_elapsed"], 1)
        self.assertEqual(result["combat_prayer_points"], 0)
        self.assertEqual(result["combat_selected_prayers"], [])


class TestQuestCombatCadenceBoundary(unittest.TestCase):
    def test_live_quest_combat_uses_collapsed_stage_while_flag_off_keeps_legacy_ticks(self):
        observed_ticks = []

        def fake_combat(player_data, *_args, **kwargs):
            observed_ticks.append(
                (kwargs["ticks"], kwargs["stop_after_first_kill"])
            )
            return copy.deepcopy(player_data), True, {
                "encounter_id": "proof",
                "xp_rewards": {},
                "display_name": "Proof encounter",
                "reason": "quest_combat_resolved",
            }

        base_player = {
            "current_quest": "rune_mysteries",
            "inventory": {},
            "quests": {
                "rune_mysteries": {
                    "started": True,
                    "progress": 0,
                    "completed": False,
                }
            },
            "completed_achievements": [],
        }
        with (
            patch.object(
                runtime_actions_production,
                "quest_current_stage_resolvable_combat_blockers_pure",
                return_value=[{"encounter_id": "proof"}],
            ),
            patch.object(
                runtime_actions_production,
                "apply_quest_combat_encounter_pure",
                side_effect=fake_combat,
            ),
        ):
            legacy_ctx = _context(copy.deepcopy(base_player))
            legacy_ctx.cadence_live_enabled = False
            self.assertTrue(handle_quest_answer(legacy_ctx))

            live_ctx = _context(copy.deepcopy(base_player))
            live_ctx.cadence_live_enabled = True
            self.assertTrue(handle_quest_answer(live_ctx))

        self.assertEqual(observed_ticks, [(50, False), (None, True)])

    def test_live_collapsed_quest_combat_rewards_only_one_required_kill(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["quests"]["toktz_ket_dill"] = {
            "started": True,
            "progress": 6,
            "completed": False,
        }
        player["quest_combat_config"] = {"resolver_enabled": True}
        player["attack_level"] = 99
        player["strength_level"] = 99
        player["defense_level"] = 99
        player["constitution_level"] = 99
        rolls = iter((0.0, 0.999) * 500)

        resolved, ok, result = apply_quest_combat_encounter_pure(
            player,
            "toktz_ket_dill",
            QUEST_DATA,
            rng=lambda: next(rolls, 0.999),
            equipment_data=EQUIPMENT_DATA,
            stop_after_first_kill=True,
        )

        encounter_id = "toktz_ket_dill_lava_monster_47"
        self.assertTrue(ok)
        self.assertEqual(result["kills"], 1)
        self.assertEqual(result["completed_quantity"], 1)
        self.assertEqual(result["remaining_quantity"], 1)
        self.assertEqual(
            resolved["quest_combat_encounter_counts"]["toktz_ket_dill"][
                encounter_id
            ],
            1,
        )


class TestAnsweredCardResidualEffects(unittest.TestCase):
    def test_bunyip_and_special_points_use_exact_six_tick_residuals(self):
        player = {
            "summoning_level": 99,
            "constitution_level": 99,
            "combat_lifepoints": 500,
            "summoning_state": {
                "special_move_points_current": 0,
                "active_follower": {
                    "kind": "familiar",
                    "entity_id": "bunyip",
                    "remaining_reviews": 20,
                    "max_reviews": 20,
                },
            },
        }
        healed = []
        for _ in range(9):
            player, info = advance_summoning_world_tick_pure(
                player, successful_answer=False
            )
            healed.append(info["passive_healing"])
        state = player["summoning_state"]
        self.assertEqual(healed, [0, 0, 0, 0, 20, 0, 0, 0, 20])
        self.assertEqual(state["active_follower"]["bunyip_heal_residual"], 4)
        self.assertEqual(state["special_move_points_current"], 15)
        self.assertEqual(state["special_move_recharge_residual"], 4)


if __name__ == "__main__":
    unittest.main()


class SingleTickExemptionSetTest(unittest.TestCase):
    def test_every_never_multiplied_utility_contract_is_in_the_one_tick_set(self):
        """The runtime's exemption set must cover every declaration.

        Bork and Skeletal Horror both shipped foreground-multiplied because
        their contracts said "Never foreground-multiplied" while the runtime
        set silently omitted them. This cross-check makes the drift a failure
        instead of a live cadence bug.
        """
        from ankiscape.logic.cadence_coverage import SINGLE_TICK_UTILITY_IDS

        missing = [
            row["action_id"]
            for row in cadence_coverage_rows_pure()
            if row.get("handler_key") == "utility"
            and "ever foreground-multiplied" in str(row.get("multiplier_behavior", ""))
            and "Never" in str(row.get("multiplier_behavior", ""))
            and row["action_id"] not in SINGLE_TICK_UTILITY_IDS
        ]
        self.assertEqual(
            missing,
            [],
            "utility contracts declared never-multiplied but absent from "
            f"SINGLE_TICK_UTILITY_IDS: {missing}",
        )
