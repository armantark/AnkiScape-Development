"""UI and runtime transitions around a live combat Encounter."""

import copy
import sys
import types
import unittest

from tests import test_direct_action_undo_seam as _undo_seam
from tests import test_integration_smoke as _integration
from tests import test_main_menu_widget as _main_menu

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication, QComboBox


class EncounterMethodChangeIntegrationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.integration = _integration.TestIntegrationSmoke(methodName="runTest")
        self.integration.setUp()

    def tearDown(self) -> None:
        self.integration.tearDown()

    def _live_combat_addon(self, module_name, **player_overrides):
        addon = _integration._load_addon_as_package(module_name)
        addon.mw = _integration._DummyMW(_integration._DummyCol())
        errors = []
        addon.save_player_data = lambda: None
        addon.check_achievements = lambda _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon._refresh_open_carried_inventory = lambda: None
        addon.show_error_message = lambda title, message: errors.append(
            (title, message)
        )
        encounter = {
            "target_id": "black_bear",
            "enemy_lifepoints": 173,
            "player_attack_ticks_remaining": 0,
            "enemy_attack_ticks_remaining": 5,
        }
        player_data = {
            "inventory": {},
            "equipment": {"weapon": "Rune scimitar"},
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "magic_level": 99,
            "constitution_level": 28,
            "combat_lifepoints": 280,
            "current_combat_target": "black_bear",
            "combat_action": "attack",
            "combat_attack_style": "aggressive",
            "combat_attack_style_type": "crush",
            "current_combat_spell": "wind_strike",
            "combat_pack_mode": "max_safety",
            "combat_auto_eat_food": ["Shrimps"],
            "combat_auto_flee": False,
            "combat_supply_loadout": {},
            "combat_encounter": dict(encounter),
        }
        player_data.update(player_overrides)
        addon._state.current_skill = "Combat"
        addon._state.player_data = player_data
        return addon, encounter, errors

    def _run_live_combat_review(self, addon, *, rolls=(0.0, 0.25)):
        combat = sys.modules[
            f"{addon.__name__}.logic_pure.logic_pure_combat_engine"
        ]
        random_rolls = iter(rolls)
        return combat.apply_combat_burst_pure(
            addon._state.player_data,
            addon.COMBAT_ENEMY_DATA,
            addon.EQUIPMENT_DATA,
            ticks=1,
            rng=lambda: next(random_rolls, 0.999999),
            live_cadence=True,
            allow_bank_run=False,
        )

    def test_live_encounter_style_change_applies_on_the_next_review(self):
        addon, encounter, errors = self._live_combat_addon(
            "ankiscape_combat_live_style"
        )

        self.assertTrue(addon._set_combat_attack_style(("accurate", "slash")))
        self.assertEqual(addon._state.player_data["combat_encounter"], encounter)

        fought, ok, result = self._run_live_combat_review(addon)

        self.assertTrue(ok, result)
        self.assertEqual(errors, [])
        self.assertGreater(result["xp_rewards"]["attack_exp"], 0)
        self.assertNotIn("strength_exp", result["xp_rewards"])
        self.assertLess(fought["combat_encounter"]["enemy_lifepoints"], 173)

    def test_live_encounter_spell_change_applies_on_the_next_review(self):
        addon, encounter, errors = self._live_combat_addon(
            "ankiscape_combat_live_spell",
            inventory={"Water rune": 5},
            equipment={"weapon": "Staff"},
            combat_attack_style="magic_standard",
            combat_attack_style_type="auto",
            combat_supply_loadout={"runes": {"Air rune": 5, "Mind rune": 5}},
        )

        self.assertTrue(
            addon._set_combat_method_values({"current_combat_spell": "water_strike"})
        )
        self.assertEqual(addon._state.player_data["combat_encounter"], encounter)

        _fought, ok, result = self._run_live_combat_review(addon)

        self.assertTrue(ok, result)
        self.assertEqual(errors, [])
        self.assertEqual(result["spell_id"], "water_strike")
        self.assertEqual(
            result["runes_used"],
            {"Air rune": 1, "Mind rune": 1, "Water rune": 1},
        )
        self.assertGreater(result["xp_rewards"]["magic_exp"], 0)

    def test_live_encounter_weapon_equip_applies_on_the_next_review(self):
        addon, encounter, errors = self._live_combat_addon(
            "ankiscape_combat_live_weapon_equip",
            inventory={"Staff": 1, "Air rune": 5, "Mind rune": 5},
            equipment={},
        )

        self.assertTrue(addon.on_equip_item("Staff"))
        self.assertEqual(addon._state.player_data["combat_encounter"], encounter)

        fought, ok, result = self._run_live_combat_review(addon)

        self.assertTrue(ok, result)
        self.assertEqual(errors, [])
        self.assertEqual(result["weapon"], "Staff")
        self.assertEqual(result["combat_class"], "magic")
        self.assertEqual(fought["combat_encounter"]["player_attack_ticks_remaining"], 4)

    def test_live_encounter_weapon_unequip_applies_on_the_next_review(self):
        addon, encounter, errors = self._live_combat_addon(
            "ankiscape_combat_live_weapon_unequip",
            inventory={},
            equipment={"weapon": "Staff"},
            combat_attack_style="magic_standard",
            combat_attack_style_type="auto",
            combat_supply_loadout={"runes": {"Air rune": 5, "Mind rune": 5}},
        )

        self.assertTrue(addon.on_unequip_slot("weapon"))
        self.assertEqual(addon._state.player_data["combat_encounter"], encounter)

        fought, ok, result = self._run_live_combat_review(addon)

        self.assertTrue(ok, result)
        self.assertEqual(errors, [])
        self.assertEqual(result["weapon"], "")
        self.assertEqual(result["combat_class"], "melee")
        self.assertEqual(result["runes_used"], {})
        self.assertEqual(fought["combat_encounter"]["player_attack_ticks_remaining"], 3)

    def test_live_encounter_pack_mode_change_applies_on_the_next_review(self):
        addon, encounter, errors = self._live_combat_addon(
            "ankiscape_combat_live_pack_mode",
            inventory={"Shrimps": 68},
            combat_lifepoints=200,
            combat_auto_eat_threshold_percent=99,
            combat_supply_loadout={"food": {"Shrimps": 20}},
            combat_encounter={
                "target_id": "black_bear",
                "enemy_lifepoints": 173,
                "player_attack_ticks_remaining": 0,
                "enemy_attack_ticks_remaining": 0,
            },
        )

        self.assertTrue(addon.on_set_combat_pack_mode("max_output"))
        retained_encounter = {**encounter, "enemy_attack_ticks_remaining": 0}
        self.assertEqual(
            addon._state.player_data["combat_encounter"], retained_encounter
        )
        self.assertEqual(
            addon._state.player_data["combat_supply_loadout"]["food"],
            {"Shrimps": 8},
        )

        fought, ok, result = self._run_live_combat_review(
            addon, rolls=(0.0, 0.0, 0.0, 0.999999)
        )

        self.assertTrue(ok, result)
        self.assertEqual(errors, [])
        self.assertGreater(len(result["food_used"]), 0)
        self.assertLess(sum(fought["combat_supply_loadout"]["food"].values()), 8)

    def test_live_encounter_finisher_selection_stays_within_combat(self):
        finisher_encounter = {
            "target_id": "desert_lizard",
            "enemy_lifepoints": 30,
            "player_attack_ticks_remaining": 2,
            "enemy_attack_ticks_remaining": 5,
        }
        addon, _encounter, errors = self._live_combat_addon(
            "ankiscape_combat_live_finisher",
            current_combat_target="desert_lizard",
            slayer_level=22,
            combat_encounter=dict(finisher_encounter),
            combat_supply_loadout={"finishers": {"Ice cooler": 1}},
        )

        self.assertTrue(
            addon._set_combat_method_values({"combat_action": "finisher"})
        )
        self.assertEqual(addon._state.current_skill, "Combat")
        self.assertEqual(
            addon._state.player_data["combat_encounter"], finisher_encounter
        )

        self.assertTrue(
            addon.runtime_actions.handle_combat_answer(
                self.integration._runtime_context(addon, rolls=(0.999999,))
            )
        )

        self.assertEqual(errors, [])
        self.assertEqual(addon._state.player_data["combat_action"], "attack")
        self.assertEqual(addon._state.player_data["combat_encounter"], {})
        self.assertEqual(
            addon._state.player_data["combat_supply_loadout"]["finishers"], {}
        )

    def test_grand_exchange_collection_starts_live_combat_bank_run(self):
        addon = _integration._load_addon_as_package(
            "ankiscape_grand_exchange_collection_bank_run_integration"
        )
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon.mw = _integration._DummyMW(_integration._DummyCol())
        addon._state.current_skill = "Combat"
        ge_logic = sys.modules[f"{addon.__name__}.logic.grand_exchange_logic"]
        review_strip_logic = sys.modules[
            f"{addon.__name__}.logic.review_strip_logic"
        ]
        item_spec = addon.GE_ITEM_CATALOG["Logs"]
        initial, placed = ge_logic.place_ge_offer_pure(
            {"inventory": {"Coins": 10_000}, "smithing_level": 1},
            side="buy",
            item_name="Logs",
            quantity=1,
            unit_price=int(item_spec["guide_price"]),
            item_spec=item_spec,
        )
        self.assertTrue(placed["ok"])
        order = initial["ge_player_orders"][0]
        order.update(
            remaining_quantity=0,
            completed_quantity=1,
            escrow_coins=0,
            collectible_items=1,
            status="complete",
        )
        initial.update(
            {
                "current_combat_target": "chicken",
                "combat_encounter": {
                    "target_id": "chicken",
                    "enemy_lifepoints": 10,
                    "disengaged": False,
                },
            }
        )
        addon._state.player_data = initial
        initial_snapshot = copy.deepcopy(initial)
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._on_main_menu()

        result = captured["on_ge_action"](
            "collect_offer", {"order_id": order["id"]}
        )

        self.assertTrue(result["ok"])
        self.assertTrue(result["bank_run_triggered"])
        self.assertEqual(
            addon._state.player_data["combat_bank_run"],
            {"reviews_remaining": 2, "target_id": "chicken"},
        )

        self.assertEqual(addon._state.player_data["combat_encounter"], {})
        travel = review_strip_logic.review_bank_run_travel_view_pure(
            addon._state.player_data, "combat"
        )
        self.assertTrue(travel["active"])
        self.assertFalse(travel["queued"])
        self.assertEqual(travel["kind"], "combat")
        self.assertEqual(travel["total"], 2)
        self.assertEqual(travel["remaining"], 2)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial_snapshot)

        result = captured["on_ge_action"]("collect_all", {})
        self.assertTrue(result["ok"])
        self.assertTrue(result["bank_run_triggered"])
        self.assertEqual(
            addon._state.player_data["combat_bank_run"],
            {"reviews_remaining": 2, "target_id": "chicken"},
        )

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial_snapshot)


class EncounterDirectActionTransitionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.seam = _undo_seam.DirectActionUndoSeamTest(methodName="runTest")
        self.seam.setUp()
        self.addon = self.seam.addon

    def tearDown(self) -> None:
        self.seam.tearDown()

    def _enemy_lifepoints_on_return(self, target_id):
        """Lifepoints the next fight opens the chosen enemy on.

        Every roll misses and the supply run is held back, so a fresh enemy
        still reads full when the burst returns.
        """
        combat = sys.modules[
            f"{self.addon.__name__}.logic_pure.logic_pure_combat_engine"
        ]
        fought, ok, result = combat.apply_combat_burst_pure(
            dict(self.addon._state.player_data, current_combat_target=target_id),
            ticks=1,
            rng=lambda: 0.999999,
            allow_bank_run=False,
            live_cadence=True,
        )
        self.assertTrue(ok, result)
        return fought["combat_encounter"].get("enemy_lifepoints")

    def test_choosing_another_skill_ends_the_fight_it_left(self):
        self.addon._state.current_skill = "Combat"
        self.addon._state.player_data["current_combat_target"] = "chicken"
        self.addon._state.player_data["combat_encounter"] = {
            "target_id": "chicken",
            "enemy_lifepoints": 4,
        }

        self.addon.save_skill("Mining", None)

        self.assertEqual(self.addon._state.current_skill, "Mining")
        self.assertEqual(self.addon._state.player_data["combat_encounter"], {})
        self.assertEqual(len(self.seam.saves), 1, "the ended fight must persist")
        self.assertEqual(
            self._enemy_lifepoints_on_return("chicken"),
            self.addon.COMBAT_ENEMY_DATA["chicken"]["stats"]["hitpoints"],
        )

    def test_choosing_another_target_ends_the_fight_and_undo_restores_it(self):
        self.addon._state.current_skill = "Combat"
        self.addon._state.player_data["current_combat_target"] = "goblin"
        encounter = {"target_id": "goblin", "enemy_lifepoints": 4}
        self.addon._state.player_data["combat_encounter"] = dict(encounter)

        self.assertTrue(self.addon._set_combat_target("chicken"))

        self.assertEqual(self.addon._state.player_data["combat_encounter"], {})
        self.assertEqual(
            self._enemy_lifepoints_on_return("chicken"),
            self.addon.COMBAT_ENEMY_DATA["chicken"]["stats"]["hitpoints"],
        )
        self.addon._on_state_did_undo(
            type("Changes", (), {"operation": "AnkiScape direct action"})()
        )
        self.assertEqual(self.addon._state.player_data["combat_encounter"], encounter)

    def test_starting_bankstanding_ends_the_fight_it_left(self) -> None:
        """The owner's path: the utility was already the stored one, and the
        fight still has to end, because the action is what changed."""
        self.addon._state.player_data = {
            "current_utility": "bankstanding",
            "current_combat_target": "chicken",
            "combat_encounter": {"target_id": "chicken", "enemy_lifepoints": 4},
        }
        self.addon._state.current_skill = "Combat"
        self.addon.update_review_hud = lambda _data, _skill: None

        self.assertTrue(self.addon.start_activity_for_reviews("bankstanding"))

        self.assertEqual(self.addon._state.current_skill, "Utilities")
        self.assertEqual(self.addon._state.player_data["combat_encounter"], {})


@unittest.skipUnless(
    _main_menu.HAS_AQT,
    "aqt/PyQt6 not installed (use .venv-qt)",
)
class EncounterMenuSelectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _main_menu.MainMenuWidgetTest.setUpClass()

    def setUp(self) -> None:
        self.menu = _main_menu.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()

    def tearDown(self) -> None:
        self.menu.tearDown()

    def test_combat_supply_mode_changes_during_an_active_fight(self) -> None:
        calls: list = []
        player = _main_menu._make_player_data()
        player["combat_pack_mode"] = "balanced"
        player["combat_encounter"] = {
            "target_id": "chicken",
            "enemy_lifepoints": 3,
        }
        from ankiscape.logic_pure.logic_pure_combat_engine import (
            set_combat_pack_mode_pure,
        )

        def set_mode(mode):
            calls.append(mode)
            updated, ok, _reason = set_combat_pack_mode_pure(player, mode)
            player.update(updated)
            return ok

        dialog = self.menu._open(
            player,
            current_skill="Combat",
            on_set_combat_pack_mode=set_mode,
        )
        combo = dialog.findChild(QComboBox, "combatPackModeCombo")
        combo.setCurrentIndex(combo.findData("max_output"))
        QApplication.processEvents()
        self.assertEqual(combo.currentData(), "max_output")
        self.assertIn("max_output", calls)
        dialog.deleteLater()

    def test_live_encounter_keeps_every_combat_method_selection(self) -> None:
        from ankiscape.core.constants import EQUIPMENT_DATA
        from ankiscape.logic_pure.logic_pure import reconcile_combat_method_pure

        player = _main_menu._make_player_data()
        player.update(
            {
                "current_combat_target": "desert_lizard",
                "combat_action": "attack",
                "combat_attack_style": "aggressive",
                "combat_attack_style_type": "slash",
                "current_combat_spell": "wind_strike",
                "equipment": {"weapon": "Bronze longsword"},
                "slayer_level": 99,
                "combat_encounter": {
                    "target_id": "desert_lizard",
                    "enemy_lifepoints": 30,
                },
                "combat_supply_loadout": {
                    "finishers": {"Ice cooler": 1},
                    "hazards": {"Waterskin (4)": 1},
                },
            }
        )
        attempts = {}

        def accept(key, value, updates):
            attempts[key] = value
            updated, ok, reason = reconcile_combat_method_pure(
                player, updates, EQUIPMENT_DATA
            )
            self.assertTrue(ok, reason)
            self.assertEqual(updated["combat_encounter"], player["combat_encounter"])
            return ok

        dialog = self.menu._open(
            player,
            current_skill="Combat",
            on_set_combat_action=lambda value: accept(
                "action", value, {"combat_action": value}
            ),
            on_set_combat_style=lambda value: accept(
                "style",
                value,
                {
                    "combat_attack_style": value[0],
                    "combat_attack_style_type": value[1],
                },
            ),
            on_set_combat_spell=lambda value: accept(
                "spell", value, {"current_combat_spell": value}
            ),
        )

        action_combo = dialog.findChild(QComboBox, "combatActionCombo")
        style_combo = dialog.findChild(QComboBox, "combatStyleCombo")
        spell_combo = dialog.findChild(QComboBox, "combatSpellCombo")
        self.assertIsNotNone(action_combo)
        self.assertIsNotNone(style_combo)
        self.assertIsNotNone(spell_combo)

        action_combo.setCurrentIndex(action_combo.findData("finisher"))
        QApplication.processEvents()
        style_combo.setCurrentIndex(
            next(
                index
                for index in range(style_combo.count())
                if style_combo.itemData(index) == ("defensive", "slash")
            )
        )
        QApplication.processEvents()
        spell_combo.setCurrentIndex(spell_combo.findData("water_strike"))
        QApplication.processEvents()

        self.assertEqual(action_combo.currentData(), "finisher")
        self.assertEqual(style_combo.currentData(), ("defensive", "slash"))
        self.assertEqual(spell_combo.currentData(), "water_strike")
        self.assertEqual(
            attempts,
            {
                "action": "finisher",
                "style": ("defensive", "slash"),
                "spell": "water_strike",
            },
        )


if __name__ == "__main__":
    unittest.main()
