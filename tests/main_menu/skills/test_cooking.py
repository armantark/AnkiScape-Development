from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _ADDON_DIR,
    _cooking_family_node,
    _cooking_row,
    _find_artisan_skill_list,
    _goto_cooking,
    _icon_pixels,
    _make_player_data,
    _panel_title,
    os,
    patch,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QAbstractItemView, QApplication, QCheckBox, QComboBox, QIcon, QLabel, QMessageBox, QPushButton, QToolButton, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_cooking_is_selectable_and_shows_grouped_source_targets(self) -> None:
        pd = _make_player_data()
        pd["cooking_level"] = 33
        pd["inventory"] = {"Raw shrimps": 2}
        pd["current_cooking"] = "cook_shrimps"
        dialog = self._open(pd)
        tree = _goto_cooking(dialog)
        skill_list = _find_artisan_skill_list(dialog)
        cooking_item = next(
            skill_list.item(i)
            for i in range(skill_list.count())
            if skill_list.item(i).text() == "Cooking"
        )
        title = _panel_title(dialog)
        self.assertTrue(
            title.startswith("Cooking"),
            f"panel did not switch to Cooking; still shows {title!r}",
        )
        self.assertFalse(cooking_item.icon().isNull(), "Cooking skill row has no icon")
        self.assertEqual(
            _icon_pixels(cooking_item.icon()),
            _icon_pixels(QIcon(self._ui.skill_icon_path_for("Cooking"))),
            "Cooking skill row did not use icon/cooking_icon.png",
        )
        self.assertNotEqual(
            _icon_pixels(cooking_item.icon()),
            _icon_pixels(QIcon(os.path.join(_ADDON_DIR, "icon", "achievement_icon.png"))),
            "Cooking skill row fell back to the achievement icon",
        )

        family_roles = [
            tree.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole)
            for i in range(tree.topLevelItemCount())
        ]
        self.assertIn("__cooking_family__:fish", family_roles)
        self.assertIn("__cooking_family__:pies", family_roles)
        self.assertIn("__cooking_family__:karambwan", family_roles)

        shrimps = _cooking_row(tree, "cook_shrimps")
        shark = _cooking_row(tree, "cook_shark")
        wine = _cooking_row(tree, "make_wine")
        malt = _cooking_row(tree, "malt_barley")
        poison_karambwan = _cooking_row(tree, "cook_poison_karambwan")
        thorough_karambwan = _cooking_row(tree, "cook_karambwan_thoroughly")
        karambwanji = _cooking_row(tree, "cook_karambwanji")
        self.assertFalse(shrimps.isDisabled())
        self.assertFalse(shrimps.icon(0).isNull(), "Cooking target row has no icon")
        self.assertIn("Success output: Shrimps x1", shrimps.toolTip(0))
        self.assertIn("Burn output: Burnt shrimp x1, no XP", shrimps.toolTip(0))
        self.assertIn("Success chance:", shrimps.toolTip(0))
        self.assertTrue(shark.isDisabled())
        self.assertIn("Locked due to:", shark.toolTip(0))
        self.assertTrue(wine.isDisabled())
        self.assertIn("Bad output: Jug of bad wine x1, no XP", wine.toolTip(0))
        self.assertFalse(wine.icon(0).isNull())
        self.assertFalse(malt.isDisabled())
        self.assertFalse(malt.icon(0).isNull())
        self.assertIn("Cannot burn or fail", malt.toolTip(0))
        for row in (poison_karambwan, thorough_karambwan, karambwanji):
            self.assertTrue(row.isDisabled())
            self.assertFalse(row.icon(0).isNull())
        self.assertIn("Burn output: Burnt karambwan x1", poison_karambwan.toolTip(0))
        self.assertIn("Cannot burn or fail", thorough_karambwan.toolTip(0))
        self.assertIn("Burn output: Ashes x1", karambwanji.toolTip(0))

        tree.itemClicked.emit(shrimps, 0)
        QApplication.processEvents()
        self.assertEqual(self._cooking_calls[-1], "cook_shrimps")
        self.assertTrue(_cooking_family_node(tree, "fish").isExpanded())

    def test_cooking_details_expose_target_equipment_policy_and_recovery(self) -> None:
        from ankiscape.logic.cooking_gauntlets_logic import (
            recover_family_gauntlets_pure,
            set_cooking_equipment_choice_pure,
        )

        pd = _make_player_data()
        pd.update(
            {
                "cooking_level": 94,
                "current_cooking": "cook_shark",
                "family_gauntlet_enchantment": "cooking",
                "cooking_equipment_choices": {},
                "cooking_equipment_swap": {},
            }
        )
        pd["inventory"] = {"Raw shark": 1, "Cooking gauntlets": 0}
        pd["equipment"] = {}
        pd["quests"]["family_crest"] = {
            "started": True,
            "progress": 16,
            "completed": True,
        }
        policy_calls = []

        def set_policy(target_id, choice):
            policy_calls.append((target_id, choice))
            updated, ok = set_cooking_equipment_choice_pure(
                pd, target_id, choice
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return ok

        def gauntlet_command(command, _payload):
            self.assertEqual(command, "recover")
            updated, ok, message = recover_family_gauntlets_pure(pd)
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": message}

        dialog = self._open(
            pd,
            current_skill="Cooking",
            on_set_cooking_equipment_choice=set_policy,
            on_cooking_gauntlets_command=gauntlet_command,
        )
        dialog.show()
        QApplication.processEvents()
        details = dialog.findChild(QToolButton, "targetDetailsToggle")
        details.click()
        QApplication.processEvents()

        combo = dialog.findChild(
            QComboBox, "cookingEquipmentChoice::cook_shark"
        )
        self.assertIsNotNone(combo)
        self.assertEqual(combo.currentData(), "auto")
        self.assertIn("Casual", combo.currentText())
        combo.setCurrentIndex(combo.findData("none"))
        QApplication.processEvents()
        self.assertEqual(policy_calls[-1], ("cook_shark", "none"))

        recover = dialog.findChild(QPushButton, "recoverFamilyGauntletsAction")
        self.assertIsNotNone(recover)
        self.assertTrue(recover.isEnabled())
        self.assertEqual(recover.text(), "Recover Cooking gauntlets")
        recover.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Cooking gauntlets"], 1)
        visible_recovery_buttons = [
            button
            for button in dialog.findChildren(
                QPushButton, "recoverFamilyGauntletsAction"
            )
            if button.isVisibleTo(dialog)
        ]
        self.assertEqual(visible_recovery_buttons, [])
        dialog.deleteLater()

    def test_brawling_wilderness_toggle_coexists_with_cooking_policy(self) -> None:
        from ankiscape.data.brawling_gloves_data import BRAWLING_GLOVE_DATA
        from ankiscape.logic.brawling_gloves_logic import (
            set_brawling_wilderness_target_pure,
        )

        pd = _make_player_data()
        pd.update(
            {
                "cooking_level": 94,
                "current_cooking": "cook_shark",
                "cooking_equipment_choices": {},
                "cooking_equipment_swap": {},
                "brawling_wilderness_targets": {},
            }
        )
        item_name = BRAWLING_GLOVE_DATA["cooking"]["item_name"]
        pd["inventory"] = {"Raw shark": 1}
        pd["equipment"] = {"hands": item_name}
        calls = []

        def set_wilderness(skill_id, target_id, enabled):
            calls.append((skill_id, target_id, enabled))
            updated = set_brawling_wilderness_target_pure(
                pd, skill_id, target_id, enabled
            )
            pd.clear()
            pd.update(updated)
            return True

        dialog = self._open(
            pd,
            current_skill="Cooking",
            on_set_brawling_wilderness_target=set_wilderness,
        )
        dialog.show()
        QApplication.processEvents()
        details = dialog.findChild(QToolButton, "targetDetailsToggle")
        details.click()
        QApplication.processEvents()

        self.assertIsNotNone(
            dialog.findChild(QComboBox, "cookingEquipmentChoice::cook_shark")
        )
        charge = dialog.findChild(
            QLabel, "brawlingGloveState::cooking::cook_shark"
        )
        toggle = dialog.findChild(
            QCheckBox, "brawlingWildernessTargetToggle::cooking::cook_shark"
        )
        self.assertIsNotNone(charge)
        self.assertIn("1,109 actions remaining (of 1,109)", charge.text())
        self.assertIsNotNone(toggle)
        self.assertIn("1%", toggle.toolTip())

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            toggle.click()
            QApplication.processEvents()
        self.assertEqual(calls[-1], ("cooking", "cook_shark", True))
        dialog.deleteLater()

    def test_cooking_locked_rows_are_inert(self) -> None:
        pd = _make_player_data()
        pd["cooking_level"] = 1
        pd["inventory"] = {"Raw beef": 1}
        dialog = self._open(pd)
        tree = _goto_cooking(dialog)
        locked = _cooking_row(tree, "cook_shark")
        self.assertTrue(locked.isDisabled())
        before = list(self._cooking_calls)
        tree.itemClicked.emit(locked, 0)
        tree.itemActivated.emit(locked, 0)
        QApplication.processEvents()
        self.assertEqual(self._cooking_calls, before, "locked cooking target must not be selectable")

    def test_lava_eel_row_uses_existing_quest_asset_and_never_burns(self) -> None:
        pd = _make_player_data()
        pd["cooking_level"] = 53
        pd["inventory"] = {"Raw lava eel": 1}
        dialog = self._open(pd)
        tree = _goto_cooking(dialog)

        lava_eel = _cooking_row(tree, "cook_lava_eel")
        self.assertFalse(lava_eel.isDisabled())
        self.assertFalse(lava_eel.icon(0).isNull())
        self.assertIn("Cannot burn or fail.", lava_eel.toolTip(0))
        self.assertIn("Success chance: 100%", lava_eel.toolTip(0))

    def test_cheese_wheel_rows_explain_slice_all_and_use_period_art(self) -> None:
        pd = _make_player_data()
        pd["cooking_level"] = 48
        pd["inventory"] = {
            "Bucket of milk": 1,
            "Pat of butter": 1,
            "Cheese wheel": 1,
        }
        pd["current_cooking"] = "slice_cheese_wheel"
        dialog = self._open(pd)
        tree = _goto_cooking(dialog)

        dairy = _cooking_family_node(tree, "dairy")
        self.assertEqual(dairy.text(0), "Dairy  (3)")
        slice_row = _cooking_row(tree, "slice_cheese_wheel")
        self.assertFalse(slice_row.isDisabled())
        self.assertFalse(slice_row.icon(0).isNull())
        self.assertEqual(
            tree.selectionMode(),
            QAbstractItemView.SelectionMode.SingleSelection,
        )
        self.assertFalse(slice_row.isSelected())
        self.assertTrue(slice_row.font(0).bold())
        self.assertIn(
            "Success output: Cheese x5-35 (one Slice-all action)",
            slice_row.toolTip(0),
        )
        self.assertIn("Base XP: 4 per slice", slice_row.toolTip(0))
        milk_row = _cooking_row(tree, "churn_milk_cheese_wheel")
        self.assertIn("Also returns: Bucket x1", milk_row.toolTip(0))

        tree.itemClicked.emit(slice_row, 0)
        QApplication.processEvents()
        self.assertEqual(self._cooking_calls[-1], "slice_cheese_wheel")

    def test_cooking_region_quest_locks_are_inert(self) -> None:
        pd = _make_player_data()
        pd["cooking_level"] = 99
        pd["inventory"] = {
            "Slimy eel": 1,
            "Raw yak meat": 1,
            "Raw karambwan": 2,
            "Raw karambwanji": 1,
        }
        dialog = self._open(pd)
        tree = _goto_cooking(dialog)

        slimy_eel = _cooking_row(tree, "cook_slimy_eel")
        yak = _cooking_row(tree, "cook_yak")
        self.assertTrue(slimy_eel.isDisabled())
        self.assertIn("Priest in Peril", slimy_eel.toolTip(0))
        self.assertTrue(yak.isDisabled())
        self.assertIn("The Fremennik Isles", yak.toolTip(0))
        self.assertTrue(_cooking_row(tree, "cook_poison_karambwan").isDisabled())
        self.assertTrue(_cooking_row(tree, "cook_karambwan_thoroughly").isDisabled())
        self.assertTrue(_cooking_row(tree, "cook_karambwanji").isDisabled())

        before = list(self._cooking_calls)
        tree.itemClicked.emit(slimy_eel, 0)
        tree.itemActivated.emit(yak, 0)
        QApplication.processEvents()
        self.assertEqual(self._cooking_calls, before, "quest-locked cooking rows must not be selectable")

        pd["quests"]["priest_in_peril"] = {"started": True, "progress": 6, "completed": True}
        pd["quests"]["the_fremennik_isles"] = {"started": True, "progress": 6, "completed": True}
        pd["quests"]["tai_bwo_wannai_trio"] = {"started": True, "progress": 1, "completed": False}
        started_dialog = self._open(pd)
        started_tree = _goto_cooking(started_dialog)
        self.assertFalse(_cooking_row(started_tree, "cook_poison_karambwan").isDisabled())
        self.assertTrue(_cooking_row(started_tree, "cook_karambwan_thoroughly").isDisabled())
        self.assertTrue(_cooking_row(started_tree, "cook_karambwanji").isDisabled())

        pd["quests"]["tai_bwo_wannai_trio"] = {"started": True, "progress": 6, "completed": True}
        unlocked_dialog = self._open(pd)
        unlocked_tree = _goto_cooking(unlocked_dialog)
        self.assertFalse(_cooking_row(unlocked_tree, "cook_slimy_eel").isDisabled())
        self.assertFalse(_cooking_row(unlocked_tree, "cook_yak").isDisabled())
        self.assertFalse(_cooking_row(unlocked_tree, "cook_poison_karambwan").isDisabled())
        self.assertFalse(_cooking_row(unlocked_tree, "cook_karambwan_thoroughly").isDisabled())
        self.assertFalse(_cooking_row(unlocked_tree, "cook_karambwanji").isDisabled())
