from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _expand_quest_card,
    _make_player_data,
    _open_quests_tab,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QLabel, QPushButton
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_quests_tab_offers_shield_black_arm_contextual_combat(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "shield_of_arrav"
        pd["quests"]["shield_of_arrav"] = {"started": True, "progress": 5, "completed": False}
        pd["quest_route_states"] = {"shield_of_arrav": ["Join the Black Arm Gang"]}
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertTrue(all("Needs Weapon store key" not in label for label in labels))
        action = dialog.findChild(QPushButton, "questAction_shield_of_arrav")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())
        self.assertNotIn("Needs Weapon store key", action.toolTip())
        self.assertNotIn("Phoenix Gang partner", action.toolTip())
        self.assertNotIn("Use the weapon store key", action.toolTip())
        self.assertIn("Weaponsmaster level 23", action.toolTip())

    def test_quests_tab_allows_resolver_ready_combat_gate_selection(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Stake": 1, "Stake hammer": 1}
        pd["current_quest"] = "vampyre_slayer"
        pd["quests"]["vampyre_slayer"] = {"started": True, "progress": 3, "completed": False}
        pd["attack_level"] = 40
        pd["strength_level"] = 40
        pd["defense_level"] = 35
        pd["constitution_level"] = 40
        pd["prayer_level"] = 20
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Battle required: Count Draynor level 37"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_vampyre_slayer")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

        action.click()
        QApplication.processEvents()
        self.assertIn("vampyre_slayer", self._quest_calls)

    def test_quests_tab_allows_merlins_crystal_mordred_combat_gate_selection(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "merlins_crystal"
        pd["quests"]["merlins_crystal"] = {"started": True, "progress": 3, "completed": False}
        pd["attack_level"] = 50
        pd["strength_level"] = 50
        pd["defense_level"] = 50
        pd["constitution_level"] = 50
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Battle required: Sir Mordred level 39"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_merlins_crystal")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

        action.click()
        QApplication.processEvents()
        self.assertIn("merlins_crystal", self._quest_calls)

    def test_quests_tab_allows_identical_source_generated_combat_gate_selection(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "elemental_workshop_i"
        pd["inventory"].update({"Thread": 1, "Leather": 1})
        pd["quests"]["elemental_workshop_i"] = {"started": True, "progress": 2, "completed": False}
        pd["attack_level"] = 40
        pd["strength_level"] = 40
        pd["defense_level"] = 40
        pd["constitution_level"] = 40
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = (
            "Blocked: Action required: Complete Elemental Workshop I stage 2 objective, "
            "Battle required: Earth Elemental level 35"
        )
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_elemental_workshop_i")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

        action.click()
        QApplication.processEvents()
        self.assertIn("elemental_workshop_i", self._quest_calls)

    def test_quests_tab_allows_beast_fallback_ranged_combat_gate_selection(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "toktz_ket_dill"
        pd["quests"]["toktz_ket_dill"] = {"started": True, "progress": 6, "completed": False}
        pd["attack_level"] = 50
        pd["strength_level"] = 50
        pd["defense_level"] = 50
        pd["constitution_level"] = 50
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = (
            "Blocked: Action required: Complete TokTz-Ket-Dill stage 6 objective, "
            "This fight is not modelled yet (combat stats missing): TokTz-Ket-Dill level 100, "
            "Battle required: Lava monster level 47 x2, +1 more"
        )
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_toktz_ket_dill")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

        action.click()
        QApplication.processEvents()
        self.assertIn("toktz_ket_dill", self._quest_calls)

    def test_quests_tab_allows_no_combat_levels_beast_stat_gate_selection(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "forgiveness_of_a_chaos_dwarf"
        pd["quests"]["forgiveness_of_a_chaos_dwarf"] = {"started": True, "progress": 4, "completed": False}
        pd["attack_level"] = 80
        pd["strength_level"] = 80
        pd["defense_level"] = 80
        pd["constitution_level"] = 80
        pd["prayer_level"] = 80
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Battle required: Chaos dwarf hand cannoneer level 100"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_forgiveness_of_a_chaos_dwarf")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

        action.click()
        QApplication.processEvents()
        self.assertIn("forgiveness_of_a_chaos_dwarf", self._quest_calls)

    def test_quests_tab_shows_remaining_combat_quantity_after_partial_resolution(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "toktz_ket_dill"
        pd["quests"]["toktz_ket_dill"] = {"started": True, "progress": 6, "completed": False}
        pd["quest_combat_encounter_counts"] = {"toktz_ket_dill": {"toktz_ket_dill_lava_monster_47": 1}}
        pd["attack_level"] = 50
        pd["strength_level"] = 50
        pd["defense_level"] = 50
        pd["constitution_level"] = 50
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = (
            "Blocked: Action required: Complete TokTz-Ket-Dill stage 6 objective, "
            "This fight is not modelled yet (combat stats missing): TokTz-Ket-Dill level 100, "
            "Battle required: Lava monster level 47, +1 more"
        )
        self.assertIn(expected, labels)

    def test_quests_tab_keeps_historical_metadata_only_combat_rows_blocked(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "fight_arena"
        pd["quests"]["fight_arena"] = {"started": True, "progress": 8, "completed": False}
        pd["attack_level"] = 150
        pd["strength_level"] = 150
        pd["defense_level"] = 150
        pd["constitution_level"] = 150
        pd["prayer_level"] = 150
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: This fight is not modelled yet (combat stats missing): Khazard ogre level 63"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_fight_arena")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())

    def test_quests_tab_allows_fight_arena_bouncer_gate_selection(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "fight_arena"
        pd["quests"]["fight_arena"] = {"started": True, "progress": 10, "completed": False}
        pd["quest_combat_encounters"] = {
            "fight_arena": ["fight_arena_khazard_ogre_63", "fight_arena_khazard_scorpion_44"]
        }
        pd["attack_level"] = 150
        pd["strength_level"] = 150
        pd["defense_level"] = 150
        pd["constitution_level"] = 150
        pd["prayer_level"] = 150
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Battle required: Bouncer level 137"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_fight_arena")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

    def test_quests_tab_allows_witchs_house_form_combat_gate_selection(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "witchs_house"
        pd["quests"]["witchs_house"] = {"started": True, "progress": 12, "completed": False}
        pd["attack_level"] = 60
        pd["strength_level"] = 60
        pd["defense_level"] = 60
        pd["constitution_level"] = 60
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = (
            "Blocked: Battle required: Witch's experiment (Skavid form) level 19, "
            "Battle required: Witch's experiment (Spider form) level 30, "
            "Battle required: Witch's experiment (Bear form) level 42, +1 more"
        )
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_witchs_house")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

        action.click()
        QApplication.processEvents()
        self.assertIn("witchs_house", self._quest_calls)

    def test_quests_tab_allows_style_aware_magic_combat_gate_selection(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "another_slice_of_h_a_m"
        pd["quests"]["another_slice_of_h_a_m"] = {"started": True, "progress": 4, "completed": False}
        pd["quest_combat_encounters"] = {"another_slice_of_h_a_m": ["another_slice_of_h_a_m_sigmund_64"]}
        pd["attack_level"] = 40
        pd["strength_level"] = 40
        pd["defense_level"] = 40
        pd["constitution_level"] = 40
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = (
            "Blocked: Action required: Complete Another Slice of H.A.M. stage 4 objective, "
            "Battle required: H.A.M. mage level 30, "
            "Battle required: H.A.M. ranger level 30"
        )
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_another_slice_of_h_a_m")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

        action.click()
        QApplication.processEvents()
        self.assertIn("another_slice_of_h_a_m", self._quest_calls)

    def test_quests_tab_shows_split_golem_combat_gates(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "spirits_of_the_elid"
        pd["quests"]["spirits_of_the_elid"] = {"started": True, "progress": 4, "completed": False}
        pd["attack_level"] = 90
        pd["strength_level"] = 90
        pd["defense_level"] = 90
        pd["constitution_level"] = 90
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = (
            "Blocked: Action required: Complete Spirits of the Elid stage 4 objective, "
            "Battle required: Black golem level 75, "
            "Battle required: White golem level 75, +1 more"
        )
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_spirits_of_the_elid")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

        action.click()
        QApplication.processEvents()
        self.assertIn("spirits_of_the_elid", self._quest_calls)

    def test_quests_tab_shows_a_souls_bane_split_combat_gates(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "a_souls_bane"
        pd["quests"]["a_souls_bane"] = {"started": True, "progress": 3, "completed": False}
        pd["quest_action_proofs"] = ["Fill the rage meter with an anger weapon"]
        pd["attack_level"] = 100
        pd["strength_level"] = 100
        pd["defense_level"] = 100
        pd["constitution_level"] = 100
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = (
            "Blocked: Battle required: Fear reaper level 42 x5, "
            "Battle required: Confusion beast level 43 x5, "
            "Battle required: Hopeless creature level 40 x3"
        )
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_a_souls_bane")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

        action.click()
        QApplication.processEvents()
        self.assertIn("a_souls_bane", self._quest_calls)

    def test_quests_tab_allows_stolen_hearts_mercenary_stage_selection(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "stolen_hearts"
        pd["quests"]["stolen_hearts"] = {
            "started": True,
            "progress": 3,
            "completed": False,
        }
        pd["attack_level"] = 99
        pd["strength_level"] = 99
        pd["defense_level"] = 99
        pd["constitution_level"] = 99
        pd["ranged_level"] = 99
        pd["magic_level"] = 99
        pd["prayer_level"] = 99
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [label.text() for label in dialog.findChildren(QLabel)]
        self.assertIn(
            (
                "Blocked: Battle required: Mercenary Joe level 2, "
                "Battle required: Skulls mercenary level 2 x2"
            ),
            labels,
        )
        action = dialog.findChild(QPushButton, "questAction_stolen_hearts")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())
        self.assertNotIn("Complete Stolen Hearts stage", action.toolTip())

        action.click()
        QApplication.processEvents()
        self.assertIn("stolen_hearts", self._quest_calls)

    def test_quests_tab_allows_diamond_in_the_rough_ambush_selection(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "diamond_in_the_rough"
        pd["inventory"] = {"Heavy weight": 1}
        pd["quests"]["stolen_hearts"] = {
            "started": True,
            "progress": 6,
            "completed": True,
        }
        pd["quests"]["diamond_in_the_rough"] = {
            "started": True,
            "progress": 2,
            "completed": False,
        }
        pd["attack_level"] = 99
        pd["strength_level"] = 99
        pd["defense_level"] = 99
        pd["constitution_level"] = 99
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [label.text() for label in dialog.findChildren(QLabel)]
        self.assertIn(
            (
                "Blocked: Battle required: Bandit (Diamond in the Rough) level 2 x5, "
                "Battle required: Bandit king level 3"
            ),
            labels,
        )
        action = dialog.findChild(QPushButton, "questAction_diamond_in_the_rough")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())
        self.assertNotIn("Complete Diamond in the Rough stage", action.toolTip())

        action.click()
        QApplication.processEvents()
        self.assertIn("diamond_in_the_rough", self._quest_calls)

    def test_quests_tab_allows_icthlarins_canopic_guardian_selection(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "icthlarins_little_helper"
        pd["inventory"] = {}
        pd["quests"]["icthlarins_little_helper"] = {
            "started": True,
            "progress": 4,
            "completed": False,
        }
        pd["attack_level"] = 99
        pd["strength_level"] = 99
        pd["defense_level"] = 99
        pd["constitution_level"] = 99
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [label.text() for label in dialog.findChildren(QLabel)]
        self.assertIn("Blocked: Battle required: Canopic guardian level 81", labels)
        action = dialog.findChild(QPushButton, "questAction_icthlarins_little_helper")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())
        self.assertNotIn("Complete Icthlarin's Little Helper stage", action.toolTip())

        action.click()
        QApplication.processEvents()
        self.assertIn("icthlarins_little_helper", self._quest_calls)

    def test_quests_tab_surfaces_smoking_kills_boss_at_quest_combat_requirement(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "smoking_kills"
        pd["inventory"] = {"Masked earmuffs": 1}
        pd["quests"]["smoking_kills"] = {
            "started": True,
            "progress": 11,
            "completed": False,
        }
        pd["attack_level"] = 74
        pd["strength_level"] = 74
        pd["defense_level"] = 74
        pd["constitution_level"] = 74
        pd["ranged_level"] = 1
        pd["magic_level"] = 1
        pd["prayer_level"] = 1
        pd["summoning_level"] = 1
        dialog = self._open(pd)
        _open_quests_tab(dialog)
        _expand_quest_card(dialog, "smoking_kills")

        labels = [label.text() for label in dialog.findChildren(QLabel)]
        self.assertIn("Blocked: Battle required: Banshee Mistress level 111", labels)
        self.assertIn(
            "At half health the Banshee Mistress calls four level 141 Insectoid Assassins into the same battle.",
            labels,
        )
        action = dialog.findChild(QPushButton, "questAction_smoking_kills")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())
        self.assertNotIn("Complete Smoking Kills stage", action.toolTip())

        action.click()
        QApplication.processEvents()
        self.assertIn("smoking_kills", self._quest_calls)

    def test_quests_tab_surfaces_shilo_village_three_form_boss_chain(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "shilo_village"
        pd["inventory"] = {"Bone key": 1, "Beads of the dead": 1}
        pd["quests"]["shilo_village"] = {
            "started": True,
            "progress": 10,
            "completed": False,
        }
        for level_key in (
            "attack_level",
            "strength_level",
            "defense_level",
            "constitution_level",
            "ranged_level",
            "magic_level",
            "prayer_level",
        ):
            pd[level_key] = 200
        dialog = self._open(pd)
        _open_quests_tab(dialog)
        _expand_quest_card(dialog, "shilo_village")

        labels = [label.text() for label in dialog.findChildren(QLabel)]
        combat_status = next(label for label in labels if label.startswith("Blocked: Battle required: Nazastarool"))
        for encounter_text in (
            "Nazastarool (Zombie) level 91",
            "Nazastarool (Skeleton) level 68",
            "Nazastarool (Ghost) level 93",
        ):
            self.assertIn(encounter_text, combat_status)
        self.assertIn(
            "Nazastarool will return as a zombie, skeleton, and ghost before yielding Rashiliyia's corpse.",
            labels,
        )
        action = dialog.findChild(QPushButton, "questAction_shilo_village")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())
        self.assertNotIn("Complete Shilo Village stage", action.toolTip())

        action.click()
        QApplication.processEvents()
        self.assertIn("shilo_village", self._quest_calls)

    def test_quests_tab_allows_conflict_overridden_dad_combat_gate_selection(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Coins": 12}
        pd["current_quest"] = "troll_stronghold"
        pd["quests"]["troll_stronghold"] = {"started": True, "progress": 2, "completed": False}
        pd["quest_combat_encounters"] = {
            "troll_stronghold": ["troll_stronghold_twig_troll_71", "troll_stronghold_troll_general_171"]
        }
        pd["attack_level"] = 100
        pd["strength_level"] = 100
        pd["defense_level"] = 100
        pd["constitution_level"] = 100
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = (
            "Blocked: Action required: Complete Troll Stronghold stage 2 objective, "
            "Battle required: Dad level 101"
        )
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_troll_stronghold")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

        action.click()
        QApplication.processEvents()
        self.assertIn("troll_stronghold", self._quest_calls)

    def test_quests_tab_allows_source_backed_focused_combat_override(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "the_restless_ghost"
        pd["inventory"]["Muddy skull"] = 1
        pd["quests"]["the_restless_ghost"] = {"started": True, "progress": 4, "completed": False}
        pd["quest_action_proofs"] = ["Return the muddy skull to the ghost's coffin"]
        pd["attack_level"] = 20
        pd["strength_level"] = 20
        pd["defense_level"] = 20
        pd["constitution_level"] = 20
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Battle required: Skeleton warlock level 11"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_the_restless_ghost")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

        action.click()
        QApplication.processEvents()
        self.assertIn("the_restless_ghost", self._quest_calls)
