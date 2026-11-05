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
                for key in ("equipment", "equipment_ammunition_count", "inventory", "carried_inventory", "ground_ammunition", "ground_ammunition_tick", "review_event_log"):
                    self.assertEqual(addon._state.player_data[key], before[key])
                addon.save_player_data()
                addon.load_player_data()
                self.assertEqual(addon._state.player_data["equipment"], before["equipment"])
                self.assertEqual(addon._state.player_data["equipment_ammunition_count"], count)
                for name, amount in inventory.items():
                    self.assertEqual(addon._state.player_data["inventory"][name], amount)

    def test_pickup_undo_and_review_undo_restore_the_pile_and_log(self):
        addon = self._addon("ankiscape_ground_ammo_undo")
        addon.mw.col.set_config("ankiscape_review_action_multiplier", 10)
        self._new_save(addon, equipment={"weapon": "Shortbow", "ammunition": "Bronze arrows"},
                       equipment_ammunition_count=840, combat_prayers_enabled=False,
                       combat_auto_flee=False, combat_auto_eat_food=[])
        addon._state.current_skill = "Combat"
        before = copy.deepcopy(addon._state.player_data)
        with patch.object(addon.random, "random", return_value=0.75):
            self._answer(addon)
        save = addon._state.player_data
        self.assertGreater(sum(row["count"] for row in save["ground_ammunition"]), 0)
        lines = [row["text"] for row in save["review_event_log"] if row["text"].startswith("Ammo:")]
        self.assertEqual(len(lines), 1)
        self.assertIn("fired · 0 broken", lines[0])
        addon.save_player_data()
        addon.load_player_data()
        after_review = copy.deepcopy(addon._state.player_data)
        self.assertTrue(addon.on_pickup_review_ammo())
        self.assertEqual(addon._state.player_data["ground_ammunition"], [])
        self.assertEqual(addon._state.player_data["equipment_ammunition_count"], 840)
        self.assertEqual(addon._state.player_data["ground_ammunition_tick"], after_review["ground_ammunition_tick"])
        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        for key in ("ground_ammunition", "ground_ammunition_tick", "equipment_ammunition_count", "inventory", "review_event_log"):
            self.assertEqual(addon._state.player_data[key], after_review[key])
        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card", changes=types.SimpleNamespace(study_queues=True, card=True)))
        for key in ("ground_ammunition", "ground_ammunition_tick", "equipment_ammunition_count", "inventory", "review_event_log"):
            self.assertEqual(addon._state.player_data[key], before[key])

    def test_again_and_noncombat_cards_age_arrows_without_firing(self):
        for speed in (1, 10):
            with self.subTest(speed=speed):
                addon = self._addon("ankiscape_ground_ammo_clock_" + str(speed))
                addon.mw.col.set_config("ankiscape_review_action_multiplier", speed)
                self._new_save(addon, ground_ammunition=[{"name": "Bronze arrows", "count": 7, "expires_at": 6 * speed}],
                               ground_ammunition_tick=0)
                addon._state.current_skill = "Mining"
                self._answer(addon)
                self.assertEqual(addon._state.player_data["ground_ammunition"], [])
                self.assertEqual(addon._state.player_data["ground_ammunition_tick"], 6 * speed)
                addon._state.player_data["ground_ammunition"] = [{"name": "Bronze arrows", "count": 7, "expires_at": 12 * speed}]
                addon._state.current_skill = "Combat"
                from tests.test_integration_smoke import _FakeReviewer
                addon._state.card_turned = addon._state.answer_shown = True
                addon._state.exp_awarded = False
                addon.on_answer_card(_FakeReviewer(), 1, lambda _self, _ease: "answered")
                self.assertEqual(addon._state.player_data["ground_ammunition"], [])
                self.assertEqual(addon._state.player_data["ground_ammunition_tick"], 12 * speed)
