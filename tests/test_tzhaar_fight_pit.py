import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.equipment_data import EQUIPMENT_DATA
from ankiscape.logic.tzhaar_fight_pit_logic import (
    apply_tzhaar_fight_pit_review_pure,
    enter_tzhaar_fight_pit_pure,
    leave_tzhaar_fight_pit_pure,
    sanitize_tzhaar_fight_pit_state_pure,
    set_tzhaar_fight_pit_policy_pure,
)
from ankiscape.runtime.runtime_actions_activities import handle_tzhaar_fight_pit_answer
from tests.test_runtime_actions import _context


def player(**changes):
    data = {
        "attack_level": 60,
        "strength_level": 60,
        "defense_level": 60,
        "constitution_level": 60,
        "ranged_level": 1,
        "magic_level": 1,
        "prayer_level": 43,
        "summoning_level": 1,
        "combat_lifepoints": 600,
        "inventory": {},
        "equipment": {},
        "activity_session": {"active_id": ""},
        "combat_encounter": {},
        "current_combat_target": "chicken",
    }
    data.update(changes)
    return data


class FightPitPureTest(unittest.TestCase):
    def test_entry_persists_three_bounded_opponents(self):
        updated, ok, _ = enter_tzhaar_fight_pit_pure(player())
        self.assertTrue(ok)
        session = updated["tzhaar_fight_pit"]
        self.assertEqual(len(session["roster"]), 3)
        self.assertEqual(updated["activity_session"]["active_id"], "tzhaar_fight_pit")
        self.assertEqual(updated["current_combat_target"], "tzhaar_fight_pit_opponent")
        self.assertTrue(all(3 <= row["combat_level"] <= 138 for row in session["roster"]))

    def test_player_kill_adds_exact_combat_level(self):
        entered, _, _ = enter_tzhaar_fight_pit_pure(player())
        engaged = entered["tzhaar_fight_pit"]["engaged_opponent_id"]
        victim = next(row for row in entered["tzhaar_fight_pit"]["roster"] if row["opponent_id"] == engaged)
        combat_result = ({**entered, "combat_encounter": {}}, True, {"killed": True, "died": False, "ticks_elapsed": 1})
        with patch("ankiscape.logic.tzhaar_fight_pit_logic.apply_combat_burst_pure", return_value=combat_result):
            updated, ok, result = apply_tzhaar_fight_pit_review_pure(entered)
        self.assertTrue(ok)
        self.assertEqual(updated["tzhaar_fight_pit"]["pending_tokkul"], victim["combat_level"])
        self.assertEqual(result["player_kill"]["opponent_id"], victim["opponent_id"])

    def test_advanced_policy_is_saved_before_entry_and_selects_strongest(self):
        planned, ok, _ = set_tzhaar_fight_pit_policy_pure(player(), "aggressive")
        self.assertTrue(ok)
        entered, ok, _ = enter_tzhaar_fight_pit_pure(planned)
        self.assertTrue(ok)
        session = entered["tzhaar_fight_pit"]
        engaged = next(
            row for row in session["roster"]
            if row["opponent_id"] == session["engaged_opponent_id"]
        )
        self.assertEqual(
            engaged["combat_level"],
            max(row["combat_level"] for row in session["roster"]),
        )

    def test_other_opponent_attrition_never_inflates_pending_tokkul(self):
        entered, _, _ = enter_tzhaar_fight_pit_pure(player())
        session = entered["tzhaar_fight_pit"]
        for row in session["roster"]:
            if row["opponent_id"] != session["engaged_opponent_id"]:
                row["lifepoints"] = 1
        combat_result = (
            {**entered, "combat_encounter": {"enemy_lifepoints": 100}},
            True,
            {"killed": False, "died": False, "ticks_elapsed": 6},
        )
        with patch("ankiscape.logic.tzhaar_fight_pit_logic.apply_combat_burst_pure", return_value=combat_result):
            updated, ok, result = apply_tzhaar_fight_pit_review_pure(entered)
        self.assertTrue(ok)
        self.assertEqual(updated["tzhaar_fight_pit"]["pending_tokkul"], 0)
        self.assertEqual(len(result["other_eliminated"]), 2)

    def test_last_standing_settles_sum_and_fire_cape_double(self):
        entered, _, _ = enter_tzhaar_fight_pit_pure(player(equipment={"cape": "Fire cape"}))
        session = entered["tzhaar_fight_pit"]
        victim = session["roster"][0]
        session["roster"] = [victim]
        session["engaged_opponent_id"] = victim["opponent_id"]
        session["pending_tokkul"] = 100
        combat_result = ({**entered, "combat_encounter": {}}, True, {"killed": True, "died": False, "ticks_elapsed": 1})
        with patch("ankiscape.logic.tzhaar_fight_pit_logic.apply_combat_burst_pure", return_value=combat_result):
            updated, ok, result = apply_tzhaar_fight_pit_review_pure(entered)
        expected = (100 + victim["combat_level"]) * 2
        self.assertTrue(ok)
        self.assertEqual(result["tokkul"], expected)
        self.assertEqual(updated["inventory"]["Tokkul"], expected)
        self.assertEqual(updated["tzhaar_fight_pit_wins"], 1)
        self.assertEqual(updated["tzhaar_fight_pit"], {})

    def test_safe_defeat_preserves_items_and_restores_resources(self):
        entered, _, _ = enter_tzhaar_fight_pit_pure(player(inventory={"Coins": 10}))
        defeated = {**entered, "combat_lifepoints": 600, "combat_encounter": {}}
        combat_result = (defeated, True, {"killed": False, "died": True, "ticks_elapsed": 1})
        with patch("ankiscape.logic.tzhaar_fight_pit_logic.apply_combat_burst_pure", return_value=combat_result):
            updated, ok, result = apply_tzhaar_fight_pit_review_pure(entered)
        self.assertTrue(ok)
        self.assertEqual(result["outcome"], "loss")
        self.assertEqual(updated["inventory"], {"Coins": 10})
        self.assertEqual(updated["combat_lifepoints"], 600)
        self.assertEqual(updated["current_combat_target"], "chicken")

    def test_leave_forfeits_pending_purse(self):
        entered, _, _ = enter_tzhaar_fight_pit_pure(player())
        entered["tzhaar_fight_pit"]["pending_tokkul"] = 90
        updated, ok, result = leave_tzhaar_fight_pit_pure(entered)
        self.assertTrue(ok)
        self.assertEqual(result["forfeited_tokkul"], 90)
        self.assertNotIn("Tokkul", updated["inventory"])
        self.assertEqual(updated["tzhaar_fight_pit_forfeits"], 1)

    def test_sanitizer_drops_cross_activity_session(self):
        entered, _, _ = enter_tzhaar_fight_pit_pure(player())
        entered["activity_session"] = {"active_id": "castle_wars"}
        self.assertEqual(sanitize_tzhaar_fight_pit_state_pure(entered)["tzhaar_fight_pit"], {})

    def test_entry_conflict_is_atomic(self):
        original = player(activity_session={"active_id": "castle_wars"})
        updated, ok, result = enter_tzhaar_fight_pit_pure(original)
        self.assertFalse(ok)
        self.assertEqual(updated, original)
        self.assertIn("persistent activity", result["reason"])

    def test_entry_rejects_a_loaded_multicannon_pack(self):
        original = player(combat_supply_loadout={"cannonballs": 10})
        updated, ok, result = enter_tzhaar_fight_pit_pure(original)
        self.assertFalse(ok)
        self.assertEqual(updated, original)
        self.assertIn("multicannon", result["reason"])

    def test_malformed_empty_roster_cannot_pay_pending_tokkul(self):
        corrupt = player(
            activity_session={"active_id": "tzhaar_fight_pit"},
            tzhaar_fight_pit={"match_number": 1, "pending_tokkul": 999},
        )
        self.assertEqual(
            sanitize_tzhaar_fight_pit_state_pure(corrupt)["tzhaar_fight_pit"],
            {},
        )
        updated, ok, result = apply_tzhaar_fight_pit_review_pure(corrupt)
        self.assertFalse(ok)
        self.assertEqual(updated, corrupt)
        self.assertNotIn("Tokkul", updated["inventory"])

    def test_match_disables_generic_auto_flee_without_changing_the_setting(self):
        entered, _, _ = enter_tzhaar_fight_pit_pure(player(combat_auto_flee=True))
        combat_result = (
            {**entered, "combat_auto_flee": False, "combat_encounter": {}},
            True,
            {"killed": False, "died": False, "fled": False, "ticks_elapsed": 6},
        )
        with patch("ankiscape.logic.tzhaar_fight_pit_logic.apply_combat_burst_pure", return_value=combat_result) as burst:
            updated, ok, _result = apply_tzhaar_fight_pit_review_pure(entered)
        self.assertTrue(ok)
        self.assertFalse(burst.call_args.args[0]["combat_auto_flee"])
        self.assertTrue(updated["combat_auto_flee"])

    def test_real_six_tick_combat_reaches_a_terminal_result(self):
        entered, _, _ = enter_tzhaar_fight_pit_pure(
            player(equipment={"weapon": "Rune scimitar"})
        )
        result = {}
        for _review in range(30):
            entered, ok, result = apply_tzhaar_fight_pit_review_pure(
                entered,
                lambda: 0.5,
                equipment_data=EQUIPMENT_DATA,
            )
            self.assertTrue(ok)
            if result.get("terminal"):
                break
        self.assertEqual(result.get("outcome"), "win")
        self.assertGreater(result.get("tokkul", 0), 0)

    def test_runtime_loss_is_recorded_as_a_safe_death_failure(self):
        entered, _, _ = enter_tzhaar_fight_pit_pure(player(combat_lifepoints=1))
        self.assertTrue(handle_tzhaar_fight_pit_answer(_context(entered, random_values=[0.0] * 200)))
        self.assertEqual(entered["tzhaar_fight_pit_losses"], 1)
        record = entered["action_telemetry"]["actions"]["utility:tzhaar_fight_pit"]
        self.assertEqual(record["successes"], 0)
        self.assertEqual(record["failures"], 1)
        self.assertEqual(record["failure_kinds"], {"safe_death": 1})


if __name__ == "__main__":
    unittest.main()
