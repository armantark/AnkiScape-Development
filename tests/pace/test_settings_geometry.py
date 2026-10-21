"""The Settings page keeps every control usable at laptop window heights."""

from unittest.mock import patch

from tests.pace import test_pace_settings_qt as pace

if pace.HAS_AQT:
    from aqt.qt import QApplication, QCheckBox, QComboBox, QLabel, QPushButton, QScrollArea, QSpinBox, QWidget
    from tests import test_main_menu_widget as menu


class SettingsGeometryTests(pace.PaceQtCase):
    def setUp(self):
        menu.MainMenuWidgetTest.setUpClass()
        self.menu = menu.MainMenuWidgetTest()
        self.menu.setUp()
        self.addCleanup(self.menu.tearDown)

    def _assert_settings_control_heights(self, page) -> None:
        controls = (QLabel, QCheckBox, QPushButton, QSpinBox, QComboBox)
        for control in page.findChildren(QWidget):
            if not control.isVisible() or not isinstance(control, controls):
                continue
            name = control.objectName() or getattr(control, "text", lambda: "")()
            self.assertGreaterEqual(control.height(), control.minimumSizeHint().height(), name)
            if isinstance(control, QLabel) and control.wordWrap():
                self.assertGreaterEqual(control.height(), control.heightForWidth(control.width()), name)

    def test_settings_controls_keep_their_minimum_height_at_laptop_sizes(self) -> None:
        dialog = self.menu._open(menu._make_player_data())
        dialog.show()
        tabs = menu._find_main_tabs(dialog)
        tabs.setCurrentIndex(next(i for i in range(tabs.count()) if tabs.tabText(i) == "Settings"))
        surface = tabs.currentWidget()
        page = surface.widget() if isinstance(surface, QScrollArea) else surface
        follow = page.findChild(QCheckBox, "settingsWorldDayFollowToggle")
        developer = next(box for box in page.findChildren(QCheckBox) if box.text().startswith("Enable developer mode"))
        with patch("ankiscape.core.debug.set_debug_enabled"):
            developer.setChecked(True)
            for following in (True, False):
                follow.setChecked(following)
                for height in (540, 560):
                    dialog.resize(720, height)
                    for _ in range(4):
                        QApplication.processEvents()
                    with self.subTest(following=following, height=height):
                        self.assertEqual((dialog.width(), dialog.height()), (720, height))
                        self._assert_settings_control_heights(page)
        self.assertIsInstance(surface, QScrollArea)
        self.assertEqual(surface.horizontalScrollBar().maximum(), 0)

