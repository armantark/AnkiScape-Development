from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _expand_quest_card,
    _find_named_line_edit,
    _make_player_data,
    _open_quests_tab,
    copy,
    patch,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QCheckBox, QComboBox, QLabel, QPushButton, QWidget
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_quests_tab_starts_rune_mysteries_via_quest_action(self) -> None:
        pd = _make_player_data()
        pd["quests"]["rune_mysteries"] = {"started": False, "progress": 0, "completed": False}
        dialog = self._open(pd)
        _open_quests_tab(dialog)
        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertIn("Rune Mysteries", labels)
        self.assertIn("Quest points: 0", labels)

        start_btn = dialog.findChild(QPushButton, "questAction_rune_mysteries")
        self.assertIsNotNone(start_btn)
        start_btn.click()
        QApplication.processEvents()
        self.assertEqual(self._quest_calls[-1], "rune_mysteries")
        self.assertEqual(start_btn.text(), "Currently active")
        self.assertFalse(start_btn.isEnabled())

    def test_quests_tab_defaults_release_sort_and_collapses_completed_journals(self) -> None:
        pd = _make_player_data()
        pd["quests"]["rune_mysteries"] = {"started": True, "progress": 6, "completed": True}
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        sort_combo = dialog.findChild(QComboBox, "questSortCombo")
        self.assertIsNotNone(sort_combo)
        self.assertEqual(sort_combo.currentText(), "Release Order")
        self.assertIn("Difficulty", [sort_combo.itemText(i) for i in range(sort_combo.count())])
        self.assertIn("Length", [sort_combo.itemText(i) for i in range(sort_combo.count())])
        quest_cards = [
            widget for widget in dialog.findChildren(QWidget)
            if widget.objectName().startswith("questCard_")
        ]
        self.assertGreaterEqual(len(quest_cards), 194)

        body = dialog.findChild(QWidget, "questBody_rune_mysteries")
        toggle = dialog.findChild(QPushButton, "questToggle_rune_mysteries")
        self.assertIsNotNone(body)
        self.assertIsNotNone(toggle)
        self.assertTrue(body.isHidden())
        toggle.click()
        QApplication.processEvents()
        self.assertFalse(body.isHidden())

    def test_quests_tab_filters_completed_and_unable_to_start_cards(self) -> None:
        pd = _make_player_data()
        pd["quests"]["rune_mysteries"] = {"started": True, "progress": 6, "completed": True}
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        hide_completed = dialog.findChild(QCheckBox, "questHideCompletedCheck")
        hide_locked = dialog.findChild(QCheckBox, "questHideLockedCheck")
        summary = dialog.findChild(QLabel, "questFilterSummaryLabel")
        self.assertIsNotNone(hide_completed)
        self.assertIsNotNone(hide_locked)
        self.assertIsNotNone(summary)
        self.assertIsNotNone(dialog.findChild(QWidget, "questCard_rune_mysteries"))
        self.assertIsNotNone(dialog.findChild(QWidget, "questCard_lost_city"))
        self.assertIsNotNone(dialog.findChild(QWidget, "questCard_cooks_assistant"))

        hide_completed.setChecked(True)
        QApplication.processEvents()
        self.assertIsNone(dialog.findChild(QWidget, "questCard_rune_mysteries"))
        self.assertIsNotNone(dialog.findChild(QWidget, "questCard_lost_city"))

        hide_locked.setChecked(True)
        QApplication.processEvents()
        self.assertIsNone(dialog.findChild(QWidget, "questCard_lost_city"))
        self.assertIsNotNone(dialog.findChild(QWidget, "questCard_cooks_assistant"))
        self.assertRegex(summary.text(), r"^Showing \d+/198$")

    def test_quests_tab_shows_stage_blockers_without_hiding_started_quests(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "the_knights_sword"
        pd["quests"]["the_knights_sword"] = {"started": True, "progress": 2, "completed": False}
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertIn("Blocked: Needs Redberry pie x1", labels)
        action = dialog.findChild(QPushButton, "questAction_the_knights_sword")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Needs Redberry pie x1", action.toolTip())

        hide_locked = dialog.findChild(QCheckBox, "questHideLockedCheck")
        self.assertIsNotNone(hide_locked)
        hide_locked.setChecked(True)
        QApplication.processEvents()
        self.assertIsNotNone(dialog.findChild(QWidget, "questCard_the_knights_sword"))

    def test_quests_tab_shows_shield_of_arrav_route_branch_blockers(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "shield_of_arrav"
        pd["quests"]["shield_of_arrav"] = {"started": True, "progress": 4, "completed": False}
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Choose path: Phoenix Gang or Black Arm Gang"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_shield_of_arrav")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Phoenix Gang", action.toolTip())
        phoenix = dialog.findChild(QPushButton, "questChoice_shield_of_arrav_join_the_phoenix_gang")
        black_arm = dialog.findChild(QPushButton, "questChoice_shield_of_arrav_join_the_black_arm_gang")
        self.assertIsNotNone(phoenix)
        self.assertIsNotNone(black_arm)
        self.assertEqual(phoenix.text(), "Phoenix Gang")
        self.assertEqual(black_arm.text(), "Black Arm Gang")
        black_arm.click()
        QApplication.processEvents()
        self.assertEqual(self._quest_choice_calls[-1], ("shield_of_arrav", "Join the Black Arm Gang"))

    def test_quests_tab_shows_demon_slayer_item_stage_blocker(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "demon_slayer"
        pd["quests"]["demon_slayer"] = {"started": True, "progress": 3, "completed": False}
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Needs Bucket of water x1"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_demon_slayer")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Bucket of water x1", action.toolTip())

    def test_quests_tab_shows_ernest_machine_part_stage_blocker(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "ernest_the_chicken"
        pd["quests"]["ernest_the_chicken"] = {"started": True, "progress": 3, "completed": False}
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Needs Fish food x1, Needs Poison x1"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_ernest_the_chicken")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Fish food x1", action.toolTip())

    def test_quests_tab_shows_dragon_slayer_oracle_item_option_blocker(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {
            "Wizard's mind bomb": 1,
            "Silk": 1,
            "Bowl (unfired)": 1,
        }
        pd["current_quest"] = "dragon_slayer"
        pd["quests"]["dragon_slayer"] = {"started": True, "progress": 8, "completed": False}
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Needs Crayfish cage x1 or Lobster pot x1"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_dragon_slayer")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Crayfish cage x1 or Lobster pot x1", action.toolTip())

    def test_quests_tab_shows_fishing_contest_current_stage_blocker(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Fishing rod": 1}
        pd["current_quest"] = "fishing_contest"
        pd["quests"]["fishing_contest"] = {"started": True, "progress": 4, "completed": False}
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Needs Red vine worm x1 or Fishing bait x1"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_fishing_contest")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Red vine worm x1 or Fishing bait x1", action.toolTip())

    def test_quests_tab_shows_another_slice_stage_blocker_overflow(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "another_slice_of_h_a_m"
        pd["quests"]["another_slice_of_h_a_m"] = {
            "started": True,
            "progress": 1,
            "completed": False,
        }
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = (
            "Blocked: Needs Trowel x1, Needs Specimen brush x1, "
            "Needs HAM ranger x30 or HAM mage x30, +1 more"
        )
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_another_slice_of_h_a_m")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertEqual(action.toolTip(), expected)

    def test_quests_tab_shows_plague_city_hangover_cure_blocker(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Bucket of milk": 1}
        pd["current_quest"] = "plague_city"
        pd["quests"]["plague_city"] = {"started": True, "progress": 14, "completed": False}
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        # The pestle and mortar is on the tool belt, so only the ingredients block.
        expected = "Blocked: Needs Chocolate dust x1, Needs Snape grass x1"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_plague_city")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Needs Chocolate dust x1", action.toolTip())
        self.assertIn("Needs Snape grass x1", action.toolTip())

    def test_quests_tab_shows_biohazard_guidor_disguise_blocker(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {
            "Liquid honey": 1,
            "Ethenea": 1,
            "Sulphuric broline": 1,
            "Plague sample": 1,
            "Touch paper": 1,
        }
        pd["current_quest"] = "biohazard"
        pd["quests"]["biohazard"] = {"started": True, "progress": 11, "completed": False}
        pd["quest_route_states"] = {
            "biohazard": ["Reach Guidor's house without Varrock guards confiscating the vials"]
        }
        pd["quest_action_proofs"] = [
            "Give sulphuric broline to Hops",
            "Give ethenea to Da Vinci",
            "Give liquid honey to Chancy",
            "Collect the sulphuric broline from Hops in Varrock",
            "Collect the ethenea from Da Vinci in Varrock",
            "Collect the liquid honey from Chancy in Varrock",
            "Enter Guidor's room wearing priest gowns",
            "Give Guidor the vials, plague sample, and touch paper",
        ]
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertIn("Blocked: Needs Priest gown x2", labels)
        action = dialog.findChild(QPushButton, "questAction_biohazard")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Needs Priest gown x2", action.toolTip())

    def test_quests_tab_shows_heroes_black_arm_disguise_blocker(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Id papers": 1}
        pd["equipment"] = {"head": "Black full helm", "body": "Black platebody"}
        pd["current_quest"] = "heroes_quest"
        pd["quests"]["heroes_quest"] = {"started": True, "progress": 10, "completed": False}
        pd["quest_route_states"] = {"heroes_quest": ["Join the Black Arm Gang"]}
        pd["quest_action_proofs"] = ["Show the Id papers to Garv", "Search Scarface Pete's candlestick chest"]
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertIn("Blocked: Needs Black platelegs", labels)
        action = dialog.findChild(QPushButton, "questAction_heroes_quest")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Needs Black platelegs", action.toolTip())

    def test_quests_tab_shows_family_crest_jewellery_blocker(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {
            "Perfect gold bar": 2,
            "Ruby": 1,
            "Ring mould": 1,
            "Necklace mould": 1,
        }
        pd["current_quest"] = "family_crest"
        pd["quests"]["family_crest"] = {"started": True, "progress": 10, "completed": False}
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertIn("Blocked: Needs Ruby x2", labels)
        action = dialog.findChild(QPushButton, "questAction_family_crest")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Needs Ruby x2", action.toolTip())

    def test_quests_tab_shows_temple_of_ikov_fire_warrior_bow_blocker(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Ice arrows": 1}
        pd["current_quest"] = "temple_of_ikov"
        pd["quests"]["temple_of_ikov"] = {"started": True, "progress": 7, "completed": False}
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected_prefix = "Blocked: Needs Yew shortbow x1 or Yew longbow x1"
        self.assertTrue(
            any(label.startswith(expected_prefix) for label in labels),
            f"Expected Temple bow blocker in labels: {labels}",
        )
        action = dialog.findChild(QPushButton, "questAction_temple_of_ikov")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Needs Yew shortbow x1", action.toolTip())

    def test_quests_tab_shows_holy_grail_excalibur_stage_blocker(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Magic whistle": 1}
        pd["current_quest"] = "holy_grail"
        pd["quests"]["holy_grail"] = {"started": True, "progress": 5, "completed": False}
        pd["quest_route_states"] = {"holy_grail": ["Reach the Fisher Realm crossing at the six stone heads"]}
        pd["quest_action_proofs"] = ["Blow the Magic whistle at the six stone heads"]
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertTrue(
            any(label.startswith("Blocked: Needs Excalibur") for label in labels),
            f"Expected Holy Grail Excalibur blocker in labels: {labels}",
        )
        action = dialog.findChild(QPushButton, "questAction_holy_grail")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Needs Excalibur", action.toolTip())

    def test_quests_tab_shows_cooks_assistant_container_stage_blocker(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "cooks_assistant"
        pd["quests"]["cooks_assistant"] = {"started": True, "progress": 1, "completed": False}
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertNotIn(
            "Blocked: Needs Top-quality milk x1, Needs Extra fine flour x1, Needs Super large egg x1",
            labels,
        )
        action = dialog.findChild(QPushButton, "questAction_cooks_assistant")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

        dialog.close()
        pd = _make_player_data()
        pd["current_quest"] = "cooks_assistant"
        pd["quests"]["cooks_assistant"] = {"started": True, "progress": 2, "completed": False}
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertIn(
            "Blocked: Needs Bucket x1",
            labels,
        )
        action = dialog.findChild(QPushButton, "questAction_cooks_assistant")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Bucket x1", action.toolTip())

    def test_quests_tab_shows_witchs_house_mouse_stage_blocker(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Magnet": 1}
        pd["current_quest"] = "witchs_house"
        pd["quests"]["witchs_house"] = {"started": True, "progress": 4, "completed": False}
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Needs Cheese x1"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_witchs_house")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Needs Cheese x1", action.toolTip())
        self.assertNotIn("Use cheese on the mouse hole", action.toolTip())

    def test_quests_tab_shows_merlins_crystal_wax_stage_blocker(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Bucket": 1}
        pd["current_quest"] = "merlins_crystal"
        pd["quests"]["merlins_crystal"] = {"started": True, "progress": 4, "completed": False}
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Needs Insect repellent x1"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_merlins_crystal")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Insect repellent x1", action.toolTip())

    def test_quests_tab_shows_required_action_stage_blocker(self) -> None:
        from ankiscape.ui import ui_tab_quests

        quest_id = "required_action_widget_fixture"
        required_action = "Complete the required-action widget fixture"
        quest_data = copy.deepcopy(ui_tab_quests.QUEST_DATA)
        fixture = copy.deepcopy(quest_data["rune_mysteries"])
        fixture.update(
            {
                "id": quest_id,
                "display_name": "Required-action widget fixture",
                "stages": 1,
                "point_reward": 0,
                "rewards": {},
                "requirements": (),
                "required_items": {},
                "start_inventory": {},
                "required_quests": (),
                "required_skills": (),
                "required_quest_points": 0,
                "xp_rewards": (),
                "lamp_rewards": (),
                "combat": "",
                "unlocks": (),
                "stage_requirements": (
                    {
                        "stage": 1,
                        "description": "Require a constructed action blocker.",
                        "required_actions": (required_action,),
                    },
                ),
                "choices": (),
            }
        )
        quest_data[quest_id] = fixture
        pd = _make_player_data()
        pd["quests"][quest_id] = {"started": True, "progress": 0, "completed": False}

        with (
            patch.object(self._ui, "QUEST_DATA", quest_data),
            patch.object(ui_tab_quests, "QUEST_DATA", quest_data),
        ):
            dialog = self._open(pd)
            _open_quests_tab(dialog)

            labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
            expected = "Blocked: Action required: Complete the required-action widget fixture"
            self.assertIn(expected, labels)
            action = dialog.findChild(QPushButton, f"questAction_{quest_id}")
            self.assertIsNotNone(action)
            self.assertFalse(action.isEnabled())
            self.assertEqual(action.toolTip(), expected)

    def test_quests_tab_vampyre_slayer_easy_items_are_not_prestart_requirements(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "vampyre_slayer"
        pd["quests"]["vampyre_slayer"] = {"started": True, "progress": 1, "completed": False}
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        card = dialog.findChild(QWidget, "questCard_vampyre_slayer")
        self.assertIsNotNone(card)
        labels = [lbl.text() for lbl in card.findChildren(QLabel)]
        self.assertFalse(any(text.startswith("Blocked:") for text in labels))
        self.assertFalse(any(text.startswith("Requires:") for text in labels))

    def test_quests_tab_shows_priest_in_peril_essence_stage_blocker(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "priest_in_peril"
        pd["quests"]["priest_in_peril"] = {"started": True, "progress": 8, "completed": False}
        pd["inventory"] = {"Pure essence": 24}
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Needs Rune essence x50 or Pure essence x25"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_priest_in_peril")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Pure essence x25", action.toolTip())

    def test_quests_tab_lists_stage_items_before_knights_sword_start(self) -> None:
        pd = _make_player_data()
        pd["mining_level"] = 10
        dialog = self._open(pd)
        _open_quests_tab(dialog)
        _expand_quest_card(dialog, "the_knights_sword")

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertIn(
            "Requires: Mining 10, Used during quest: Redberry pie x1, Blurite ore x1, Iron bar x2",
            labels,
        )

    def test_quests_tab_filters_by_catalog_metadata(self) -> None:
        dialog = self._open(_make_player_data())
        _open_quests_tab(dialog)

        access_filter = dialog.findChild(QComboBox, "questAccessFilterCombo")
        difficulty_filter = dialog.findChild(QComboBox, "questDifficultyFilterCombo")
        length_filter = dialog.findChild(QComboBox, "questLengthFilterCombo")
        timeline_filter = dialog.findChild(QComboBox, "questTimelineFilterCombo")
        self.assertIsNotNone(access_filter)
        self.assertIsNotNone(difficulty_filter)
        self.assertIsNotNone(length_filter)
        self.assertIsNotNone(timeline_filter)
        self.assertIn("Members quests", [access_filter.itemText(i) for i in range(access_filter.count())])
        self.assertIn("Grandmaster", [difficulty_filter.itemText(i) for i in range(difficulty_filter.count())])
        self.assertIn("Long", [length_filter.itemText(i) for i in range(length_filter.count())])
        self.assertIn("Fifth Age", [timeline_filter.itemText(i) for i in range(timeline_filter.count())])

        access_filter.setCurrentText("Free quests")
        QApplication.processEvents()
        self.assertIsNotNone(dialog.findChild(QWidget, "questCard_cooks_assistant"))
        self.assertIsNone(dialog.findChild(QWidget, "questCard_lost_city"))

        access_filter.setCurrentText("All access")
        difficulty_filter.setCurrentText("Grandmaster")
        QApplication.processEvents()
        self.assertIsNone(dialog.findChild(QWidget, "questCard_cooks_assistant"))
        self.assertIsNotNone(dialog.findChild(QWidget, "questCard_while_guthix_sleeps"))

    def test_quests_tab_groups_miniquests_under_their_own_heading(self) -> None:
        dialog = self._open(_make_player_data())
        _open_quests_tab(dialog)

        heading = dialog.findChild(QLabel, "questSection_Miniquests")
        self.assertIsNotNone(heading)
        self.assertEqual(heading.text(), "Miniquests")
        self.assertIsNotNone(dialog.findChild(QLabel, "questSection_Quests"))
        self.assertIsNotNone(dialog.findChild(QWidget, "questCard_hunt_for_surok"))
        self.assertIsNotNone(dialog.findChild(QWidget, "questCard_lair_of_tarn_razorlor"))

        # The heading must sit above its own rows and below every ordinary quest.
        layout = dialog.findChild(QWidget, "questCard_cooks_assistant").parentWidget().layout()
        order = [layout.itemAt(i).widget().objectName() for i in range(layout.count() - 1)]
        self.assertLess(order.index("questSection_Miniquests"), order.index("questCard_hunt_for_surok"))
        self.assertGreater(order.index("questSection_Miniquests"), order.index("questCard_cooks_assistant"))

        # A search that hits only miniquests leaves one group, so the heading goes.
        search = _find_named_line_edit(dialog, "questSearchInput")
        search.setText("hunt_for_surok")
        QApplication.processEvents()
        self.assertIsNotNone(dialog.findChild(QWidget, "questCard_hunt_for_surok"))
        self.assertIsNone(dialog.findChild(QLabel, "questSection_Miniquests"))

    def test_quest_search_composes_with_filters_and_has_shared_empty_state(self) -> None:
        dialog = self._open(_make_player_data())
        _open_quests_tab(dialog)
        search = _find_named_line_edit(dialog, "questSearchInput")
        summary = dialog.findChild(QLabel, "questFilterSummaryLabel")

        search.setText("while_guthix_sleeps")
        QApplication.processEvents()
        self.assertIsNotNone(dialog.findChild(QWidget, "questCard_while_guthix_sleeps"))
        self.assertEqual(summary.text(), "Showing 1/198")

        hide_locked = dialog.findChild(QCheckBox, "questHideLockedCheck")
        hide_locked.setChecked(True)
        QApplication.processEvents()
        self.assertEqual(summary.text(), "Showing 0/198")
        self.assertIsNotNone(dialog.findChild(QLabel, "questEmptyFilterLabel"))

        hide_locked.setChecked(False)
        search.clear()
        QApplication.processEvents()
        self.assertEqual(summary.text(), "Showing 198/198")
        dialog.deleteLater()
