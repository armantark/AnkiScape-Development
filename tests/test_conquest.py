from __future__ import annotations

import copy
import os
import random
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import (
    EQUIPMENT_DATA,
    ITEM_DEFINITIONS,
    ORE_DATA,
    UTILITY_ACTIVITY_DATA,
)
from ankiscape.core.storage_pure import (
    CURRENT_CONFIG_VERSION,
    default_player_data,
    migrate_loaded_data,
)
from ankiscape.data.conquest_data import (
    CONQUEST_BOARD_SIZE,
    CONQUEST_COMMANDS,
    CONQUEST_DEFAULT_COMMANDS,
    CONQUEST_DEFAULT_SQUAD,
    CONQUEST_DEFLECTOR_ITEM,
    CONQUEST_DEPLOYMENT_ROWS,
    CONQUEST_SETUP_BUDGET,
    CONQUEST_UNIT_CAP,
    CONQUEST_UNITS_BY_ID,
)
from ankiscape.logic.cadence_coverage import cadence_coverage_rows_pure
from ankiscape.data.pest_control_data import PEST_CONTROL_COMMENDATION_CAP
from ankiscape.logic.conquest_logic import (
    _commendation_multiplier,
    _distance,
    _rating_delta,
    _reachable_positions,
    _turn_ratio,
    apply_conquest_command_pure,
    apply_conquest_review_pure,
    conquest_view_pure,
    enter_conquest_pure,
    sanitize_conquest_state_pure,
    set_conquest_policy_pure,
)
from ankiscape.logic.music_log_logic import refresh_music_log_pure
from ankiscape.logic.pest_control_logic import (
    apply_pest_control_command_pure,
    enter_pest_control_pure,
    pest_control_view_pure,
)
from ankiscape.runtime.runtime_actions import handle_utility_answer
from tests.test_runtime_actions import _context


def _player(level: int = 40, **overrides) -> dict:
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    for key in (
        "attack_level",
        "strength_level",
        "defense_level",
        "constitution_level",
        "ranged_level",
        "magic_level",
        "prayer_level",
    ):
        player[key] = level
    player["summoning_level"] = 1
    player["activity_session"] = {"active_id": ""}
    player["combat_encounter"] = {}
    player["current_utility"] = "make_soft_clay"
    player["inventory"] = {}
    player["equipment"] = {}
    player.update(overrides)
    return player


def _entered(seed: int = 0, **overrides) -> dict:
    rng = random.Random(seed)
    player, ok, info = enter_conquest_pure(
        _player(**overrides),
        {},
        rng.random,
    )
    assert ok, info
    return player


class ConquestDataTests(unittest.TestCase):
    def test_corrected_roster_and_absences_are_exact(self):
        self.assertEqual(CONQUEST_UNITS_BY_ID["knight"].attack_range, 1)
        self.assertEqual(CONQUEST_UNITS_BY_ID["mage"].attack_range, 4)
        self.assertEqual(CONQUEST_UNITS_BY_ID["champion"].lifepoints, 500)
        self.assertEqual(set(CONQUEST_UNITS_BY_ID), {
            "scout",
            "foot_soldier",
            "halberdier",
            "archer",
            "mage",
            "knight",
            "champion",
        })
        self.assertNotIn("hybrid", CONQUEST_UNITS_BY_ID)

    def test_all_nine_commands_keep_exact_costs_and_cooldowns(self):
        self.assertEqual(
            [(row.display_name, row.cost, row.cooldown) for row in CONQUEST_COMMANDS],
            [
                ("Battle Cry", 75, 5),
                ("Stoicism", 75, 5),
                ("Regenerate", 150, 4),
                ("Bombard", 200, 2),
                ("Winds of Fate", 150, 2),
                ("Charge", 75, 5),
                ("Chastise", 50, 3),
                ("Vigilance", 50, 3),
                ("Shield Wall", 50, 5),
            ],
        )

    def test_default_squad_is_ten_units_and_under_budget(self):
        count = sum(CONQUEST_DEFAULT_SQUAD.values())
        cost = sum(
            CONQUEST_UNITS_BY_ID[unit_id].cost * quantity
            for unit_id, quantity in CONQUEST_DEFAULT_SQUAD.items()
        )
        self.assertEqual(count, CONQUEST_UNIT_CAP)
        self.assertLessEqual(cost, CONQUEST_SETUP_BUDGET)
        self.assertEqual(len(CONQUEST_DEFAULT_COMMANDS), 4)

    def test_activity_and_deflector_assets_are_registered(self):
        icon = UTILITY_ACTIVITY_DATA["conquest"].get("icon_path")
        self.assertTrue(icon)
        self.assertTrue(os.path.exists(icon))
        item = next(
            row for row in ITEM_DEFINITIONS if row.storage_key == CONQUEST_DEFLECTOR_ITEM
        )
        self.assertTrue(item.asset_path)
        self.assertTrue(os.path.exists(item.asset_path))
        self.assertEqual(EQUIPMENT_DATA[CONQUEST_DEFLECTOR_ITEM].slot, "shield")


class ConquestEntryAndSetupTests(unittest.TestCase):
    def test_combat_40_entry_and_persistent_activity_arbitration(self):
        _data, ok, info = enter_conquest_pure(_player(3))
        self.assertFalse(ok)
        self.assertIn("combat level 40", info["reason"])
        busy = _player(activity_session={"active_id": "soul_wars"})
        unchanged = copy.deepcopy(busy)
        result, ok, info = enter_conquest_pure(busy)
        self.assertFalse(ok)
        self.assertIn("persistent activity", info["reason"])
        self.assertEqual(result, unchanged)
        _result, ok, info = enter_pest_control_pure(_entered())
        self.assertFalse(ok)
        self.assertIn("persistent activity", info["reason"])

    def test_casual_forces_default_and_advanced_validates_budget_and_cap(self):
        casual, ok, _info = set_conquest_policy_pure(
            _player(),
            {
                "automation_mode": "casual",
                "squad": {"champion": 10},
                "commands": [],
            },
        )
        self.assertTrue(ok)
        self.assertEqual(casual["conquest_policy"]["squad"], CONQUEST_DEFAULT_SQUAD)
        original = _player()
        advanced, ok, info = set_conquest_policy_pure(
            original,
            {
                "automation_mode": "advanced",
                "squad": {"champion": 6},
                "commands": [],
            },
        )
        self.assertFalse(ok)
        self.assertIn("setup points", info["reason"])
        self.assertEqual(advanced, original)
        _advanced, ok, info = set_conquest_policy_pure(
            original,
            {
                "automation_mode": "advanced",
                "squad": CONQUEST_DEFAULT_SQUAD,
                "commands": [
                    "battle_cry",
                    "stoicism",
                    "regenerate",
                    "bombard",
                    "charge",
                ],
            },
        )
        self.assertFalse(ok)
        self.assertIn("at most 4 commands", info["reason"])

    def test_over_cap_squad_is_refused_rather_than_clamped(self):
        draft = {
            "automation_mode": "advanced",
            "squad": {"scout": CONQUEST_UNIT_CAP + 1},
            "commands": [],
        }
        original = _player()
        unchanged, ok, info = set_conquest_policy_pure(original, draft)
        self.assertFalse(ok)
        self.assertIn(f"{CONQUEST_UNIT_CAP} troops", info["reason"])
        self.assertEqual(unchanged, original)
        view = conquest_view_pure(original, draft)
        self.assertFalse(view["save_enabled"])
        self.assertEqual(view["squad_rows"][0]["count"], CONQUEST_UNIT_CAP + 1)

    def test_simulated_opponent_rating_stays_inside_the_disclosed_band(self):
        for roll in (0.0, 0.999999999):
            with self.subTest(roll=roll):
                player, ok, info = enter_conquest_pure(
                    _player(conquest_rating=1_000), {}, lambda: roll
                )
                self.assertTrue(ok, info)
                self.assertLessEqual(
                    abs(player["conquest"]["opponent_rating"] - 1_000), 100
                )

    def test_entry_builds_a_bounded_board_and_unlocks_both_tracks(self):
        player = _entered()
        session = player["conquest"]
        self.assertEqual(player["activity_session"], {"active_id": "conquest"})
        self.assertEqual(session["opponent_label"], "Bounded simulated opponent")
        self.assertTrue(
            all(
                0 <= unit[axis] < CONQUEST_BOARD_SIZE
                for unit in session["units"]
                for axis in ("x", "y")
            )
        )
        player, newly = refresh_music_log_pure(player)
        self.assertEqual(set(newly), set())
        unlocked = {
            row.name
            for row in __import__(
                "ankiscape.data.music_log_data", fromlist=["MUSIC_TRACKS"]
            ).MUSIC_TRACKS
            if row.id in player["music_log"]["unlocked_tracks"]
        }
        self.assertIn("Right of Conquest", unlocked)
        self.assertIn("Unavoidable Conflict", unlocked)

    def test_the_starting_formation_is_the_registered_placeholder(self):
        """The arrangement is unsourced, so it must stay a marked placeholder."""
        session = _entered()["conquest"]
        player_rows = set(range(CONQUEST_DEPLOYMENT_ROWS))
        opponent_rows = {
            CONQUEST_BOARD_SIZE - 1 - row for row in range(CONQUEST_DEPLOYMENT_ROWS)
        }
        for unit in session["units"]:
            rows = player_rows if unit["side"] == "player" else opponent_rows
            self.assertIn(unit["y"], rows)
        self.assertEqual(
            [
                (unit["x"], unit["y"])
                for unit in session["units"]
                if unit["side"] == "player"
            ],
            [(column, 0) for column in range(CONQUEST_UNIT_CAP)],
        )

    def test_view_owns_draft_validation_and_command_limit_decisions(self):
        draft = {
            "automation_mode": "advanced",
            "squad": {"champion": 6},
            "commands": list(CONQUEST_DEFAULT_COMMANDS),
        }
        view = conquest_view_pure(_player(), draft)
        self.assertFalse(view["save_enabled"])
        self.assertTrue(view["setup_errors"])
        full = conquest_view_pure(
            _player(),
            {
                "automation_mode": "advanced",
                "squad": CONQUEST_DEFAULT_SQUAD,
                "commands": list(CONQUEST_DEFAULT_COMMANDS),
            },
        )
        self.assertTrue(
            all(
                row["enabled"] == row["selected"]
                for row in full["command_rows"]
            )
        )


class ConquestReviewTests(unittest.TestCase):
    def _command_state(self, command_id: str) -> dict:
        player = _entered()
        session = player["conquest"]
        session["first_player"] = "player"
        session["commands"] = {
            "player": [command_id],
            "opponent": [],
        }
        session["cooldowns"] = {
            "player": {command_id: 0},
            "opponent": {},
        }
        session["command_points"] = {
            "player": next(
                row.cost for row in CONQUEST_COMMANDS if row.id == command_id
            ),
            "opponent": 0,
        }
        session["obstacles"] = []
        session["units"] = [
            {
                **session["units"][0],
                "id": "player-champion",
                "unit_type": "champion",
                "lifepoints": 500,
                "x": 0,
                "y": 0,
            },
            {
                **session["units"][10],
                "id": "opponent-scout",
                "unit_type": "scout",
                "lifepoints": 100,
                "x": 19,
                "y": 19,
            },
        ]
        return player

    def test_one_productive_review_is_one_complete_turn_exchange(self):
        before = _entered(seed=1)
        frozen = copy.deepcopy(before)
        after, ok, result = apply_conquest_review_pure(
            before, random.Random(9).random
        )
        self.assertTrue(ok, result)
        self.assertEqual(after["conquest"]["round"], 1)
        self.assertEqual(after["conquest"]["side_turns"], 2)
        self.assertEqual(before, frozen)
        self.assertFalse(
            apply_conquest_review_pure(after, productive=False)[1]
        )

    def test_opening_player_gets_no_passive_cp_and_second_player_gets_25(self):
        player = _entered(seed=1)
        first = player["conquest"]["first_player"]
        second = "opponent" if first == "player" else "player"
        after, ok, result = apply_conquest_review_pure(player, lambda: 0.5)
        self.assertTrue(ok, result)
        self.assertEqual(after["conquest"]["command_points"][first], 0)
        self.assertEqual(after["conquest"]["command_points"][second], 25)

    def test_normal_kill_pays_unit_cost(self):
        player = _entered()
        session = player["conquest"]
        session["first_player"] = "player"
        session["commands"] = {"player": [], "opponent": []}
        session["cooldowns"] = {"player": {}, "opponent": {}}
        session["units"] = [
            {
                **session["units"][0],
                "id": "player-champion",
                "unit_type": "champion",
                "lifepoints": 500,
                "x": 0,
                "y": 0,
            },
            {
                **session["units"][10],
                "id": "opponent-scout-near",
                "unit_type": "scout",
                "lifepoints": 100,
                "x": 0,
                "y": 1,
            },
            {
                **session["units"][11],
                "id": "opponent-scout-far",
                "unit_type": "scout",
                "lifepoints": 100,
                "x": 19,
                "y": 19,
            },
        ]
        after, ok, result = apply_conquest_review_pure(player, lambda: 0.5)
        self.assertTrue(ok, result)
        self.assertEqual(after["conquest"]["command_points"]["player"], 25)

    def test_bombard_kill_pays_nothing(self):
        player = _entered()
        session = player["conquest"]
        session["first_player"] = "player"
        session["commands"] = {"player": ["bombard"], "opponent": []}
        session["cooldowns"] = {"player": {"bombard": 0}, "opponent": {}}
        session["command_points"] = {"player": 200, "opponent": 0}
        session["units"] = [
            {
                **session["units"][0],
                "id": "player-scout",
                "unit_type": "scout",
                "lifepoints": 100,
                "x": 0,
                "y": 0,
            },
            {
                **session["units"][10],
                "id": "opponent-scout-one",
                "unit_type": "scout",
                "lifepoints": 100,
                "x": 19,
                "y": 19,
            },
            {
                **session["units"][11],
                "id": "opponent-scout-two",
                "unit_type": "scout",
                "lifepoints": 100,
                "x": 18,
                "y": 19,
            },
        ]
        after, ok, result = apply_conquest_review_pure(player, lambda: 0.5)
        self.assertTrue(ok, result)
        self.assertEqual(after["conquest"]["command_points"]["player"], 0)
        self.assertEqual(after["conquest"]["cooldowns"]["player"]["bombard"], 2)

    def test_all_non_targeting_command_effects_run_through_the_review_reducer(self):
        expected = {
            "battle_cry": ("battle_cry", 700),
            "stoicism": ("stoicism", 900),
            "vigilance": ("vigilance", 500),
            "shield_wall": ("shield_wall", 500),
        }
        for command_id, (effect_id, lifepoints) in expected.items():
            with self.subTest(command=command_id):
                after, ok, result = apply_conquest_review_pure(
                    self._command_state(command_id), lambda: 0.5
                )
                self.assertTrue(ok, result)
                unit = next(
                    row
                    for row in after["conquest"]["units"]
                    if row["side"] == "player"
                )
                self.assertTrue(unit["effects"][effect_id])
                self.assertEqual(unit["lifepoints"], lifepoints)
                self.assertEqual(
                    after["conquest"]["cooldowns"]["player"][command_id],
                    next(
                        row.cooldown
                        for row in CONQUEST_COMMANDS
                        if row.id == command_id
                    ),
                )
                self.assertEqual(
                    after["conquest"]["command_points"]["player"],
                    0,
                )

        regenerate = self._command_state("regenerate")
        regenerate["conquest"]["units"][0]["lifepoints"] = 100
        after, ok, result = apply_conquest_review_pure(regenerate, lambda: 0.5)
        self.assertTrue(ok, result)
        self.assertEqual(after["conquest"]["units"][0]["lifepoints"], 500)

        charge = self._command_state("charge")
        after, ok, result = apply_conquest_review_pure(charge, lambda: 0.5)
        self.assertTrue(ok, result)
        player_unit = next(
            row for row in after["conquest"]["units"] if row["side"] == "player"
        )
        self.assertEqual(
            abs(player_unit["x"] - 19) + abs(player_unit["y"] - 19),
            30,
        )

        winds = self._command_state("winds_of_fate")
        winds["conquest"]["commands"]["player"].append("charge")
        winds["conquest"]["cooldowns"]["player"]["charge"] = 2
        after, ok, result = apply_conquest_review_pure(winds, lambda: 0.5)
        self.assertTrue(ok, result)
        self.assertEqual(after["conquest"]["cooldowns"]["player"]["charge"], 0)
        self.assertEqual(
            after["conquest"]["cooldowns"]["player"]["winds_of_fate"],
            2,
        )

    def test_chastise_never_targets_the_last_enemy_troop(self):
        player = _entered()
        session = player["conquest"]
        session["first_player"] = "player"
        session["commands"] = {"player": ["chastise"], "opponent": []}
        session["cooldowns"] = {"player": {"chastise": 0}, "opponent": {}}
        session["command_points"] = {"player": 50, "opponent": 0}
        session["units"] = [
            {**session["units"][0], "x": 0, "y": 0},
            {**session["units"][10], "x": 19, "y": 19},
        ]
        _after, ok, result = apply_conquest_review_pure(player, lambda: 0.5)
        self.assertTrue(ok, result)
        self.assertNotIn("Chastise", " ".join(result["events"]))

    def test_elimination_settles_and_resignation_is_direct(self):
        player = _entered()
        player["conquest"]["round"] = 4
        player["conquest"]["first_player"] = "player"
        player["conquest"]["commands"] = {"player": [], "opponent": []}
        player["conquest"]["cooldowns"] = {"player": {}, "opponent": {}}
        player["conquest"]["units"] = [
            {
                **player["conquest"]["units"][0],
                "unit_type": "champion",
                "lifepoints": 500,
                "x": 0,
                "y": 0,
            },
            {
                **player["conquest"]["units"][10],
                "unit_type": "scout",
                "lifepoints": 100,
                "x": 0,
                "y": 1,
            },
        ]
        won, ok, result = apply_conquest_review_pure(player, lambda: 0.5)
        self.assertTrue(ok, result)
        self.assertTrue(result["terminal"])
        self.assertTrue(result["won"])
        self.assertEqual(won["activity_session"], {"active_id": ""})

        resigned, ok, result = apply_conquest_command_pure(
            _entered(), "resign"
        )
        self.assertTrue(ok, result)
        self.assertEqual(resigned["conquest_resignations"], 1)
        self.assertEqual(resigned["activity_session"], {"active_id": ""})

    def test_reward_curve_and_bands_are_monotonic_with_no_win_bonus(self):
        self.assertEqual([_turn_ratio(value) for value in range(1, 35)], sorted(
            _turn_ratio(value) for value in range(1, 35)
        ))
        self.assertEqual(_turn_ratio(19), 7)
        self.assertEqual(_commendation_multiplier(40), (2, 20))
        self.assertEqual(_commendation_multiplier(70), (3, 30))
        self.assertEqual(_commendation_multiplier(100), (4, 40))
        self.assertEqual(_rating_delta(2_500, 1_311), 11)

        win_state = _entered()
        win_state["conquest"]["round"] = 18
        win_state["conquest"]["first_player"] = "player"
        win_state["conquest"]["commands"] = {"player": [], "opponent": []}
        win_state["conquest"]["cooldowns"] = {"player": {}, "opponent": {}}
        win_state["conquest"]["units"] = [
            {
                **win_state["conquest"]["units"][0],
                "unit_type": "champion",
                "lifepoints": 500,
                "x": 0,
                "y": 0,
            },
            {
                **win_state["conquest"]["units"][10],
                "unit_type": "scout",
                "lifepoints": 100,
                "x": 0,
                "y": 1,
            },
        ]
        won_state, ok, win = apply_conquest_review_pure(
            win_state, lambda: 0.5
        )
        self.assertTrue(ok, win)
        self.assertEqual(
            won_state["pest_control_commendations"],
            win["commendations"],
        )

        loss_state = _entered()
        loss_state["conquest"]["round"] = 18
        loss_state["conquest"]["first_player"] = "opponent"
        loss_state["conquest"]["commands"] = {"player": [], "opponent": []}
        loss_state["conquest"]["cooldowns"] = {"player": {}, "opponent": {}}
        loss_state["conquest"]["units"] = [
            {
                **loss_state["conquest"]["units"][0],
                "unit_type": "scout",
                "lifepoints": 100,
                "x": 0,
                "y": 0,
            },
            {
                **loss_state["conquest"]["units"][10],
                "unit_type": "champion",
                "lifepoints": 500,
                "x": 0,
                "y": 1,
            },
        ]
        lost_state, ok, loss = apply_conquest_review_pure(
            loss_state, lambda: 0.5
        )
        self.assertTrue(ok, loss)
        self.assertEqual(win["commendations"], loss["commendations"])
        self.assertEqual(
            lost_state["pest_control_commendations"],
            loss["commendations"],
        )

    def test_a_capped_wallet_reports_only_the_commendations_it_paid(self):
        player = _entered(
            pest_control_commendations=PEST_CONTROL_COMMENDATION_CAP - 5
        )
        player["conquest"]["round"] = 18
        player["conquest"]["first_player"] = "player"
        player["conquest"]["commands"] = {"player": [], "opponent": []}
        player["conquest"]["cooldowns"] = {"player": {}, "opponent": {}}
        player["conquest"]["units"] = [
            {
                **player["conquest"]["units"][0],
                "unit_type": "champion",
                "lifepoints": 500,
                "x": 0,
                "y": 0,
            },
            {
                **player["conquest"]["units"][10],
                "unit_type": "scout",
                "lifepoints": 100,
                "x": 0,
                "y": 1,
            },
        ]
        settled, ok, result = apply_conquest_review_pure(player, lambda: 0.5)
        self.assertTrue(ok, result)
        self.assertEqual(
            settled["pest_control_commendations"], PEST_CONTROL_COMMENDATION_CAP
        )
        self.assertEqual(result["commendations"], 5)
        self.assertIn("5 commendations", result["message"])

    def test_range_and_movement_share_the_registered_four_direction_metric(self):
        self.assertEqual(_distance({"x": 3, "y": 3}, {"x": 4, "y": 4}), 2)
        unit = {"id": "solo", "x": 3, "y": 3}
        self.assertEqual(
            _reachable_positions({"units": [unit], "obstacles": []}, unit, 1),
            {(3, 3), (2, 3), (4, 3), (3, 2), (3, 4)},
        )
        register = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "memory-bank",
            "placeholder-values.md",
        )
        with open(register, encoding="utf-8") as handle:
            rows = handle.read()
        for placeholder_id in (
            "conquest.board_metric",
            "conquest.default_squad",
            "conquest.default_commands",
        ):
            self.assertIn(placeholder_id, rows)

    def test_cadence_declares_exact_review_and_direct_action_boundaries(self):
        row = next(
            row
            for row in cadence_coverage_rows_pure()
            if row["handler_key"] == "utility" and row["action_id"] == "conquest"
        )
        self.assertIn("turn exchange", row["source_reason"])
        self.assertIn("entry, setup, and resignation", row["source_reason"])
        self.assertEqual(row["undo_boundary"], "one answered-card transaction")

    def test_runtime_dispatch_records_conquest_telemetry(self):
        player = _entered()
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        self.assertTrue(
            handle_utility_answer(
                _context(player, calls, random_values=(0.5,) * 50)
            )
        )
        self.assertEqual(calls["saves"], 1)
        self.assertIn(
            "utility:conquest", player["action_telemetry"]["actions"]
        )

    def test_bounded_opponent_always_finishes_sampled_matches(self):
        for seed in range(20):
            with self.subTest(seed=seed):
                rng = random.Random(seed)
                player, ok, result = enter_conquest_pure(
                    _player(),
                    {},
                    rng.random,
                )
                self.assertTrue(ok, result)
                for _exchange in range(60):
                    player, ok, result = apply_conquest_review_pure(
                        player,
                        rng.random,
                    )
                    self.assertTrue(ok, result)
                    if result["terminal"]:
                        break
                self.assertTrue(result["terminal"])
                self.assertEqual(
                    player["activity_session"],
                    {"active_id": ""},
                )


class ConquestStorageAndShopTests(unittest.TestCase):
    def test_schema_102_migrates_and_repairs_malformed_conquest(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 101,
                "activity_session": {"active_id": "conquest"},
                "conquest": {"units": "bad"},
                "conquest_rating": -12,
                "conquest_policy": {
                    "automation_mode": "advanced",
                    "squad": {"champion": 99},
                    "commands": ["bad"],
                },
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        # Schema-relative, per convention: later branches add versions above
        # Conquest's own v102 migration.
        self.assertGreaterEqual(CURRENT_CONFIG_VERSION, 102)
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["conquest"], {})
        self.assertEqual(migrated["activity_session"], {"active_id": ""})
        self.assertEqual(migrated["conquest_rating"], 0)
        self.assertEqual(
            migrated["conquest_policy"]["squad"], CONQUEST_DEFAULT_SQUAD
        )

    def test_schema_102_drops_a_persisted_over_cap_squad(self):
        session = copy.deepcopy(_entered()["conquest"])
        session["units"].append(
            {
                **session["units"][0],
                "id": "player-scout-extra",
                "x": 5,
                "y": 5,
            }
        )
        migrated = migrate_loaded_data(
            {
                "config_version": 101,
                "activity_session": {"active_id": "conquest"},
                "conquest": session,
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["conquest"], {})
        self.assertEqual(migrated["activity_session"], {"active_id": ""})

    def test_rating_keeps_no_undocumented_maximum(self):
        state = sanitize_conquest_state_pure({"conquest_rating": 1_000_000})
        self.assertEqual(state["conquest_rating"], 1_000_000)

    def test_sanitizer_repairs_missing_and_conflicting_activity_ownership(self):
        entered = _entered()
        entered["activity_session"] = {"active_id": ""}
        repaired = sanitize_conquest_state_pure(entered)
        self.assertEqual(repaired["activity_session"], {"active_id": "conquest"})
        entered["activity_session"] = {"active_id": "soul_wars"}
        repaired = sanitize_conquest_state_pure(entered)
        self.assertEqual(repaired["conquest"], {})
        self.assertNotIn("activity_session", repaired)

    def test_deflector_uses_shared_wallet_and_both_gates(self):
        low = _player(
            conquest_rating=1_249,
            pest_control_commendations=500,
        )
        _data, ok, info = apply_pest_control_command_pure(
            low, "buy_void_knight_deflector"
        )
        self.assertFalse(ok)
        self.assertIn("1,250", info["reason"])
        ready = _player(
            conquest_rating=1_250,
            pest_control_commendations=150,
        )
        bought, ok, info = apply_pest_control_command_pure(
            ready, "buy_void_knight_deflector"
        )
        self.assertTrue(ok, info)
        self.assertEqual(bought["pest_control_commendations"], 0)
        self.assertEqual(bought["inventory"][CONQUEST_DEFLECTOR_ITEM], 1)
        self.assertTrue(pest_control_view_pure(bought)["deflector_owned"])

    def test_shared_shop_is_blocked_while_conquest_is_active(self):
        entered = _entered(pest_control_commendations=500, conquest_rating=1_250)
        view = pest_control_view_pure(entered)
        self.assertFalse(view["seal_enabled"])
        self.assertFalse(view["deflector_enabled"])
        for command in ("buy_void_seal", "buy_void_knight_deflector"):
            _data, ok, info = apply_pest_control_command_pure(entered, command)
            self.assertFalse(ok)
            self.assertIn("persistent activity", info["reason"])


if __name__ == "__main__":
    unittest.main()
