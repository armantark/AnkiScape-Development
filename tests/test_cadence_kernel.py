import copy
import json
import pickle
import sys
import types
import unittest
from collections import Counter

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic.cadence_kernel import (
    CAP_ONE_ACTION,
    COMBAT_TICKS,
    EMBEDDED_PROBABILITY,
    PASSTHROUGH,
    RATE_LIMITED,
    R,
    ActorLock,
    CadenceProfile,
    ResourceLock,
    advance_cadence_pure,
    default_cadence_profile_state_pure,
    rate_limited_profile_pure,
    sanitize_cadence_kernel_state_pure,
    validate_overflow_policy_pure,
)
from ankiscape.core.constants import ORE_DATA
from ankiscape.core.storage_pure import CURRENT_CONFIG_VERSION, migrate_loaded_data
from tests.test_integration_smoke import (
    _DummyCol,
    _DummyMW,
    _FakeReviewer,
    _install_runtime_fakes,
    _load_addon_as_package,
)


class TestCadenceKernelPure(unittest.TestCase):
    def test_public_contract_declares_r_modes_and_lock_shapes(self):
        self.assertEqual(R, 1000)
        self.assertEqual(ResourceLock("gem_stall").resource_id, "gem_stall")
        self.assertEqual(ActorLock("fight_1").actor_id, "fight_1")

        passthrough = CadenceProfile("crafting", PASSTHROUGH)
        state = default_cadence_profile_state_pure(opening_ready=False)
        result = advance_cadence_pure(passthrough, state)
        self.assertTrue(result.emitted)
        self.assertEqual(result.state["assigned_reviews"], 1)
        self.assertEqual(result.state["opportunities_emitted"], 1)

    def test_gem_stall_emits_exactly_81_opportunities_in_4000_reviews(self):
        profile = CadenceProfile("gem_stall", RATE_LIMITED, 81, 4000)
        state = default_cadence_profile_state_pure(opening_ready=False)
        emitted_at = []
        for review_number in range(1, 4001):
            result = advance_cadence_pure(profile, state)
            state = result.state
            if result.emitted:
                emitted_at.append(review_number)

        intervals = [current - previous for previous, current in zip([0] + emitted_at, emitted_at)]
        self.assertEqual(len(emitted_at), 81)
        self.assertEqual(Counter(intervals), Counter({49: 50, 50: 31}))
        self.assertEqual(state["credit"], 0)
        self.assertEqual(state["assigned_reviews"], 4000)
        self.assertEqual(state["opportunities_emitted"], 81)

    def test_switching_away_freezes_credit_and_switching_back_resumes_exactly(self):
        active = CadenceProfile("active", RATE_LIMITED, 3, 10)
        other = CadenceProfile("other", RATE_LIMITED, 7, 13)
        active_state = default_cadence_profile_state_pure(opening_ready=False)
        other_state = default_cadence_profile_state_pure(opening_ready=False)

        for _ in range(4):
            active_state = advance_cadence_pure(active, active_state).state
        frozen = copy.deepcopy(active_state)
        for _ in range(10_000):
            other_state = advance_cadence_pure(other, other_state).state

        self.assertEqual(active_state, frozen)
        resumed = advance_cadence_pure(active, active_state).state

        uninterrupted = default_cadence_profile_state_pure(opening_ready=False)
        for _ in range(5):
            uninterrupted = advance_cadence_pure(active, uninterrupted).state
        self.assertEqual(resumed, uninterrupted)

    def test_opening_ready_emits_immediately_once_and_never_regenerates(self):
        profile = CadenceProfile("stall", RATE_LIMITED, 1, 5)
        state = default_cadence_profile_state_pure(opening_ready=True)
        emitted_at = []
        for review_number in range(1, 21):
            result = advance_cadence_pure(profile, state)
            state = result.state
            if result.emitted:
                emitted_at.append(review_number)

        self.assertEqual(emitted_at, [1, 6, 11, 16])
        self.assertFalse(state["opening_ready"])

    def test_round_robin_routes_produce_weighted_average_not_sum(self):
        slow = CadenceProfile("slow", RATE_LIMITED, 1, 4)
        fast = CadenceProfile("fast", RATE_LIMITED, 3, 4)
        states = {
            "slow": default_cadence_profile_state_pure(opening_ready=False),
            "fast": default_cadence_profile_state_pure(opening_ready=False),
        }
        emitted = 0
        for review_number in range(8000):
            profile = slow if review_number % 2 == 0 else fast
            result = advance_cadence_pure(profile, states[profile.profile_id])
            states[profile.profile_id] = result.state
            emitted += int(result.emitted)

        self.assertEqual(emitted, 4000)
        self.assertEqual(states["slow"]["opportunities_emitted"], 1000)
        self.assertEqual(states["fast"]["opportunities_emitted"], 3000)
        self.assertNotEqual(emitted, 8000)

    def test_overflow_requires_cap_one_action_declaration(self):
        with self.assertRaises(ValueError):
            rate_limited_profile_pure("zero", 0)
        with self.assertRaises(ValueError):
            validate_overflow_policy_pure(1001)
        with self.assertRaises(ValueError):
            rate_limited_profile_pure("overflow", 1001)

        capped = rate_limited_profile_pure(
            "overflow",
            1001,
            overflow_policy=CAP_ONE_ACTION,
        )
        self.assertEqual(
            (capped.increment_numerator, capped.threshold_denominator),
            (1, 1),
        )

    def test_non_rate_modes_emit_one_live_opportunity_per_review(self):
        state = default_cadence_profile_state_pure(opening_ready=False)
        with self.assertRaises(ValueError):
            advance_cadence_pure(
                CadenceProfile("embedded", EMBEDDED_PROBABILITY, 3, 7),
                state,
            )
        for mode in (EMBEDDED_PROBABILITY, COMBAT_TICKS):
            with self.subTest(mode=mode):
                result = advance_cadence_pure(CadenceProfile(mode, mode), state)
                self.assertTrue(result.emitted)
                self.assertEqual(result.state["assigned_reviews"], 1)
                self.assertEqual(result.state["opportunities_emitted"], 1)

    def test_save_load_round_trip_preserves_exact_residual_and_never_float(self):
        residual = {
            "credit": 3973,
            "opening_ready": False,
            "assigned_reviews": 49,
            "opportunities_emitted": 0,
            "cadence_version": 1,
        }
        loaded = migrate_loaded_data(
            {
                "config_version": 33,
                "inventory": {},
                "cadence_profiles": {"gem_stall": residual},
            },
            ORE_DATA,
        )
        reloaded = migrate_loaded_data(json.loads(json.dumps(loaded)), ORE_DATA)

        self.assertEqual(loaded["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(reloaded["cadence_profiles"]["gem_stall"], residual)
        self._assert_no_float(reloaded["cadence_profiles"])

        sanitized = sanitize_cadence_kernel_state_pure(
            {
                "bad": {
                    "credit": 1.5,
                    "opening_ready": False,
                    "assigned_reviews": 2.5,
                    "opportunities_emitted": 3.5,
                    "cadence_version": 1.5,
                }
            }
        )
        self._assert_no_float(sanitized)

    def _assert_no_float(self, value):
        self.assertNotIsInstance(value, float)
        if isinstance(value, dict):
            for nested in value.values():
                self._assert_no_float(nested)
        elif isinstance(value, (list, tuple)):
            for nested in value:
                self._assert_no_float(nested)


class TestCadenceKernelIntegration(unittest.TestCase):
    def setUp(self):
        self._original_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._original_modules)

    def test_config_flag_defaults_on_and_accepts_only_explicit_boolean_false(self):
        addon = _load_addon_as_package("ankiscape_cadence_config")
        addon.mw = _DummyMW(_DummyCol())
        self.assertTrue(addon._cadence_kernel_enabled())

        addon.mw = _DummyMW(_DummyCol({"ankiscape_cadence_kernel": True}))
        self.assertTrue(addon._cadence_kernel_enabled())

        addon.mw = _DummyMW(_DummyCol({"ankiscape_cadence_kernel": False}))
        self.assertFalse(addon._cadence_kernel_enabled())

        addon.mw = _DummyMW(_DummyCol({"ankiscape_cadence_kernel": "true"}))
        self.assertTrue(addon._cadence_kernel_enabled())

    def test_review_undo_restores_exact_cadence_residual(self):
        addon = _load_addon_as_package("ankiscape_cadence_undo")
        initial = {
            "credit": 3973,
            "opening_ready": False,
            "assigned_reviews": 49,
            "opportunities_emitted": 0,
            "cadence_version": 1,
        }
        addon._state.player_data = {"cadence_profiles": {"gem_stall": copy.deepcopy(initial)}}
        addon._state.current_skill = "None"
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None

        before = addon._capture_player_data_snapshot()
        addon._state.player_data["cadence_profiles"]["gem_stall"] = {
            **initial,
            "credit": 54,
            "assigned_reviews": 50,
            "opportunities_emitted": 1,
        }
        addon._remember_review_award_snapshot(before)
        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon._state.player_data["cadence_profiles"]["gem_stall"], initial)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_again_disengages_without_advancing_persisted_combat_phase(self):
        addon = _load_addon_as_package("ankiscape_cadence_again")
        addon.mw = _DummyMW(
            _DummyCol({"ankiscape_cadence_kernel": True})
        )
        phase = {
            "target_id": "chicken",
            "enemy_lifepoints": 17,
            "player_attack_ticks_remaining": 3,
            "enemy_attack_ticks_remaining": 2,
            "curse_attack_count": 4,
        }
        addon._state.player_data = {
            "inventory": {},
            "current_combat_target": "chicken",
            "combat_encounter": copy.deepcopy(phase),
            "completed_achievements": [],
        }
        addon._state.current_skill = "Combat"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None

        addon.on_answer_card(
            _FakeReviewer(),
            1,
            lambda _self, _ease: "answered",
        )

        self.assertEqual(
            addon._state.player_data["combat_encounter"],
            {**phase, "disengaged": True},
        )

    def test_successful_live_combat_answer_does_not_fake_disengagement(self):
        addon = _load_addon_as_package("ankiscape_cadence_combat_success")
        runtime = sys.modules["ankiscape_cadence_combat_success.runtime.runtime_actions"]
        phase = {
            "target_id": "chicken",
            "enemy_lifepoints": 17,
            "player_attack_ticks_remaining": 3,
            "enemy_attack_ticks_remaining": 2,
        }
        seen = []

        def handler(ctx):
            seen.append(copy.deepcopy(ctx.player_data["combat_encounter"]))
            return True

        runtime.ANSWER_HANDLERS["combat"] = handler
        runtime.CAN_START_HANDLERS["combat"] = lambda _ctx: True
        addon.mw = _DummyMW(
            _DummyCol({"ankiscape_cadence_kernel": True})
        )
        addon._state.player_data = {
            "inventory": {},
            "current_combat_target": "chicken",
            "combat_encounter": copy.deepcopy(phase),
            "completed_achievements": [],
        }
        addon._state.current_skill = "Combat"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.level_up_check = lambda *_args: None
        addon.check_achievements = lambda *_args: None

        addon.on_answer_card(
            _FakeReviewer(),
            4,
            lambda _self, _ease: "answered",
        )

        self.assertEqual(seen, [phase])

    def test_a_mid_fight_style_change_reaches_the_next_live_review(self):
        """Owner ruling (Pass 14): a change applies from the next review.

        The style is changed with the bear alive, and the very next live review
        swings with it: Attack is trained, Strength is not, and the bear is the
        same one.
        """
        addon = _load_addon_as_package("ankiscape_cadence_live_style_change")
        addon.mw = _DummyMW(_DummyCol({"ankiscape_cadence_kernel": True}))
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._refresh_open_carried_inventory = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._show_exp = lambda _value: None
        addon._show_activity_gain = lambda _value: None
        addon._state.player_data = {
            "inventory": {},
            "equipment": {"weapon": "Rune scimitar"},
            "attack_level": 40,
            "strength_level": 40,
            "defense_level": 21,
            "constitution_level": 28,
            "combat_lifepoints": 280,
            "attack_exp": 0.0,
            "strength_exp": 0.0,
            "current_combat_target": "black_bear",
            "combat_action": "attack",
            "combat_attack_style": "aggressive",
            "combat_attack_style_type": "slash",
            "combat_encounter": {
                "target_id": "black_bear",
                "enemy_lifepoints": 230,
                "player_attack_ticks_remaining": 0,
                "enemy_attack_ticks_remaining": 99,
            },
            "completed_achievements": [],
        }
        addon._state.current_skill = "Combat"

        self.assertTrue(addon._set_combat_attack_style(("accurate", "slash")))

        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        original_random = addon.random.random
        addon.random.random = lambda: 0.5  # every roll lands for half the maximum
        try:
            addon.on_answer_card(
                _FakeReviewer(), 4, lambda _self, _ease: "answered"
            )
        finally:
            addon.random.random = original_random

        player_data = addon._state.player_data
        self.assertGreater(player_data["attack_exp"], 0.0)
        self.assertEqual(player_data["strength_exp"], 0.0)
        self.assertEqual(
            player_data["combat_encounter"]["target_id"], "black_bear"
        )

    def test_flag_off_preserves_exact_outputs_and_rng_consumption(self):
        baseline_output, baseline_rng = self._run_legacy_review(
            "ankiscape_cadence_off_baseline",
            {"ankiscape_cadence_kernel": False},
        )
        off_output, off_rng = self._run_legacy_review(
            "ankiscape_cadence_off",
            {
                "ankiscape_cadence_kernel": False,
                "unrelated_addon_setting": "unchanged",
            },
        )

        self.assertEqual(off_output, baseline_output)
        self.assertEqual(off_rng, baseline_rng)

    def test_quest_multiplier_is_legacy_only_when_live_cadence_is_disabled(self):
        def run(module_name, enabled):
            addon = _load_addon_as_package(module_name)
            runtime = sys.modules[f"{module_name}.runtime.runtime_actions"]
            calls = []

            def handler(_ctx):
                calls.append("quest")
                return True

            runtime.ANSWER_HANDLERS["quest"] = handler
            runtime.CAN_START_HANDLERS["quest"] = lambda _ctx: True
            addon.mw = _DummyMW(
                _DummyCol(
                    {
                        "ankiscape_cadence_kernel": enabled,
                        "ankiscape_review_action_multiplier": 3,
                    }
                )
            )
            addon._state.player_data = {"inventory": {}, "completed_achievements": []}
            addon._state.current_skill = "Quests"
            addon._state.exp_awarded = False
            addon.update_review_hud = lambda *_args: None
            addon._refresh_skill_availability = lambda: None
            addon.on_good_answer({})
            return calls

        self.assertEqual(
            run("ankiscape_cadence_quest_legacy", False),
            ["quest", "quest", "quest"],
        )
        self.assertEqual(
            run("ankiscape_cadence_quest_live", True),
            ["quest"],
        )

    def _run_legacy_review(self, module_name, config):
        addon = _load_addon_as_package(module_name)
        runtime = sys.modules[f"{module_name}.runtime.runtime_actions"]
        runtime.advance_live_cadence_route_pure = lambda *_args, **_kwargs: self.fail(
            "explicit flag-off review dispatch must bypass the live cadence kernel"
        )
        calls = {"xp": [], "gains": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._show_exp = lambda value: calls["xp"].append(value)
        addon._show_activity_gain = lambda value: calls["gains"].append(value)
        addon.mw = _DummyMW(_DummyCol(config))
        addon._state.player_data = {
            "inventory": {},
            "woodcutting_level": 1,
            "woodcutting_exp": 0,
            "current_tree": "tree",
            "toolbelt": {"woodcutting": ["bronze_hatchet"]},
            "completed_achievements": [],
        }
        addon._state.current_skill = "Woodcutting"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.random.seed(20260713)

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        output_bytes = pickle.dumps(
            {"player_data": addon._state.player_data, "calls": calls},
            protocol=5,
        )
        return output_bytes, addon.random.getstate()


if __name__ == "__main__":
    unittest.main()
