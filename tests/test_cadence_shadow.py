import json
import random
import subprocess
import sys
import tempfile
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
from runtime_actions import RuntimeActionContext, _record_action
from storage_pure import migrate_loaded_data
from constants import COOKING_DATA, FIREMAKING_DATA, FISHING_DATA, HUNTER_DATA, ORE_DATA, TREE_DATA
from tools.cadence_shadow_report import catalog_rows, render_text


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



if __name__ == "__main__":
    unittest.main()
