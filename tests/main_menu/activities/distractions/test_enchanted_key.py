from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_named_button,
    _find_named_label,
    _find_named_widget,
    _make_player_data,
    _utility_row,
    replace,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QLabel
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_enchanted_key_card_renders_the_view_flags_and_selects_a_site(self) -> None:
        """The panel must render the gates the view owns, never re-derive them."""
        from ankiscape.data.enchanted_key_data import (
            ENCHANTED_KEY_ITEM,
            ENCHANTED_KEY_SITE_IDS,
            ENCHANTED_KEY_SPADE,
        )
        from ankiscape.logic.enchanted_key_logic import (
            default_enchanted_key_state_pure,
            enchanted_key_view_pure,
        )

        dialog = None
        try:
            pd = _make_player_data()
            pd["enchanted_key"] = default_enchanted_key_state_pure()
            pd["activity_session"] = {"active_id": ""}
            dialog = self._open(pd)
            activity_tree = self._open_activities(dialog)
            row = _utility_row(activity_tree, "enchanted_key")
            self.assertFalse(row.icon(0).isNull())
            activity_tree.setCurrentItem(row)
            activity_tree.itemActivated.emit(row, 0)
            QApplication.processEvents()

            panel = _find_named_widget(dialog, "enchantedKeyPanel")
            icon = panel.findChild(QLabel, "enchantedKeyIcon")
            status = _find_named_label(dialog, "enchantedKeyStatusChip")
            summary = _find_named_label(dialog, "enchantedKeySummary")
            roster = panel.findChild(QComboBox, "enchantedKeyRoster")
            primary = _find_named_button(dialog, "enchantedKeyPrimaryButton")
            replace = _find_named_button(dialog, "enchantedKeyReplaceButton")

            self.assertIsNotNone(icon.pixmap())
            self.assertFalse(icon.pixmap().isNull())
            self.assertEqual(status.text(), "LOCKED")
            self.assertIn("Making History", summary.text())
            self.assertEqual(roster.count(), len(ENCHANTED_KEY_SITE_IDS))
            self.assertFalse(primary.isEnabled())
            self.assertTrue(replace.isHidden())

            pd["quests"]["making_history"] = {
                "started": True,
                "progress": 4,
                "completed": True,
            }
            pd["inventory"][ENCHANTED_KEY_ITEM] = 1
            pd["inventory"][ENCHANTED_KEY_SPADE] = 1
            activity_tree.itemActivated.emit(row, 0)
            QApplication.processEvents()
            view = enchanted_key_view_pure(pd)
            self.assertEqual(status.text(), f"{len(ENCHANTED_KEY_SITE_IDS)} LEFT")
            self.assertIn(str(roster.currentData()), view["selectable_site_ids"])
            self.assertTrue(primary.isEnabled())

            chosen = str(roster.currentData())
            primary.click()
            QApplication.processEvents()
            self.assertEqual(
                self._enchanted_key_calls[-1],
                ("select_site", {"site_id": chosen}),
            )
            self.assertEqual(pd["enchanted_key"]["selected_site_id"], chosen)
            self.assertTrue(enchanted_key_view_pure(pd)["can_review"])
        finally:
            if dialog is not None:
                dialog.deleteLater()
