from __future__ import annotations

import copy
import unittest
from unittest.mock import patch

from shades_of_mortton_data import (
    SHADES_LOAR_PRAYER_XP,
    SHADES_PYRE_LOGS,
    SHADES_OF_MORTTON_COMBAT_TARGET_ID,
    shades_of_mortton_activity_as_dict,
    shades_of_mortton_loar_enemy_pure,
)
from shades_of_mortton_logic import (
    apply_shades_of_mortton_command_pure,
    apply_shades_of_mortton_review_pure,
    bless_shades_item_pure,
    enter_shades_of_mortton_pure,
    leave_shades_of_mortton_pure,
    light_shades_altar_pure,
    make_shades_pyre_logs_pure,
    open_shades_bronze_chest_pure,
    sanitize_shades_of_mortton_state_pure,
    set_shades_of_mortton_policy_pure,
    shades_of_mortton_view_pure,
)


def _player(**overrides):
    player = {
        "quests": {"shades_of_mortton": {"completed": True}},
        "activity_session": {"active_id": ""},
        "inventory": {},
        "firemaking_level": 80,
        "combat_lifepoints": 500,
        "hitpoints_level": 50,
    }
    player.update(overrides)
    return player


def _entered(**overrides):
    player, ok, info = enter_shades_of_mortton_pure(_player(**overrides))
    assert ok, info
    return player


def _combat_stub(*, killed=False, enemy_lifepoints=200):
    def run(player_data, enemy_data, equipment_data, **kwargs):
        updated = copy.deepcopy(player_data)
        assert kwargs["ticks"] == 6
        assert kwargs["live_cadence"]
        assert kwargs["stop_after_first_kill"]
        assert not kwargs["safe_death"]
        assert kwargs["allow_bank_run"]
        assert enemy_data[SHADES_OF_MORTTON_COMBAT_TARGET_ID]["stats"]["hitpoints"] == 380
        updated["combat_encounter"] = (
            {} if killed else {
                "target_id": SHADES_OF_MORTTON_COMBAT_TARGET_ID,
                "enemy_lifepoints": enemy_lifepoints,
            }
        )
        if killed:
            inventory = dict(updated.get("inventory", {}))
            inventory["Loar remains"] = inventory.get("Loar remains", 0) + 1
            updated["inventory"] = inventory
        return updated, True, {
            "reason": "combat_burst",
            "ticks": 6,
            "killed": killed,
            "enemy_lifepoints": 0 if killed else enemy_lifepoints,
            "died": False,
        }

    return run


class ShadesOfMorttonSourceDataTests(unittest.TestCase):
    def test_horizontal_registry_and_loar_enemy_are_period_shaped(self):
        activity = shades_of_mortton_activity_as_dict()["shades_of_mortton"]
        self.assertEqual(activity["requirements"], {"quest": "shades_of_mortton"})
        self.assertIn("Fine cloth", activity["outputs"])
        enemy = shades_of_mortton_loar_enemy_pure()
        self.assertEqual(enemy["level"], 40)
        self.assertEqual(enemy["stats"]["hitpoints"], 380)
        self.assertEqual(enemy["max_hit"], 40)

    def test_all_easy_to_harvest_pyre_rows_are_recorded(self):
        self.assertEqual(len(SHADES_PYRE_LOGS), 10)
        self.assertEqual(SHADES_PYRE_LOGS["Pyre logs"]["oil_doses"], 2)
        self.assertEqual(SHADES_PYRE_LOGS["Magic pyre logs"]["level"], 80)
        self.assertEqual(SHADES_PYRE_LOGS["Pyre logs"]["creation_xp"], 12.0)
        self.assertEqual(SHADES_PYRE_LOGS["Magic pyre logs"]["creation_xp"], 16.0)
        self.assertEqual(SHADES_PYRE_LOGS["Magic pyre logs"]["cremation_xp"], 404.5)
        self.assertEqual(SHADES_LOAR_PRAYER_XP["Pyre logs"], 25.0)
        self.assertEqual(SHADES_LOAR_PRAYER_XP["Magic pyre logs"], 35.0)


class ShadesOfMorttonEntryAndPersistenceTests(unittest.TestCase):
    def test_entry_requires_the_quest_and_a_free_persistent_activity_slot(self):
        for player, expected in (
            (_player(quests={}), "Complete Shades"),
            (_player(activity_session={"active_id": "barrows"}), "persistent activity"),
            (_player(combat_encounter={"target_id": "rat"}), "Combat encounter"),
        ):
            with self.subTest(expected=expected):
                _unchanged, ok, info = enter_shades_of_mortton_pure(player)
                self.assertFalse(ok)
                self.assertIn(expected, info["reason"])

    def test_open_loop_leave_preserves_communal_and_personal_meters(self):
        player = _entered()
        player["shades_of_mortton"].update(
            {"temple_repair": 73, "sanctity_tenths": 420, "resources": 4}
        )
        player, ok, info = leave_shades_of_mortton_pure(player)
        self.assertTrue(ok, info)
        self.assertFalse(player["shades_of_mortton"]["active"])
        self.assertEqual(player["shades_of_mortton"]["temple_repair"], 73)
        self.assertEqual(player["shades_of_mortton"]["sanctity_tenths"], 420)
        self.assertEqual(player["activity_session"], {"active_id": ""})

    def test_sanitizer_clamps_malformed_state_without_touching_other_data(self):
        malformed = _player(
            shades_of_mortton={
                "active": True,
                "temple_repair": 999,
                "sanctity_tenths": -5,
                "resources": 500,
                "altar_lit": True,
                "sanctity_decay_progress": 99,
            },
            activity_session={"active_id": "shades_of_mortton"},
            unrelated={"kept": True},
        )
        state = sanitize_shades_of_mortton_state_pure(malformed)["shades_of_mortton"]
        self.assertEqual(state["temple_repair"], 100)
        self.assertEqual(state["sanctity_tenths"], 0)
        self.assertEqual(state["resources"], 100)
        self.assertEqual(state["sanctity_decay_progress"], 9)
        self.assertEqual(malformed["unrelated"], {"kept": True})


class ShadesOfMorttonRepairAndPopulationTests(unittest.TestCase):
    def test_repair_consumes_one_source_pack_then_one_resource_on_success(self):
        player = _entered(
            inventory={
                "Timber beam": 1,
                "Limestone brick": 1,
                "Swamp paste": 5,
                "Hammer": 1,
            }
        )
        rolls = iter((0.0, 0.0))
        player, ok, result = apply_shades_of_mortton_review_pure(
            player, lambda: next(rolls), population="quiet"
        )
        self.assertTrue(ok, result)
        self.assertTrue(result["success"])
        self.assertEqual(result["skill_xp"], {"crafting": 20.0})
        self.assertEqual(player["shades_of_mortton"]["resources"], 4)
        self.assertEqual(player["shades_of_mortton"]["temple_repair"], 4)
        self.assertEqual(player["shades_of_mortton"]["sanctity_tenths"], 50)
        self.assertEqual(player["inventory"], {"Hammer": 1})

    def test_failed_repair_grants_small_xp_without_spending_a_resource(self):
        player = _entered(inventory={"Hammer": 1})
        player["shades_of_mortton"]["resources"] = 3
        rolls = iter((0.9, 0.99))
        player, ok, result = apply_shades_of_mortton_review_pure(
            player, lambda: next(rolls), population="quiet"
        )
        self.assertTrue(ok, result)
        self.assertFalse(result["success"])
        self.assertEqual(result["skill_xp"], {"crafting": 9.0})
        self.assertEqual(player["shades_of_mortton"]["resources"], 3)
        self.assertEqual(player["shades_of_mortton"]["sanctity_tenths"], 0)

    def test_missing_hammer_does_not_consume_a_resource_pack(self):
        inventory = {"Timber beam": 1, "Limestone brick": 1, "Swamp paste": 5}
        player = _entered(inventory=inventory)
        player, ok, result = apply_shades_of_mortton_review_pure(
            player, population="quiet"
        )
        self.assertTrue(ok, result)
        self.assertTrue(result["blocked"])
        self.assertEqual(player["inventory"], inventory)
        self.assertEqual(player["shades_of_mortton"]["resources"], 0)

    def test_crowd_moves_only_communal_repair_and_never_personal_rewards(self):
        player = _entered()
        player["shades_of_mortton"]["temple_repair"] = 50
        before_inventory = dict(player["inventory"])
        player, ok, result = apply_shades_of_mortton_review_pure(
            player, productive=False, population="busy"
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["communal_repair_delta"], 1)
        self.assertEqual(player["shades_of_mortton"]["temple_repair"], 51)
        self.assertEqual(player["shades_of_mortton"]["sanctity_tenths"], 0)
        self.assertEqual(player["inventory"], before_inventory)

    def test_sanctity_decay_uses_review_progress_only_while_active(self):
        player = _entered()
        player["shades_of_mortton"]["sanctity_tenths"] = 100
        for _ in range(10):
            player, ok, _result = apply_shades_of_mortton_review_pure(
                player, productive=False, population="normal"
            )
            self.assertTrue(ok)
        self.assertEqual(player["shades_of_mortton"]["sanctity_tenths"], 90)
        left, ok, _info = leave_shades_of_mortton_pure(player)
        self.assertTrue(ok)
        unchanged, ok, _result = apply_shades_of_mortton_review_pure(
            left, productive=False
        )
        self.assertFalse(ok)
        self.assertEqual(unchanged["shades_of_mortton"]["sanctity_tenths"], 90)


class ShadesOfMorttonCombatTests(unittest.TestCase):
    def test_loar_combat_is_one_live_six_tick_slice_and_kill_grants_only_player_rewards(self):
        player, ok, info = set_shades_of_mortton_policy_pure(
            _player(), {"automation_mode": "advanced", "duty": "combat"}
        )
        self.assertTrue(ok, info)
        player, ok, info = enter_shades_of_mortton_pure(player)
        self.assertTrue(ok, info)
        with patch("shades_of_mortton_logic.apply_combat_burst_pure", _combat_stub(killed=True)):
            player, ok, result = apply_shades_of_mortton_review_pure(player)
        self.assertTrue(ok, result)
        self.assertTrue(result["killed"])
        self.assertEqual(player["inventory"]["Loar remains"], 1)
        self.assertEqual(player["shades_of_mortton"]["sanctity_tenths"], 20)
        self.assertEqual(player["shades_of_mortton"]["encounter"], {})

    def test_unfinished_loar_encounter_persists_between_reviews(self):
        player = _entered()
        with patch("shades_of_mortton_logic.apply_combat_burst_pure", _combat_stub(enemy_lifepoints=177)):
            player, ok, result = apply_shades_of_mortton_review_pure(player)
        self.assertTrue(ok, result)
        self.assertEqual(player["shades_of_mortton"]["encounter"]["enemy_lifepoints"], 177)


class ShadesOfMorttonProductionTests(unittest.TestCase):
    def _altar_ready(self, *, sanctity=500, inventory=None):
        player = _entered(inventory=inventory or {"Tinderbox": 1})
        player["shades_of_mortton"].update(
            {"temple_repair": 99, "sanctity_tenths": sanctity}
        )
        return player

    def test_altar_has_a_provisional_failure_roll_and_pays_xp_once_when_lit(self):
        player = self._altar_ready()
        failed, ok, result = light_shades_altar_pure(player, lambda: 0.9)
        self.assertTrue(ok, result)
        self.assertFalse(failed["shades_of_mortton"]["altar_lit"])
        self.assertEqual(result["skill_xp"], {})
        lit, ok, result = light_shades_altar_pure(player, lambda: 0.0)
        self.assertTrue(ok, result)
        self.assertTrue(lit["shades_of_mortton"]["altar_lit"])
        self.assertEqual(result["skill_xp"], {"firemaking": 100.0})
        _same, ok, result = light_shades_altar_pure(lit, lambda: 0.0)
        self.assertFalse(ok)
        self.assertIn("already lit", result["reason"])

    def test_oil_requires_more_than_ten_percent_and_uses_point_nine_per_dose(self):
        player = self._altar_ready(
            sanctity=100, inventory={"Tinderbox": 1, "Olive oil (4)": 1}
        )
        player["shades_of_mortton"]["altar_lit"] = True
        _unchanged, ok, info = bless_shades_item_pure(player, "Olive oil (4)")
        self.assertFalse(ok)
        self.assertIn("10.1%", info["reason"])
        player["shades_of_mortton"]["sanctity_tenths"] = 101
        player, ok, result = bless_shades_item_pure(player, "Olive oil (4)")
        self.assertTrue(ok, result)
        self.assertEqual(player["shades_of_mortton"]["sanctity_tenths"], 65)
        self.assertNotIn("Olive oil (4)", player["inventory"])
        self.assertEqual(player["inventory"]["Sacred oil (4)"], 1)

    def test_serum_208_requires_twenty_percent_and_costs_twenty_percent(self):
        player = self._altar_ready(
            sanctity=200, inventory={"Tinderbox": 1, "Serum 207 (4)": 1}
        )
        player["shades_of_mortton"]["altar_lit"] = True
        player, ok, result = bless_shades_item_pure(player, "Serum 207 (4)")
        self.assertTrue(ok, result)
        self.assertEqual(player["shades_of_mortton"]["sanctity_tenths"], 0)
        self.assertEqual(player["inventory"]["Serum 208 (4)"], 1)

    def test_pyre_log_production_preserves_remaining_doses_and_exact_xp(self):
        player = _player(inventory={"Logs": 1, "Sacred oil (4)": 1})
        player, ok, result = make_shades_pyre_logs_pure(player, "Pyre logs")
        self.assertTrue(ok, result)
        self.assertEqual(result["skill_xp"], {"firemaking": 12.0})
        self.assertEqual(player["inventory"]["Pyre logs"], 1)
        self.assertEqual(player["inventory"]["Sacred oil (2)"], 1)
        self.assertNotIn("Logs", player["inventory"])

    def test_pyre_log_production_can_combine_multiple_nonstackable_oil_vials(self):
        player = _player(inventory={"Logs": 1, "Sacred oil (1)": 2})
        player, ok, result = make_shades_pyre_logs_pure(player, "Pyre logs")
        self.assertTrue(ok, result)
        self.assertEqual(player["inventory"]["Pyre logs"], 1)
        self.assertEqual(player["inventory"]["Vial"], 2)
        self.assertNotIn("Sacred oil (1)", player["inventory"])


class ShadesOfMorttonCremationAndChestTests(unittest.TestCase):
    def _cremator(self):
        player, ok, info = set_shades_of_mortton_policy_pure(
            _player(inventory={"Pyre logs": 1, "Loar remains": 1}),
            {"automation_mode": "advanced", "duty": "cremate"},
        )
        self.assertTrue(ok, info)
        player, ok, info = enter_shades_of_mortton_pure(player)
        self.assertTrue(ok, info)
        return player

    def test_cremation_consumes_both_inputs_and_can_award_a_low_bronze_key(self):
        player = self._cremator()
        rolls = iter((0.0, 0.0))
        player, ok, result = apply_shades_of_mortton_review_pure(
            player, lambda: next(rolls), population="normal"
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["skill_xp"], {"firemaking": 50.0, "prayer": 25.0})
        self.assertEqual(player["inventory"]["Bronze key red"], 1)
        self.assertNotIn("Pyre logs", player["inventory"])
        self.assertNotIn("Loar remains", player["inventory"])

    def test_cremation_coin_branch_stays_within_the_period_range(self):
        player = self._cremator()
        rolls = iter((0.9, 0.999))
        player, ok, result = apply_shades_of_mortton_review_pure(
            player, lambda: next(rolls)
        )
        self.assertTrue(ok, result)
        self.assertEqual(player["inventory"]["Coins"], 500)

    def test_bronze_chest_is_direct_consumes_key_and_returns_representative_outputs(self):
        player = _player(inventory={"Bronze key red": 1})
        rolls = iter((0.0, 0.999, 0.0, 0.0))
        player, ok, result = open_shades_bronze_chest_pure(
            player, "Bronze key red", lambda: next(rolls)
        )
        self.assertTrue(ok, result)
        self.assertNotIn("Bronze key red", player["inventory"])
        self.assertEqual(result["rewards"], {"Coins": 10, "Fine cloth": 1, "Swamp paste": 10})
        self.assertEqual(player["shades_of_mortton_chests_opened"], 1)

    def test_bronze_chest_requires_the_completed_quest(self):
        player = _player(quests={}, inventory={"Bronze key red": 1})
        unchanged, ok, result = open_shades_bronze_chest_pure(
            player, "Bronze key red"
        )
        self.assertFalse(ok)
        self.assertIn("Complete Shades", result["reason"])
        self.assertEqual(unchanged["inventory"], {"Bronze key red": 1})

    def test_command_router_and_view_expose_the_open_loop_without_mutation(self):
        player, ok, result = apply_shades_of_mortton_command_pure(
            _player(), "enter", {"automation_mode": "advanced", "duty": "combat"}
        )
        self.assertTrue(ok, result)
        view = shades_of_mortton_view_pure(player)
        self.assertTrue(view["active"])
        self.assertEqual(view["policy"]["duty"], "combat")
        unknown, ok, result = apply_shades_of_mortton_command_pure(player, "wat")
        self.assertFalse(ok)
        self.assertEqual(unknown, player)
        self.assertIn("Unknown", result["reason"])


if __name__ == "__main__":
    unittest.main()
