import copy
import json
import pickle
import random
import subprocess
import sys
import tempfile
import types
import unittest
from fractions import Fraction
from pathlib import Path

from cadence_shadow import (
    RANGE_SPLIT,
    SHADOW_STATE_KEY,
    SOURCE_BLOCKED,
    cadence_shadow_report_rows_pure,
    record_cadence_shadow_pure,
    resolve_cadence_shadow_rate_pure,
    sanitize_cadence_shadow_state_pure,
)
from cadence_kernel import default_cadence_profile_state_pure
from runtime_actions import RuntimeActionContext, _record_action
from storage_pure import migrate_loaded_data
from constants import COOKING_DATA, FIREMAKING_DATA, FISHING_DATA, HUNTER_DATA, ORE_DATA, TREE_DATA
from tools.cadence_shadow_report import catalog_rows, render_text
from tests.test_integration_smoke import (
    _DummyCol,
    _DummyMW,
    _FakeReviewer,
    _install_runtime_fakes,
    _load_addon_as_package,
)


class CadenceShadowPureTest(unittest.TestCase):
    def test_rate_resolution_preserves_ranges_and_blocks_missing_sources(self):
        maple = resolve_cadence_shadow_rate_pure("woodcutting", "maple")
        self.assertEqual(maple["low_actions_per_hour"], [300, 1])
        self.assertEqual(maple["high_actions_per_hour"], [300, 1])

        magic = resolve_cadence_shadow_rate_pure("woodcutting", "magic")
        self.assertEqual(magic["low_actions_per_hour"], [170, 3])
        self.assertEqual(magic["high_actions_per_hour"], [100, 1])

        runite = resolve_cadence_shadow_rate_pure("mining", "runite")
        self.assertEqual(runite["source_status"], SOURCE_BLOCKED)
        self.assertNotIn("low_actions_per_hour", runite)

        rocktail = resolve_cadence_shadow_rate_pure("fishing", "catch_rocktail")
        self.assertEqual(rocktail["source_status"], SOURCE_BLOCKED)
        self.assertEqual(rocktail["source_low_xp_hour"], [48_000, 1])

        for skill_id, action_id in (
            ("cooking", "cook_lobster"),
            ("cooking", "cook_monkfish"),
            ("cooking", "cook_shark"),
            ("cooking", "cook_tuna"),
            ("firemaking", "magic_logs"),
        ):
            embedded = resolve_cadence_shadow_rate_pure(skill_id, action_id)
            self.assertEqual(embedded["low_overflow_policy"], "cap_one_action")
            self.assertEqual(embedded["high_overflow_policy"], "cap_one_action")

    def test_shadow_state_round_trips_without_floats(self):
        player_data = {}
        for review in range(31):
            record_cadence_shadow_pure(
                player_data,
                "woodcutting",
                "magic",
                review % 3 == 0,
                live_xp=250 if review % 3 == 0 else 0,
            )
        reloaded = sanitize_cadence_shadow_state_pure(
            json.loads(json.dumps(player_data[SHADOW_STATE_KEY]))
        )
        self.assertEqual(reloaded, player_data[SHADOW_STATE_KEY])
        self._assert_no_float(reloaded)

    def test_shadow_tracks_live_and_proposed_results_separately(self):
        player_data = {}
        for review in range(10):
            record_cadence_shadow_pure(
                player_data,
                "woodcutting",
                "maple",
                review % 2 == 0,
                live_xp=100 if review % 2 == 0 else 0,
            )
        row = cadence_shadow_report_rows_pure(player_data)[0]
        self.assertEqual(row["assigned_reviews"], 10)
        self.assertEqual(row["live_successes"], 5)
        self.assertEqual(row["live_failures"], 5)
        self.assertEqual(row["current_xp_hour"], [50_000, 1])
        self.assertEqual(row["proposed_low_xp_hour"], [30_000, 1])
        self.assertEqual(row["proposed_high_xp_hour"], [30_000, 1])
        self.assertEqual(row["range_splits"], 0)

        ranged = {}
        for _review in range(20):
            record_cadence_shadow_pure(ranged, "woodcutting", "magic", False)
        ranged_row = cadence_shadow_report_rows_pure(ranged)[0]
        self.assertGreater(ranged_row["range_splits"], 0)
        self.assertEqual(ranged_row["last_proposed_decision"], RANGE_SPLIT)

        embedded = {}
        record_cadence_shadow_pure(
            embedded,
            "cooking",
            "cook_shark",
            True,
            live_xp=210,
            proposed_outcome_success=True,
        )
        self.assertNotIn("cooking:cook_shark", embedded[SHADOW_STATE_KEY]["profiles"])

    def test_six_adapter_skills_use_one_flagged_shadow_sink(self):
        routes = (
            ("mining", "iron", 35),
            ("woodcutting", "magic", 250),
            ("fishing", "catch_sharks", 110),
            ("hunter", "catch_red_chinchompa", 265),
            ("cooking", "cook_shark", 210),
            ("firemaking", "magic_logs", 303.8),
        )
        enabled_data = {}
        enabled = self._context(enabled_data, True)
        for skill_id, action_id, xp in routes:
            with self.subTest(skill_id=skill_id):
                _record_action(enabled, skill_id, action_id, True, primary_xp=xp)
                self.assertIn(f"{skill_id}:{action_id}", enabled_data[SHADOW_STATE_KEY]["routes"])

        disabled_data = {}
        disabled = self._context(disabled_data, False)
        _record_action(disabled, "mining", "iron", True, primary_xp=35)
        self.assertNotIn(SHADOW_STATE_KEY, disabled_data)
        self.assertIn("action_telemetry", disabled_data)

    def test_report_renders_all_six_skills_and_blocked_findings(self):
        rows = catalog_rows()
        expected_routes = {
            *(f"mining:{route}" for route in ORE_DATA),
            *(f"woodcutting:{route}" for route in TREE_DATA),
            *(f"fishing:{route}" for route in FISHING_DATA),
            *(f"hunter:{route}" for route in HUNTER_DATA),
            *(f"cooking:{route}" for route in COOKING_DATA),
            *(f"firemaking:{route}" for route in FIREMAKING_DATA),
        }
        self.assertEqual(
            {f"{row['skill_id']}:{row['action_id']}" for row in rows},
            expected_routes,
        )
        self.assertEqual(
            {row["skill_id"] for row in rows},
            {"mining", "woodcutting", "fishing", "hunter", "cooking", "firemaking"},
        )
        text = render_text(rows)
        self.assertIn("catch_rocktail", text)
        self.assertIn("source_blocked", text)
        self.assertIn("cook_shark", text)
        self.assertIn("263,000", text)
        by_route = {f"{row['skill_id']}:{row['action_id']}": row for row in rows}
        for route_id in ("mining:sandstone", "mining:granite"):
            current = by_route[route_id]["current_xp_hour"]
            self.assertGreater(Fraction(current[0], current[1]), 0)

    def test_report_cli_reads_accumulated_shadow_json(self):
        player_data = {}
        for review in range(10):
            record_cadence_shadow_pure(
                player_data,
                "woodcutting",
                "maple",
                review % 2 == 0,
                live_xp=100 if review % 2 == 0 else 0,
            )
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "player.json"
            input_path.write_text(json.dumps(player_data), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve().parent.parent / "tools" / "cadence_shadow_report.py"),
                    "--input",
                    str(input_path),
                    "--format",
                    "json",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        rows = json.loads(completed.stdout)
        self.assertEqual([row["profile_id"] for row in rows], ["woodcutting:maple"])
        self.assertEqual(rows[0]["current_xp_hour"], [50_000, 1])
        self.assertEqual(rows[0]["proposed_low_xp_hour"], [30_000, 1])

    def test_load_sanitizes_shadow_only_when_it_exists(self):
        absent = migrate_loaded_data({"config_version": 34, "inventory": {}}, ORE_DATA)
        self.assertNotIn(SHADOW_STATE_KEY, absent)

        present = migrate_loaded_data(
            {
                "config_version": 34,
                "inventory": {},
                SHADOW_STATE_KEY: {
                    "profiles": {"woodcutting:maple": {"low": {"credit": 1.5}, "high": {}}},
                    "routes": {},
                },
            },
            ORE_DATA,
        )
        self.assertEqual(present[SHADOW_STATE_KEY]["profiles"]["woodcutting:maple"]["low"]["credit"], 0)

    def _context(self, player_data, enabled):
        noop = lambda *_args, **_kwargs: None
        return RuntimeActionContext(
            player_data=player_data,
            random_random=lambda: 0.0,
            show_error_message=noop,
            deactivate_current_skill=noop,
            award_skill_exp=lambda _key, amount: amount,
            award_hidden_skill_exp=noop,
            level_up_check=noop,
            check_achievements=noop,
            save_player_data=noop,
            refresh_skill_availability=noop,
            refresh_skill_availability_partial=noop,
            can_smith_any=lambda: False,
            show_exp=noop,
            show_activity_gain=noop,
            implemented_exp_keys_snapshot=lambda: {},
            show_quest_exp_delta=noop,
            cadence_shadow_enabled=enabled,
        )

    def _assert_no_float(self, value):
        self.assertNotIsInstance(value, float)
        if isinstance(value, dict):
            for nested in value.values():
                self._assert_no_float(nested)
        elif isinstance(value, (list, tuple)):
            for nested in value:
                self._assert_no_float(nested)


class CadenceShadowIntegrationTest(unittest.TestCase):
    def setUp(self):
        self._original_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._original_modules)

    def test_flag_on_off_preserve_each_review_gameplay_bytes_rng_xp_and_loot(self):
        for index, (skill, route, fixture) in enumerate(self._route_fixtures()):
            with self.subTest(skill=skill, route=route):
                off_sequence, off_rng, off_data = self._run_reviews(
                    f"ankiscape_shadow_{index}_off",
                    {"ankiscape_cadence_kernel": False},
                    skill,
                    fixture,
                )
                on_sequence, on_rng, on_data = self._run_reviews(
                    f"ankiscape_shadow_{index}_on",
                    {"ankiscape_cadence_kernel": True},
                    skill,
                    fixture,
                )
                self.assertEqual(on_sequence, off_sequence)
                self.assertEqual(on_rng, off_rng)
                self.assertNotIn(SHADOW_STATE_KEY, off_data)
                self.assertEqual(
                    on_data[SHADOW_STATE_KEY]["routes"][route]["assigned_reviews"],
                    16,
                )
                self.assertEqual(on_data["cadence_profiles"], off_data["cadence_profiles"])

    def test_review_undo_restores_shadow_residual_with_gameplay(self):
        addon = _load_addon_as_package("ankiscape_shadow_undo")
        initial_shadow = {}
        addon.player_data = {
            "inventory": {},
            "woodcutting_level": 99,
            "woodcutting_exp": 0,
            "current_tree": "magic",
            "toolbelt": {"woodcutting": ["rune_hatchet"]},
            "completed_achievements": [],
            "cadence_profiles": {},
        }
        addon.current_skill = "Woodcutting"
        addon.mw = _DummyMW(_DummyCol({"ankiscape_cadence_kernel": True}))
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.update_farming_hud_badge = lambda _data, _callback: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda _value: None
        addon._show_activity_gain = lambda _value: None
        before = addon._capture_player_data_snapshot()
        addon.card_turned = addon.answer_shown = True
        addon.exp_awarded = False
        addon.random.seed(7)
        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        self.assertIn(SHADOW_STATE_KEY, addon.player_data)
        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )
        self.assertEqual(addon.player_data.get(SHADOW_STATE_KEY, {}), initial_shadow)
        self.assertEqual(addon.player_data, before["player_data"])

    def test_valid_source_blocked_runite_records_live_results_without_residual(self):
        _sequence, _rng, data = self._run_reviews(
            "ankiscape_shadow_runite",
            {"ankiscape_cadence_kernel": True},
            "Mining",
            {
                "inventory": {},
                "mining_level": 99,
                "mining_exp": 0,
                "current_ore": "runite",
                "toolbelt": {"mining": ["rune_pickaxe"]},
            },
        )
        route = data[SHADOW_STATE_KEY]["routes"]["mining:runite"]
        self.assertEqual(route["source_status"], SOURCE_BLOCKED)
        self.assertEqual(route["assigned_reviews"], 16)
        self.assertEqual(route["live_successes"], 6)
        self.assertEqual(route["live_xp"], [750, 1])
        self.assertNotIn("mining:runite", data[SHADOW_STATE_KEY]["profiles"])
        self.assertEqual(data["inventory"]["Runite ore"], 6)
        self.assertEqual(data["mining_exp"], 750)
        report = cadence_shadow_report_rows_pure(data)[0]
        self.assertEqual(report["current_xp_hour"], [46_875, 1])

    def _run_reviews(self, module_name, config, skill, fixture):
        addon = _load_addon_as_package(module_name)
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
        addon.player_data = {
            "completed_achievements": [],
            "cadence_profiles": {
                "sentinel": copy.deepcopy(default_cadence_profile_state_pure(opening_ready=False))
            },
            **copy.deepcopy(fixture),
        }
        addon.current_skill = skill
        addon.random.seed(20260713)
        sequence = []
        for _ in range(16):
            addon.card_turned = addon.answer_shown = True
            addon.exp_awarded = False
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
            gameplay = {key: value for key, value in addon.player_data.items() if key != SHADOW_STATE_KEY}
            sequence.append(pickle.dumps({"player_data": gameplay, "calls": calls}, protocol=5))
        return sequence, addon.random.getstate(), addon.player_data

    def _route_fixtures(self):
        return (
            (
                "Mining",
                "mining:iron",
                {
                    "inventory": {},
                    "mining_level": 99,
                    "mining_exp": 0,
                    "current_ore": "iron",
                    "toolbelt": {"mining": ["rune_pickaxe"]},
                },
            ),
            (
                "Woodcutting",
                "woodcutting:magic",
                {
                    "inventory": {},
                    "woodcutting_level": 99,
                    "woodcutting_exp": 0,
                    "current_tree": "magic",
                    "toolbelt": {"woodcutting": ["rune_hatchet"]},
                },
            ),
            (
                "Fishing",
                "fishing:catch_sharks",
                {
                    "inventory": {},
                    "fishing_level": 99,
                    "fishing_exp": 0,
                    "strength_level": 99,
                    "agility_level": 99,
                    "current_fishing": "catch_sharks",
                },
            ),
            (
                "Hunter",
                "hunter:catch_red_chinchompa",
                {
                    "inventory": {"Box trap": 1},
                    "hunter_level": 99,
                    "hunter_exp": 0,
                    "current_hunter": "catch_red_chinchompa",
                },
            ),
            (
                "Cooking",
                "cooking:cook_shark",
                {
                    "inventory": {"Raw shark": 100},
                    "cooking_level": 99,
                    "cooking_exp": 0,
                    "current_cooking": "cook_shark",
                },
            ),
            (
                "Firemaking",
                "firemaking:magic_logs",
                {
                    "inventory": {"Magic logs": 100},
                    "firemaking_level": 99,
                    "firemaking_exp": 0,
                    "current_firemaking": "magic_logs",
                },
            ),
        )


if __name__ == "__main__":
    unittest.main()
