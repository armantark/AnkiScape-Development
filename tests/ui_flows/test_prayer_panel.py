"""The Prayer panel names the selected method and shows the altar mode box only for an altar."""

import unittest

import pkg_alias  # noqa: F401
from tests import test_main_menu_widget as _main_menu

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication, QComboBox, QLabel, QListWidget, QPushButton, QTreeWidget, QWidget

    from tests.ui_flows.qt_text_fit import text_fit_defects

# The owner's laptop dialog height.
_OWNER_SIZE = (900, 560)


def _pump() -> None:
    for _ in range(6):
        QApplication.processEvents()


def _open_prayer_panel(menu, player):
    """Show the main menu at the owner's size and open the Prayer skill panel."""
    dialog = menu._open(player, current_skill="Mining")
    dialog.show()
    dialog.resize(*_OWNER_SIZE)
    _pump()
    next(button for button in dialog.findChildren(QPushButton) if button.text() == "Combat").click()
    _pump()
    skill_list = next(
        widget
        for widget in dialog.findChildren(QListWidget)
        if "Prayer" in {widget.item(i).text() for i in range(widget.count())}
    )
    skill_list.setCurrentRow(next(i for i in range(skill_list.count()) if skill_list.item(i).text() == "Prayer"))
    _pump()
    return dialog


def _visible_gilded_mode(dialog):
    mode = dialog.findChild(QComboBox, "prayerGildedModeCombo")
    return mode if mode is not None and mode.isVisibleTo(dialog) else None


@unittest.skipUnless(_main_menu.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class PrayerPanelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _main_menu.MainMenuWidgetTest.setUpClass()

    def setUp(self) -> None:
        self.menu = _main_menu.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()

    def tearDown(self) -> None:
        self.menu.tearDown()

    def test_bury_hides_the_altar_box_until_a_gilded_target_is_chosen(self) -> None:
        player = _main_menu._make_player_data()
        player.update(prayer_level=99, current_prayer="bury_bones", inventory={"Bones": 30})
        dialog = _open_prayer_panel(self.menu, player)
        panel = dialog.findChild(QWidget, "prayerSkillPanel")

        self.assertEqual(dialog.findChild(QLabel, "prayerMethodStatus").text(), "Bury: Bones · 1x XP")
        self.assertIsNone(_visible_gilded_mode(dialog))
        self.assertEqual(text_fit_defects(panel), [])

        tree = dialog.findChild(QTreeWidget, "prayerTargetTree")
        tree.itemClicked.emit(_main_menu._tree_row(tree, "gilded_altar_bones"), 0)
        _pump()
        panel = dialog.findChild(QWidget, "prayerSkillPanel")

        self.assertEqual(player["current_prayer"], "gilded_altar_bones")
        self.assertEqual(
            dialog.findChild(QLabel, "prayerMethodStatus").text(), "Gilded altar (hosted): Bones · 3.5x XP"
        )
        self.assertEqual(_visible_gilded_mode(dialog).currentText(), "Hosted - 350% XP")
        self.assertEqual(text_fit_defects(panel), [])
        dialog.deleteLater()


if __name__ == "__main__":
    unittest.main()
