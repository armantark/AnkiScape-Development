"""Sawmill labels retain saved utility identities and the paid review path."""

from unittest.mock import patch

from tests.integration_smoke import fixtures


class SawmillReviewTest(fixtures.ReviewedProfile):
    def test_saved_queued_conversions_make_one_plank_for_the_existing_fee(self):
        from ankiscape.core.action_queue import action_queue_view_pure, add_to_action_queue

        cases = (
            ("convert_logs_to_planks", "Logs", "Plank", 100),
            ("convert_oak_logs_to_oak_planks", "Oak logs", "Oak plank", 250),
            ("convert_teak_logs_to_teak_planks", "Teak logs", "Teak plank", 500),
            ("convert_mahogany_logs_to_mahogany_planks", "Mahogany logs", "Mahogany plank", 1500),
        )
        for utility_id, log, plank, fee in cases:
            with self.subTest(utility=utility_id):
                addon = self._addon(f"ankiscape_sawmill_{utility_id}")
                self._new_save(addon, inventory={log: 1, "Coins": fee + 1}, current_utility=utility_id)
                addon._state.current_skill = "Utilities"
                action = {"kind": "utility", "utility_id": utility_id}
                self.assertEqual(add_to_action_queue(addon, action, 1), "")
                addon.save_player_data()
                addon.load_player_data()
                self.assertEqual(addon._state.player_data["current_utility"], utility_id)
                queue = action_queue_view_pure(addon._state.player_data)
                self.assertIn(f"Sawmill: {plank}", queue["entries"][0]["name"])
                with patch.object(addon.random, "random", return_value=0.5):
                    self._answer(addon)
                self.assertEqual(self.errors, [])
                inventory = addon._state.player_data["inventory"]
                self.assertEqual((inventory[log], inventory["Coins"], inventory[plank]), (0, 1, 1))
                addon.load_player_data()
                self.assertEqual(addon._state.player_data["inventory"][plank], 1)
                self.assertEqual(action_queue_view_pure(addon._state.player_data)["entries"], [])
