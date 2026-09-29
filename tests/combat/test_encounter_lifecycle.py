"""Encounter lifecycle and live combat-method regression coverage."""

import unittest

import pkg_alias  # noqa: F401
from ankiscape.logic_pure.logic_pure import repair_combat_supply_loadout_class_pure
from tests import test_combat_logic as _combat
from tests import test_storage_pure as _storage


class EncounterLifecycleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.combat = _combat.CombatStatPotionAutoDrinkTest(methodName="runTest")

    def _melee(self, **overrides):
        return self.combat._melee(**overrides)

    def _enemy_lifepoints_on_return(self, player_data, target_id="chicken"):
        """Lifepoints the fight after an ended encounter opens on.

        Every roll misses, so a fresh enemy still reads full when the burst returns,
        and the supply run is held back so the burst measures only the encounter.
        """
        fought, ok, result = _combat.apply_combat_burst_pure(
            dict(player_data, current_combat_target=target_id),
            _combat.COMBAT_ENEMY_DATA,
            _combat.EQUIPMENT_DATA,
            ticks=1,
            rng=_combat._rng([]),
            allow_bank_run=False,
            live_cadence=True,
        )
        self.assertTrue(ok, result)
        return fought["combat_encounter"].get("enemy_lifepoints")

    def test_a_manual_bank_run_ends_the_encounter_and_returns_to_a_fresh_enemy(self):
        player = self._melee(
            combat_encounter={"target_id": "chicken", "enemy_lifepoints": 4},
            combat_supply_loadout={"food": {"Shrimps": 20}},
        )

        requested, ok, reason = _combat.request_combat_bank_run_now_pure(player)

        self.assertTrue(ok, reason)
        self.assertEqual(requested["combat_encounter"], {})
        walking, ok, first = _combat.apply_combat_burst_pure(
            requested,
            _combat.COMBAT_ENEMY_DATA,
            _combat.EQUIPMENT_DATA,
            ticks=1,
            rng=_combat._rng([]),
        )
        self.assertTrue(ok, first)
        self.assertEqual(first["reason"], "combat_bank_run")
        arrived, ok, second = _combat.apply_combat_burst_pure(
            walking,
            _combat.COMBAT_ENEMY_DATA,
            _combat.EQUIPMENT_DATA,
            ticks=1,
            rng=_combat._rng([]),
        )
        self.assertTrue(ok, second)
        self.assertTrue(second["bank_run_completed"])
        self.assertEqual(
            self._enemy_lifepoints_on_return(arrived),
            _combat.COMBAT_ENEMY_DATA["chicken"]["stats"]["hitpoints"],
        )

    def test_an_automatic_bank_run_ends_the_encounter_it_walked_away_from(self):
        # An empty pack with food in the bank forces the run in mid-fight.
        player = self._melee(
            inventory={"Shrimps": 30},
            combat_supply_loadout={"food": {}},
            combat_encounter={"target_id": "chicken", "enemy_lifepoints": 4},
        )

        walking, ok, result = _combat.apply_combat_burst_pure(
            player,
            _combat.COMBAT_ENEMY_DATA,
            _combat.EQUIPMENT_DATA,
            ticks=1,
            rng=_combat._rng([]),
        )

        self.assertTrue(ok, result)
        self.assertEqual(result["reason"], "combat_bank_run")
        self.assertEqual(walking["combat_encounter"], {})
        arrived, ok, result = _combat.apply_combat_burst_pure(
            walking,
            _combat.COMBAT_ENEMY_DATA,
            _combat.EQUIPMENT_DATA,
            ticks=1,
            rng=_combat._rng([]),
        )
        self.assertTrue(ok, result)
        self.assertTrue(result["bank_run_completed"])
        self.assertEqual(
            self._enemy_lifepoints_on_return(arrived),
            _combat.COMBAT_ENEMY_DATA["chicken"]["stats"]["hitpoints"],
        )

    def test_a_kill_returns_to_a_fresh_enemy(self):
        killed, ok, result = _combat.apply_combat_burst_pure(
            self._melee(
                combat_encounter={"target_id": "chicken", "enemy_lifepoints": 1}
            ),
            _combat.COMBAT_ENEMY_DATA,
            _combat.EQUIPMENT_DATA,
            ticks=500,
            rng=_combat._rng([0.0, 0.999999, 0.0]),
        )

        self.assertTrue(ok, result)
        self.assertTrue(result["killed"], result)
        self.assertEqual(killed["combat_encounter"], {})
        self.assertEqual(
            self._enemy_lifepoints_on_return(killed),
            _combat.COMBAT_ENEMY_DATA["chicken"]["stats"]["hitpoints"],
        )

    def test_a_salted_rockslug_respawns_fighting_back(self):
        # At 1 LP the slug has stopped fighting back; the player's first hit
        # spends the Bag of salt to kill it, and the burst chains into the next
        # spawn, which must fight back like any fresh slug.
        fought, ok, result = _combat.apply_combat_burst_pure(
            _combat._player(
                current_combat_target="rockslug",
                slayer_level=99,
                slayer_quick_finishers_unlocked=True,
                combat_encounter={"target_id": "rockslug", "enemy_lifepoints": 1},
                combat_supply_loadout={"finishers": {"Bag of salt": 1}},
            ),
            _combat.COMBAT_ENEMY_DATA,
            _combat.EQUIPMENT_DATA,
            ticks=6,
            rng=lambda: 0.0,
        )

        self.assertTrue(ok, result)
        self.assertEqual((result["kills"], result["automatic_finishers"]), (1, 1))
        self.assertFalse(result["enemy_retaliation_stopped"], fought["combat_encounter"])
        self.assertNotIn("retaliation_stopped", fought["combat_encounter"])
        self.assertEqual(result["enemy_damage"], 1)
        self.assertEqual(fought["combat_lifepoints"], 99)

    def test_auto_flee_returns_to_a_fresh_enemy(self):
        fled, ok, result = _combat.apply_combat_burst_pure(
            _combat._player(
                current_combat_target="killer",
                combat_lifepoints=1,
                equipment={"weapon": "Iron sword"},
                combat_supply_loadout={},
                combat_encounter={"target_id": "killer", "enemy_lifepoints": 7},
            ),
            _combat._KILLER_ENEMY_DATA,
            _combat.EQUIPMENT_DATA,
            ticks=5,
            rng=lambda: 0.0,
        )

        self.assertTrue(ok, result)
        self.assertTrue(result["fled"], result)
        self.assertEqual(fled["combat_encounter"], {})
        self.assertEqual(
            self._enemy_lifepoints_on_return(
                dict(fled, combat_lifepoints=100)
            ),
            _combat.COMBAT_ENEMY_DATA["chicken"]["stats"]["hitpoints"],
        )

    def test_a_death_returns_to_a_fresh_enemy(self):
        died, ok, result = _combat.apply_combat_burst_pure(
            _combat._player(
                current_combat_target="killer",
                attack_level=1,
                strength_level=1,
                combat_lifepoints=1,
                combat_auto_flee=False,
                equipment={"weapon": "Iron sword"},
                combat_encounter={"target_id": "killer", "enemy_lifepoints": 7},
            ),
            _combat._KILLER_ENEMY_DATA,
            _combat.EQUIPMENT_DATA,
            ticks=5,
            rng=_combat._rng([0.999999, 0.0, 0.999999]),
        )

        self.assertTrue(ok, result)
        self.assertTrue(result["died"], result)
        self.assertEqual(died["combat_encounter"], {})
        self.assertEqual(
            self._enemy_lifepoints_on_return(died),
            _combat.COMBAT_ENEMY_DATA["chicken"]["stats"]["hitpoints"],
        )

    def test_pack_mode_repairs_invalid_dream_fight_and_applies_in_a_real_fight(self):
        reported = self._melee(
            magic_level=1,
            quests={"dream_mentor": {"completed": False}},
            combat_dream_thrift=True,
            combat_encounter={"target_id": "citizen", "enemy_lifepoints": 67},
            inventory={"Shrimps": 89},
            combat_auto_eat_food=["Shrimps"],
            combat_supply_loadout={"food": {"Shrimps": 1}},
        )

        repaired, ok, reason = _combat.set_combat_pack_mode_pure(
            reported, "max_safety", _combat.EQUIPMENT_DATA
        )
        self.assertTrue(ok, reason)
        self.assertFalse(repaired["combat_dream_thrift"])
        self.assertEqual(repaired["combat_encounter"], {})
        self.assertEqual(repaired["combat_supply_loadout"]["food"], {"Shrimps": 20})

        active = dict(repaired)
        active_encounter = {
            "target_id": "chicken",
            "enemy_lifepoints": 3,
            "player_attack_ticks_remaining": 2,
            "enemy_attack_ticks_remaining": 4,
        }
        active["combat_encounter"] = active_encounter
        switched, ok, reason = _combat.set_combat_pack_mode_pure(
            active, "max_output", _combat.EQUIPMENT_DATA
        )
        self.assertTrue(ok, reason)
        self.assertEqual(switched["combat_pack_mode"], "max_output")
        self.assertEqual(switched["combat_supply_loadout"]["food"], {"Shrimps": 8})
        self.assertEqual(switched["combat_encounter"], active_encounter)

    def test_combat_method_reconciliation_accepts_a_live_encounter(self):
        encounter = {
            "target_id": "chicken",
            "enemy_lifepoints": 30,
            "player_attack_ticks_remaining": 2,
            "enemy_attack_ticks_remaining": 4,
        }
        player = _combat._player(
            combat_attack_style="magic_standard",
            current_combat_spell="wind_strike",
            equipment={"weapon": "Staff"},
            inventory={"Water rune": 5},
            combat_supply_loadout={"runes": {"Air rune": 5, "Mind rune": 5}},
            combat_encounter=encounter,
        )

        updated, ok, reason = _combat.reconcile_combat_method_pure(
            player,
            {"current_combat_spell": "water_strike"},
            _combat.EQUIPMENT_DATA,
        )

        self.assertTrue(ok, reason)
        self.assertEqual(updated["current_combat_spell"], "water_strike")
        self.assertEqual(
            updated["combat_supply_loadout"]["runes"],
            {"Air rune": 5, "Mind rune": 5, "Water rune": 5},
        )
        self.assertEqual(updated["combat_encounter"], encounter)

    def test_manual_refill_loadout_applies_inside_active_encounter(self):
        encounter = {
            "target_id": "chicken",
            "enemy_lifepoints": 30,
            "player_attack_ticks_remaining": 2,
            "enemy_attack_ticks_remaining": 4,
        }
        player = _combat._player(
            inventory={"Shark": 30},
            combat_auto_eat_food=["Shark"],
            combat_encounter=encounter,
        )

        refilled, ok, reason = _combat.refill_combat_supply_loadout_pure(
            player, _combat.EQUIPMENT_DATA
        )

        self.assertTrue(ok, reason)
        loaded_sharks = refilled["combat_supply_loadout"]["food"]["Shark"]
        self.assertGreater(loaded_sharks, 0)
        self.assertEqual(refilled["inventory"]["Shark"] + loaded_sharks, 30)
        self.assertEqual(refilled["combat_encounter"], encounter)

    def test_manual_unload_loadout_applies_inside_active_encounter(self):
        encounter = {
            "target_id": "chicken",
            "enemy_lifepoints": 30,
            "player_attack_ticks_remaining": 2,
            "enemy_attack_ticks_remaining": 4,
        }
        player = _combat._player(
            combat_supply_loadout={"food": {"Shark": 3}},
            combat_encounter=encounter,
        )

        unloaded, ok, reason = _combat.unload_combat_supply_loadout_pure(player)

        self.assertTrue(ok, reason)
        self.assertEqual(unloaded["inventory"]["Shark"], 3)
        self.assertEqual(unloaded["combat_supply_loadout"]["food"], {})
        self.assertEqual(unloaded["combat_encounter"], encounter)

    def test_live_class_repair_repacks_without_resetting_the_encounter(self):
        encounter = {
            "target_id": "chicken",
            "enemy_lifepoints": 30,
            "player_attack_ticks_remaining": 2,
            "enemy_attack_ticks_remaining": 4,
        }
        player = _combat._player(
            equipment={"weapon": "Rune scimitar"},
            inventory={"Shark": 30},
            combat_auto_eat_food=["Shark"],
            combat_supply_loadout={
                "ammo": {"Bronze arrows": 5},
                "runes": {"Air rune": 5},
            },
            combat_encounter=encounter,
        )

        repaired = repair_combat_supply_loadout_class_pure(
            player, _combat.EQUIPMENT_DATA
        )

        loaded_sharks = repaired["combat_supply_loadout"]["food"]["Shark"]
        self.assertGreater(loaded_sharks, 0)
        self.assertEqual(repaired["inventory"]["Shark"] + loaded_sharks, 30)
        self.assertEqual(repaired["combat_supply_loadout"]["ammo"], {})
        self.assertEqual(repaired["combat_supply_loadout"]["runes"], {})
        self.assertEqual(repaired["inventory"]["Bronze arrows"], 5)
        self.assertEqual(repaired["inventory"]["Air rune"], 5)
        self.assertEqual(repaired["combat_encounter"], encounter)

    def test_load_repairs_incompatible_supplies_without_resetting_the_encounter(self):
        saved = _storage.default_player_data(
            _storage.ORE_DATA, _storage.ITEM_DEFINITIONS
        )
        saved.update(
            {
                "inventory": {},
                "equipment": {},
                "combat_attack_style": "accurate",
                "current_combat_target": "chicken",
                "combat_encounter": {
                    "target_id": "chicken",
                    "enemy_lifepoints": 1,
                    "player_attack_ticks_remaining": 2,
                    "enemy_attack_ticks_remaining": 4,
                },
                "combat_supply_loadout": {
                    "runes": {"Air rune": 5, "Mind rune": 5},
                },
            }
        )

        migrated = _storage.migrate_loaded_data(
            saved, _storage.ORE_DATA, _storage.ITEM_DEFINITIONS
        )

        self.assertEqual(migrated["combat_supply_loadout"]["runes"], {})
        self.assertEqual(migrated["inventory"]["Air rune"], 5)
        self.assertEqual(migrated["inventory"]["Mind rune"], 5)
        for key, value in saved["combat_encounter"].items():
            self.assertEqual(migrated["combat_encounter"][key], value)


if __name__ == "__main__":
    unittest.main()
