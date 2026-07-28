from __future__ import annotations

import json
import os
import random
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import (
    COMBAT_ENEMY_DATA,
    EQUIPMENT_DATA,
    EXP_TABLE,
    EXTRA_ITEM_DATA,
    EXTRA_ITEM_IMAGES,
    ITEM_DEFINITIONS,
    ORE_DATA,
    UTILITY_ACTIVITY_DATA,
)
from ankiscape.core.storage_pure import CURRENT_CONFIG_VERSION, default_player_data, migrate_loaded_data
from ankiscape.data.troll_invasion_data import (
    TROLL_INVASION_ACTIVITY_ID,
    TROLL_INVASION_COMBAT_MODE,
    TROLL_INVASION_COMBAT_TARGET_ID,
    TROLL_INVASION_HARD,
    TROLL_INVASION_HARD_WAVES,
    TROLL_INVASION_MONTH_REVIEWS,
    TROLL_INVASION_REPAIR_ACTION_CEILING,
    TROLL_INVASION_REPAIR_JOBS,
    TROLL_INVASION_REPAIR_MODE,
    TROLL_INVASION_REPAIR_TROLL_TARGET,
    TROLL_INVASION_REWARD_BOOK,
    TROLL_INVASION_STANDARD,
    TROLL_INVASION_STANDARD_WAVES,
)
from ankiscape.logic.troll_invasion_logic import (
    apply_troll_invasion_command_pure,
    apply_troll_invasion_review_pure,
    default_troll_invasion_state_pure,
    enter_troll_invasion_pure,
    leave_troll_invasion_pure,
    redeem_troll_invasion_book_pure,
    sanitize_troll_invasion_state_pure,
    set_troll_invasion_policy_pure,
    troll_invasion_reward_xp_pure,
    troll_invasion_view_pure,
)
from ankiscape.logic_pure.logic_pure import calculate_new_level
from ankiscape.runtime.runtime_actions import (
    RuntimeActionContext,
    handle_troll_invasion_answer,
    handle_utility_answer,
)

try:
    from aqt.qt import QApplication, QComboBox, QPushButton
    from ankiscape.ui.troll_invasion_panel import TrollInvasionPanel

    QT_AVAILABLE = True
except Exception:
    QT_AVAILABLE = False


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STANDARD_WIN_SEED = 3
HARD_WIN_SEED = 1
SAFE_DEATH_SEED = 3


def _player(level: int = 99, **overrides):
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    for key in (
        "attack_level",
        "strength_level",
        "defense_level",
        "constitution_level",
        "magic_level",
        "ranged_level",
    ):
        data[key] = level
    data["combat_lifepoints"] = level * 10
    data["equipment"] = {
        "weapon": "Abyssal whip",
        "body": "Rune platebody",
        "legs": "Rune platelegs",
        "head": "Rune full helm",
        "shield": "Dragon defender",
        "cape": "Fire cape",
    }
    data["inventory"] = {"Shark": 100_000}
    data["combat_supply_loadout"] = {"food": {"Shark": 26}}
    data.update(overrides)
    return data


def _play_combat(data, difficulty, seed):
    data, ok, info = enter_troll_invasion_pure(
        data, {"mode": TROLL_INVASION_COMBAT_MODE, "difficulty": difficulty}
    )
    if not ok:
        raise AssertionError(info)
    rng = random.Random(seed).random
    observed = {"reviews": 0, "waves": set(), "supply_destroyed": 0}
    for _ in range(1_000):
        observed["reviews"] += 1
        observed["waves"].add(data["troll_invasion"]["wave"])
        data, ok, result = apply_troll_invasion_review_pure(
            data, rng, equipment_data=EQUIPMENT_DATA
        )
        if not ok:
            raise AssertionError(result)
        observed["supply_destroyed"] += int(bool(result.get("supply_destroyed")))
        if result.get("terminal"):
            return data, result, observed
    raise AssertionError("Troll Invasion Combat did not terminate")


def _context(player_data, calls):
    def award_skill_exp(exp_key, amount):
        player_data[exp_key] = float(player_data.get(exp_key, 0.0)) + float(amount)
        return float(amount)

    def level_up(display_name, data):
        skill_id = display_name.lower()
        exp_key = f"{skill_id}_exp"
        level_key = f"{skill_id}_level"
        data[level_key] = calculate_new_level(
            data.get(exp_key, 0.0), data.get(level_key, 1), EXP_TABLE
        )

    return RuntimeActionContext(
        player_data=player_data,
        random_random=calls["rng"],
        show_error_message=lambda title, message: calls["errors"].append((title, message)),
        deactivate_current_skill=lambda: calls.__setitem__("deactivated", True),
        award_skill_exp=award_skill_exp,
        award_hidden_skill_exp=lambda *_args: None,
        level_up_check=level_up,
        check_achievements=lambda _data: calls.__setitem__("achievements", True),
        save_player_data=lambda: calls.__setitem__("saves", calls["saves"] + 1),
        refresh_skill_availability=lambda: calls.__setitem__("refresh", True),
        refresh_skill_availability_partial=lambda *_args: None,
        can_smith_any=lambda: False,
        show_exp=lambda amount: calls["xp"].append(amount),
        show_activity_gain=lambda message: calls["activity"].append(message),
        implemented_exp_keys_snapshot=lambda: {},
        show_quest_exp_delta=lambda _before: None,
    )


class TrollInvasionRegistryLayerTest(unittest.TestCase):
    def test_registry_rows_assets_and_source_shape_are_live(self):
        activity = UTILITY_ACTIVITY_DATA[TROLL_INVASION_ACTIVITY_ID]
        self.assertEqual(activity["surface"], "activities")
        self.assertEqual(activity["group"], "distractions_and_diversions")
        self.assertTrue(os.path.isfile(activity["icon_path"]))
        self.assertIn(TROLL_INVASION_REWARD_BOOK, EXTRA_ITEM_DATA)
        self.assertTrue(os.path.isfile(EXTRA_ITEM_IMAGES[TROLL_INVASION_REWARD_BOOK]))
        self.assertIn(TROLL_INVASION_COMBAT_TARGET_ID, COMBAT_ENEMY_DATA)
        self.assertEqual(
            COMBAT_ENEMY_DATA[TROLL_INVASION_COMBAT_TARGET_ID]["group"],
            "Troll Invasion",
        )
        with open(os.path.join(ROOT, "assets_provenance.json"), encoding="utf-8") as handle:
            provenance = json.load(handle)
        for path in (
            "activityicons/troll_invasion.png",
            "activityitems/troll_invasion_reward_book.png",
        ):
            self.assertIn(path, provenance)
            self.assertLess(provenance[path]["timestamp"], "2012-11-20T00:00:00Z")

    def test_period_counts_formula_and_calendar_mapping_are_literal_pins(self):
        self.assertEqual(TROLL_INVASION_STANDARD_WAVES, 20)
        self.assertEqual(TROLL_INVASION_HARD_WAVES, 7)
        self.assertEqual(TROLL_INVASION_MONTH_REVIEWS, 7_200)
        self.assertEqual(TROLL_INVASION_REPAIR_TROLL_TARGET, 1_500)
        self.assertEqual(TROLL_INVASION_REPAIR_ACTION_CEILING, 167)
        self.assertEqual(troll_invasion_reward_xp_pure(50, 1.0), 20_000.0)
        self.assertEqual(troll_invasion_reward_xp_pure(50, 0.25), 5_000.0)


class TrollInvasionPureLayerTest(unittest.TestCase):
    def test_policy_and_entry_gates_unlock_hard_on_attempt_not_completion(self):
        player = _player()
        _, ok, info = set_troll_invasion_policy_pure(
            player,
            {"mode": TROLL_INVASION_COMBAT_MODE, "difficulty": TROLL_INVASION_HARD, "reward_skill": "agility"},
        )
        self.assertFalse(ok)
        self.assertIn("Attempt Standard", info["reason"])

        entered, ok, info = enter_troll_invasion_pure(
            player,
            {"mode": TROLL_INVASION_COMBAT_MODE, "difficulty": TROLL_INVASION_STANDARD},
        )
        self.assertTrue(ok, info)
        self.assertTrue(entered["troll_invasion_hard_unlocked"])
        left, ok, info = leave_troll_invasion_pure(entered)
        self.assertTrue(ok, info)
        hard, ok, info = enter_troll_invasion_pure(
            left,
            {"mode": TROLL_INVASION_COMBAT_MODE, "difficulty": TROLL_INVASION_HARD},
        )
        self.assertTrue(ok, info)
        self.assertEqual(hard["troll_invasion"]["difficulty"], TROLL_INVASION_HARD)

        busy = _player()
        busy["activity_session"] = {"active_id": "clan_wars"}
        _, ok, info = enter_troll_invasion_pure(busy, {})
        self.assertFalse(ok)
        self.assertIn("persistent activity", info["reason"])
        fighting = _player()
        fighting["combat_encounter"] = {"target_id": "chicken"}
        _, ok, info = enter_troll_invasion_pure(fighting, {})
        self.assertFalse(ok)
        self.assertIn("Combat encounter", info["reason"])

    def test_standard_and_hard_complete_through_real_combat_with_every_wave_observed(self):
        standard, result, observed = _play_combat(_player(), TROLL_INVASION_STANDARD, STANDARD_WIN_SEED)
        self.assertTrue(result["complete"])
        self.assertEqual(result["completion_fraction"], 1.0)
        self.assertEqual(observed["waves"], set(range(1, 21)))
        self.assertGreater(observed["reviews"], TROLL_INVASION_STANDARD_WAVES)
        self.assertEqual(standard["inventory"][TROLL_INVASION_REWARD_BOOK], 1)
        self.assertEqual(standard["attack_exp"] > 0, True)

        hard_player = _player(troll_invasion_hard_unlocked=True)
        hard, result, observed = _play_combat(hard_player, TROLL_INVASION_HARD, HARD_WIN_SEED)
        self.assertTrue(result["complete"])
        self.assertEqual(observed["waves"], set(range(1, 8)))
        self.assertEqual(hard["inventory"][TROLL_INVASION_REWARD_BOOK], 1)

    def test_safe_combat_death_is_reachable_and_never_creates_a_grave(self):
        weak = _player(level=10, equipment={"weapon": "Bronze sword"}, combat_lifepoints=100, combat_auto_flee=False)
        defeated, result, observed = _play_combat(weak, TROLL_INVASION_STANDARD, SAFE_DEATH_SEED)
        self.assertEqual(result["outcome"], "failure")
        self.assertGreaterEqual(observed["reviews"], 1)
        self.assertEqual(defeated["equipment"], {"weapon": "Bronze sword"})
        self.assertEqual(defeated["combat_grave"], {})
        self.assertEqual(defeated["death_office"], {})
        self.assertEqual(defeated["troll_invasion_failures"], 1)

    def test_supply_restoration_and_dynamite_destruction_are_both_reachable(self):
        supplied, ok, info = enter_troll_invasion_pure(
            _player(combat_lifepoints=100),
            {"mode": TROLL_INVASION_COMBAT_MODE, "difficulty": TROLL_INVASION_STANDARD},
        )
        self.assertTrue(ok, info)
        supplied, ok, result = apply_troll_invasion_review_pure(
            supplied, lambda: 1.0, equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok, result)
        self.assertTrue(result["supply_used"])
        self.assertEqual(supplied["troll_invasion"]["supply_uses"], 4)

        destroyed, ok, info = enter_troll_invasion_pure(
            _player(),
            {"mode": TROLL_INVASION_COMBAT_MODE, "difficulty": TROLL_INVASION_STANDARD},
        )
        self.assertTrue(ok, info)
        destroyed, ok, result = apply_troll_invasion_review_pure(
            destroyed, lambda: 0.0, equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok, result)
        self.assertTrue(result["supply_destroyed"])
        self.assertTrue(destroyed["troll_invasion"]["supply_destroyed"])
        self.assertEqual(destroyed["troll_invasion"]["supply_uses"], 0)

    def test_partial_leave_awards_a_real_fraction_book_and_redeems_exact_xp(self):
        player, ok, info = enter_troll_invasion_pure(
            _player(), {"mode": TROLL_INVASION_COMBAT_MODE, "difficulty": TROLL_INVASION_STANDARD}
        )
        self.assertTrue(ok, info)
        rng = random.Random(STANDARD_WIN_SEED).random
        while player["troll_invasion"]["waves_completed"] < 3:
            player, ok, result = apply_troll_invasion_review_pure(player, rng, equipment_data=EQUIPMENT_DATA)
            self.assertTrue(ok, result)
        left, ok, result = leave_troll_invasion_pure(player)
        self.assertTrue(ok, result)
        self.assertEqual(result["completion_fraction"], 3 / 20)
        self.assertTrue(result["book_awarded"])
        before = left["agility_exp"]
        before_level = left["agility_level"]
        redeemed, ok, info = redeem_troll_invasion_book_pure(left, "agility")
        self.assertTrue(ok, info)
        expected = troll_invasion_reward_xp_pure(left["agility_level"], 3 / 20)
        self.assertEqual(info["xp_rewards"], {"agility_exp": expected})
        self.assertEqual(redeemed["agility_exp"], before)
        self.assertEqual(redeemed["agility_level"], before_level)
        self.assertNotIn(TROLL_INVASION_REWARD_BOOK, redeemed["inventory"])
        self.assertEqual(redeemed["troll_invasion_books_redeemed"], 1)

    def test_repair_reaches_every_job_xp_morale_power_and_completion_without_mocks(self):
        player, ok, info = enter_troll_invasion_pure(
            _player(), {"mode": TROLL_INVASION_REPAIR_MODE}
        )
        self.assertTrue(ok, info)
        jobs = set()
        skills_paid = set()
        morale_powers = 0
        interruptions = 0
        emergencies = 0
        reviews = 0
        rng = random.Random(8).random
        while True:
            player, ok, result = apply_troll_invasion_review_pure(
                player, rng, equipment_data=EQUIPMENT_DATA
            )
            self.assertTrue(ok, result)
            reviews += 1
            jobs.add(result["job"])
            skills_paid.update(result["skill_xp"])
            morale_powers += int(bool(result["morale_power"]))
            interruptions += int(bool(result["interrupted"]))
            emergencies += int(bool(result["emergency"]))
            if result.get("terminal"):
                break
        self.assertEqual(jobs, {row["id"] for row in TROLL_INVASION_REPAIR_JOBS})
        self.assertEqual(skills_paid, {"construction", "crafting", "firemaking"})
        self.assertGreater(morale_powers, 0)
        self.assertGreater(interruptions, 0)
        self.assertGreater(emergencies, 0)
        self.assertEqual(reviews, TROLL_INVASION_REPAIR_ACTION_CEILING)
        self.assertTrue(result["complete"])
        self.assertEqual(player["inventory"][TROLL_INVASION_REWARD_BOOK], 1)

    def test_severe_pressure_and_interruption_use_independent_rolls(self):
        severe, ok, info = enter_troll_invasion_pure(
            _player(), {"mode": TROLL_INVASION_REPAIR_MODE}
        )
        self.assertTrue(ok, info)
        rolls = iter((0.0, 0.5))
        severe, ok, result = apply_troll_invasion_review_pure(
            severe, lambda: next(rolls), equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["pressure"], 30)
        self.assertFalse(result["interrupted"])
        self.assertEqual(result["credited_trolls"], 10)

        interrupted, ok, info = enter_troll_invasion_pure(
            _player(), {"mode": TROLL_INVASION_REPAIR_MODE}
        )
        self.assertTrue(ok, info)
        rolls = iter((0.5, 0.0))
        interrupted, ok, result = apply_troll_invasion_review_pure(
            interrupted, lambda: next(rolls), equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["pressure"], 4)
        self.assertTrue(result["interrupted"])
        self.assertEqual(result["credited_trolls"], 0)

    def test_repair_gatehouse_failure_is_reachable_through_the_real_reducer(self):
        player, ok, info = enter_troll_invasion_pure(
            _player(), {"mode": TROLL_INVASION_REPAIR_MODE}
        )
        self.assertTrue(ok, info)
        rng = random.Random(0).random
        emergencies = 0
        for reviews in range(1, TROLL_INVASION_REPAIR_ACTION_CEILING + 1):
            player, ok, result = apply_troll_invasion_review_pure(
                player, rng, equipment_data=EQUIPMENT_DATA
            )
            self.assertTrue(ok, result)
            emergencies += int(bool(result["emergency"]))
            if result.get("terminal"):
                break
        self.assertEqual(result["outcome"], "failure")
        self.assertGreater(reviews, 1)
        self.assertGreater(emergencies, 0)
        self.assertGreater(result["completion_fraction"], 0.0)
        self.assertEqual(player["troll_invasion_failures"], 1)
        self.assertEqual(player["activity_session"], {"active_id": ""})

    def test_monthly_allowances_bank_to_two_and_runs_remain_playable_without_one(self):
        player = _player()
        self.assertEqual(troll_invasion_view_pure(player)["troll_invasion_reward_allowances"], 1)
        player["shop_market_clock"]["answered_cards"] = TROLL_INVASION_MONTH_REVIEWS * 4
        self.assertEqual(troll_invasion_view_pure(player)["troll_invasion_reward_allowances"], 1)
        player["troll_invasion_reward_month_index"] = 0
        player["troll_invasion_reward_allowances"] = 0
        self.assertEqual(troll_invasion_view_pure(player)["troll_invasion_reward_allowances"], 2)

        player["troll_invasion_reward_month_index"] = 4
        player["troll_invasion_reward_allowances"] = 0
        entered, ok, info = enter_troll_invasion_pure(player, {"mode": TROLL_INVASION_REPAIR_MODE})
        self.assertTrue(ok, info)
        left, ok, result = leave_troll_invasion_pure(entered)
        self.assertTrue(ok, result)
        self.assertFalse(result["book_awarded"])
        self.assertEqual(left["troll_invasion_attempts"], 1)

    def test_view_owns_every_panel_flag_and_hard_lock(self):
        idle = troll_invasion_view_pure(_player())
        self.assertTrue(idle["can_enter"])
        self.assertTrue(idle["primary_enabled"])
        self.assertFalse(idle["leave_visible"])
        self.assertFalse(idle["reward_visible"])
        hard = next(row for row in idle["difficulty_options"] if row["id"] == TROLL_INVASION_HARD)
        self.assertFalse(hard["unlocked"])
        self.assertFalse(hard["selectable"])

        active, ok, _ = enter_troll_invasion_pure(_player(), {"mode": TROLL_INVASION_REPAIR_MODE})
        self.assertTrue(ok)
        view = troll_invasion_view_pure(active)
        self.assertTrue(view["active"])
        self.assertFalse(view["policy_controls_enabled"])
        self.assertTrue(view["leave_visible"])
        self.assertFalse(view["difficulty_visible"])
        self.assertEqual(view["status_label"], "ACTIVE · SAFE")

        booked = _player()
        booked["inventory"][TROLL_INVASION_REWARD_BOOK] = 1
        booked["troll_invasion_reward_fractions"] = [1.0]
        booked, ok, info = enter_troll_invasion_pure(
            booked,
            {"mode": TROLL_INVASION_COMBAT_MODE, "difficulty": TROLL_INVASION_STANDARD},
        )
        self.assertTrue(ok, info)
        combat_view = troll_invasion_view_pure(booked)
        self.assertTrue(combat_view["reward_visible"])
        self.assertFalse(combat_view["reward_enabled"])
        self.assertEqual(
            [row["id"] for row in combat_view["difficulty_options"] if row["selectable"]],
            [TROLL_INVASION_STANDARD],
        )


class TrollInvasionPersistenceLayerTest(unittest.TestCase):
    def test_schema_91_migration_and_interrupted_session_round_trip(self):
        old = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        old["config_version"] = 90
        for key in default_troll_invasion_state_pure():
            old.pop(key, None)
        migrated = migrate_loaded_data(old, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(CURRENT_CONFIG_VERSION, 91)
        self.assertEqual(migrated["config_version"], 91)
        self.assertEqual(migrated["troll_invasion"], {})
        self.assertEqual(migrated["troll_invasion_policy"]["mode"], TROLL_INVASION_COMBAT_MODE)

        active, ok, info = enter_troll_invasion_pure(
            _player(), {"mode": TROLL_INVASION_COMBAT_MODE, "difficulty": TROLL_INVASION_STANDARD}
        )
        self.assertTrue(ok, info)
        active, ok, info = apply_troll_invasion_review_pure(active, random.Random(4).random, equipment_data=EQUIPMENT_DATA)
        self.assertTrue(ok, info)
        loaded = migrate_loaded_data(json.loads(json.dumps(active)), ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(loaded["activity_session"], {"active_id": TROLL_INVASION_ACTIVITY_ID})
        self.assertEqual(loaded["troll_invasion"]["wave"], active["troll_invasion"]["wave"])
        self.assertEqual(loaded["troll_invasion"]["enemy_lifepoints"], active["troll_invasion"]["enemy_lifepoints"])

    def test_sanitizer_clamps_corruption_and_drops_foreign_session(self):
        state = sanitize_troll_invasion_state_pure(
            {
                "activity_session": {"active_id": "clan_wars"},
                "troll_invasion": {"mode": TROLL_INVASION_REPAIR_MODE, "components": {"walls": -10}},
                "inventory": {TROLL_INVASION_REWARD_BOOK: 2},
                "troll_invasion_reward_allowances": 99,
                "troll_invasion_reward_fractions": [-1, 0.5, 9],
            }
        )
        self.assertEqual(state["troll_invasion"], {})
        self.assertEqual(state["troll_invasion_reward_allowances"], 2)
        self.assertEqual(state["troll_invasion_reward_fractions"], [0.5, 1.0])


class TrollInvasionRuntimeLayerTest(unittest.TestCase):
    def test_selected_repair_dispatches_through_runtime_and_persists(self):
        player, ok, info = enter_troll_invasion_pure(_player(), {"mode": TROLL_INVASION_REPAIR_MODE})
        self.assertTrue(ok, info)
        calls = {"errors": [], "activity": [], "xp": [], "saves": 0, "deactivated": False, "rng": random.Random(0).random}
        self.assertTrue(handle_utility_answer(_context(player, calls)))
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(player["troll_invasion"]["repair_actions"], 1)
        self.assertGreater(player["construction_exp"], 0)
        self.assertEqual(calls["xp"], [24.0])
        self.assertIn("Repaired", calls["activity"][-1])
        telemetry = player["action_telemetry"]["actions"][f"utility:{TROLL_INVASION_ACTIVITY_ID}"]
        self.assertEqual(telemetry["attempts"], 1)

    def test_repair_runtime_awards_all_three_skills_and_updates_levels(self):
        player, ok, info = enter_troll_invasion_pure(
            default_player_data(ORE_DATA, ITEM_DEFINITIONS),
            {"mode": TROLL_INVASION_REPAIR_MODE},
        )
        self.assertTrue(ok, info)
        calls = {"errors": [], "activity": [], "xp": [], "saves": 0, "deactivated": False, "rng": random.Random(14).random}
        ctx = _context(player, calls)
        ctx.review_action_multiplier = 3
        for _ in range(10):
            self.assertTrue(handle_utility_answer(ctx))
        for skill_id in ("construction", "crafting", "firemaking"):
            with self.subTest(skill=skill_id):
                self.assertGreater(player[f"{skill_id}_exp"], 0)
                self.assertGreater(player[f"{skill_id}_level"], 1)
        self.assertEqual(
            player["action_telemetry"]["actions"][f"utility:{TROLL_INVASION_ACTIVITY_ID}"]["attempts"],
            30,
        )

    def test_multiplier_repeats_repair_actions_but_never_spills_combat_into_next_wave(self):
        repair, ok, info = enter_troll_invasion_pure(_player(), {"mode": TROLL_INVASION_REPAIR_MODE})
        self.assertTrue(ok, info)
        calls = {"errors": [], "activity": [], "xp": [], "saves": 0, "deactivated": False, "rng": random.Random(0).random}
        ctx = _context(repair, calls)
        ctx.review_action_multiplier = 3
        self.assertTrue(handle_utility_answer(ctx))
        self.assertEqual(repair["troll_invasion"]["repair_actions"], 3)
        self.assertEqual(
            repair["action_telemetry"]["actions"][f"utility:{TROLL_INVASION_ACTIVITY_ID}"]["attempts"],
            3,
        )

        combat, ok, info = enter_troll_invasion_pure(
            _player(), {"mode": TROLL_INVASION_COMBAT_MODE, "difficulty": TROLL_INVASION_STANDARD}
        )
        self.assertTrue(ok, info)
        combat["troll_invasion"]["enemy_lifepoints"] = 1
        calls = {"errors": [], "activity": [], "xp": [], "saves": 0, "deactivated": False, "rng": lambda: 0.0}
        ctx = _context(combat, calls)
        ctx.review_action_multiplier = 3
        self.assertTrue(handle_utility_answer(ctx))
        self.assertEqual(combat["troll_invasion"]["waves_completed"], 1)
        self.assertEqual(combat["troll_invasion"]["wave"], 2)
        self.assertEqual(
            combat["action_telemetry"]["actions"][f"utility:{TROLL_INVASION_ACTIVITY_ID}"]["attempts"],
            1,
        )

    def test_again_records_a_non_productive_attempt_without_progress(self):
        player, ok, info = enter_troll_invasion_pure(
            _player(), {"mode": TROLL_INVASION_REPAIR_MODE}
        )
        self.assertTrue(ok, info)
        calls = {"errors": [], "activity": [], "xp": [], "saves": 0, "deactivated": False, "rng": random.Random(0).random}
        self.assertTrue(handle_troll_invasion_answer(_context(player, calls), productive=False))
        self.assertEqual(player["troll_invasion"]["repair_actions"], 0)
        telemetry = player["action_telemetry"]["actions"][
            f"utility:{TROLL_INVASION_ACTIVITY_ID}"
        ]
        self.assertEqual(telemetry["attempts"], 1)
        self.assertEqual(telemetry["successes"], 0)

    def test_unselected_activity_refuses_and_deactivates(self):
        player = _player(current_utility=TROLL_INVASION_ACTIVITY_ID)
        calls = {"errors": [], "activity": [], "xp": [], "saves": 0, "deactivated": False, "rng": random.Random(0).random}
        self.assertFalse(handle_utility_answer(_context(player, calls)))
        self.assertTrue(calls["deactivated"])
        self.assertIn("Troll Invasion unavailable", calls["errors"][0][0])


@unittest.skipUnless(QT_AVAILABLE, "offscreen Qt lane only")
class TrollInvasionQtLayerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_panel_renders_view_owned_controls_at_laptop_height(self):
        panel = TrollInvasionPanel(
            _player(),
            on_command=lambda *_args: {"ok": True},
            on_select=lambda _activity_id: True,
        )
        panel.show()
        panel.resize(520, 560)
        for _ in range(4):
            self.app.processEvents()
        self.assertGreater(panel.height(), 0)
        self.assertIsNotNone(panel.findChild(QComboBox, "trollInvasionModeCombo"))
        hard_combo = panel.findChild(QComboBox, "trollInvasionDifficultyCombo")
        self.assertEqual(hard_combo.count(), 1, "Hard must stay absent until Standard is attempted")
        self.assertFalse(panel.findChild(QPushButton, "trollInvasionLeaveButton").isVisible())
        self.assertFalse(panel.findChild(QPushButton, "trollInvasionRedeemButton").isVisible())
        panel.close()


class TrollInvasionCommandLayerTest(unittest.TestCase):
    def test_command_router_covers_every_direct_action(self):
        player = _player()
        planned, ok, info = apply_troll_invasion_command_pure(
            player,
            "set_policy",
            {"mode": TROLL_INVASION_REPAIR_MODE, "difficulty": TROLL_INVASION_STANDARD, "reward_skill": "mining"},
        )
        self.assertTrue(ok, info)
        entered, ok, info = apply_troll_invasion_command_pure(planned, "enter", {})
        self.assertTrue(ok, info)
        left, ok, info = apply_troll_invasion_command_pure(entered, "leave", {})
        self.assertTrue(ok, info)
        _, ok, info = apply_troll_invasion_command_pure(left, "collapse_gatehouse", {})
        self.assertFalse(ok)
        self.assertIn("Unknown", info["reason"])


if __name__ == "__main__":
    unittest.main()
