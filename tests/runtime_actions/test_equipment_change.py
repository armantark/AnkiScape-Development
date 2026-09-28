"""The Equipment panel's Unequip action refuses an empty slot without saving."""

import copy
import unittest

from tests import test_integration_smoke as integration


class TestEquipmentChange(unittest.TestCase):
    setUp = integration.TestIntegrationSmoke.setUp
    tearDown = integration.TestIntegrationSmoke.tearDown

    def test_unequipping_an_empty_slot_refuses_and_leaves_the_save_alone(self):
        addon = integration._load_addon_as_package("ankiscape_equipment_change_refusal")
        saves = []
        errors = []
        addon.save_player_data = lambda: saves.append(copy.deepcopy(addon._state.player_data))
        addon.show_error_message = lambda title, message: errors.append((title, message))
        addon._state.player_data = {
            "inventory": {"Bronze platebody": 1},
            "equipment": {"head": "Bronze full helm"},
        }
        before = copy.deepcopy(addon._state.player_data)

        self.assertFalse(addon.on_unequip_slot("body"))

        self.assertEqual(errors, [("Cannot unequip item", "That equipment slot is already empty.")])
        self.assertEqual(saves, [])
        self.assertEqual(addon._state.player_data, before)


if __name__ == "__main__":
    unittest.main()
