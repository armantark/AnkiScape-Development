from __future__ import annotations

import copy
import unittest
from pathlib import Path
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, UTILITY_ACTIVITY_DATA
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from ankiscape.data.dagannoth_kings_data import (
    DAGANNOTH_KING_IDS,
    DAGANNOTH_KINGS_ENEMY_DATA,
    DAGANNOTH_KINGS_RESPAWN_TICKS,
)
from ankiscape.data.slayer_data import SLAYER_FAMILIES_BY_ID
from ankiscape.logic.dagannoth_kings_logic import (
    apply_dagannoth_kings_command_pure,
    apply_dagannoth_kings_review_pure,
    dagannoth_kings_view_pure,
)
from ankiscape.runtime.runtime_actions import RuntimeActionContext, handle_utility_answer


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
            "combat_lifepoints": 800,
            "combat_prayer_points": 800,
            "combat_auto_eat_food": [],
            "combat_auto_flee": False,
            "inventory": {"Shark": 4},
            "current_combat_target": "chicken",
        }
    )
    data.update(overrides)
    return data


def _entered(**overrides):
    data, ok, info = apply_dagannoth_kings_command_pure(
        _player(**overrides), "enter"
    )
    assert ok, info
    data["current_utility"] = "dagannoth_kings"
    return data


def _combat_result(*, killed=False, died=False, lifepoints=None):
    def _apply(data, enemies, _equipment, **kwargs):
        updated = copy.deepcopy(data)
        before = int(updated["combat_encounter"]["enemy_lifepoints"])
        after = 0 if killed else int(lifepoints if lifepoints is not None else before)
        updated["combat_encounter"]["enemy_lifepoints"] = max(0, after)
        if died:
            updated["combat_encounter"] = {}
        return updated, True, {
            "killed": killed,
            "died": died,
            "fled": False,
            "enemy_lifepoints": after,
            "xp_rewards": {"attack_exp": 4.0} if killed else {},
            "drops": {"Dragon hatchet": 1} if killed else {},
            "target_id": next(iter(enemies)),
            "ticks_requested": kwargs.get("ticks"),
        }

    return _apply


class DagannothKingsDataTests(unittest.TestCase):
    def test_minimum_room_data_and_period_assets_are_registered(self):
        self.assertEqual(DAGANNOTH_KING_IDS, (
            "dagannoth_prime",
            "dagannoth_supreme",
            "dagannoth_rex",
        ))
        self.assertEqual(
            [DAGANNOTH_KINGS_ENEMY_DATA[key]["attack_style"] for key in DAGANNOTH_KING_IDS],
            ["magic", "ranged", "melee"],
        )
        self.assertEqual(
            [DAGANNOTH_KINGS_ENEMY_DATA[key]["max_hit"] for key in DAGANNOTH_KING_IDS],
            [610, 300, 280],
        )
        self.assertEqual(DAGANNOTH_KINGS_RESPAWN_TICKS, 59)
        for enemy_id in DAGANNOTH_KING_IDS:
            drops = DAGANNOTH_KINGS_ENEMY_DATA[enemy_id]["drops"]
            self.assertEqual(drops["guaranteed"], (
                ("Dagannoth bones", 1),
                ("Dagannoth hide", 1),
            ))
            self.assertEqual(drops["tables"][0]["total"], 128)
            self.assertEqual(drops["tables"][0]["slots"][0]["item"], "Dragon hatchet")
            self.assertTrue(Path(f"combatenemies/{enemy_id}.png").is_file())

        activity = UTILITY_ACTIVITY_DATA["dagannoth_kings"]
        self.assertEqual(activity["outputs"]["Dragon hatchet"], 1)
        self.assertTrue(Path(activity["icon_path"]).is_file())
        family = SLAYER_FAMILIES_BY_ID["dagannoths"]
        self.assertTrue(set(DAGANNOTH_KING_IDS).issubset(family.target_ids))


class DagannothKingsCommandTests(unittest.TestCase):
    def test_entry_resume_mode_target_and_leave_are_persistent(self):
        original = _player()
        original_snapshot = copy.deepcopy(original)
        entered, ok, info = apply_dagannoth_kings_command_pure(original, "enter")
        self.assertTrue(ok, info)
        self.assertEqual(original, original_snapshot)
        self.assertFalse(original["dagannoth_kings"]["active"])
        self.assertEqual(entered["activity_session"], {"active_id": "dagannoth_kings"})
        self.assertEqual(len(entered["dagannoth_kings"]["roster"]), 3)
        self.assertEqual(
            dagannoth_kings_view_pure(entered)["roster_view"][0]["enemy_id"],
            "dagannoth_prime",
        )

        resumed, ok, info = apply_dagannoth_kings_command_pure(entered, "enter")
        self.assertTrue(ok, info)
        self.assertEqual(resumed["dagannoth_kings"]["trips"], 1)

        advanced, ok, info = apply_dagannoth_kings_command_pure(
            resumed, "set_mode", {"automation_mode": "advanced"}
        )
        self.assertTrue(ok, info)
        selected, ok, info = apply_dagannoth_kings_command_pure(
            advanced, "select_target", {"enemy_id": "dagannoth_rex"}
        )
        self.assertTrue(ok, info)
        self.assertEqual(selected["dagannoth_kings"]["engaged_enemy_id"], "dagannoth_rex")

        left, ok, info = apply_dagannoth_kings_command_pure(selected, "leave")
        self.assertTrue(ok, info)
        self.assertFalse(left["dagannoth_kings"]["active"])
        self.assertEqual(left["activity_session"], {"active_id": ""})
        self.assertEqual(left["current_combat_target"], "chicken")

    def test_competing_persistent_activity_blocks_entry(self):
        data = _player(activity_session={"active_id": "fight_caves"})
        unchanged, ok, info = apply_dagannoth_kings_command_pure(data, "enter")
        self.assertFalse(ok)
        self.assertIn("Another persistent activity", info["reason"])
        self.assertEqual(unchanged, data)

    def test_leave_restores_an_empty_prior_combat_target(self):
        entered, ok, info = apply_dagannoth_kings_command_pure(
            _player(current_combat_target=""), "enter"
        )
        self.assertTrue(ok, info)
        entered["current_combat_target"] = "dagannoth_prime"

        left, ok, info = apply_dagannoth_kings_command_pure(entered, "leave")

        self.assertTrue(ok, info)
        self.assertEqual(left["current_combat_target"], "")


class DagannothKingsMechanicsTests(unittest.TestCase):
    def test_real_combat_engine_kill_awards_minimum_room_drops(self):
        data = _entered(
            attack_level=99,
            strength_level=99,
            defense_level=99,
            ranged_level=99,
            magic_level=99,
            constitution_level=99,
            combat_lifepoints=990,
            inventory={},
        )
        prime = data["dagannoth_kings"]["roster"][0]
        prime["lifepoints"] = 1
        prime["encounter"]["enemy_lifepoints"] = 1

        updated, ok, result = apply_dagannoth_kings_review_pure(
            data, lambda: 0.0
        )

        self.assertTrue(ok, result)
        self.assertTrue(result["killed"])
        self.assertEqual(result["drops"], {
            "Dagannoth bones": 1,
            "Dagannoth hide": 1,
            "Dragon hatchet": 1,
        })
        self.assertEqual(updated["inventory"]["Dragon hatchet"], 1)
        self.assertEqual(updated.get("combat_bank_run", {}), {})

    @patch(
        "ankiscape.logic.boss_room_logic.combat_enemy_pressure_attack_pure",
        return_value={"damage": 0, "attack_style": "melee"},
    )
    @patch(
        "ankiscape.logic.boss_room_logic.apply_combat_burst_pure",
        side_effect=_combat_result(killed=True),
    )
    def test_casual_engages_prime_then_tracks_kill_and_review_respawn(
        self, combat, pressure
    ):
        data, ok, result = apply_dagannoth_kings_review_pure(
            _entered(), lambda: 0.5
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["engaged_enemy_id"], "dagannoth_prime")
        self.assertEqual(combat.call_args.kwargs["ticks"], 6)
        self.assertFalse(combat.call_args.kwargs["safe_death"])
        self.assertEqual(pressure.call_count, 2)
        state = data["dagannoth_kings"]
        self.assertEqual(state["trip_kills"], 1)
        self.assertEqual(state["kill_counts"], {"dagannoth_prime": 1})
        prime = next(row for row in state["roster"] if row["enemy_id"] == "dagannoth_prime")
        self.assertEqual(prime["lifepoints"], 0)
        self.assertEqual(prime["respawn_ticks"], 59)

        for row in state["roster"]:
            row["lifepoints"] = 0
            row["respawn_ticks"] = 59
            row["encounter"] = {}
        with patch(
            "ankiscape.logic.boss_room_logic.apply_combat_burst_pure",
            side_effect=_combat_result(lifepoints=2500),
        ) as respawn_combat:
            for _ in range(9):
                data, ok, result = apply_dagannoth_kings_review_pure(
                    data, lambda: 0.5
                )
                self.assertTrue(ok, result)
            self.assertEqual(respawn_combat.call_count, 0)
            data, ok, result = apply_dagannoth_kings_review_pure(
                data, lambda: 0.5
            )
            self.assertTrue(ok, result)
            self.assertEqual(respawn_combat.call_count, 1)
            self.assertEqual(set(result["respawned"]), set(DAGANNOTH_KING_IDS))

    @patch(
        "ankiscape.logic.boss_room_logic.combat_enemy_pressure_attack_pure",
        return_value={"damage": 40, "attack_style": "ranged"},
    )
    @patch(
        "ankiscape.logic.boss_room_logic.apply_combat_burst_pure",
        side_effect=_combat_result(lifepoints=2500),
    )
    def test_roster_pressure_uses_dangerous_death_and_ends_the_trip(
        self, _combat, _pressure
    ):
        def _die(data, damage, **kwargs):
            updated = copy.deepcopy(data)
            updated["combat_lifepoints"] = 0
            return updated, {"damage": damage, "died": True, "food_used": None}

        with patch(
            "ankiscape.logic.boss_room_logic.apply_thieving_damage_pure",
            side_effect=_die,
        ) as damage:
            updated, ok, result = apply_dagannoth_kings_review_pure(
                _entered(), lambda: 0.5
            )
        self.assertTrue(ok, result)
        self.assertTrue(result["died"])
        self.assertFalse(updated["dagannoth_kings"]["active"])
        self.assertFalse(damage.call_args.kwargs["safe_death"])


class DagannothKingsStorageAndRuntimeTests(unittest.TestCase):
    def test_migration_repairs_state_and_activity_session(self):
        raw = _player()
        raw["dagannoth_kings"] = {
            "active": True,
            "roster": [
                {
                    "enemy_id": "dagannoth_prime",
                    "lifepoints": 99999,
                    "respawn_ticks": -5,
                },
                {"enemy_id": "not_a_king", "lifepoints": 50},
            ],
            "automation_mode": "invalid",
        }
        migrated = migrate_loaded_data(raw, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(migrated["activity_session"], {"active_id": "dagannoth_kings"})
        self.assertEqual(migrated["dagannoth_kings"]["automation_mode"], "casual")
        self.assertEqual(len(migrated["dagannoth_kings"]["roster"]), 3)
        self.assertEqual(
            migrated["dagannoth_kings"]["roster"][0]["lifepoints"], 2550
        )

    def test_runtime_dispatch_records_and_persists_one_room_review(self):
        player = _entered()
        saved = []
        gains = []
        deactivated = []
        ctx = RuntimeActionContext(
            player_data=player,
            random_random=lambda: 0.5,
            show_error_message=lambda *_args: self.fail("unexpected runtime error"),
            deactivate_current_skill=lambda: deactivated.append(True),
            award_skill_exp=lambda *_args: self.fail("combat reducer owns its XP"),
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
        updated = copy.deepcopy(player)
        updated["dagannoth_kings"]["last_result"] = "Prime review complete"
        with patch(
            "ankiscape.runtime.runtime_actions_activities.apply_dagannoth_kings_review_pure",
            return_value=(
                updated,
                True,
                {"status": "Prime review complete", "xp_rewards": {"ranged_exp": 4.0}},
            ),
        ):
            self.assertTrue(handle_utility_answer(ctx))
        self.assertEqual(saved, [True])
        self.assertEqual(deactivated, [])
        self.assertIn("Prime review complete", gains)


if __name__ == "__main__":
    unittest.main()
