"""A real review, undo and JSON reload retain both combat ownership models."""

import copy
from unittest.mock import patch

from tests.integration_smoke.fixtures import ReviewedProfile
from tests.test_integration_smoke import types


class AmmunitionUndoTest(ReviewedProfile):
    def test_selecting_a_target_equips_ammo_before_its_first_card_and_undo_restores_the_bank(self):
        addon = self._addon("ankiscape_starting_ammo")
        self._new_save(addon, equipment={"weapon": "Shortbow"}, inventory={"Bronze arrows": 840},
                       combat_prayers_enabled=False, combat_auto_flee=False, combat_auto_eat_food=[])
        before = copy.deepcopy(addon._state.player_data)
        self.assertTrue(addon._set_combat_target("cow"))
        save = addon._state.player_data
        self.assertEqual((save["equipment"]["ammunition"], save["equipment_ammunition_count"]), ("Bronze arrows", 840))
        self.assertEqual(save["inventory"]["Bronze arrows"], 0)
        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        for key in ("equipment", "equipment_ammunition_count", "equipment_ammunition_manual", "inventory", "current_combat_target"):
            self.assertEqual(addon._state.player_data.get(key), before.get(key))

    def test_review_undo_and_reload_restore_ammunition_and_carried_runes(self):
        cases = (
            ("Shortbow", {"ammunition": "Bronze arrows"}, {}, {}, 840),
            ("Staff", {}, {"Air rune": 10, "Mind rune": 10}, {"chicken": {"Air rune": 10, "Mind rune": 10}}, 0),
        )
        for weapon, ammunition, inventory, carried, count in cases:
            with self.subTest(weapon=weapon):
                addon = self._addon("ankiscape_ammunition_undo_" + weapon)
                addon.mw.col.set_config("ankiscape_review_action_multiplier", 10)
                self._new_save(addon, equipment={"weapon": weapon, **ammunition}, equipment_ammunition_count=count,
                               inventory=inventory, carried_inventory=carried, current_combat_target="chicken",
                               combat_prayers_enabled=False, combat_auto_flee=False, combat_auto_eat_food=[])
                addon._state.current_skill = "Combat"
                before = copy.deepcopy(addon._state.player_data)
                with patch.object(addon.random, "random", return_value=0.99):
                    self._answer(addon)
                result = addon._state.player_data["combat_last_result"]
                self.assertGreater(sum(result["ammo_used"].values()) + sum(result["runes_used"].values()), 0)
                self.assertEqual(len(addon._state.review_undo_stack), 1)
                addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card", changes=types.SimpleNamespace(study_queues=True, card=True)))
                for key in ("equipment", "equipment_ammunition_count", "inventory", "carried_inventory"):
                    self.assertEqual(addon._state.player_data[key], before[key])
                addon.save_player_data()
                addon.load_player_data()
                self.assertEqual(addon._state.player_data["equipment"], before["equipment"])
                self.assertEqual(addon._state.player_data["equipment_ammunition_count"], count)
                for name, amount in inventory.items():
                    self.assertEqual(addon._state.player_data["inventory"][name], amount)
